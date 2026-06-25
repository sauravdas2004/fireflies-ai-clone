from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import SummaryRead
from app.services.meetings import generate_meeting_summary

router = APIRouter(tags=["summaries"])


@router.post("/meetings/{meeting_id}/generate-summary", response_model=SummaryRead)
def post_generate_summary(meeting_id: int, db: Session = Depends(get_db)):
    return generate_meeting_summary(db, meeting_id)

