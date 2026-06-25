from __future__ import annotations

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    meeting_id: int | None = None


class AskResponse(BaseModel):
    answer: str
    source: str | None = None
