from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from reddit_sentiment_analysis.app import app

client = TestClient(app)


def test_generic_error_while_fetching_subfeddit_comments(
    mocker: MockerFixture,
):
    """
    Test that the service returns an error when the feddit api is unreachable
    """

    mocker.patch("reddit_sentiment_analysis.services.feddit_api.fetch_subfeddit_comments", side_effect=Exception)
    resp = client.get("/api/v1/detect-comments-sentiment?subfeddit_id=1")
    assert resp.status_code == 500
