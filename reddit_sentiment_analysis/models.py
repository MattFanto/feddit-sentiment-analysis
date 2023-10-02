from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class SortOrder(str, Enum):
    """
    Sort order for comments.
    Using django style syntax
    """
    CREATED_AT_DESC = '-created_at'
    CREATED_AT_ASC = '+created_at'
    SENTIMENT_SCORE_DESC = '-sentiment_score'
    SENTIMENT_SCORE_ASC = '+sentiment_score'
    NONE = ''


class SentimentScore(BaseModel):
    score: float = Field(...,
                         description="Score from -1 to 1",
                         examples=['0.89', '-0.32'])
    sentiment: str = Field(...,
                           description='Sentiment name',
                           examples=['happy'])


class CommentSentiment(BaseModel):
    id: int = Field(...,
                    description="Comment ID",
                    examples=[999])
    text: str = Field(...,
                      description='Original comment\'s text',
                      examples=['Awesome product'])
    created_at: int = Field(...,
                            description="Created time of the subfeddit in Unix"
                                        " epochs.", examples=[1695757477])
    sentiment: SentimentScore = Field(...,
                                      description="Sentiment inferred by the model for this comment")


class SentimentResponse(BaseModel):
    data: List[CommentSentiment] = Field(...,
                                         description='Comments with sentiment score')
    limit: int = Field(...,
                       description="Max comment per request.",
                       examples=[50])
    skip: int = Field(...,
                      description="Items skipped.",
                      examples=[0])
