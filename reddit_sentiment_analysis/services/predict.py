import json
import time

import openai

from reddit_sentiment_analysis.logs import logger
from reddit_sentiment_analysis.models import SentimentScore
from reddit_sentiment_analysis.utils import ElapsedTimer
from reddit_sentiment_analysis.metrics import OPENAI_PROMPT_TOKENS, OPENAI_COMPLETION_TOKENS


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
Given the the text below return a sentiment score (float) in the range -1 to 1 (included) where:
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
{"score": 0.7, "sentiment": "happy"}

The output will be parsed in Python, it's extremely important to return JSON format only response

This is the prompt:
"""


def predict_sentiment(feedit_data) -> SentimentScore:
    prompt = PROMPT + feedit_data['text']
    # Call the sentiment analysis API with the prompt
    t = ElapsedTimer()
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0,
        max_tokens=50,
        n=1,
        stop=None,
        timeout=10,
    )
    openai_output = response.choices[0].text.strip()
    logger.info("OpenAI response", extra={
        "openai_output": openai_output,
        "duration_ms": t.elapsed(),
        "usage": response["usage"],
    })
    OPENAI_PROMPT_TOKENS.observe(response['usage']['prompt_tokens'])
    OPENAI_COMPLETION_TOKENS.observe(response['usage']['completion_tokens'])
    try:
        score = extract_json_objects(openai_output)
        return SentimentScore(**score)
    except Exception as e:
        logger.error("Failed to parse JSON response from OpenAI: ", extra={
            "original_response": openai_output,
            "exception": str(e)
        })
        raise e
