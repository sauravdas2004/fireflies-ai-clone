from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedTranscriptLine:
    speaker_name: str
    start_time: float
    end_time: float
    text: str
    order_index: int


SPEAKER_LINE_RE = re.compile(r"^\s*(?P<speaker>[^:]{1,120}):\s*(?P<text>.+?)\s*$")
VTT_TIMESTAMP_RE = re.compile(r"^(?P<start>\d{2}:\d{2}:\d{2}\.\d{3})\s+-->\s+(?P<end>\d{2}:\d{2}:\d{2}\.\d{3})$")


def _timestamp_to_seconds(timestamp: str) -> float:
    hours, minutes, remainder = timestamp.split(":")
    seconds, milliseconds = remainder.split(".")
    return (int(hours) * 3600) + (int(minutes) * 60) + int(seconds) + (int(milliseconds) / 1000)


def _estimate_duration(text: str) -> float:
    # Shorter utterances get a smaller duration; this keeps pasted transcripts playable.
    word_count = max(1, len(text.split()))
    return max(8.0, min(45.0, word_count * 1.8))


def parse_text_transcript(raw_text: str) -> list[ParsedTranscriptLine]:
    lines: list[ParsedTranscriptLine] = []
    cursor = 0.0
    for order_index, raw_line in enumerate(raw_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        match = SPEAKER_LINE_RE.match(line)
        if match:
            speaker_name = match.group("speaker").strip()
            text = match.group("text").strip()
        else:
            speaker_name = "Speaker"
            text = line
        duration = _estimate_duration(text)
        lines.append(
            ParsedTranscriptLine(
                speaker_name=speaker_name,
                start_time=round(cursor, 3),
                end_time=round(cursor + duration, 3),
                text=text,
                order_index=order_index,
            )
        )
        cursor += duration
    return lines


def parse_vtt_transcript(raw_text: str) -> list[ParsedTranscriptLine]:
    lines: list[ParsedTranscriptLine] = []
    blocks = [block.strip() for block in raw_text.split("\n\n") if block.strip()]
    order_index = 1
    for block in blocks:
        block_lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not block_lines or block_lines[0].upper() == "WEBVTT":
            continue
        timestamp_line = next((line for line in block_lines if "-->" in line), None)
        if not timestamp_line:
            continue
        timestamp_match = VTT_TIMESTAMP_RE.match(timestamp_line)
        if not timestamp_match:
            continue
        start_time = _timestamp_to_seconds(timestamp_match.group("start"))
        end_time = _timestamp_to_seconds(timestamp_match.group("end"))
        payload_lines = [line for line in block_lines if line != timestamp_line]
        payload_text = " ".join(payload_lines)
        speaker_match = SPEAKER_LINE_RE.match(payload_text)
        if speaker_match:
            speaker_name = speaker_match.group("speaker").strip()
            text = speaker_match.group("text").strip()
        else:
            speaker_name = "Speaker"
            text = payload_text.strip()
        lines.append(
            ParsedTranscriptLine(
                speaker_name=speaker_name,
                start_time=round(start_time, 3),
                end_time=round(end_time, 3),
                text=text,
                order_index=order_index,
            )
        )
        order_index += 1
    return lines


def parse_json_transcript(raw_text: str) -> list[ParsedTranscriptLine]:
    payload = json.loads(raw_text)
    if isinstance(payload, dict):
        segments = payload.get("segments", payload.get("transcript_segments", []))
    else:
        segments = payload

    lines: list[ParsedTranscriptLine] = []
    cursor = 0.0
    for order_index, segment in enumerate(segments, start=1):
        speaker_name = str(segment.get("speaker_name") or segment.get("speaker") or "Speaker")
        text = str(segment.get("text") or "").strip()
        if not text:
            continue
        start_time = segment.get("start_time")
        end_time = segment.get("end_time")
        if start_time is None or end_time is None:
            start_time = cursor
            end_time = cursor + _estimate_duration(text)
        lines.append(
            ParsedTranscriptLine(
                speaker_name=speaker_name,
                start_time=float(start_time),
                end_time=float(end_time),
                text=text,
                order_index=order_index,
            )
        )
        cursor = float(end_time)
    return lines


def parse_transcript_file(filename: str, raw_text: str) -> list[ParsedTranscriptLine]:
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return parse_text_transcript(raw_text)
    if suffix == ".vtt":
        return parse_vtt_transcript(raw_text)
    if suffix == ".json":
        return parse_json_transcript(raw_text)
    raise ValueError(f"Unsupported transcript file type: {suffix or 'unknown'}")
