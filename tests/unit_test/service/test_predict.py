import boto3
import moto
import pytest

from reddit_sentiment_analysis.services.predict import aws_predict_sentiment


def test_aws_predict_sentiment_success():
    with moto.mock_comprehend() as m:
        comment = {"text": "This is a great day!"}
        client = boto3.client("comprehend")
        response = client.detect_sentiment(Text=comment["text"], LanguageCode="en")
        res = aws_predict_sentiment(comment)
        assert res.score == response["SentimentScore"]["Positive"] - response["SentimentScore"]["Negative"]
        assert res.sentiment == response["Sentiment"]


def test_aws_predict_empty_input():
    with moto.mock_comprehend() as m:
        comment = {"text": ""}
        with pytest.raises(Exception):
            aws_predict_sentiment(comment)
