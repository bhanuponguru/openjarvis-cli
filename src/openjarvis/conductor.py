import json
import re
from collections.abc import Generator, Iterator
from pathlib import Path

from openjarvis.config_loader import get_delegation_mask, load_config
from openjarvis.parser import is_route_tag, parse_route_tag
from openjarvis.providers import call_llm, call_llm_stream
from openjarvis.types import ConductorConfig, SpecialistConfig

# A routing tag always starts at the beginning of a line.
_TAG_START = re.compile(r"(?:^|(?<=\n))[ \t]*\[[^\n]*$")


def _stream_without_tag(deltas: Iterator[str]) -> Iterator[tuple[str, str]]:
    """Pass deltas through while withholding a possibly-incomplete routing tag.

    Tags arrive at the very end of a stream and split across arbitrary chunk
    boundaries, so a naive filter shows the user ``[ROUTE: ma`` before it can
    tell what it is. The invariant here: never emit text from the last
    line-initial ``[`` onward until the line completes. If the completed line is
    a tag it is dropped; otherwise it is released intact.

    Yields ``(raw_delta, text_to_emit)``; ``text_to_emit`` is ``""`` when the
    chunk is entirely withheld. The caller reassembles the raw text for parsing.
    """
    pending = ""   # accumulated-but-unemitted tail
    for delta in deltas:
        pending += delta
        match = _TAG_START.search(pending)
        # Everything before a candidate tag start is safe to show now.
        safe_upto = match.start() if match else len(pending)
        emit, pending = pending[:safe_upto], pending[safe_upto:]

        # A withheld line that has completed and is NOT a tag gets released.
        if pending and "\n" in pending:
            line, rest = pending.split("\n", 1)
            if not is_route_tag(line):
                emit += line + "\n"
            pending = rest

        yield delta, emit

    # End of stream: release the tail unless it is the routing tag itself.
    if pending and not is_route_tag(pending):
        yield "", pending


