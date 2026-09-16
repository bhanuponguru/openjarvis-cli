import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import httpx
import yaml

from openjarvis.tools import tool


class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.convert_charrefs = True
        self.text = []
        self.skip_content = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip_content = True

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self.skip_content = False

    def handle_data(self, data):
        if not self.skip_content:
            self.text.append(data)

    def get_data(self):
        return "".join(self.text)

@tool()
def fetch_url(url: str, timeout: int = 15) -> str:
    """Fetch the content of a URL.

    Args:
        url: URL to fetch (must start with http:// or https://).
        timeout: Request timeout in seconds.

    Returns:
        Page text with HTML tags removed, truncated to 8000 characters.
    """
    if not url.startswith(("http://", "https://")):
        return "Error: URL must start with http:// or https://"

    try:
        response = httpx.get(url, timeout=timeout, follow_redirects=True)
        response.raise_for_status()

        html = response.text
        stripper = HTMLStripper()
        stripper.feed(html)
        text = stripper.get_data()

        text = re.sub(r"\s+", " ", text).strip()

        if len(text) > 8000:
            text = text[:8000] + "\n... [truncated at 8000 chars]"

        return text
    except httpx.HTTPError as e:
        return f"Error fetching URL: {e}"
    except Exception as e:
        return f"Error: {e}"

@tool()
def search_web(query: str, num_results: int = 5) -> list[dict]:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query string.
        num_results: Number of results to return (default 5, max 20).

    Returns:
        List of dicts with 'title', 'url', and 'snippet' keys.
    """
    if num_results > 20:
        num_results = 20

    try:
        from ddgs import DDGS

        results = []
        ddgs = DDGS(timeout=10)
        for result in ddgs.text(query, max_results=num_results):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", ""),
            })
        return results if results else [{"error": "No results found"}]
    except ImportError:
        return [{"error": "duckduckgo-search not installed"}]
    except Exception as e:
        return [{"error": str(e)}]

@tool()
def fetch_wikipedia(topic: str, sentences: int = 5) -> str:
    """Fetch a Wikipedia summary for a topic.

    Args:
        topic: Topic name to search for.
        sentences: Number of sentences to return (max 10).

    Returns:
        Wikipedia summary text.
    """
    if sentences > 10:
        sentences = 10

    try:
        response = httpx.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + topic.replace(" ", "_"),
            timeout=15,
            headers={"User-Agent": "OpenJarvis/1.0"},
        )
        response.raise_for_status()

        data = response.json()
        if "extract" in data:
            extract = data["extract"]
            sent_list = extract.split(". ")[:sentences]
            return ". ".join(sent_list) + "."
        else:
            return f"Error: Wikipedia article not found for '{topic}'"
    except httpx.HTTPError as e:
        return f"Error fetching Wikipedia: {e}"
    except Exception as e:
        return f"Error: {e}"


@tool()
def http_request(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    data: str | None = None,
    json_data: dict[str, Any] | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    """Execute an HTTP/REST API request.

    Args:
        url: Full destination URL (must start with http:// or https://).
        method: HTTP method: GET, POST, PUT, DELETE, PATCH, or HEAD (default "GET").
        headers: Optional key-value mapping of HTTP request headers.
        params: Optional key-value query string parameters.
        data: Optional raw string body payload (for form data or plain text).
        json_data: Optional JSON payload dict (automatically serialized and sent with application/json).
        timeout: Request timeout in seconds (default 15).

    Returns:
        Dict with 'status_code', 'body' (parsed JSON or text capped at 8000 chars), and 'headers'.
    """
    if not url.startswith(("http://", "https://")):
        return {"error": "URL must start with http:// or https://"}

    clean_method = method.strip().upper()
    valid_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"}
    if clean_method not in valid_methods:
        return {"error": f"Unsupported HTTP method '{method}'. Valid: {', '.join(sorted(valid_methods))}"}

    try:
        req_headers = dict(headers or {})
        if "User-Agent" not in req_headers:
            req_headers["User-Agent"] = "OpenJarvis-Client/1.0"

        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.request(
                clean_method,
                url,
                headers=req_headers,
                params=params,
                content=data,
                json=json_data,
            )

        resp_headers = dict(response.headers)
        content_type = resp_headers.get("content-type", "").lower()

        parsed_body: Any
        if "application/json" in content_type:
            try:
                parsed_body = response.json()
            except Exception:
                parsed_body = response.text
        else:
            parsed_body = response.text

        if isinstance(parsed_body, str) and len(parsed_body) > 8000:
            parsed_body = parsed_body[:8000] + "\n... [truncated at 8000 chars]"

        return {
            "status_code": response.status_code,
            "headers": {k: v for k, v in resp_headers.items() if k.lower() in ("content-type", "date", "server")},
            "body": parsed_body,
        }
    except httpx.TimeoutException:
        return {"error": f"Request timed out after {timeout} seconds"}
    except httpx.HTTPError as exc:
        return {"error": f"HTTP error occurred: {exc}"}
    except Exception as exc:
        return {"error": f"Request failed: {exc}"}


@tool()
def parse_openapi_spec(
    spec_text: str | None = None,
    spec_path: str | None = None,
) -> dict[str, Any]:
    """Parse an OpenAPI or Swagger 2.0/3.0 specification from text or file.

    Args:
        spec_text: OpenAPI or Swagger specification in JSON or YAML string format.
        spec_path: Optional path to an OpenAPI JSON or YAML file.

    Returns:
        Dict summarizing API info, version, and structured list of endpoints with methods and descriptions.
    """
    raw_content = ""
    if spec_text:
        raw_content = spec_text
    elif spec_path:
        p = Path(spec_path)
        if not p.exists():
            return {"error": f"Specification file '{spec_path}' not found."}
        try:
            raw_content = p.read_text(encoding="utf-8")
        except Exception as exc:
            return {"error": f"Failed to read specification file: {exc}"}
    else:
        return {"error": "Either 'spec_text' or 'spec_path' must be provided."}

    try:
        data = yaml.safe_load(raw_content)
    except Exception as exc:
        return {"error": f"Failed to parse OpenAPI YAML/JSON: {exc}"}

    if not isinstance(data, dict):
        return {"error": "OpenAPI specification must be a JSON/YAML object mapping."}

    info = data.get("info", {})
    title = info.get("title", "Unknown API")
    version = info.get("version", "unknown")
    openapi_version = data.get("openapi") or data.get("swagger", "unknown")

    endpoints: list[dict[str, Any]] = []
    paths = data.get("paths", {})
    if isinstance(paths, dict):
        for path_key, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if method.lower() not in {"get", "post", "put", "delete", "patch", "options", "head"}:
                    continue
                if isinstance(operation, dict):
                    endpoints.append({
                        "path": path_key,
                        "method": method.upper(),
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", "")[:200],
                        "operation_id": operation.get("operationId", ""),
                        "parameters": [
                            {
                                "name": p.get("name"),
                                "in": p.get("in"),
                                "required": p.get("required", False),
                                "description": p.get("description", ""),
                            }
                            for p in operation.get("parameters", [])
                            if isinstance(p, dict)
                        ],
                    })

    return {
        "title": title,
        "version": version,
        "openapi_version": openapi_version,
        "total_endpoints": len(endpoints),
        "endpoints": endpoints[:50],
    }
