import asyncio
import json
import logging
import re

import aiohttp
from reddit_sentiment_analysis.config import settings
import openai


from json import JSONDecoder

def extract_json_objects(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.

    """
    firstValue = text.index("{")
    lastValue = len(text) - text[::-1].index("}")
    jsonString = text[firstValue:lastValue]
    return jsonString


logger = logging.getLogger()

PROMPT = """
Given the the text below return a sentiment score (float) in the range -1 to 1 (included) where:
* -1 is extremely negative
* 0 is neutral
* 1 is extremely positive 
The output has to be in JSON format, example:
{"score": 0.7, "sentiment": "happy"}

The output will be parsed in Python, it's extremely important to return JSON format only response

This is the prompt:
"""

def predict_sentiment(feedit_data):
    prompt = PROMPT + feedit_data['text']
    # Call the sentiment analysis API with the prompt
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0,
        max_tokens=50,
        n=1,
        stop=None,
        timeout=10,
    )
    out = response.choices[0].text.strip()
    out = extract_json_objects(out)
    try:
        out = json.loads(out)
        assert "score" in out
        assert "sentiment" in out
        return out
    except Exception as e:
        logger.error("Failed to parse JSON response from OpenAI: ", out)
        raise e


async def fetch_subfeedits_comments(subfeddit_id: int, limit: int):
    async with aiohttp.ClientSession() as session:

        url = (
            settings.FEDDIT_URL +
            f"/api/v1/comments/" +
            f"?subfeddit_id={subfeddit_id}&limit={limit}"
        )
        async with session.get(url) as resp:
            data = await resp.json()

    return data
