"""
Router for managing news articles.
Provides endpoints to list articles and retrieve a single article by ID.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud

router = APIRouter(
    prefix="/api/articles",
    tags=["articles"],
)


@router.get("/")
def list_articles_endpoint(
    feed_id: int | None = Query(default=None, description="Filter by feed ID"),
    search: str | None = Query(
        default=None, description="Search in titles (case-insensitive)"
    ),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db),
):
    """
    Retrieve a paginated list of articles, with optional filters.
    """
    return crud.get_articles(
        db,
        feed_id=feed_id,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.get("/{article_id}")
def get_article_endpoint(article_id: int, db: Session = Depends(get_db)):
    """
    Get a single article by its ID.
    """
    article = crud.get_article_by_id(db, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
