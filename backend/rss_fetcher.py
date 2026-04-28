"""
Fetches and parses articles from an RSS/Atom feed.
"""

import logging
from typing import Optional, Dict, Any
import feedparser

# Set up a logger for this module
logger = logging.getLogger(__name__)


def fetch_feed(url: str) -> list[Dict[str, Any]]:
    """
    Download and parse a feed from the given URL.

    Returns a list of dictionaries, each representing one article.
    The dictionaries contain the following keys:
        - title
        - link
        - description
        - image_url
        - published_at
        - guid
    Returns an empty list if the feed cannot be parsed or is empty.
    """
    logger.info(f"Fetching feed: {url}")
    parsed = feedparser.parse(url)

    # If the feed is not well-formed or has no entries, return an empty list
    if not parsed or not parsed.entries:
        logger.warning(f"No entries found for feed: {url}")
        return []

    articles = []
    for entry in parsed.entries:
        # Extract the required fields, using None if they don't exist
        article = {
            "title": entry.get("title"),
            "link": entry.get("link"),
            "description": entry.get("description"),
            "image_url": _extract_image(entry),
            "published_at": _extract_published_date(entry),
            "guid": entry.get(
                "id"
            ),  # 'id' is the globally unique identifier in feedparser
        }
        articles.append(article)

    logger.info(f"Fetched {len(articles)} articles from {url}")
    return articles


def _extract_image(entry: dict) -> Optional[str]:
    """
    Try to find a main image URL in a feed entry.
    RSS feeds can embed images in different ways (media_content, enclosures, etc.).
    This function checks several common fields and returns the first URL found.
    """
    # 1. Check media_content (used by many sites including BBC)
    if "media_content" in entry and entry.media_content:
        for media in entry.media_content:
            if "url" in media:
                return media["url"]

    # 2. Check enclosures (often used for audio/podcasts but also images)
    if "enclosures" in entry and entry.enclosures:
        for enclosure in entry.enclosures:
            if "href" in enclosure and "image" in enclosure.get("type", ""):
                return enclosure["href"]

    # 3. Check links with type image
    if "links" in entry:
        for link in entry.links:
            if link.get("type") and link["type"].startswith("image"):
                return link["href"]

    return None


def _extract_published_date(entry: dict) -> Optional[str]:
    """
    Extract the publication date from a feed entry.
    Returns an ISO-formatted string if a date is found, otherwise None.
    """
    # Common fields: published_parsed (time.struct_time), published (string)
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        from datetime import datetime, timezone

        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        return dt.isoformat()

    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        from datetime import datetime, timezone

        dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
        return dt.isoformat()

    # Fallback to string date if parsing fails
    if hasattr(entry, "published") and entry.published:
        return entry.published

    return None
