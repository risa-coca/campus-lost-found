from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    type: Literal[0, 1]
    category: str = Field(min_length=1, max_length=32)
    title: str = Field(min_length=1, max_length=128)
    description: str = Field(default="", max_length=2000)
    location: str = Field(default="", max_length=128)
    event_time: datetime | None = None
    image_url: str | None = None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    type: int
    category: str
    title: str
    description: str
    location: str | None
    event_time: datetime | None
    image_url: str | None
    status: int
    created_at: datetime


class ItemListOut(BaseModel):
    total: int
    items: list[ItemOut]