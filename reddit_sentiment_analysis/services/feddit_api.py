import time

import aiohttp
from fastapi import HTTPException
from pydantic import BaseModel

from reddit_sentiment_analysis.config import settings
from reddit_sentiment_analysis.logs import logger
from reddit_sentiment_analysis.utils import ElapsedTimer


class CommentsResponse(BaseModel):
    subfeddit_id: int
    limit: int
    skip: int
    comments: list["Comment"]


class Comment(BaseModel):
    id: int
    username: str
    text: str
    created_at: int


async def fetch_subfeddit_comments(subfeddit_id: int, limit: int) -> CommentsResponse:
    async with aiohttp.ClientSession() as session:
        url = f"{settings.feddit_url}/api/v1/comments/?subfeddit_id={subfeddit_id}&limit={limit}"
        t = ElapsedTimer()
        async with session.get(url) as resp:
            if resp.status != 200:
                # raise same status code as the feddit api, don't provide all details to the client
                # there are the logs for that
                logger.error(
                    f"Failed to fetch comments for subfeddit",
                    extra={
                        "subfeddit_id": subfeddit_id,
                        "limit": limit,
                        "status_code": resp.status,
                        "response": await resp.text(),
                    },
                )
                raise HTTPException(status_code=resp.status, detail="Failed to fetch comments")
            # N.B. the feddit api doesn't return a 404 when the subfeddit doesn't exist only empty list
            # there is no easy way to handle that error
            data = await resp.json()

        logger.info(
            f"Fetched comments for subfeddit",
            extra={
                "subfeddit_id": subfeddit_id,
                "limit": limit,
                "comments_count": len(data["comments"]),
                "duration_ms": t.elapsed(),
            },
        )
    data = CommentsResponse(**data)
    return data
