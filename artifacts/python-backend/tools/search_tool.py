"""
Web Search Tool using DuckDuckGo (free, no API key required).
Returns a list of search result dicts with title, url, and snippet.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def duckduckgo_search(query: str, max_results: int = 8) -> List[Dict]:
    """
    Search DuckDuckGo and return top results.

    Args:
        query: The search query string
        max_results: Maximum number of results to return

    Returns:
        List of dicts with keys: title, url, snippet
    """
    results = []

    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            search_results = list(
                ddgs.text(
                    query,
                    max_results=max_results,
                    safesearch="moderate",
                )
            )

        for item in search_results:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", ""),
                }
            )

        logger.info(f"DuckDuckGo search returned {len(results)} results for: {query}")
        return results

    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return []


def search_energy_topics(query: str, max_results: int = 8) -> List[Dict]:
    """
    Enhanced energy-focused search — appends 'energy' context to generic queries.

    Args:
        query: Raw user query
        max_results: Max results to return

    Returns:
        List of search result dicts
    """
    energy_terms = ["energy", "solar", "wind", "renewable", "electricity", "power", "fuel"]
    has_energy_term = any(term.lower() in query.lower() for term in energy_terms)

    search_query = query if has_energy_term else f"{query} energy"

    return duckduckgo_search(search_query, max_results=max_results)
