"""
Analysis Agent — filters content, extracts key sentences, and builds references.
Falls back to search snippets when scraped content is sparse.
References are always populated from search results regardless of scraping success.
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

        # Filter scraped pages by relevance score
        filtered: Dict[str, str] = {}
        for url, text in scraped.items():
            low = text.lower()
            score = sum(low.count(t) for t in all_terms)
            if score > 2:
                filtered[url] = text

        # Extract key sentences from filtered pages
        key_points = self._extract_key_points(filtered, all_terms)

        # Always supplement with search snippets (ensures we have content even when scraping fails)
        seen = set(key_points)
        for r in search_results:
            snippet = r.get("snippet", "").strip()
            if len(snippet) > 60 and snippet not in seen:
                key_points.append(snippet)
                seen.add(snippet)

        # References always include ALL search results (not just scraped ones)
        # This guarantees references are never empty when search succeeds
        source_meta: List[Dict] = []
        seen_urls: set = set()
        for r in search_results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                source_meta.append({
                    "url": url,
                    "title": r.get("title", url)[:120],
                    "snippet": r.get("snippet", "")[:200],
                })
                seen_urls.add(url)

        # Also include successfully scraped URLs that weren't in search results
        for url in filtered:
            if url not in seen_urls:
                source_meta.append({"url": url, "title": url, "snippet": ""})
                seen_urls.add(url)

        notify(f"✅ {len(key_points)} key points · {len(source_meta)} sources")
        return {
            "filtered_content": filtered,
            "key_points": key_points[:15],
            "source_metadata": source_meta[:10],
        }

    def _extract_key_points(self, content: Dict[str, str], terms: set) -> List[str]:
        points: List[str] = []
        seen: set = set()
        for text in content.values():
            for sentence in re.split(r"(?<=[.!?])\s+", text):
                s = sentence.strip()
                if len(s) < 60 or len(s) > 400 or s in seen:
                    continue
                if sum(1 for t in terms if t in s.lower()) >= 2:
                    seen.add(s)
                    points.append(s)
                if len(points) >= 15:
                    return points
        return points