class Conductor:
    """OpenJarvis Conductor — state machine routing through generalist + specialists.

    The conductor is the main loop of the OpenJarvis system:
      1. User sends a message
      2. Generalist LLM responds with a routing tag ([ROUTE: return] or [ROUTE: specialist])
      3. If routed, a specialist LLM handles the request and can return ([RETURN])
         or delegate ([DELEGATE: X]) to another specialist
      4. Delegation is enforced against the delegation mask from config
      5. The whole exchange is capped at ``config.max_hops`` LLM calls
    """

    def __init__(
        self,
        config_path: str | None = None,
        config: ConductorConfig | None = None,
    ) -> None:
        """Initialize conductor with either a config path or a ConductorConfig.

        Args:
            config_path: Path to a YAML config file (loaded via load_config).
            config: A pre-built ConductorConfig instance.
        """
        if config_path:
            self.config = load_config(config_path)
        elif config:
            self.config = config
        else:
            self.config = load_config("specialists.yaml")
        self.history: list[dict] = []
        self._delegation_mask = get_delegation_mask(self.config.specialists)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_api_key(self, specialist_name: str) -> str | None:
        """Get API key from environment variable for a specialist."""
        import os

        spec = self._get_specialist(specialist_name)
        if spec and spec.api_key_env:
            return os.environ.get(spec.api_key_env)
        return None

    def _get_specialist(self, name: str) -> SpecialistConfig | None:
        """Resolve a role name to its SpecialistConfig."""
        if name == "generalist" or name == self.config.generalist.name:
            return self.config.generalist
        return self.config.specialists.get(name)

    def _format_history(self) -> list[dict]:
        """Project internal history onto the roles a chat API actually accepts.

        Internally each turn is tagged with its *speaker* ("generalist", "math",
        ...), which is what the routing state machine needs. Chat APIs accept
        only system/user/assistant/tool, so every model turn maps to
        ``assistant`` with the speaker preserved as a ``[name]:`` content prefix.
        That keeps multi-participant identity legible to the next model without
        sending a role the server will reject.

        The ``route`` key is metadata and is never sent.
        """
        messages: list[dict] = []
        for msg in self.history:
            role, content = msg["role"], msg["content"]
            if role in ("user", "system"):
                messages.append({"role": role, "content": content})
            else:
                messages.append({"role": "assistant", "content": f"[{role}]: {content}"})
        return messages

    def _final_answer_prompt(self) -> str:
        return (
            "[Hop limit reached. Stop routing and answer the user directly using "
            "everything discussed so far. End your reply with [ROUTE: return].]"
        )

    def _forced_final(self, error_prefix: str) -> tuple[str, str | None]:
        """Make one last generalist call that is instructed to answer, not route.

        Returns (content, error). Used when the hop cap is hit -- a degraded but
        real answer is better for the user than an exception or a silent hang.
        """
        self.history.append(
            {"role": "system", "content": self._final_answer_prompt(), "route": None}
        )
        try:
            response = call_llm(
                self._format_history(),
                self.config.generalist,
                api_key=self._get_api_key("generalist"),
            )
        except Exception as exc:
            return "", f"{error_prefix}: {exc}"

        content, _ = parse_route_tag(response)
        self.history.append({"role": "generalist", "content": content, "route": "return"})
        return content, None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, message: str) -> Generator[dict, None, str]:
        """Send a user message and run the delegation loop.

        This is a **generator** that yields intermediate events and
        returns the final response string.

        **Yielded events (dict):**

        ============== =================================================
        ``type``        Description
        ============== =================================================
        ``"route"``     A routing/delegation decision (keys:
                        ``from_role``, ``to_role``).
        ``"intermediate"``  Intermediate response from a model (keys:
                            ``role``, ``content``).
        ``"final"``     The final response returned to the user (key:
                        ``content``).
        ``"error"``     An error occurred (key: ``content``).
        ============== =================================================

        Args:
            message: The user's input message.

        Yields:
            Event dicts as described above.

        Returns:
            The final response string.
        """
        self.history.append({"role": "user", "content": message, "route": None})

        current_role = "generalist"
        hops = 0

        while True:
            if hops >= self.config.max_hops:
                yield {
                    "type": "error",
                    "content": (
                        f"Hop limit of {self.config.max_hops} reached; forcing a "
                        "final answer from the generalist."
                    ),
                }
                content, error = self._forced_final("Error calling generalist")
                if error:
                    yield {"type": "error", "content": error}
                    return error
                yield {"type": "final", "content": content, "role": "generalist"}
                return content

            specialist_config = self._get_specialist(current_role)
            if specialist_config is None:
                error_msg = f"Unknown role '{current_role}' — no config found."
                yield {"type": "error", "content": error_msg}
                return error_msg

            # Build conversation history for this turn
            messages = self._format_history()

            # Call the LLM
            try:
                api_key = self._get_api_key(current_role)
                response = call_llm(messages, specialist_config, api_key=api_key)
            except Exception as exc:
                error_msg = f"Error calling {current_role}: {exc}"
                yield {"type": "error", "content": error_msg}
                return error_msg
            hops += 1

            # Parse the routing tag from the response
            is_generalist = current_role == "generalist"
            cleaned_content, route_target = parse_route_tag(response)

            # Append the model's response to conversation history
            self.history.append(
                {
                    "role": current_role,
                    "content": cleaned_content,
                    "route": route_target,
                }
            )

            # --- Handle "return": generalist return yields final; specialist return goes back to generalist ---
            if route_target == "return":
                if is_generalist:
                    yield {"type": "final", "content": cleaned_content, "role": current_role}
                    return cleaned_content
                else:
                    yield {"type": "route", "from_role": current_role, "to_role": "generalist"}
                    yield {"type": "intermediate", "role": current_role, "content": cleaned_content}
                    current_role = "generalist"
                    continue

            target_role = route_target

            # --- A generalist routing to itself makes zero progress ---
            if is_generalist and target_role == "generalist":
                error_msg = "The generalist routed to itself; treating as a final answer."
                yield {"type": "error", "content": error_msg}
                yield {"type": "final", "content": cleaned_content, "role": current_role}
                return cleaned_content

            # --- Validate that the target specialist exists ---
            if target_role not in self.config.specialists and target_role != "generalist":
                error_msg = f"Cannot route to '{target_role}': unknown specialist."
                yield {"type": "error", "content": error_msg}

                # Inject a system message so the generalist knows what happened
                self.history.append(
                    {
                        "role": "system",
                        "content": (
                            f"[The {current_role} tried to route to '{target_role}' "
                            "which does not exist. You are the generalist — handle this.]"
                        ),
                        "route": None,
                    }
                )
                previous_role = current_role
                current_role = "generalist"
                yield {"type": "route", "from_role": previous_role, "to_role": "generalist"}
                continue

            # --- Enforce delegation mask (specialist → specialist only) ---
            if not is_generalist:
                allowed = self._delegation_mask.get(current_role, [])
                if target_role not in allowed:
                    error_msg = (
                        f"'{current_role}' cannot delegate to '{target_role}'. "
                        f"Allowed targets: {allowed}"
                    )
                    yield {"type": "error", "content": error_msg}

                    self.history.append(
                        {
                            "role": "system",
                            "content": (
                                f"[The {current_role} specialist attempted to "
                                f"delegate to {target_role}, which is not permitted. "
                                "You are the generalist — handle this.]"
                            ),
                            "route": None,
                        }
                    )
                    previous_role = current_role
                    current_role = "generalist"
                    yield {"type": "route", "from_role": previous_role, "to_role": "generalist"}
                    continue

            # --- Route to the target ---
            yield {"type": "route", "from_role": current_role, "to_role": target_role}
            yield {"type": "intermediate", "role": current_role, "content": cleaned_content}
            current_role = target_role

    def chat_stream(self, message: str) -> Iterator[str]:
        """Run the routing loop, streaming generalist turns as they are produced.

        Design note: the routing protocol puts the tag at the END of a response,
        so a turn's role (routing vs. final) is not knowable until it is over.
        Two designs are possible, and this picks the cheaper one:

        - Buffer every generalist turn, then re-issue the final one with
          ``stream: true``. True token streaming, but it calls the generalist
          twice for every message -- real money, and the second call can
          disagree with the first.
        - Stream each generalist turn once, live. A turn that turns out to be a
          routing hop has its narration ("Let me check with the math
          specialist") shown to the user, which :meth:`chat` already surfaces as
          an ``intermediate`` event anyway.

        Specialist turns are never streamed -- their output is internal.
        The routing tag itself is always suppressed.

        Args:
            message: The user's input message.

        Yields:
            Content deltas of the generalist's output.
        """
        self.history.append({"role": "user", "content": message, "route": None})

        current_role = "generalist"
        hops = 0

        while True:
            if hops >= self.config.max_hops:
                content, error = self._forced_final("Error calling generalist")
                yield error if error else content
                return

            specialist_config = self._get_specialist(current_role)
            if specialist_config is None:
                yield f"[error] Unknown role '{current_role}' — no config found."
                return

            is_generalist = current_role == "generalist"
            messages = self._format_history()
            api_key = self._get_api_key(current_role)

            try:
                if is_generalist:
                    chunks: list[str] = []
                    for delta, emit in _stream_without_tag(
                        call_llm_stream(messages, specialist_config, api_key=api_key)
                    ):
                        chunks.append(delta)
                        if emit:
                            yield emit
                    response = "".join(chunks)
                else:
                    response = call_llm(messages, specialist_config, api_key=api_key)
            except Exception as exc:
                yield f"[error] Error calling {current_role}: {exc}"
                return
            hops += 1

            cleaned_content, route_target = parse_route_tag(response)
            self.history.append(
                {"role": current_role, "content": cleaned_content, "route": route_target}
            )

            if route_target == "return":
                if is_generalist:
                    return
                current_role = "generalist"
                continue

            if is_generalist and route_target == "generalist":
                return  # self-route makes no progress; the text is already streamed

            if route_target not in self.config.specialists:
                self.history.append(
                    {
                        "role": "system",
                        "content": (
                            f"[The {current_role} tried to route to '{route_target}' "
                            "which does not exist. You are the generalist — handle this.]"
                        ),
                        "route": None,
                    }
                )
                current_role = "generalist"
                continue

            if not is_generalist and route_target not in self._delegation_mask.get(current_role, []):
                self.history.append(
                    {
                        "role": "system",
                        "content": (
                            f"[The {current_role} specialist attempted to delegate to "
                            f"{route_target}, which is not permitted. You are the "
                            "generalist — handle this.]"
                        ),
                        "route": None,
                    }
                )
                current_role = "generalist"
                continue

            current_role = route_target

    def save_history(self, path: str) -> None:
        """Save conversation history to a JSON file.

        Args:
            path: Filesystem path for the JSON output.
        """
        Path(path).write_text(json.dumps(self.history, indent=2))

    def load_history(self, path: str) -> None:
        """Load conversation history from a JSON file.

        Args:
            path: Filesystem path to read.
        """
        self.history = json.loads(Path(path).read_text())
