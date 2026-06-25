from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import KeyTopicRead, ParticipantCreate, ParticipantRead, SummaryRead, TagRead, TranscriptSegmentRead
from app.schemas.action_items import ActionItemRead


class MeetingUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    participants: list[ParticipantCreate] | None = None


class MeetingListItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    date: datetime
    duration_seconds: int
    audio_url: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    participants: list[ParticipantRead] = Field(default_factory=list)
    tags: list[TagRead] = Field(default_factory=list)


class MeetingDetailRead(MeetingListItemRead):
    summary: SummaryRead | None = None
    transcript_segments: list[TranscriptSegmentRead] = Field(default_factory=list)
    key_topics: list[KeyTopicRead] = Field(default_factory=list)
    action_items: list[ActionItemRead] = Field(default_factory=list)


class MeetingCreateResponse(MeetingDetailRead):
    pass


class TranscriptSearchResponse(BaseModel):
    meeting_id: int
    query: str | None = None
    segments: list[TranscriptSegmentRead]

