from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=20)
    level: str = Field(default="B1", max_length=20)
    source: str = Field(default="user_upload", max_length=200)


class ArticleOut(BaseModel):
    id: int
    title: str
    content: str
    level: str
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleBrief(BaseModel):
    id: int
    title: str
    level: str
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

