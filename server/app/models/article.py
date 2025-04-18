from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime


class SourceModel(BaseModel):
    name: str
    url: Optional[HttpUrl]


class ArticleModel(BaseModel):
    title: str
    description: Optional[str]
    content: Optional[str]
    url: HttpUrl
    image: Optional[HttpUrl]
    category: list[str]
    language: str
    country: str
    publishedAt: datetime
    popularity:int
    source: SourceModel
    
class ArticleInDB(ArticleModel):
    id: Optional[str] = Field(alias="_id")
