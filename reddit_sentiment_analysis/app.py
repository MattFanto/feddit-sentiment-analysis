import os

from fastapi import FastAPI

from reddit_sentiment_analysis.api import router

API_BASE_URL = '/api/v1'

app = FastAPI(
    title="Reddit Sentiment Analysis API",
    debug=True,
    openapi_url=f"{API_BASE_URL}/openapi.json",
)
app.include_router(router, prefix=API_BASE_URL)


if __name__ == '__main__':
    import uvicorn
    # TODO productionize
    uvicorn.run("app:app", host='0.0.0.0', port=8000, reload=True)
