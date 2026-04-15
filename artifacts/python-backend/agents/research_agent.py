"""
Research Agent — searches the web and extracts content concurrently.
"""

import logging
from typing import Callable, Dict, Optional

from tools.search_tool import search
from tools.scraper_tool import scrape_urls

logger = logging.getLogger(__name__)


class ResearchAgent:
    def __init__(self, max_sources: int = 5):
        self.max_sources = max_sources

    def run(self, query: str, progress_cb: Optional[Callable[[str], None]] = None) -> Dict:
        def notify(msg: str):
            logger.info(msg)
            if progress_cb:
                progress_cb(msg)

        notify("🔍 Searching the web...")
        search_results = search(query, max_results=self.max_sources + 3)

        if not search_results:
            logger.warning("No search results found")
            return {"search_results": [], "scraped_content": {}, "urls": []}

        notify(f"📥 Fetching content from {len(search_results)} sources...")
        urls = [r["url"] for r in search_results if r.get("url")]
        scraped_content = scrape_urls(urls, max_sources=self.max_sources)

        notify(f"✅ Collected {len(scraped_content)} sources")
        return {
            "search_results": search_results,
            "scraped_content": scraped_content,
            "urls": list(scraped_content.keys()),
        }
