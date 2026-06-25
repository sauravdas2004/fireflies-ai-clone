from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


@dataclass(slots=True)
class ParsedTranscriptSegment:
    speaker_name: str
    start_time: float
    end_time: float
    text: str
    order_index: int


_TXT_LINE_RE = re.compile(r"^(?P<speaker>[^:]{1,120}):\s*(?P<text>.+)$")
_VTT_TIMESTAMP_RE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2}\.\d{3})"
)


def _timestamp_to_seconds(timestamp: str) -> float:
    hours, minutes, rest = timestamp.split(":")
    seconds, milliseconds = rest.split(".")
    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(milliseconds) / 1000.0
    )


def _estimate_duration(text: str) -> float:
    # Shorter notes should stay brief; longer transcript lines get a slightly longer synthetic duration.
    word_count = max(len(text.split()), 1)
    return max(4.0, min(18.0, word_count * 0.42))


def parse_transcript_text(raw_text: str) -> list[ParsedTranscriptSegment]:
    segments: list[ParsedTranscriptSegment] = []
    cursor = 0.0
    for order_index, line in enumerate(raw_text.splitlines(), start=1):
        cleaned = line.strip()
        if not cleaned:
            continue
        match = _TXT_LINE_RE.match(cleaned)
        if match:
            speaker = match.group("speaker").strip()
            text = match.group("text").strip()
        else:
            speaker = "Speaker"
            text = cleaned
        duration = _estimate_duration(text)
        segments.append(
            ParsedTranscriptSegment(
                speaker_name=speaker,
                start_time=round(cursor, 3),
                end_time=round(cursor + duration, 3),
                text=text,
                order_index=order_index,
            )
        )
        cursor += duration
    return segments


def parse_txt_transcript(raw_text: str) -> list[ParsedTranscriptSegment]:
    return parse_transcript_text(raw_text)


def parse_vtt_transcript(raw_text: str) -> list[ParsedTranscriptSegment]:
    segments: list[ParsedTranscriptSegment] = []
    cues = re.split(r"\n\s*\n", raw_text.strip())
    order_index = 0
    for cue in cues:
        lines = [line.strip() for line in cue.splitlines() if line.strip()]
        if not lines or lines[0] == "WEBVTT":
            continue
        timestamp_line = next((line for line in lines if "-->" in line), None)
        if not timestamp_line:
            continue
        timestamp_match = _VTT_TIMESTAMP_RE.search(timestamp_line)
        if not timestamp_match:
            continue
        content_lines = [line for line in lines if line != timestamp_line]
        text = " ".join(content_lines).strip()
        speaker = "Speaker"
        if ":" in text:
            prefix, remainder = text.split(":", 1)
            if len(prefix) <= 120:
                speaker = prefix.strip()
                text = remainder.strip()
        order_index += 1
        segments.append(
            ParsedTranscriptSegment(
                speaker_name=speaker,
                start_time=_timestamp_to_seconds(timestamp_match.group("start")),
                end_time=_timestamp_to_seconds(timestamp_match.group("end")),
                text=text,
                order_index=order_index,
            )
        )
    return segments


def parse_json_transcript(raw_text: str) -> list[ParsedTranscriptSegment]:
    payload = json.loads(raw_text)
    if isinstance(payload, dict):
        items = payload.get("segments") or payload.get("transcript") or []
    else:
        items = payload

    segments: list[ParsedTranscriptSegment] = []
    for index, item in enumerate(items, start=1):
        speaker = item.get("speaker_name") or item.get("speaker") or "Speaker"
        segments.append(
            ParsedTranscriptSegment(
                speaker_name=speaker,
                start_time=float(item.get("start_time", 0)),
                end_time=float(item.get("end_time", 0)),
                text=str(item.get("text", "")).strip(),
                order_index=int(item.get("order_index", index)),
            )
        )
    return segments


def parse_uploaded_transcript(filename: str, content: bytes) -> list[ParsedTranscriptSegment]:
    raw_text = content.decode("utf-8", errors="replace")
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return parse_txt_transcript(raw_text)
    if suffix == ".vtt":
        return parse_vtt_transcript(raw_text)
    if suffix == ".json":
        return parse_json_transcript(raw_text)
    raise ValueError("Unsupported transcript file type. Use .txt, .vtt, or .json.")

