"""
Analysis Agent — filters content and extracts key sentences.
Falls back to search snippets when scraped content is sparse.
"""

import logging
import re
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

_ENERGY_TERMS = {
    "energy", "solar", "wind", "renewable", "electricity", "power", "fuel",
    "carbon", "emission", "fossil", "oil", "gas", "nuclear", "hydrogen",
    "battery", "storage", "grid", "efficiency", "sustainability", "climate",
    "transition", "generation", "consumption", "photovoltaic", "turbine",
    "biofuel", "geothermal", "hydropower", "kilowatt", "megawatt",
}


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
        query_terms = {w.lower() for w in query.split() if len(w) > 3}
        all_terms = _ENERGY_TERMS | query_terms

        # Filter scraped content by relevance score
        filtered = {}
        for url, text in scraped.items():
            low = text.lower()
            score = sum(low.count(t) for t in all_terms)
            if score > 2:
                filtered[url] = text

        # Extract key points from filtered content
        key_points = self._extract_key_points(filtered, all_terms)

        # Fall back to search snippets if we don't have enough
        if len(key_points) < 5:
            for r in search_results:
                snippet = r.get("snippet", "").strip()
                if len(snippet) > 60 and snippet not in key_points:
                    key_points.append(snippet)

        # Build references from search results
        source_meta = [
            {"url": r["url"], "title": r.get("title", r["url"])[:120], "snippet": r.get("snippet", "")[:200]}
            for r in search_results
            if r.get("url")
        ][:10]

        notify(f"✅ {len(key_points)} key points extracted")
        return {"filtered_content": filtered, "key_points": key_points[:15], "source_metadata": source_meta}

    def _extract_key_points(self, content: Dict[str, str], terms: set) -> List[str]:
        points = []
        seen = set()
        for text in content.values():
            for sentence in re.split(r"(?<=[.!?])\s+", text):
                s = sentence.strip()
                if len(s) < 60 or len(s) > 400 or s in seen:
                    continue
                low = s.lower()
                if sum(1 for t in terms if t in low) >= 2:
                    seen.add(s)
                    points.append(s)
                if len(points) >= 15:
                    return points
        return points
