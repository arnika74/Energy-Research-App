"""
Web Scraping Tool using BeautifulSoup for extracting text content from websites.
Handles timeouts, errors, and content cleaning gracefully.
"""

import logging
import time
import re
from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup

from config.settings import REQUEST_TIMEOUT, MAX_CONTENT_LENGTH, SCRAPER_DELAY

logger = logging.getLogger(__name__)

# User-Agent header to avoid bot detection
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Domains to skip (paywalled, login-required, etc.)
SKIP_DOMAINS = [
    "jstor.org",
    "nature.com/articles",
    "sciencedirect.com",
    "springer.com",
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "linkedin.com",
    "youtube.com",
]


def should_skip_url(url: str) -> bool:
    """Check if a URL should be skipped based on domain blacklist."""
    return any(domain in url for domain in SKIP_DOMAINS)


def extract_text_from_url(url: str) -> Optional[str]:
    """
    Fetch and extract clean text content from a URL.

    Args:
        url: The URL to scrape

    Returns:
        Cleaned text content or None if scraping failed
    """
    if should_skip_url(url):
        logger.debug(f"Skipping URL (blacklisted domain): {url}")
        return None

    try:
        time.sleep(SCRAPER_DELAY)  # Polite delay between requests

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type and "text/plain" not in content_type:
            logger.debug(f"Skipping non-HTML content: {url}")
            return None

        return clean_html_content(response.text)

    except requests.exceptions.Timeout:
        logger.warning(f"Timeout scraping: {url}")
        return None
    except requests.exceptions.ConnectionError:
        logger.warning(f"Connection error scraping: {url}")
        return None
    except Exception as e:
        logger.warning(f"Error scraping {url}: {e}")
        return None


def clean_html_content(html: str) -> str:
    """
    Parse HTML and extract clean, readable text content.

    Args:
        html: Raw HTML string

    Returns:
        Cleaned text content
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "nav", "footer", "header",
                      "aside", "advertisement", "iframe", "noscript"]):
        tag.decompose()

    # Try to find main content area first
    main_content = (
        soup.find("main")
        or soup.find("article")
        or soup.find(class_=re.compile(r"content|article|post|main", re.I))
        or soup.find("body")
    )

    if main_content:
        text = main_content.get_text(separator="\n", strip=True)
    else:
        text = soup.get_text(separator="\n", strip=True)

    # Clean up whitespace
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if len(line) > 30]  # Remove short/empty lines
    text = "\n".join(lines)

    # Truncate to max length
    if len(text) > MAX_CONTENT_LENGTH:
        text = text[:MAX_CONTENT_LENGTH] + "..."

    return text


def scrape_multiple_urls(urls: list, max_sources: int = 5) -> Dict[str, str]:
    """
    Scrape text from multiple URLs, returning a dict of url -> content.

    Args:
        urls: List of URLs to scrape
        max_sources: Maximum number of successful sources to collect

    Returns:
        Dict mapping url to extracted text content
    """
    results = {}
    attempted = 0

    for url in urls:
        if len(results) >= max_sources:
            break

        if not url or not url.startswith("http"):
            continue

        attempted += 1
        logger.info(f"Scraping ({len(results)+1}/{max_sources}): {url}")

        content = extract_text_from_url(url)
        if content and len(content) > 200:
            results[url] = content

    logger.info(
        f"Successfully scraped {len(results)} out of {attempted} attempted URLs"
    )
    return results
