from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import TranscriptSegmentSearchResult
from app.services.meetings import get_transcript_results

router = APIRouter(tags=["transcripts"])


@router.get("/meetings/{meeting_id}/transcript", response_model=list[TranscriptSegmentSearchResult])
def get_transcript(meeting_id: int, search: str | None = None, db: Session = Depends(get_db)):
    return get_transcript_results(db, meeting_id, search)

