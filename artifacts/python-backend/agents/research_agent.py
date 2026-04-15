"""
Research Agent — searches the web and extracts limited high-quality sources.
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

        # ✅ STRICT LIMIT: only top results
        search_results = search(query, max_results=self.max_sources)

        if not search_results:
            return {"search_results": [], "scraped_content": {}, "urls": []}

        # ✅ keep only top N URLs
        urls = [r["url"] for r in search_results[:self.max_sources] if r.get("url")]

        notify(f"📥 Scraping top {len(urls)} sources...")

        scraped_content = scrape_urls(urls, max_sources=self.max_sources)

        notify(f"✅ Collected {len(scraped_content)} sources")

        return {
            "search_results": search_results[:self.max_sources],
            "scraped_content": scraped_content,
            "urls": list(scraped_content.keys()),
        }