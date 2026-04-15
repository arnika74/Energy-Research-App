"""
Concurrent web scraper using BeautifulSoup.
Fetches multiple URLs in parallel via a thread pool for fast execution.
"""

import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from config.settings import REQUEST_TIMEOUT, MAX_CONTENT_LENGTH, SCRAPER_MAX_WORKERS

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
}

_SKIP_DOMAINS = [
    "jstor.org", "sciencedirect.com", "springer.com", "nature.com/articles",
    "facebook.com", "twitter.com", "instagram.com", "linkedin.com", "youtube.com",
    "tiktok.com", "reddit.com",
]


def _should_skip(url: str) -> bool:
    return any(d in url for d in _SKIP_DOMAINS)


def _fetch_one(url: str) -> tuple[str, str | None]:
    """Fetch and extract text from a single URL. Returns (url, text|None)."""
    if _should_skip(url) or not url.startswith("http"):
        return url, None
    try:
        r = requests.get(url, headers=_HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        r.raise_for_status()
        if "text/html" not in r.headers.get("Content-Type", ""):
            return url, None
        return url, _extract_text(r.text)
    except Exception as e:
        logger.debug(f"Scrape failed {url}: {e}")
        return url, None


def _extract_text(html: str) -> str | None:
    """Parse HTML and return clean text, or None if too short."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
        tag.decompose()

    body = (
        soup.find("main")
        or soup.find("article")
        or soup.find(class_=re.compile(r"content|article|post|main", re.I))
        or soup.find("body")
    )
    raw = (body or soup).get_text(separator="\n", strip=True)
    lines = [l.strip() for l in raw.splitlines() if len(l.strip()) > 40]
    text = "\n".join(lines)
    if len(text) < 200:
        return None
    return text[:MAX_CONTENT_LENGTH]


def scrape_urls(urls: List[str], max_sources: int = 5) -> Dict[str, str]:
    """
    Concurrently scrape multiple URLs.
    Returns {url: content} for successful fetches, up to max_sources.
    """
    results: Dict[str, str] = {}
    workers = min(SCRAPER_MAX_WORKERS, len(urls))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_fetch_one, url): url for url in urls}
        for future in as_completed(futures):
            if len(results) >= max_sources:
                # Cancel remaining futures
                for f in futures:
                    f.cancel()
                break
            url, text = future.result()
            if text:
                results[url] = text

    logger.info(f"Scraped {len(results)}/{len(urls)} URLs successfully")
    return results
