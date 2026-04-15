"""
Summary Agent — generates a structured research report using the LLM.
Uses 2 LLM calls total (title+intro in one, conclusion in one) for speed.
Key insights come directly from extracted sentences — no extra LLM call needed.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

from models.llm_model import generate_text

logger = logging.getLogger(__name__)


class SummaryAgent:
    def run(
        self,
        query: str,
        analysis_data: Dict,
        progress_cb: Optional[Callable[[str], None]] = None,
    ) -> Dict:
        def notify(msg: str):
            logger.info(msg)
            if progress_cb:
                progress_cb(msg)

        key_points = analysis_data.get("key_points", [])
        source_meta = analysis_data.get("source_metadata", [])
        filtered_content = analysis_data.get("filtered_content", {})

        notify("✍️ Generating report...")

        # Use top 5 key points as context for LLM calls
        context = " ".join(key_points[:5])[:800]

        # Call 1: title + introduction together (one inference pass)
        title, introduction = self._gen_title_and_intro(query, context)
        notify(f"📄 {title}")

        # Key insights: extracted sentences directly — no LLM call
        insights = self._build_insights(query, key_points)
        notify(f"💡 {len(insights)} insights")

        # Call 2: conclusion
        conclusion = self._gen_conclusion(query, context)

        references = [
            {
                "url": s["url"],
                "title": s.get("title", s["url"])[:120],
                "snippet": s.get("snippet", "")[:200],
            }
            for s in source_meta if s.get("url")
        ]

        report = {
            "id": str(uuid.uuid4()),
            "query": query,
            "title": title,
            "introduction": introduction,
            "keyInsights": insights,
            "conclusion": conclusion,
            "references": references,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "sources": list(filtered_content.keys()),
        }
        notify("✅ Report complete")
        return report

    def _gen_title_and_intro(self, query: str, context: str) -> tuple[str, str]:
        """Generate title and introduction in one LLM call."""
        prompt = (
            f"Research topic: {query}\n"
            f"Context: {context[:600]}\n"
            f"Write a short title and then a 2-sentence introduction.\n"
            f"Title:"
        )
        raw = generate_text(prompt, max_tokens=150)

        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        title = ""
        intro_lines = []

        for i, line in enumerate(lines):
            if not title:
                title = line.strip('"\'').strip()
            else:
                intro_lines.append(line)

        title = title or f"Energy Research: {query.title()}"
        introduction = " ".join(intro_lines).strip()

        if not introduction or len(introduction) < 20:
            introduction = (
                f"This report analyzes {query} using data collected from multiple sources. "
                "The findings highlight current trends and developments in the energy sector."
            )

        return title, introduction

    def _build_insights(self, query: str, key_points: List[str]) -> List[str]:
        """Build insights from extracted key sentences — no LLM inference."""
        insights = [p.strip() for p in key_points[:8] if len(p.strip()) > 40]

        if not insights:
            insights = [
                f"Research on {query} highlights significant activity in the global energy sector.",
                "Renewable energy adoption is accelerating across major economies.",
                "Policy frameworks and investment are key drivers of energy transition.",
                "Technological innovation continues to drive down clean energy costs.",
                "Energy efficiency improvements are central to decarbonization strategies.",
            ]
        return insights[:8]

    def _gen_conclusion(self, query: str, context: str) -> str:
        """Generate a conclusion paragraph."""
        prompt = (
            f"Write a 2-sentence conclusion for a research report on: {query}\n"
            f"Based on: {context[:500]}\nConclusion:"
        )
        result = generate_text(prompt, max_tokens=80)
        r = result.strip()
        if len(r) > 30:
            return r
        return (
            f"Research on {query} underscores the dynamic evolution of the global energy landscape. "
            "Continued investment in clean technology and supportive policies remain essential for a sustainable future."
        )
