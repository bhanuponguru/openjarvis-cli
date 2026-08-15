import csv
import io
import json
import re

from openjarvis.tools import tool


@tool()
def parse_json(json_str: str) -> str:
    """Parse and pretty-print JSON.

    Args:
        json_str: JSON string to parse.

    Returns:
        Pretty-printed JSON or error message.
    """
    try:
        data = json.loads(json_str)
        return json.dumps(data, indent=2)
    except json.JSONDecodeError as e:
        return f"JSON Error: {e}"
    except Exception as e:
        return f"Error: {e}"

@tool()
def jq_query(json_str: str, path: str) -> str:
    """Query JSON using dot notation.

    Args:
        json_str: JSON string to query.
        path: Dot-notation path (e.g., "users.0.name" or "data.items").

    Returns:
        Result as JSON string or error message.
    """
    try:
        data = json.loads(json_str)

        keys = path.split(".")
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key, None)
            elif isinstance(data, list):
                try:
                    index = int(key)
                    data = data[index] if 0 <= index < len(data) else None
                except (ValueError, IndexError):
                    data = None

            if data is None:
                return f"Path '{path}' not found"

        return json.dumps(data, indent=2) if data is not None else "null"
    except json.JSONDecodeError as e:
        return f"JSON Error: {e}"
    except Exception as e:
        return f"Error: {e}"

@tool()
def parse_csv(csv_str: str, delimiter: str = ",") -> str:
    """Parse CSV and return as markdown table.

    Args:
        csv_str: CSV string to parse.
        delimiter: Field delimiter (default ",").

    Returns:
        Markdown table string (limited to first 20 rows).
    """
    try:
        reader = csv.reader(io.StringIO(csv_str), delimiter=delimiter)
        rows = list(reader)

        if not rows:
            return "Error: Empty CSV"

        if len(rows) > 20:
            rows = rows[:20]
            truncated = "\n\n... [truncated to 20 rows]"
        else:
            truncated = ""

        header = rows[0]
        markdown = "| " + " | ".join(header) + " |\n"
        markdown += "|" + "|".join(["---"] * len(header)) + "|\n"

        for row in rows[1:]:
            padded_row = row + [""] * (len(header) - len(row))
            markdown += "| " + " | ".join(padded_row[:len(header)]) + " |\n"

        return markdown + truncated
    except Exception as e:
        return f"Error parsing CSV: {e}"

@tool()
def regex_search(pattern: str, text: str) -> list[str]:
    """Search for regex pattern matches in text.

    Args:
        pattern: Regular expression pattern.
        text: Text to search in.

    Returns:
        List of matching strings (limited to first 20 matches).
    """
    try:
        matches = re.findall(pattern, text)
        return matches[:20] if matches else ["No matches found"]
    except re.error as e:
        return [f"Regex Error: {e}"]
    except Exception as e:
        return [f"Error: {e}"]

@tool()
def regex_replace(pattern: str, replacement: str, text: str) -> str:
    """Replace text matching a regex pattern.

    Args:
        pattern: Regular expression pattern to match.
        replacement: Replacement string.
        text: Text to perform replacement in.

    Returns:
        Modified text.
    """
    try:
        result = re.sub(pattern, replacement, text)
        return result
    except re.error as e:
        return f"Regex Error: {e}"
    except Exception as e:
        return f"Error: {e}"
