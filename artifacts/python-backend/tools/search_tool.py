"""
DuckDuckGo web search — no API key required.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

_ENERGY_TERMS = {"energy", "solar", "wind", "renewable", "electricity", "power",
                  "fuel", "carbon", "climate", "grid", "battery", "hydrogen"}


def search(query: str, max_results: int = 8) -> List[Dict]:
    """
    Search DuckDuckGo and return results as list of {title, url, snippet}.
    Automatically appends 'energy' context if query lacks energy keywords.
    """
    has_energy = any(t in query.lower() for t in _ENERGY_TERMS)
    search_query = query if has_energy else f"{query} energy"

    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            raw = list(ddgs.text(search_query, max_results=max_results, safesearch="moderate"))

        results = [
            {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
            for r in raw
        ]
        logger.info(f"Search returned {len(results)} results for: {query!r}")
        return results
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return []
