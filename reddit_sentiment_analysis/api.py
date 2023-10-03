from typing import List

from fastapi import APIRouter

from reddit_sentiment_analysis.models import CommentSentiment, SentimentResponse, SortOrder
from reddit_sentiment_analysis.services.predict import predict_sentiment_batch
from reddit_sentiment_analysis.services.feddit_api import fetch_subfeddit_comments

router = APIRouter()


def sort_comments(predictions: List[CommentSentiment], order_by: SortOrder):
    reverse_order = order_by.value.startswith('-')
    if order_by in [SortOrder.CREATED_AT_DESC, SortOrder.CREATED_AT_ASC]:
        predictions = sorted(predictions, key=lambda x: x.created_at, reverse=reverse_order)
    elif order_by in [SortOrder.SENTIMENT_SCORE_DESC, SortOrder.SENTIMENT_SCORE_ASC]:
        predictions = sorted(predictions, key=lambda x: x.sentiment.score, reverse=reverse_order)
    elif order_by == SortOrder.NONE:
        pass
    else:
        raise ValueError(f"Unknown sort order: {order_by}")

    return predictions


@router.get("/predict", response_model=SentimentResponse)
async def predict(
        subfeddit_id: int,
        order_by: SortOrder = SortOrder.NONE,
):
    # From the problem statement: "Suppose a limit of 25 comments"
    limit = 25
    comments = await fetch_subfeddit_comments(subfeddit_id, limit=limit)
    predictions = await predict_sentiment_batch(comments['comments'])
    res = []
    for comment, sentiment_pred in zip(comments['comments'], predictions):
        res.append(CommentSentiment(
            id=comment["id"],
            text=comment["text"],
            created_at=comment["created_at"],
            sentiment=sentiment_pred
        ))
    res = sort_comments(res, order_by)

    return SentimentResponse(
        data=res,
        skip=0,
        limit=limit
    )


@router.get("/version")
async def health_check():
    return "OK"
