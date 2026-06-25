"use client";

import { useMemo } from 'react';
import type { TranscriptSegment } from '@/lib/types';
import { cn } from './cn';

function highlightText(text: string, query: string) {
  if (!query.trim()) {
    return [{ text, highlight: false }];
  }

  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'ig');
  return text.split(regex).filter(Boolean).map((part) => ({ text: part, highlight: part.toLowerCase() === query.trim().toLowerCase() }));
}

function findActiveIndex(segments: TranscriptSegment[], currentTime: number) {
  let low = 0;
  let high = segments.length - 1;
  let candidate = 0;

  // Binary search keeps sync smooth even when the transcript is long.
  while (low <= high) {
    const mid = Math.floor((low + high) / 2);
    if (segments[mid].start_time <= currentTime) {
      candidate = mid;
      low = mid + 1;
    } else {
      high = mid - 1;
    }
  }

  return candidate;
}

export function TranscriptPanel({
  segments,
  currentTime,
  searchQuery,
  activeMatchIndex,
  onSeek,
  onSelectMatch,
}: {
  segments: TranscriptSegment[];
  currentTime: number;
  searchQuery: string;
  activeMatchIndex: number;
  onSeek: (time: number) => void;
  onSelectMatch: (index: number) => void;
}) {
  const activeIndex = useMemo(() => findActiveIndex(segments, currentTime), [segments, currentTime]);
  const matches = useMemo(() => {
    if (!searchQuery.trim()) return [];
    return segments.flatMap((segment, segmentIndex) =>
      segment.match_ranges?.map((match, matchIndex) => ({ segmentIndex, matchIndex, segment, match })) ?? []
    );
  }, [segments, searchQuery]);

  return (
    <div className="rounded-[28px] border border-border bg-panel p-4 shadow-soft">
      <div className="flex items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h3 className="text-lg font-semibold">Transcript</h3>
          <p className="text-sm text-muted">Click a line to seek the player. Active line follows playback.</p>
        </div>
        <div className="rounded-full bg-panel-strong px-3 py-1 text-xs font-medium text-muted">
          {matches.length ? `${Math.min(activeMatchIndex + 1, matches.length)} / ${matches.length} matches` : 'No transcript search'}
        </div>
      </div>

      <div className="mt-4 max-h-[680px] space-y-2 overflow-auto pr-1">
        {segments.map((segment, index) => {
          const isActive = index === activeIndex;
          const isMatch = Boolean(searchQuery.trim()) && segment.text.toLowerCase().includes(searchQuery.trim().toLowerCase());
          return (
            <button
              key={segment.id}
              type="button"
              onClick={() => onSeek(segment.start_time)}
              className={cn(
                'w-full rounded-2xl border px-4 py-3 text-left transition',
                isActive ? 'border-accent bg-accent-soft' : 'border-transparent bg-panel-strong hover:border-border hover:bg-panel'
              )}
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2 text-xs text-muted">
                  <span className="font-semibold text-text">{segment.speaker_name}</span>
                  <span>{formatTimestamp(segment.start_time)}</span>
                </div>
                {isMatch ? <span className="rounded-full bg-accent px-2 py-1 text-[10px] font-semibold text-white">Match</span> : null}
              </div>
              <p className="mt-2 text-sm leading-6 text-text">
                {highlightText(segment.text, searchQuery).map((part, partIndex) => (
                  <span key={partIndex} className={cn(part.highlight && 'rounded bg-yellow-200/70 px-0.5 text-text')}>{part.text}</span>
                ))}
              </p>
            </button>
          );
        })}
      </div>

      {searchQuery.trim() ? (
        <div className="mt-4 flex items-center justify-between border-t border-border pt-4 text-sm">
          <button type="button" onClick={() => onSelectMatch(Math.max(0, activeMatchIndex - 1))} className="rounded-full border border-border px-3 py-1.5 text-muted transition hover:bg-panel-strong">
            Previous match
          </button>
          <button type="button" onClick={() => onSelectMatch(Math.min(Math.max(matches.length - 1, 0), activeMatchIndex + 1))} className="rounded-full border border-border px-3 py-1.5 text-muted transition hover:bg-panel-strong">
            Next match
          </button>
        </div>
      ) : null}
    </div>
  );
}

function formatTimestamp(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainder = Math.floor(seconds % 60);
  return `${minutes}:${String(remainder).padStart(2, '0')}`;
}
