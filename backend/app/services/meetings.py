from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import ActionItem, KeyTopic, Meeting, Participant, Summary, Tag, TranscriptSegment, User
from app.schemas.action_items import ActionItemCreate, ActionItemUpdate
from app.schemas.common import TranscriptSegmentSearchResult
from app.schemas.meeting import MeetingDetailRead, MeetingUpdateRequest
from app.services.transcript_parser import ParsedTranscriptSegment, parse_transcript_text, parse_uploaded_transcript

DEFAULT_USER_EMAIL = "alex.morgan@example.com"


def _meeting_query():
    return select(Meeting).options(
        selectinload(Meeting.created_by_user),
        selectinload(Meeting.participants),
        selectinload(Meeting.transcript_segments),
        selectinload(Meeting.summary),
        selectinload(Meeting.key_topics),
        selectinload(Meeting.action_items),
        selectinload(Meeting.tags),
    )


def _not_found(entity: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{entity} not found")


def _default_user(session: Session) -> User:
    user = session.scalar(select(User).where(User.email == DEFAULT_USER_EMAIL))
    if user is None:
        raise HTTPException(status_code=500, detail="Default user is missing")
    return user


def get_meeting_or_404(session: Session, meeting_id: int) -> Meeting:
    meeting = session.scalar(_meeting_query().where(Meeting.id == meeting_id))
    if meeting is None:
        raise _not_found("Meeting")
    return meeting


def _to_detail(meeting: Meeting) -> MeetingDetailRead:
    return MeetingDetailRead.model_validate(meeting)


def list_meetings(
    session: Session,
    search: str | None = None,
    participant: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    sort: str | None = "recency",
    tags: list[str] | None = None,
) -> list[MeetingDetailRead]:
    query = _meeting_query()
    conditions = []

    if search:
        pattern = f"%{search.strip()}%"
        query = query.join(Meeting.participants, isouter=True).join(Meeting.transcript_segments, isouter=True).join(Meeting.summary, isouter=True).join(Meeting.key_topics, isouter=True)
        conditions.append(
            or_(
                Meeting.title.ilike(pattern),
                Participant.name.ilike(pattern),
                Participant.email.ilike(pattern),
                TranscriptSegment.text.ilike(pattern),
                Summary.overview_text.ilike(pattern),
                KeyTopic.topic_text.ilike(pattern),
            )
        )

    if participant:
        participant_pattern = f"%{participant.strip()}%"
        query = query.join(Meeting.participants, isouter=True)
        conditions.append(or_(Participant.name.ilike(participant_pattern), Participant.email.ilike(participant_pattern)))

    if date_from is not None:
        conditions.append(Meeting.date >= datetime.combine(date_from, datetime.min.time(), tzinfo=timezone.utc))
    if date_to is not None:
        conditions.append(Meeting.date <= datetime.combine(date_to, datetime.max.time(), tzinfo=timezone.utc))

    if conditions:
        query = query.where(*conditions)

    if sort == "oldest":
        query = query.order_by(Meeting.date.asc())
    elif sort == "title":
        query = query.order_by(Meeting.title.asc())
    else:
        query = query.order_by(Meeting.date.desc())

    # Filter by tags if provided. Expect tags as a list of tag names (case-insensitive).
    if tags:
        cleaned = [t.strip().lower() for t in tags if t and t.strip()]
        if cleaned:
            query = query.join(Meeting.tags).where(Tag.name.in_(cleaned))

    return [_to_detail(meeting) for meeting in session.scalars(query).unique().all()]


def _segments_from_payload(items: list[ParsedTranscriptSegment]) -> list[TranscriptSegment]:
    return [
        TranscriptSegment(
            speaker_name=item.speaker_name,
            start_time=item.start_time,
            end_time=item.end_time,
            text=item.text,
            order_index=item.order_index,
        )
        for item in items
    ]


def _summary_text(segments: list[TranscriptSegment]) -> str:
    if not segments:
        return "No transcript content was provided for this meeting."
    return " ".join(segment.text for segment in segments[:3])[:500]


def _topics_from_segments(segments: list[TranscriptSegment]) -> list[KeyTopic]:
    topics = [KeyTopic(topic_text=segment.text[:120], order_index=index) for index, segment in enumerate(segments[:4], start=1)]
    if not topics:
        topics.append(KeyTopic(topic_text="General discussion", order_index=1))
    return topics


def create_meeting_from_upload(
    session: Session,
    *,
    title: str,
    date_value: datetime,
    duration_seconds: int | None,
    audio_url: str | None,
    status: str,
    participants_json: str | None,
    tags_json: str | None,
    transcript_text: str | None,
    transcript_file: UploadFile | None,
) -> MeetingDetailRead:
    user = _default_user(session)

    if transcript_file is not None:
        parsed_segments = parse_uploaded_transcript(transcript_file.filename or "transcript.txt", transcript_file.file.read())
    elif transcript_text:
        parsed_segments = parse_transcript_text(transcript_text)
    else:
        parsed_segments = []

    transcript_segments = _segments_from_payload(parsed_segments)
    meeting = Meeting(
        title=title.strip(),
        date=date_value,
        duration_seconds=duration_seconds or int(transcript_segments[-1].end_time if transcript_segments else 0),
        created_by=user.id,
        audio_url=audio_url,
        status=status,
    )

    if participants_json:
        meeting.participants = [
            Participant(name=item["name"], email=item.get("email"), role=item.get("role", "attendee"))
            for item in json.loads(participants_json)
        ]

    if tags_json:
        for tag_name in json.loads(tags_json):
            cleaned = str(tag_name).strip().lower()
            if not cleaned:
                continue
            tag = session.scalar(select(Tag).where(Tag.name == cleaned))
            if tag is None:
                tag = Tag(name=cleaned)
            meeting.tags.append(tag)

    meeting.transcript_segments = transcript_segments
    meeting.summary = Summary(overview_text=_summary_text(transcript_segments), generated_at=datetime.now(timezone.utc))
    meeting.key_topics = _topics_from_segments(transcript_segments)
    meeting.action_items = []

    session.add(meeting)
    session.commit()
    session.refresh(meeting)
    return _to_detail(get_meeting_or_404(session, meeting.id))


def build_meeting_detail(session: Session, meeting_id: int) -> MeetingDetailRead:
    return _to_detail(get_meeting_or_404(session, meeting_id))


def update_meeting(session: Session, meeting_id: int, payload: MeetingUpdateRequest) -> MeetingDetailRead:
    meeting = get_meeting_or_404(session, meeting_id)
    if payload.title is not None:
        meeting.title = payload.title.strip()
    if payload.participants is not None:
        meeting.participants.clear()
        meeting.participants.extend(Participant(name=item.name, email=item.email, role=item.role) for item in payload.participants)
    session.commit()
    return _to_detail(get_meeting_or_404(session, meeting_id))


def delete_meeting(session: Session, meeting_id: int) -> None:
    meeting = get_meeting_or_404(session, meeting_id)
    session.delete(meeting)
    session.commit()


def add_action_item(session: Session, meeting_id: int, payload: ActionItemCreate) -> ActionItem:
    get_meeting_or_404(session, meeting_id)
    action_item = ActionItem(
        meeting_id=meeting_id,
        text=payload.text,
        assignee=payload.assignee,
        due_date=payload.due_date,
        is_completed=False,
    )
    session.add(action_item)
    session.commit()
    session.refresh(action_item)
    return action_item


def update_action_item(session: Session, action_item_id: int, payload: ActionItemUpdate) -> ActionItem:
    action_item = session.get(ActionItem, action_item_id)
    if action_item is None:
        raise _not_found("Action item")
    if payload.text is not None:
        action_item.text = payload.text
    if payload.assignee is not None:
        action_item.assignee = payload.assignee
    if payload.is_completed is not None:
        action_item.is_completed = payload.is_completed
    if payload.due_date is not None:
        action_item.due_date = payload.due_date
    session.commit()
    session.refresh(action_item)
    return action_item


def delete_action_item(session: Session, action_item_id: int) -> None:
    action_item = session.get(ActionItem, action_item_id)
    if action_item is None:
        raise _not_found("Action item")
    session.delete(action_item)
    session.commit()


def get_transcript_results(session: Session, meeting_id: int, search: str | None) -> list[dict]:
    meeting = get_meeting_or_404(session, meeting_id)
    query = (search or "").strip()
    results: list[dict] = []
    for segment in sorted(meeting.transcript_segments, key=lambda item: item.order_index):
        matches: list[dict] = []
        if query:
            for match in re.finditer(re.escape(query), segment.text, flags=re.IGNORECASE):
                matches.append({"start": match.start(), "end": match.end()})
            if not matches:
                continue
        results.append(
            {
                "id": segment.id,
                "meeting_id": segment.meeting_id,
                "speaker_name": segment.speaker_name,
                "start_time": segment.start_time,
                "end_time": segment.end_time,
                "text": segment.text,
                "order_index": segment.order_index,
                "match_ranges": matches,
            }
        )
    return results


def generate_meeting_summary(session: Session, meeting_id: int) -> Summary:
    meeting = get_meeting_or_404(session, meeting_id)
    generated_text = _summary_text(list(meeting.transcript_segments))
    if meeting.summary is None:
        meeting.summary = Summary(overview_text=generated_text, generated_at=datetime.now(timezone.utc))
    else:
        meeting.summary.overview_text = generated_text
        meeting.summary.generated_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(meeting.summary)
    return meeting.summary


def search_workspace(session: Session, query: str) -> list[dict]:
    normalized = query.strip()
    if not normalized:
        return []

    pattern = f"%{normalized}%"
    meetings = session.scalars(
        _meeting_query().where(
            or_(
                Meeting.title.ilike(pattern),
                Participant.name.ilike(pattern),
                Participant.email.ilike(pattern),
                TranscriptSegment.text.ilike(pattern),
                Summary.overview_text.ilike(pattern),
                Tag.name.ilike(pattern),
                KeyTopic.topic_text.ilike(pattern),
            )
        )
    ).unique().all()

    results = []
    for meeting in meetings:
        transcript_text = " ".join(segment.text for segment in meeting.transcript_segments)
        snippet_source = meeting.summary.overview_text if meeting.summary else transcript_text
        match_count = len(re.findall(re.escape(normalized), f"{meeting.title} {snippet_source} {transcript_text}", flags=re.IGNORECASE))
        results.append(
            {
                "meeting_id": meeting.id,
                "title": meeting.title,
                "date": meeting.date,
                "snippet": snippet_source[:220],
                "match_count": match_count,
                "participants": meeting.participants,
                "tags": meeting.tags,
            }
        )
    return results
