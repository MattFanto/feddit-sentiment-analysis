from reddit_sentiment_analysis.config import settings


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "reddit_sentiment_analysis.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers,
        access_log=settings.access_log,
    )
