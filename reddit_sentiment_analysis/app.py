import logging.config

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from reddit_sentiment_analysis.api import router
from reddit_sentiment_analysis.config import settings

API_BASE_URL = '/api/v1'

app = FastAPI(
    title="Reddit Sentiment Analysis API",
    debug=settings.debug,
    openapi_url=f"{API_BASE_URL}/openapi.json",
)
app.include_router(router, prefix=API_BASE_URL)
instrumentator = Instrumentator().instrument(app)

logging.config.dictConfig(settings.LOGGING_CONFIG)


@app.get("/health")
def health_check():
    return {"status": "OK"}
