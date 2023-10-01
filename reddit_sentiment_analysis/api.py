from fastapi import APIRouter

from reddit_sentiment_analysis.models import CommentSentiment, SentimentResponse
from reddit_sentiment_analysis.services import predict_sentiment, fetch_subfeedits_comments

router = APIRouter()


@router.get("/predict", response_model=SentimentResponse)
async def predict(subfeddit_id: int, skip: int = 0, limit: int = 50):
    comments = await fetch_subfeedits_comments(subfeddit_id)
    res = []
    for comment in comments['comments']:
        sentiment = predict_sentiment(comment)
        res.append(CommentSentiment(
            id=comment["id"],
            text=comment["text"],
            sentiment=str(sentiment)
        ))

    return SentimentResponse(
        comments=res,
        skip=0,
        limit=50
    )
