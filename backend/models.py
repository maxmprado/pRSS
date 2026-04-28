"""
Database models for the news reader application.

Defines the Feed and Article tables that represent RSS sources
and the individual news items fetched from them.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .database import Base


class Feed(Base):
    """
    Represents an RSS feed source (e.g., a newspaper or blog).
    Each feed can have many articles.
    """

    __tablename__ = "feeds"

    # Primary key – unique identifier for each feed
    id = Column(Integer, primary_key=True, index=True)

    # Human-readable name of the source (e.g., "El País")
    name = Column(String, nullable=False)

    # URL of the RSS/Atom feed – must be unique to avoid duplicates
    url = Column(String, unique=True, nullable=False)

    # General topic for filtering (e.g., "Technology", "Sports")
    category = Column(String, default="General")

    # Optional URL pointing to the source's logo/favicon
    logo_url = Column(String, nullable=True)

    # Whether the feed should be actively refreshed
    active = Column(Boolean, default=True)

    # Timestamp of when the feed was added to the database
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship: a feed can fetch many articles
    # cascade="all, delete-orphan" ensures articles are deleted if the feed is deleted
    articles = relationship(
        "Article",
        back_populates="feed",
        cascade="all, delete-orphan",
    )


class Article(Base):
    """
    Represents a single news article fetched from a feed.
    Stores metadata and (optionally) the full content.
    """

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)

    feed_id = Column(Integer, ForeignKey("feeds.id"), nullable=False)

    title = Column(String, nullable=False)

    # Direct URL to the original article
    link = Column(String, unique=True, nullable=False)

    description = Column(Text, nullable=True)

    content = Column(Text, nullable=True)

    # URL of the main image/thumbnail for the article
    image_url = Column(String, nullable=True)

    # Publication date as reported by the feed
    published_at = Column(DateTime, nullable=True)

    # Timestamp of when we fetched this article from the feed
    fetched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Globally unique identifier from the RSS feed (for deduplication)
    guid = Column(String, nullable=True)

    # Relationship back to the parent feed
    feed = relationship("Feed", back_populates="articles")
