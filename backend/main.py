import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from apscheduler.schedulers.background import BackgroundScheduler
from .database import engine, Base
from . import models
from .routers import feeds, articles, refresh
from .tasks import refresh_all_feeds

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

scheduler = BackgroundScheduler()


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready")
    scheduler.add_job(refresh_all_feeds, "interval", minutes=30, id="feed_refresh")
    scheduler.start()
    logger.info("Scheduler started (feed refresh every 30 minutes)")


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down")


# Include API routers
app.include_router(feeds.router)
app.include_router(articles.router)
app.include_router(refresh.router)


# Serve the main HTML page
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("frontend/index.html") as f:
        return HTMLResponse(content=f.read())
