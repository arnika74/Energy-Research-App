"""
Research Agent — responsible for searching the web and extracting content.
Pipeline: DuckDuckGo search → URL collection → Web scraping → Content cleaning
"""

import logging
from typing import List, Dict, Callable, Optional

from tools.search_tool import search_energy_topics
from tools.scraper_tool import scrape_multiple_urls

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Agent 1: Performs web search and content extraction.
    Collects raw information from multiple web sources.
    """

    def __init__(self, max_sources: int = 5):
        """
        Initialize the Research Agent.

        Args:
            max_sources: Maximum number of web sources to scrape
        """
        self.max_sources = max_sources

    def run(
        self,
        query: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict:
        """
        Execute the full research pipeline for a given query.

        Args:
            query: The energy research query from the user
            progress_callback: Optional function to report progress status

        Returns:
            Dict with search_results, scraped_content, urls
        """
        def notify(msg: str):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        notify(f"🔍 Searching the web for: {query}")

        # Step 1: Search DuckDuckGo
        search_results = search_energy_topics(query, max_results=self.max_sources + 3)

        if not search_results:
            logger.warning("No search results found")
            return {
                "search_results": [],
                "scraped_content": {},
                "urls": [],
            }

        notify(f"📋 Found {len(search_results)} search results, extracting content...")

        # Step 2: Extract URLs from search results
        urls = [r["url"] for r in search_results if r.get("url")]

        # Step 3: Scrape content from web pages
        scraped_content = scrape_multiple_urls(urls, max_sources=self.max_sources)

        notify(
            f"✅ Extracted content from {len(scraped_content)} sources"
        )

        return {
            "search_results": search_results,
            "scraped_content": scraped_content,
            "urls": list(scraped_content.keys()),
        }
