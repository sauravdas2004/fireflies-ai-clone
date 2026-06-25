from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ActionItemCreate(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    assignee: str | None = Field(default=None, max_length=120)
    due_date: date | None = None


class ActionItemUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=4000)
    assignee: str | None = Field(default=None, max_length=120)
    is_completed: bool | None = None
    due_date: date | None = None


class ActionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    assignee: str | None = None
    is_completed: bool
    due_date: date | None = None
    created_at: datetime

