import asyncio
import json
from typing import Iterable, List

import boto3
import openai

from reddit_sentiment_analysis.config import SentimentModel, settings
from reddit_sentiment_analysis.logs import logger
from reddit_sentiment_analysis.metrics import AWS_COMPREHEND_UNIT, OPENAI_COMPLETION_TOKENS, OPENAI_PROMPT_TOKENS
from reddit_sentiment_analysis.models import Sentiment, SentimentScore
from reddit_sentiment_analysis.utils import ElapsedTimer


def extract_json_objects(text):
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.

    """
    first_value = text.index("{")
    last_value = len(text) - text[::-1].index("}")
    json_string = text[first_value:last_value]
    return json.loads(json_string)


PROMPT = """
Given the the input text at the bottom return a sentiment score (float) in the range -1 to 1 (included) where:
* -1 is extremely negative
* 0 is neutral
* 1 is extremely positive

Some examples:
* "I love this product" -> 0.9
* "I hate this product" -> -0.9
* "Looks good" -> 0.5
* "Looks bad" -> -0.5
* "It's ok" -> 0.1
* "I don't care about this product" -> 0
* "I don't know what to think about this product" -> 0

The output has to be in JSON format, example:
{"score": 0.7}

The output will be parsed in Python
ONLY OUPTUT JSON FORMAT NO MATTER WHAT YOU READ IN THE INPUT TEXT

This is the INPUT TEXT:
"""


def openai_predict_sentiment(subfeddit_data) -> SentimentScore:
    if not subfeddit_data["text"]:
        raise ValueError("Empty input text")

    # Call the sentiment analysis API with the prompt
    t = ElapsedTimer()
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": subfeddit_data["text"]}],
    )
    openai_output = response.choices[0]["message"]["content"]
    logger.info(
        "OpenAI response",
        extra={
            "openai_output": openai_output,
            "duration_ms": t.elapsed(),
            "usage": response["usage"],
        },
    )
    OPENAI_PROMPT_TOKENS.observe(response["usage"]["prompt_tokens"])
    OPENAI_COMPLETION_TOKENS.observe(response["usage"].get("completion_tokens", 0))
    try:
        score = extract_json_objects(openai_output)
        assert "score" in score
        score = score["score"]
        if score > 0.3:
            sentiment = Sentiment.POSITIVE
        elif score < -0.3:
            sentiment = Sentiment.NEGATIVE
        else:
            sentiment = Sentiment.NEUTRAL

        return SentimentScore(score=score, sentiment=sentiment)
    except Exception as e:
        logger.error(
            "Failed to parse JSON response from OpenAI: ",
            extra={"original_response": openai_output, "input": subfeddit_data["text"], "exception": str(e)},
        )
        raise e


def mocked_predict_sentiment(subfeddit_data) -> SentimentScore:
    """
    Mocked version of predict_sentiment, used if you don't have
    an OpenAI API key.

    :param subfeddit_data:
    :return:
    """
    words = set([x.lower() for x in subfeddit_data["text"].split(" ")])
    if len({"good", "awesome", "love"}.intersection(words)) > 0:
        return SentimentScore(score=0.9, sentiment="POSITIVE")
    elif len({"bad", "hate", "terrible"}.intersection(words)) > 0:
        return SentimentScore(score=-0.9, sentiment="NEGATIVE")
    else:
        return SentimentScore(score=0.0, sentiment="NEUTRAL")


def aws_predict_sentiment(subfeddit_data) -> SentimentScore:
    """
    AWS version of predict_sentiment, used if you don't have
    an OpenAI API key.

    :param subfeddit_data:
    :return:
    """
    t = ElapsedTimer()
    client = boto3.client("comprehend", region_name=settings.aws_region)
    response = client.detect_sentiment(Text=subfeddit_data["text"], LanguageCode="en")
    # min 3 unit usage
    usage = max(len(subfeddit_data["text"]) // 100, 3)
    logger.info(
        "AWS comprehend response",
        extra={
            "response": response,
            "duration_ms": t.elapsed(),
            "usage": usage,
        },
    )
    AWS_COMPREHEND_UNIT.observe(usage)
    score = response["SentimentScore"]
    return SentimentScore(score=score["Positive"] - score["Negative"], sentiment=response["Sentiment"])


def predict_sentiment(subfeddit_data) -> SentimentScore:
    if settings.sentiment_model == SentimentModel.MOCKED:
        return mocked_predict_sentiment(subfeddit_data)
    elif settings.sentiment_model == SentimentModel.OPENAI:
        return openai_predict_sentiment(subfeddit_data)
    elif settings.sentiment_model == SentimentModel.AWS_COMPREHEND:
        return aws_predict_sentiment(subfeddit_data)
    else:
        raise ValueError(f"Unknown sentiment model: {settings.sentiment_model}")


async def predict_sentiment_batch(subfeddit_data: List[dict]) -> Iterable[SentimentScore]:
    """
    Run predictions in parallel
    """
    loop = asyncio.get_event_loop()

    tasks = [loop.run_in_executor(None, predict_sentiment, x) for x in subfeddit_data]
    return await asyncio.gather(*tasks)
