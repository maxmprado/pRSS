"""
Router for managing RSS feed sources.
Provides endpoints to create, list, and deactivate feeds.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud

# Create a router instance with a prefix and tag for documentation
router = APIRouter(
    prefix="/api/feeds",
    tags=["feeds"],
)


@router.post("/", status_code=201)
def create_feed_endpoint(
    name: str, url: str, category: str = "General", db: Session = Depends(get_db)
):
    """
    Add a new RSS feed source.
    Returns an error if the URL already exists.
    """
    # Check if a feed with this URL already exists
    existing = crud.get_feed_by_url(db, url)
    if existing:
        raise HTTPException(
            status_code=409, detail="A feed with this URL already exists"
        )

    return crud.create_feed(db, name=name, url=url, category=category)


@router.get("/")
def list_feeds_endpoint(active_only: bool = True, db: Session = Depends(get_db)):
    """
    List all feeds, optionally filtering only active ones.
    """
    return crud.get_feeds(db, active_only=active_only)


@router.delete("/{feed_id}")
def deactivate_feed_endpoint(feed_id: int, db: Session = Depends(get_db)):
    """
    Deactivate a feed (does not delete its articles).
    """
    feed = crud.deactivate_feed(db, feed_id)
    if feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return {"ok": True, "feed_id": feed_id}
