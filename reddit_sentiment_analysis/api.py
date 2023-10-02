from fastapi import APIRouter

from reddit_sentiment_analysis.models import CommentSentiment, SentimentResponse
from reddit_sentiment_analysis.services import predict_sentiment, fetch_subfeedits_comments

router = APIRouter()


@router.get("/predict", response_model=SentimentResponse)
async def predict(subfeddit_id: int):
    limit = 25
    comments = await fetch_subfeedits_comments(subfeddit_id, limit=limit)
    res = []
    for comment in comments['comments']:
        sentiment = predict_sentiment(comment)
        res.append(CommentSentiment(
            id=comment["id"],
            text=comment["text"],
            sentiment=sentiment
        ))

    return SentimentResponse(
        data=res,
        skip=0,
        limit=limit
    )
