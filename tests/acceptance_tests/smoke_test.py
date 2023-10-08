import pytest
import requests

from reddit_sentiment_analysis.config import settings


def test_detect_sentiment_endpoint():
    """
    Smoke test to check deployment is working
    Run this kind of test during CI/CD after deployment against target environment (dev, qa, prod).

    This requires the service to be deployed and running.
    """
    response = requests.get(f"http://{settings.host}:{settings.port}/api/v1/detect-comments-sentiment?subfeddit_id=1")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0
