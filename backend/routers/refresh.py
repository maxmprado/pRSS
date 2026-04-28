"""
Router for manual feed refresh.
"""

from fastapi import APIRouter
from ..tasks import refresh_all_feeds

router = APIRouter(
    prefix="/api",
    tags=["refresh"],
)


@router.post("/refresh")
def manual_refresh():
    """
    Trigger an immediate refresh of all active feeds.
    Runs in the request thread (may take a few seconds).
    """
    refresh_all_feeds()
    return {"ok": True, "message": "Refresh triggered"}
