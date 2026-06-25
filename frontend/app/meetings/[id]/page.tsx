"use client";

import useSWR from 'swr';
import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { Download, Search } from 'lucide-react';
import { getMeeting, getTranscript, updateActionItem, deleteActionItem, generateSummary } from '@/lib/api';
import { downloadText, formatMeetingMarkdown } from '@/lib/export';
import { askQuestion } from '@/lib/api';
import { MediaPlayer } from '@/components/media-player';
import { TranscriptPanel } from '@/components/transcript-panel';
import { SummaryPanel } from '@/components/summary-panel';
import { ActionItemRow } from '@/components/action-item-row';
import { useToasts } from '@/components/toast-provider';
import type { ActionItem } from '@/lib/types';
import AskBox from '@/components/ask-box';

export default function MeetingDetailPage() {
  const params = useParams<{ id: string }>();
  const meetingId = Number(params.id);
  const { showToast } = useToasts();
  const [search, setSearch] = useState('');
  const [currentTime, setCurrentTime] = useState(0);
  const [activeMatchIndex, setActiveMatchIndex] = useState(0);

  const { data: meeting, mutate: mutateMeeting } = useSWR(['meeting', meetingId], () => getMeeting(meetingId));
  const { data: transcript } = useSWR(['transcript', meetingId, search], () => getTranscript(meetingId, search));

  const matches = useMemo(() => transcript?.segments.flatMap((segment) => segment.match_ranges?.map((range) => ({ segment, range })) ?? []) ?? [], [transcript]);

  useEffect(() => {
    setActiveMatchIndex(0);
  }, [search]);

  useEffect(() => {
    const activeMatch = matches[activeMatchIndex];
    if (activeMatch) {
      setCurrentTime(activeMatch.segment.start_time);
    }
  }, [activeMatchIndex, matches]);

  async function handleGenerateSummary() {
    try {
      await generateSummary(meetingId);
      await mutateMeeting();
      showToast({ kind: 'success', title: 'Summary regenerated' });
    } catch (error) {
      showToast({ kind: 'error', title: 'Could not generate summary', description: error instanceof Error ? error.message : 'Unexpected error' });
    }
  }

  function handleExport() {
    try {
      const md = formatMeetingMarkdown(meeting ?? {}, activeTranscript ?? []);
      const safeTitle = (meeting?.title ?? `meeting-${meetingId}`).replace(/[^a-z0-9-_ ]/ig, '').replace(/\s+/g, '-').toLowerCase();
      downloadText(`${safeTitle}-${meetingId}.md`, md);
      showToast({ kind: 'success', title: 'Export started' });
    } catch (error) {
      showToast({ kind: 'error', title: 'Export failed', description: error instanceof Error ? error.message : 'Unexpected error' });
    }
  }

  async function handleToggleActionItem(item: ActionItem) {
    try {
      await updateActionItem(item.id, { is_completed: !item.is_completed });
      await mutateMeeting();
      showToast({ kind: 'success', title: 'Action item updated' });
    } catch (error) {
      showToast({ kind: 'error', title: 'Update failed', description: error instanceof Error ? error.message : 'Unexpected error' });
    }
  }

  async function handleDeleteActionItem(itemId: number) {
    try {
      await deleteActionItem(itemId);
      await mutateMeeting();
      showToast({ kind: 'success', title: 'Action item deleted' });
    } catch (error) {
      showToast({ kind: 'error', title: 'Delete failed', description: error instanceof Error ? error.message : 'Unexpected error' });
    }
  }

  const activeTranscript = transcript?.segments ?? meeting?.transcript_segments ?? [];

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-border bg-panel p-5 shadow-soft">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-muted">Meeting detail</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">{meeting?.title ?? 'Loading meeting...'}</h1>
            <p className="mt-2 text-sm text-muted">
              Interactive transcript, summary, and actions for a Fireflies-style post-meeting workflow.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={handleGenerateSummary} className="rounded-2xl bg-accent px-4 py-3 text-sm font-medium text-white shadow-soft">Generate summary</button>
            <button onClick={handleExport} className="inline-flex items-center gap-2 rounded-2xl border border-border px-4 py-3 text-sm font-medium text-text">
              <Download className="h-4 w-4" /> Export
            </button>
          </div>
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <MediaPlayer
            src={meeting?.audio_url}
            currentTime={currentTime}
            onTimeUpdate={setCurrentTime}
            onSeek={setCurrentTime}
          />

          <div className="rounded-[28px] border border-border bg-panel p-4 shadow-soft">
            <div className="flex items-center gap-3 rounded-2xl border border-border bg-panel-strong px-4 py-3">
              <Search className="h-4 w-4 text-muted" />
              <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search within transcript" className="w-full bg-transparent text-sm outline-none" />
            </div>
          </div>

          <TranscriptPanel
            segments={activeTranscript}
            currentTime={currentTime}
            searchQuery={search}
            activeMatchIndex={activeMatchIndex}
            onSeek={setCurrentTime}
            onSelectMatch={setActiveMatchIndex}
          />
        </div>

        <div className="space-y-6">
          <SummaryPanel summary={meeting?.summary} topics={meeting?.key_topics ?? []} actionItems={meeting?.action_items ?? []} />

          <section className="rounded-[28px] border border-border bg-panel p-4 shadow-soft">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div>
                <h3 className="text-lg font-semibold">Ask a question</h3>
                <p className="text-sm text-muted">Get a quick answer about this meeting (mock)</p>
              </div>
            </div>
            <AskBox meetingId={meetingId} />
          </section>

          <section className="rounded-[28px] border border-border bg-panel p-4 shadow-soft">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div>
                <h3 className="text-lg font-semibold">Action items</h3>
                <p className="text-sm text-muted">Inline completion, edit, and delete behavior.</p>
              </div>
            </div>
            <div className="mt-4 space-y-3">
              {meeting?.action_items?.length ? meeting.action_items.map((item) => (
                <ActionItemRow
                  key={item.id}
                  item={item}
                  onToggle={() => void handleToggleActionItem(item)}
                  onEdit={() => showToast({ kind: 'info', title: 'Edit action items', description: 'Inline action-item editing is a Phase 4 polish item.' })}
                  onDelete={() => void handleDeleteActionItem(item.id)}
                />
              )) : <p className="text-sm text-muted">No action items on this meeting.</p>}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
