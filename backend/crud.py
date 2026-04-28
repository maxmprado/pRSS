"""
CRUD operations for feeds and articles.
Provides functions to create, read, update, and delete data
using SQLAlchemy database sessions.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from . import models


# --------------------------------------------------------------
# Helper function
# --------------------------------------------------------------


def _parse_datetime(date_value: str | None) -> datetime | None:
    """
    Convert an ISO-formatted date string to a timezone-aware datetime object.
    Returns None if the input is None or cannot be parsed.
    """
    if date_value is None:
        return None
    try:
        # fromisoformat works with ISO 8601 strings like '2026-04-28T01:44:46+00:00'
        # but only in Python 3.11+ if the string has 'Z' or offset; Python 3.10 needs a trick.
        # Our string has +00:00, which is supported from 3.7+
        dt = datetime.fromisoformat(date_value)
        # If the parsed datetime has no tzinfo, assume UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError, TypeError:
        return None


# --------------------------------------------------------------
# Feed operations
# --------------------------------------------------------------


def create_feed(
    db: Session, name: str, url: str, category: str = "General"
) -> models.Feed:
    """
    Create a new feed source in the database.
    Returns the created Feed object.
    """
    feed = models.Feed(name=name, url=url, category=category)
    db.add(feed)
    db.commit()
    db.refresh(feed)
    return feed


def get_feed_by_url(db: Session, url: str) -> models.Feed | None:
    """
    Look up a feed by its URL.
    Returns the Feed object if found, otherwise None.
    """
    return db.query(models.Feed).filter(models.Feed.url == url).first()


def get_feeds(db: Session, active_only: bool = True) -> list[models.Feed]:
    """
    Retrieve all feeds, optionally filtering only active ones.
    """
    query = db.query(models.Feed)
    if active_only:
        query = query.filter(models.Feed.active == True)
    return query.all()


def deactivate_feed(db: Session, feed_id: int) -> models.Feed | None:
    """
    Set the 'active' flag to False for a given feed.
    Returns the updated feed or None if not found.
    """
    feed = db.query(models.Feed).filter(models.Feed.id == feed_id).first()
    if feed:
        feed.active = False
        db.commit()
        db.refresh(feed)
    return feed


# --------------------------------------------------------------
# Article operations
# --------------------------------------------------------------


def save_articles(db: Session, feed_id: int, articles_data: list[dict]) -> int:
    """
    Save a batch of articles fetched from a feed.

    articles_data is a list of dicts with keys:
        - title
        - link
        - description
        - image_url
        - published_at (ISO string or None)
        - guid

    Only articles whose link (or guid) does not already exist are inserted.
    Returns the number of new articles added.
    """
    new_count = 0
    for article_data in articles_data:
        link = article_data.get("link")
        if not link:
            continue

        # Check if this article already exists (by link)
        existing = db.query(models.Article).filter(models.Article.link == link).first()
        if existing:
            continue

        # Also check by GUID if present
        guid = article_data.get("guid")
        if guid:
            existing_guid = (
                db.query(models.Article).filter(models.Article.guid == guid).first()
            )
            if existing_guid:
                continue

        # Convert the ISO date string to a datetime object
        pub_date = _parse_datetime(article_data.get("published_at"))

        article = models.Article(
            feed_id=feed_id,
            title=article_data.get("title"),
            link=link,
            description=article_data.get("description"),
            image_url=article_data.get("image_url"),
            published_at=pub_date,  # now a datetime or None
            guid=guid,
        )
        db.add(article)
        new_count += 1

    if new_count > 0:
        db.commit()
    return new_count


def get_articles(
    db: Session,
    feed_id: int | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[models.Article]:
    """
    Retrieve articles, optionally filtered by feed and/or search string.
    search matches against the article title (case-insensitive).
    Supports pagination via skip/limit.
    """
    query = db.query(models.Article)

    if feed_id is not None:
        query = query.filter(models.Article.feed_id == feed_id)

    if search:
        query = query.filter(models.Article.title.ilike(f"%{search}%"))

    query = query.order_by(models.Article.published_at.desc())
    return query.offset(skip).limit(limit).all()


def get_article_by_id(db: Session, article_id: int) -> models.Article | None:
    """
    Get a single article by its primary key.
    """
    return db.query(models.Article).filter(models.Article.id == article_id).first()
