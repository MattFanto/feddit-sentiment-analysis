import asyncio

import aiohttp
from reddit_sentiment_analysis.config import settings


def predict_sentiment(feedit_data):
    return {
        "sentiment_score": 1.0,
        "sentiment": "positive"
    }


async def fetch_subfeedits_comments(subfeddit_id: int, limit: int):
    async with aiohttp.ClientSession() as session:

        url = (
            settings.FEDDIT_URL +
            f"/api/v1/comments/" +
            f"?subfeddit_id={subfeddit_id}&limit={limit}"
        )
        async with session.get(url) as resp:
            data = await resp.json()

    return data
