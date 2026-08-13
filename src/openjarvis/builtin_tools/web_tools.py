import httpx
import re
from html.parser import HTMLParser
from openjarvis.tools import tool

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
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
        from duckduckgo_search import DDGS

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
