from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime


class SourceModel(BaseModel):
    title: str
    url: Optional[HttpUrl]
    created_utc: Optional[float]
    subreddit: Optional[str]
    media: Optional[List[HttpUrl]]
    content: Optional[str]


class ArticleModel(BaseModel):
    title: str
    summary: Optional[str] = Field(None, alias="description")  # if used interchangeably
    content: Optional[str]
    publication_date: datetime = Field(..., alias="publishedAt")
    category: str
    tags: List[str]
    popularity: int
    duration: Optional[float]
    source: SourceModel


class ArticleInDB(ArticleModel):
    id: Optional[str] = Field(default=None, alias="_id")
class DurationRequest(BaseModel):
    durationMs: float