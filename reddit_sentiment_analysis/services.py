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

        async with session.get(settings.FEDDIT_URL + f"/api/v1/comments/?subfeddit_id={subfeddit_id}&limit={limit}") as resp:
            data = await resp.json()

    return data


async def fetch_feddit_comments():
    async with aiohttp.ClientSession() as session:

        async with session.get(settings.FEDDIT_URL + "/api/v1/subfeddits") as resp:
            return await resp.json()

        async with session.get(settings.FEDDIT_URL + "/api/v1/subfeddits") as resp:
            print(resp.status)
            data = await resp.json()
            subfeddits = data['subfeddits']

        tasks = []
        for subfeddit in subfeddits:
            tasks.append(
                session.get(
                    settings.FEDDIT_URL + f"/api/v1/subfeddit/?subfeddit_id={subfeddit['id']}"))

        responses = await asyncio.gather(*tasks)
        data = await asyncio.gather(*[response.json() for response in responses])

    comments = []
    return data

