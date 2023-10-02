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

# @app.on_event("startup")
# async def startup_event():
#     """Replace uvicorn logger with our json logger"""
#     u_logger = logging.getLogger("uvicorn.access")
#     log_handler = logging.StreamHandler()
#     log_handler.setFormatter(json_log_formatter)
#     u_logger.handlers = [log_handler]
#     # prometheus metrics
#     instrumentator.expose(app)
