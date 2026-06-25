from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ask import AskRequest, AskResponse
from app.services.meetings import get_meeting_or_404

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)):
    # This is a lightweight mock for Phase 4. It returns a canned answer
    # optionally referencing the meeting summary when a meeting_id is provided.
    source_text = None
    if payload.meeting_id is not None:
        meeting = get_meeting_or_404(db, payload.meeting_id)
        if meeting.summary is not None:
            source_text = meeting.summary.overview_text

    if source_text:
        answer = f"(Mock) Based on the meeting summary: {source_text[:400]}"
    else:
        answer = "(Mock) I don't have access to an LLM in this environment, but this is where an answer would go."

    return {"answer": answer, "source": source_text}
