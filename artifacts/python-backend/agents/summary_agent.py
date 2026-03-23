"""
Summary Agent — uses the LLM to generate a structured research report.
Takes analyzed content and produces a formatted report with sections:
Title, Introduction, Key Insights, Conclusion, References.
"""

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Callable, Optional

from models.llm_model import generate_text

logger = logging.getLogger(__name__)


class SummaryAgent:
    """
    Agent 3: Generates a structured research report using the LLM.
    Formats output into professional research report sections.
    """

    def run(
        self,
        query: str,
        analysis_data: Dict,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> Dict:
        """
        Generate a structured research report.

        Args:
            query: The original research query
            analysis_data: Output from AnalysisAgent
            progress_callback: Optional function to report progress

        Returns:
            Complete structured research report dict
        """
        def notify(msg: str):
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        key_points = analysis_data.get("key_points", [])
        source_metadata = analysis_data.get("source_metadata", [])
        filtered_content = analysis_data.get("filtered_content", {})

        notify("✍️ Generating research report with AI model...")

        # Generate title
        title = self._generate_title(query)
        notify(f"📄 Title: {title}")

        # Generate introduction
        introduction = self._generate_introduction(query, key_points)

        # Generate structured insights
        insights = self._generate_insights(query, key_points, filtered_content)
        notify(f"💡 Generated {len(insights)} key insights")

        # Generate conclusion
        conclusion = self._generate_conclusion(query, insights)

        # Format references
        references = self._format_references(source_metadata)

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

        notify("✅ Research report generated successfully!")
        return report

    def _generate_title(self, query: str) -> str:
        """Generate a research report title."""
        prompt = (
            f"Write a concise, professional research report title for this topic: {query}\n"
            f"Title (one line, no quotes):"
        )
        result = generate_text(prompt, max_tokens=60)

        if result and len(result) > 5:
            # Clean up the result
            title = result.strip().strip('"').strip("'")
            title = title.split("\n")[0].strip()
            if len(title) > 10:
                return title

        return f"Energy Research Report: {query.title()}"

    def _generate_introduction(self, query: str, key_points: List[str]) -> str:
        """Generate an introduction paragraph for the research topic."""
        context = " ".join(key_points[:3]) if key_points else ""
        prompt = (
            f"Write a 2-3 sentence introduction for a research report on: {query}\n"
            f"Context from research: {context[:500]}\n"
            f"Introduction:"
        )
        result = generate_text(prompt, max_tokens=200)

        if result and len(result) > 30:
            return result.strip()

        return (
            f"This research report provides a comprehensive analysis of {query}. "
            f"The following findings are based on data collected from multiple web sources "
            f"and analyzed using advanced natural language processing techniques."
        )

    def _generate_insights(
        self,
        query: str,
        key_points: List[str],
        filtered_content: Dict[str, str],
    ) -> List[str]:
        """
        Generate a list of key insights from the research data.
        Combines LLM-generated insights with extracted sentences.
        """
        if key_points:
            # Use the top extracted key points as insights
            insights = []
            for point in key_points[:8]:
                cleaned = point.strip()
                if len(cleaned) > 40:
                    insights.append(cleaned)

            # Try to generate 2 additional LLM insights
            context = " ".join(key_points[:5])
            prompt = (
                f"Based on this research about {query}, list 2 key insights as bullet points:\n"
                f"Research data: {context[:600]}\n"
                f"Key insights:"
            )
            llm_result = generate_text(prompt, max_tokens=200)
            if llm_result:
                # Parse bullet points
                for line in llm_result.split("\n"):
                    line = line.strip().lstrip("•-*123456789. ")
                    if len(line) > 40 and line not in insights:
                        insights.append(line)

            return insights[:8] if insights else self._fallback_insights(query)

        return self._fallback_insights(query)

    def _fallback_insights(self, query: str) -> List[str]:
        """Generate generic insights when scraping yields minimal data."""
        return [
            f"Research on {query} reveals significant developments in the energy sector.",
            "Renewable energy technologies continue to advance at an unprecedented pace.",
            "Policy frameworks and international agreements are shaping the energy transition.",
            "Economic factors increasingly favor clean energy over fossil fuel alternatives.",
            "Technological innovation is driving down costs and improving efficiency.",
        ]

    def _generate_conclusion(self, query: str, insights: List[str]) -> str:
        """Generate a conclusion paragraph."""
        insights_text = " ".join(insights[:3])
        prompt = (
            f"Write a 2-sentence conclusion for a research report on {query}.\n"
            f"Based on findings: {insights_text[:400]}\n"
            f"Conclusion:"
        )
        result = generate_text(prompt, max_tokens=150)

        if result and len(result) > 30:
            return result.strip()

        return (
            f"In conclusion, the research on {query} demonstrates the dynamic nature "
            f"of the energy landscape and the importance of continued innovation, policy "
            f"development, and global cooperation to achieve a sustainable energy future."
        )

    def _format_references(self, source_metadata: List[Dict]) -> List[Dict]:
        """Format source metadata into reference objects."""
        references = []
        for source in source_metadata[:10]:
            url = source.get("url", "")
            if not url:
                continue
            references.append(
                {
                    "url": url,
                    "title": source.get("title", url)[:120],
                    "snippet": source.get("snippet", "")[:200],
                }
            )
        return references
