"""
Analysis Agent — responsible for processing and organizing raw scraped content.
Filters irrelevant content, extracts key points, and prepares data for the Summary Agent.
"""

import logging
import re
from typing import List, Dict, Callable, Optional

logger = logging.getLogger(__name__)

# Keywords indicating relevant energy content
ENERGY_KEYWORDS = [
    "energy", "solar", "wind", "renewable", "electricity", "power", "fuel",
    "carbon", "emission", "fossil", "oil", "gas", "nuclear", "hydrogen",
    "battery", "storage", "grid", "efficiency", "sustainability", "climate",
    "transition", "generation", "consumption", "kilowatt", "megawatt",
    "photovoltaic", "turbine", "biofuel", "geothermal", "hydropower",
]


class AnalysisAgent:
    """
    Agent 2: Analyzes and filters scraped content.
    Removes irrelevant information, extracts key facts, and structures data.
    """

    def run(
        self,
        query: str,
        research_data: Dict,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict:
        """
        Analyze and process research data.

        Args:
            query: The original research query
            research_data: Output from ResearchAgent (search_results, scraped_content, urls)
            progress_callback: Optional function to report progress

        Returns:
            Dict with filtered_content, key_points, source_metadata
        """
        def notify(msg: str):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        notify("🧠 Analyzing and filtering extracted content...")

        scraped_content = research_data.get("scraped_content", {})
        search_results = research_data.get("search_results", [])

        # Step 1: Filter content by relevance to energy topics
        filtered_content = self._filter_relevant_content(scraped_content, query)

        notify(f"📊 Kept {len(filtered_content)} relevant sources after filtering...")

        # Step 2: Extract key points from each source
        key_points = self._extract_key_points(filtered_content, query)

        # Step 3: Build source metadata from search results
        source_metadata = self._build_source_metadata(search_results, filtered_content)

        notify(f"✅ Analysis complete — {len(key_points)} key points extracted")

        return {
            "filtered_content": filtered_content,
            "key_points": key_points,
            "source_metadata": source_metadata,
        }

    def _filter_relevant_content(
        self, scraped_content: Dict[str, str], query: str
    ) -> Dict[str, str]:
        """
        Keep only content that is relevant to energy topics.
        Scores each page by keyword occurrence.
        """
        # Extract query-specific terms
        query_terms = [
            w.lower() for w in query.split() if len(w) > 3
        ]
        all_terms = ENERGY_KEYWORDS + query_terms

        scored = {}
        for url, content in scraped_content.items():
            content_lower = content.lower()
            score = sum(
                content_lower.count(term) for term in all_terms
            )
            if score > 2:  # Minimum relevance threshold
                scored[url] = (score, content)

        # Sort by relevance score and return top sources
        sorted_urls = sorted(scored.keys(), key=lambda u: scored[u][0], reverse=True)
        return {url: scored[url][1] for url in sorted_urls[:6]}

    def _extract_key_points(
        self, filtered_content: Dict[str, str], query: str
    ) -> List[str]:
        """
        Extract factual sentences from each source that are relevant to the query.
        Uses keyword matching to identify informative sentences.
        """
        query_terms = [w.lower() for w in query.split() if len(w) > 3]
        all_terms = set(ENERGY_KEYWORDS + query_terms)

        key_points = []
        seen = set()

        for url, content in filtered_content.items():
            sentences = re.split(r"(?<=[.!?])\s+", content)

            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 60 or len(sentence) > 500:
                    continue

                # Check relevance
                sentence_lower = sentence.lower()
                term_count = sum(1 for t in all_terms if t in sentence_lower)

                if term_count >= 2 and sentence not in seen:
                    seen.add(sentence)
                    key_points.append(sentence)

                if len(key_points) >= 20:
                    break

            if len(key_points) >= 20:
                break

        return key_points[:15]  # Return top 15 key points

    def _build_source_metadata(
        self,
        search_results: List[Dict],
        filtered_content: Dict[str, str],
    ) -> List[Dict]:
        """
        Build reference metadata from search results, only for sources with content.
        """
        filtered_urls = set(filtered_content.keys())
        metadata = []

        for result in search_results:
            url = result.get("url", "")
            if url in filtered_urls or not filtered_content:
                metadata.append(
                    {
                        "url": url,
                        "title": result.get("title", url),
                        "snippet": result.get("snippet", ""),
                    }
                )

        # Also include any scraped URLs not in search results
        search_urls = {r.get("url") for r in search_results}
        for url in filtered_urls:
            if url not in search_urls:
                metadata.append(
                    {
                        "url": url,
                        "title": url,
                        "snippet": "",
                    }
                )

        return metadata[:10]
