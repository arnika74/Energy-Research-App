"""
Analysis Agent — extracts clean, high-quality key insights + sources.
"""

import logging
import re
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AnalysisAgent:
    def run(
        self,
        query: str,
        research_data: Dict,
        progress_cb: Optional[Callable[[str], None]] = None,
    ) -> Dict:

        def notify(msg: str):
            logger.info(msg)
            if progress_cb:
                progress_cb(msg)

        notify("🧠 Analyzing content...")

        scraped = research_data.get("scraped_content", {})
        search_results = research_data.get("search_results", [])

        # safer tokenization
        query_terms = set(query.lower().split())

        key_points = []

        # ✅ extract from scraped content
        for text in scraped.values():
            sentences = re.split(r"(?<=[.!?])\s+", text)
            for s in sentences:
                s = s.strip()

                if 60 < len(s) < 300:
                    score = sum(1 for t in query_terms if t in s.lower())
                    if score >= 1:
                        key_points.append(s)

                if len(key_points) >= 10:
                    break

        # ✅ fallback from snippets
        for r in search_results:
            snip = r.get("snippet", "")
            if len(snip) > 60 and snip not in key_points:
                key_points.append(snip)

            if len(key_points) >= 12:
                break

        # ✅ STRICT LIMIT: max 8 insights
        key_points = key_points[:8]

        # ✅ clean sources (max 5)
        source_meta = []
        seen = set()

        for r in search_results:
            if len(source_meta) >= 5:
                break

            url = r.get("url")
            if url and url not in seen:
                source_meta.append({
                    "url": url,
                    "title": r.get("title", "")[:120],
                    "snippet": r.get("snippet", "")[:200],
                })
                seen.add(url)

        notify(f"✅ {len(key_points)} insights · {len(source_meta)} sources")

        return {
            "key_points": key_points,
            "source_metadata": source_meta,
            "filtered_content": scraped,
        }