"""
Web search tool — DuckDuckGo primary, Wikipedia fallback.
No API key required for either source.
Wikipedia fallback ensures references are always populated even when DuckDuckGo is rate-limited.
"""

import logging
import time
import requests
from typing import List, Dict

logger = logging.getLogger(__name__)

_ENERGY_TERMS = {
    "energy", "solar", "wind", "renewable", "electricity", "power",
    "fuel", "carbon", "climate", "grid", "battery", "hydrogen",
    "nuclear", "geothermal", "hydropower", "biofuel",
}

_WIKI_HEADERS = {"User-Agent": "EnergyResearcher/2.0 (academic-research)"}
_WIKI_API = "https://en.wikipedia.org/w/api.php"


def search(query: str, max_results: int = 8) -> List[Dict]:
    """
    Search the web for the given query.
    Tries DuckDuckGo first (3 attempts with backoff).
    Falls back to Wikipedia if DDG is rate-limited.
    Returns list of {title, url, snippet}.
    """
    has_energy = any(t in query.lower() for t in _ENERGY_TERMS)
    ddg_query = query if has_energy else f"{query} energy"

    # --- Primary: DuckDuckGo ---
    results = _try_duckduckgo(ddg_query, max_results)
    if results:
        return results

    logger.warning("DuckDuckGo unavailable, falling back to Wikipedia search")

    # --- Fallback: Wikipedia ---
    return _search_wikipedia(query, max_results)


def _try_duckduckgo(query: str, max_results: int) -> List[Dict]:
    for attempt in range(3):
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                raw = list(ddgs.text(query, max_results=max_results, safesearch="moderate"))

            results = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
                for r in raw
                if r.get("href")
            ]

            if results:
                logger.info(f"DuckDuckGo returned {len(results)} results (attempt {attempt+1})")
                return results

            logger.warning(f"DuckDuckGo returned empty results on attempt {attempt+1}")
            time.sleep(2 ** attempt)

        except Exception as e:
            err = str(e)
            if "Ratelimit" in err or "202" in err:
                logger.warning(f"DuckDuckGo rate-limited on attempt {attempt+1}")
            else:
                logger.warning(f"DuckDuckGo error on attempt {attempt+1}: {err}")
            if attempt < 2:
                time.sleep(2 ** attempt)

    return []


def _search_wikipedia(query: str, max_results: int) -> List[Dict]:
    """
    Search Wikipedia using the MediaWiki API.
    Returns results with full URL, title, and article intro as snippet.
    """
    try:
        # Step 1: Find matching article titles
        search_resp = requests.get(
            _WIKI_API,
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "srprop": "snippet",
                "format": "json",
            },
            headers=_WIKI_HEADERS,
            timeout=8,
        )
        search_resp.raise_for_status()
        search_data = search_resp.json()
        hits = search_data.get("query", {}).get("search", [])

        if not hits:
            logger.warning(f"Wikipedia found no results for: {query!r}")
            return []

        titles = [h["title"] for h in hits[:max_results]]

        # Step 2: Fetch intro extracts for all matching articles in one call
        extract_resp = requests.get(
            _WIKI_API,
            params={
                "action": "query",
                "titles": "|".join(titles),
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "exsentences": 4,
                "format": "json",
            },
            headers=_WIKI_HEADERS,
            timeout=8,
        )
        extract_resp.raise_for_status()
        pages = extract_resp.json().get("query", {}).get("pages", {})

        # Build result list, preserving search order
        page_by_title = {p["title"]: p for p in pages.values()}
        results: List[Dict] = []
        for title in titles:
            page = page_by_title.get(title, {})
            extract = page.get("extract", "").strip()
            snippet = extract[:250] if extract else ""
            url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
            results.append({
                "title": title,
                "url": url,
                "snippet": snippet,
            })

        logger.info(f"Wikipedia fallback returned {len(results)} results for: {query!r}")
        return results

    except Exception as e:
        logger.error(f"Wikipedia fallback failed: {e}")
        return []
