from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.action_items import ActionItemCreate, ActionItemRead
from app.schemas.meetings import MeetingCreateResponse, MeetingDetailRead, MeetingListItemRead, MeetingUpdateRequest, TranscriptSearchResponse
from app.services.meetings import add_action_item, build_meeting_detail, create_meeting_from_upload, delete_meeting, generate_meeting_summary, get_meeting_or_404, get_transcript_results, list_meetings, update_meeting

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("", response_model=list[MeetingListItemRead])
def get_meetings(
    search: str | None = Query(default=None),
    participant: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort: str | None = Query(default="recency"),
    tags: list[str] | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_meetings(db, search=search, participant=participant, date_from=date_from, date_to=date_to, sort=sort, tags=tags)


@router.post("", response_model=MeetingCreateResponse)
def create_meeting(
    title: str = Form(...),
    date_value: datetime = Form(...),
    duration_seconds: int | None = Form(default=None),
    audio_url: str | None = Form(default=None),
    status: str = Form(default="completed"),
    participants_json: str | None = Form(default=None),
    tags_json: str | None = Form(default=None),
    transcript_text: str | None = Form(default=None),
    transcript_file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
):
    return create_meeting_from_upload(
        db,
        title=title,
        date_value=date_value,
        duration_seconds=duration_seconds,
        audio_url=audio_url,
        status=status,
        participants_json=participants_json,
        tags_json=tags_json,
        transcript_text=transcript_text,
        transcript_file=transcript_file,
    )


@router.get("/{meeting_id}", response_model=MeetingDetailRead)
def read_meeting(meeting_id: int, db: Session = Depends(get_db)):
    return build_meeting_detail(db, meeting_id)


@router.put("/{meeting_id}", response_model=MeetingDetailRead)
def update_meeting_endpoint(meeting_id: int, payload: MeetingUpdateRequest, db: Session = Depends(get_db)):
    return update_meeting(db, meeting_id, payload)


@router.delete("/{meeting_id}")
def delete_meeting_endpoint(meeting_id: int, db: Session = Depends(get_db)):
    delete_meeting(db, meeting_id)
    return {"message": "Meeting deleted"}


@router.get("/{meeting_id}/transcript", response_model=TranscriptSearchResponse)
def read_meeting_transcript(meeting_id: int, search: str | None = Query(default=None), db: Session = Depends(get_db)):
    meeting = get_meeting_or_404(db, meeting_id)
    return {
        "meeting_id": meeting.id,
        "query": search,
        "segments": get_transcript_results(db, meeting_id, search),
    }


@router.post("/{meeting_id}/action-items", response_model=ActionItemRead)
def create_action_item(meeting_id: int, payload: ActionItemCreate, db: Session = Depends(get_db)):
    return add_action_item(db, meeting_id, payload)


@router.post("/{meeting_id}/generate-summary", response_model=MeetingDetailRead)
def generate_summary_endpoint(meeting_id: int, db: Session = Depends(get_db)):
    generate_meeting_summary(db, meeting_id)
    return get_meeting_or_404(db, meeting_id)
