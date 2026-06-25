from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ParticipantRead, TagRead


class GlobalSearchResultRead(BaseModel):
    meeting_id: int
    title: str
    date: datetime
    snippet: str
    match_count: int
    participants: list[ParticipantRead] = Field(default_factory=list)
    tags: list[TagRead] = Field(default_factory=list)


class GlobalSearchResponse(BaseModel):
    query: str
    results: list[GlobalSearchResultRead] = Field(default_factory=list)
