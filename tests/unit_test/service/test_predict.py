import boto3
import moto
import pytest

from reddit_sentiment_analysis.services.detect_sentiment import aws_detect_sentiment
from reddit_sentiment_analysis.services.feddit_api import Comment


def get_comment(text):
    return Comment(text=text, id=0, username="test", created_at=0)


def test_aws_predict_sentiment_success():
    with moto.mock_comprehend() as m:
        comment = get_comment("This is a great day!")
        client = boto3.client("comprehend")
        response = client.detect_sentiment(Text=comment.text, LanguageCode="en")
        res = aws_detect_sentiment(comment)
        assert res.score == response["SentimentScore"]["Positive"] - response["SentimentScore"]["Negative"]
        assert res.sentiment == response["Sentiment"]


def test_aws_predict_empty_input():
    with moto.mock_comprehend() as m:
        comment = get_comment("")
        with pytest.raises(Exception):
            aws_detect_sentiment(comment)
