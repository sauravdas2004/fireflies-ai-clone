from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from .common import KeyTopicRead, ParticipantCreate, ParticipantRead, SummaryRead, TagRead, TranscriptSegmentRead, UserRead
from .action_item import ActionItemRead


class MeetingUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    participants: list[ParticipantCreate] | None = None


class MeetingCreateResponse(BaseModel):
    id: int
    title: str
    status: str


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
    created_by_user: UserRead
    participants: list[ParticipantRead] = []
    tags: list[TagRead] = []


class MeetingDetailRead(MeetingListItemRead):
    transcript_segments: list[TranscriptSegmentRead] = []
    summary: SummaryRead | None = None
    key_topics: list[KeyTopicRead] = []
    action_items: list[ActionItemRead] = []

