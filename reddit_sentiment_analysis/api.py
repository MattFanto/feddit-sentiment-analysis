from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException

from reddit_sentiment_analysis.logs import logger
from reddit_sentiment_analysis.models import CommentSentiment, SentimentResponse, SortOrder
from reddit_sentiment_analysis.services.detect_sentiment import detect_sentiment_batch
from reddit_sentiment_analysis.services.feddit_api import fetch_subfeddit_comments

router = APIRouter()


def sort_comments(predictions: List[CommentSentiment], order_by: SortOrder):
    reverse_order = order_by.name.endswith("_DESC")
    if order_by in [SortOrder.CREATED_AT_DESC, SortOrder.CREATED_AT_ASC]:
        predictions = sorted(predictions, key=lambda x: x.created_at, reverse=reverse_order)
    elif order_by in [SortOrder.SENTIMENT_SCORE_DESC, SortOrder.SENTIMENT_SCORE_ASC]:
        predictions = sorted(predictions, key=lambda x: x.sentiment.score, reverse=reverse_order)
    elif order_by == SortOrder.NONE:
        pass
    else:
        raise ValueError(f"Unknown sort order: {order_by}")

    return predictions


# TODO rename to detect comments sentiment
@router.get("/detect-comments-sentiment", response_model=SentimentResponse)
async def detect_comments_sentiment(
    subfeddit_id: int,
    order_by: SortOrder = SortOrder.NONE,
):
    # From the problem statement: "Suppose a limit of 25 comments"
    # I didn't put it as a param since the problem statement is not clear about it
    # and there is some ambiguity related to filtering and sorting in the problem statement
    limit = 25
    try:
        comments_response = await fetch_subfeddit_comments(subfeddit_id, limit=limit)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Failed to fetch comments")
        raise HTTPException(status_code=500, detail="Failed to fetch comments") from e

    try:
        predictions = await detect_sentiment_batch(comments_response.comments)
    except HTTPException as e:
        raise e
    except Exception as e:
        # TODO: we may want to distinguish between retryable errors and non-retryable errors
        #    e.g. throttling (retryable) vs input too large (non-retryable)
        logger.exception("Failed to detect sentiment for comments")
        raise HTTPException(status_code=500, detail="Failed to predict sentiment") from e

    res = []
    for comment, sentiment_pred in zip(comments_response.comments, predictions):
        res.append(
            CommentSentiment(id=comment.id, text=comment.text, created_at=comment.created_at, sentiment=sentiment_pred)
        )
    res = sort_comments(res, order_by)

    return SentimentResponse(data=res, skip=0, limit=limit)
