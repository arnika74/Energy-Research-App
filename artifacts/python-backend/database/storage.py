"""
Local storage for research reports as JSON files.
Each report is saved as a separate JSON file in the reports directory.
"""

import json
import logging
import os
from typing import List, Optional, Dict

from config.settings import REPORTS_DIR

logger = logging.getLogger(__name__)


def _ensure_reports_dir():
    """Ensure the reports directory exists."""
    os.makedirs(REPORTS_DIR, exist_ok=True)


def save_report(report: Dict) -> bool:
    """
    Save a research report to disk as JSON.

    Args:
        report: The research report dict

    Returns:
        True if saved successfully
    """
    _ensure_reports_dir()
    report_id = report.get("id")
    if not report_id:
        logger.error("Cannot save report without an ID")
        return False

    filepath = os.path.join(REPORTS_DIR, f"{report_id}.json")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved report: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Failed to save report {report_id}: {e}")
        return False


def load_report(report_id: str) -> Optional[Dict]:
    """
    Load a research report by ID.

    Args:
        report_id: The report ID

    Returns:
        Report dict or None if not found
    """
    filepath = os.path.join(REPORTS_DIR, f"{report_id}.json")
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load report {report_id}: {e}")
        return None


def list_reports() -> List[Dict]:
    """
    List all stored research reports (summaries only).

    Returns:
        List of report summary dicts sorted by creation time (newest first)
    """
    _ensure_reports_dir()
    summaries = []

    for filename in os.listdir(REPORTS_DIR):
        if not filename.endswith(".json"):
            continue
        report_id = filename[:-5]
        report = load_report(report_id)
        if report:
            summaries.append(
                {
                    "id": report.get("id", report_id),
                    "query": report.get("query", ""),
                    "title": report.get("title", ""),
                    "createdAt": report.get("createdAt", ""),
                    "sourceCount": len(report.get("references", [])),
                }
            )

    # Sort by creation time descending
    summaries.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    return summaries


def delete_report(report_id: str) -> bool:
    """
    Delete a stored report by ID.

    Args:
        report_id: The report ID to delete

    Returns:
        True if deleted, False if not found or error
    """
    filepath = os.path.join(REPORTS_DIR, f"{report_id}.json")
    if not os.path.exists(filepath):
        return False

    try:
        os.remove(filepath)
        logger.info(f"Deleted report: {report_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete report {report_id}: {e}")
        return False
