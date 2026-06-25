from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ErrorDetails(BaseModel):
    code: str
    message: str
    details: dict | list | str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetails


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    avatar_url: str | None = None


class ParticipantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr | None = None
    role: str = Field(default="attendee", min_length=1, max_length=80)


class ParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    name: str
    email: EmailStr | None = None
    role: str


class MatchRange(BaseModel):
    start: int
    end: int


class SummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    overview_text: str
    generated_at: datetime


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class KeyTopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    topic_text: str
    order_index: int


class TranscriptSegmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meeting_id: int
    speaker_name: str
    start_time: float
    end_time: float
    text: str
    order_index: int


class TranscriptMatchRange(BaseModel):
    start: int
    end: int


class TranscriptSegmentSearchResult(TranscriptSegmentRead):
    match_ranges: list[TranscriptMatchRange] = Field(default_factory=list)
