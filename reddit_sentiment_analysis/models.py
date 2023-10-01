from typing import List

from pydantic import BaseModel, Field


class CommentSentiment(BaseModel):
    id: int = Field(...,
                    description="Comment ID",
                    examples=[999])
    text: str = Field(...,
                      description='Original comment\'s text',
                      examples=['Awesome product'])
    sentiment: str = Field(...,
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
