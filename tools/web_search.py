import time

from ddgs import DDGS
from ddgs.exceptions import DDGSException


SEARCH_RETRY_COUNT = 3
SEARCH_BACKOFF_BASE = 1.5
SEARCH_REGIONS = ["wt-wt", "us-en", "uk-en"]
SEARCH_BACKENDS = ["auto", "duckduckgo", "bing"]


def search_web(
    query: str,
    max_results: int = 5,
) -> dict[str, object]:
    """
    Search the web using the DuckDuckGo backend.

    Args:
        query: Words or a question to search for.
        max_results: Maximum number of results to return (1-8).

    Returns:
        A dictionary containing the query and search results.
    """

    cleaned_query = (query or "").strip()

    if not cleaned_query:
        return {
            "query": query,
            "results": [],
            "error": "The search query was empty.",
        }

    # The model may send a string or nothing; always end up with 1-8.
    try:
        requested = int(max_results)
    except (TypeError, ValueError):
        requested = 5

    result_limit = max(1, min(requested, 8))

    raw_results = []
    last_error = None

    for backend in SEARCH_BACKENDS:
        for attempt in range(SEARCH_RETRY_COUNT):
            region = SEARCH_REGIONS[attempt % len(SEARCH_REGIONS)]
            backoff = SEARCH_BACKOFF_BASE ** attempt

            try:
                raw_results = DDGS(timeout=10).text(
                    query=cleaned_query,
                    region=region,
                    safesearch="moderate",
                    max_results=result_limit,
                    backend=backend,
                )
                break
            except DDGSException as error:
                last_error = error
                if attempt < SEARCH_RETRY_COUNT - 1:
                    time.sleep(backoff)
                continue
            except Exception as error:
                return {
                    "query": cleaned_query,
                    "results": [],
                    "error": f"Web search failed: {error}",
                }

        if raw_results:
            break

    if not raw_results:
        return {
            "query": cleaned_query,
            "results": [],
            "error": f"Web search failed: {last_error}",
        }

    cleaned_results = [
        {
            "title": result.get("title", ""),
            "url": result.get("href", ""),
            "snippet": result.get("body", ""),
        }
        for result in raw_results
    ]

    return {
        "query": cleaned_query,
        "results": cleaned_results,
    }


SEARCH_WEB_TOOL = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": (
            "Search the public web using DuckDuckGo. "
            "Use this when the user asks about current events, "
            "recent information, changing facts, prices, releases, "
            "schedules, or information you are uncertain about."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A short and specific web-search query.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Number of search results to return.",
                    "minimum": 1,
                    "maximum": 8,
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}
