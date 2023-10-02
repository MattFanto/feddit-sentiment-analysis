from typing import List

from fastapi import APIRouter

from reddit_sentiment_analysis.models import CommentSentiment, SentimentResponse, SortOrder
from reddit_sentiment_analysis.services.predict import predict_sentiment
from reddit_sentiment_analysis.services.feddit_api import fetch_subfeedits_comments

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
    limit = 2
    comments = await fetch_subfeedits_comments(subfeddit_id, limit=limit)
    res = []
    for comment in comments['comments']:
        sentiment = predict_sentiment(comment)
        res.append(CommentSentiment(
            id=comment["id"],
            text=comment["text"],
            created_at=comment["created_at"],
            sentiment=sentiment
        ))
    res = sort_comments(res, order_by)

    return SentimentResponse(
        data=res,
        skip=0,
        limit=limit
    )
