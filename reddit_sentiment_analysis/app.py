import os

from fastapi import FastAPI

from reddit_sentiment_analysis.api import router
from reddit_sentiment_analysis.config import settings

API_BASE_URL = '/api/v1'

app = FastAPI(
    title="Reddit Sentiment Analysis API",
    debug=settings.debug,
    openapi_url=f"{API_BASE_URL}/openapi.json",
)
app.include_router(router, prefix=API_BASE_URL)

