import type { MeetingDetail, TranscriptSegment } from "./types";

export function downloadText(filename: string, content: string) {
  const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

function pad(n: number) {
  return n < 10 ? `0${n}` : `${n}`;
}

function formatTimestamp(sec: number) {
  const s = Math.floor(sec || 0);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const ss = s % 60;
  if (h > 0) return `${h}:${pad(m)}:${pad(ss)}`;
  return `${pad(m)}:${pad(ss)}`;
}

export function formatMeetingMarkdown(
  meeting: Partial<MeetingDetail>,
  segments: TranscriptSegment[] = [],
) {
  const lines: string[] = [];
  lines.push(`# ${meeting.title ?? "Meeting"}\n`);

  if (meeting.created_at) {
    lines.push(`**Date:** ${new Date(meeting.created_at).toLocaleString()}\n`);
  }

  if (meeting.participants && meeting.participants.length) {
    const names = meeting.participants.map((p) => p.name).join(", ");
    lines.push(`**Participants:** ${names}\n`);
  }

  if (meeting.summary?.overview_text) {
    lines.push("## Summary\n");
    lines.push(meeting.summary.overview_text + "\n");
  }

  if (meeting.key_topics && meeting.key_topics.length) {
    lines.push("## Key Topics\n");
    meeting.key_topics.forEach((t) => lines.push(`- ${t.topic_text}`));
    lines.push("");
  }

  if (meeting.action_items && meeting.action_items.length) {
    lines.push("## Action Items\n");
    meeting.action_items.forEach((ai) =>
      lines.push(
        `- [${ai.is_completed ? "x" : " "}] ${ai.text}${ai.assignee ? ` (Owner: ${ai.assignee})` : ""}`,
      ),
    );
    lines.push("");
  }

  if (segments && segments.length) {
    lines.push("## Transcript\n");
    segments.forEach((seg) => {
      const ts = formatTimestamp(seg.start_time ?? 0);
      lines.push(`- [${ts}] ${seg.speaker_name ?? "Speaker"}: ${seg.text}`);
    });
    lines.push("");
  }

  return lines.join("\n");
}
