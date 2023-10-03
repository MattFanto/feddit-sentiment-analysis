import pytest
import requests

from reddit_sentiment_analysis.config import settings


def test_predict_endpoint():
    """Smoke test to check deployment is working"""
    response = requests.get(f"http://{settings.host}:{settings.port}/api/v1/predict?subfeddit_id=1")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0
