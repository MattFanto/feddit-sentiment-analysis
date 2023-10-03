import time

import aiohttp

from reddit_sentiment_analysis.config import settings
from reddit_sentiment_analysis.logs import logger
from reddit_sentiment_analysis.utils import ElapsedTimer


async def fetch_subfeedits_comments(subfeddit_id: int, limit: int):

    async with aiohttp.ClientSession() as session:

        url = (
            settings.feddit_url +
            f"/api/v1/comments/" +
            f"?subfeddit_id={subfeddit_id}&limit={limit}"
        )
        t = ElapsedTimer()
        async with session.get(url) as resp:
            data = await resp.json()

        logger.info(f"Fetched comments for subfeddit", extra={
            "subfeddit_id": subfeddit_id,
            "limit": limit,
            "comments_count": len(data['comments']),
            "duration_ms": t.elapsed()
        })

    return data
