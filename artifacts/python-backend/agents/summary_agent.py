"""
Summary Agent — generates structured clean report with controlled LLM usage.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List

from models.llm_model import generate_text

logger = logging.getLogger(__name__)


class SummaryAgent:

    def run(self, query: str, analysis_data: Dict, progress_cb=None) -> Dict:

        def notify(msg: str):
            logger.info(msg)
            if progress_cb:
                progress_cb(msg)

        key_points = analysis_data.get("key_points", [])
        source_meta = analysis_data.get("source_metadata", [])

        notify("✍️ Generating report...")

        context = " ".join(key_points[:5])[:800]

        title, introduction = self._gen_title_and_intro(query, context)

        insights = self._build_insights(query, key_points)

        conclusion = self._gen_conclusion(query, context)

        references = [
            {
                "url": s["url"],
                "title": s.get("title", "")[:120],
                "snippet": s.get("snippet", "")[:200],
            }
            for s in source_meta[:5]
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
        }

        notify("✅ Report complete")
        return report

    def _gen_title_and_intro(self, query: str, context: str):
        prompt = f"""
Topic: {query}
Context: {context}

Generate:
1. A short title
2. A 2-sentence explanation

Format:
Title: ...
Intro: ...
"""

        raw = generate_text(prompt, max_tokens=120)

        title, intro = "Energy Report", ""

        for line in raw.split("\n"):
            if "Title:" in line:
                title = line.replace("Title:", "").strip()
            if "Intro:" in line:
                intro = line.replace("Intro:", "").strip()

        return title, intro

    def _build_insights(self, query: str, key_points: List[str]):
        return key_points[:5] if key_points else [
            f"Key trends observed in {query}",
            "Data suggests ongoing transformation in the energy sector",
            "Technology and policy are major drivers",
            "Efficiency improvements are increasing",
            "Sustainability remains a core focus"
        ]

    def _gen_conclusion(self, query: str, context: str):
        prompt = f"Write a 2-line conclusion for: {query}\nContext: {context}"
        result = generate_text(prompt, max_tokens=80)

        return result.strip() or (
            f"{query} continues to evolve with technological and policy advancements."
        )