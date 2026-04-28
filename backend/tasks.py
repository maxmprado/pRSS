"""
Scheduled tasks for refreshing feeds in the background.
"""

import logging
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import crud
from .rss_fetcher import fetch_feed

logger = logging.getLogger(__name__)


def refresh_all_feeds():
    """
    Fetch new articles from every active feed.
    Uses its own database session to avoid conflicts with request cycles.
    """
    db = SessionLocal()
    try:
        feeds = crud.get_feeds(db, active_only=True)
        if not feeds:
            logger.info("No active feeds to refresh")
            return

        for feed in feeds:
            try:
                articles = fetch_feed(feed.url)
                if articles:
                    added = crud.save_articles(db, feed.id, articles)
                    logger.info(f"Feed '{feed.name}': {added} new articles")
                else:
                    logger.warning(f"Feed '{feed.name}': no articles fetched")
            except Exception as e:
                logger.error(f"Error refreshing feed '{feed.name}': {e}")
    finally:
        db.close()
