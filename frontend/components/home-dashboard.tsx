"use client";

import useSWR from 'swr';
import Link from 'next/link';
import { CalendarRange, Filter, Plus, Search } from 'lucide-react';
import { useMemo, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { getMeetings, getTags } from '@/lib/api';
import type { MeetingListItem } from '@/lib/types';
import { cn } from './cn';
import type { Tag } from '@/lib/types';

function formatMeetingDate(value: string) {
  return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
}

function formatDuration(seconds: number) {
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${minutes}m ${String(remainder).padStart(2, '0')}s`;
}

export function HomeDashboard() {
  const [search, setSearch] = useState('');
  const [participant, setParticipant] = useState('');
  const [tags, setTags] = useState<Tag[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [sort, setSort] = useState('recency');
  const router = useRouter();

  const queryString = useMemo(() => {
    const query = new URLSearchParams();
    if (search.trim()) query.set('search', search.trim());
    if (participant.trim()) query.set('participant', participant.trim());
    if (selectedTags.length) selectedTags.forEach((t) => query.append('tags', t));
    if (sort) query.set('sort', sort);
    return query.toString();
  }, [search, participant, sort, selectedTags]);

  const { data, error, isLoading } = useSWR(['meetings', queryString], () => getMeetings(new URLSearchParams(queryString)));
  const { data: tagsData } = useSWR('tags', () => getTags());

  // update local tags when fetched
  useEffect(() => {
    if (tagsData) setTags(tagsData);
  }, [tagsData]);

  // hydrate selectedTags from URL on load
  useEffect(() => {
    try {
      const sp = new URLSearchParams(window.location.search);
      const initial = sp.getAll('tags');
      if (initial.length) setSelectedTags(initial);
    } catch (e) {
      // ignore (server rendering safety)
    }
  }, []);

  // reflect current filters in the URL (shareable)
  useEffect(() => {
    try {
      const url = queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
      router.replace(url);
    } catch (e) {
      // ignore
    }
  }, [queryString, router]);
  const meetings = data ?? [];

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-border bg-panel p-5 shadow-soft">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div className="max-w-2xl">
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-muted">Meetings library</p>
            <h2 className="mt-2 text-3xl font-semibold tracking-tight">Your recent meetings, summaries, and next steps</h2>
            <p className="mt-2 text-sm text-muted">
              A Fireflies-style workspace with searchable transcripts, meeting summaries, and task follow-up.
            </p>
          </div>
          <Link
            href="/meetings/new"
            className="inline-flex items-center gap-2 rounded-2xl bg-accent px-4 py-3 text-sm font-medium text-white shadow-soft transition hover:opacity-95"
          >
            <Plus className="h-4 w-4" />
            New meeting
          </Link>
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[1.1fr_0.8fr_0.4fr]">
        <label className="flex items-center gap-3 rounded-2xl border border-border bg-panel px-4 py-3 shadow-sm">
          <Search className="h-4 w-4 text-muted" />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by title or transcript" className="w-full bg-transparent text-sm outline-none" />
        </label>
        <label className="flex items-center gap-3 rounded-2xl border border-border bg-panel px-4 py-3 shadow-sm">
          <Filter className="h-4 w-4 text-muted" />
          <input value={participant} onChange={(event) => setParticipant(event.target.value)} placeholder="Filter by participant" className="w-full bg-transparent text-sm outline-none" />
        </label>
        <label className="flex items-center gap-3 rounded-2xl border border-border bg-panel px-4 py-3 shadow-sm">
          <CalendarRange className="h-4 w-4 text-muted" />
          <select value={sort} onChange={(event) => setSort(event.target.value)} className="w-full bg-transparent text-sm outline-none">
            <option value="recency">Sort by recency</option>
            <option value="oldest">Sort by oldest</option>
            <option value="title">Sort by title</option>
          </select>
        </label>
      </section>

      <section className="flex flex-wrap gap-2">
        {tags.map((tag) => {
          const active = selectedTags.includes(tag.name);
          return (
            <button
              key={tag.id}
              onClick={() => setSelectedTags((prev) => (prev.includes(tag.name) ? prev.filter((t) => t !== tag.name) : [...prev, tag.name]))}
              className={cn(
                'rounded-full px-3 py-1 text-sm font-medium border',
                active ? 'bg-accent text-white border-accent' : 'bg-panel border-border text-muted',
              )}
            >
              #{tag.name}
            </button>
          );
        })}
      </section>

      <div className="rounded-[28px] border border-border bg-panel p-3 shadow-soft">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {isLoading ? <div className="p-4 text-sm text-muted">Loading meetings...</div> : null}
          {error ? <div className="p-4 text-sm text-rose-600">Unable to load meetings.</div> : null}
          {meetings.map((meeting) => (
            <MeetingCard key={meeting.id} meeting={meeting} />
          ))}
          {!isLoading && meetings.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border bg-panel-strong p-8 text-sm text-muted">
              No meetings match the current filters.
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function MeetingCard({ meeting }: { meeting: MeetingListItem }) {
  return (
    <Link href={`/meetings/${meeting.id}`} className={cn('group rounded-2xl border border-border bg-panel-strong p-4 transition hover:-translate-y-0.5 hover:shadow-soft')}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold leading-6">{meeting.title}</p>
          <p className="mt-1 text-xs text-muted">{formatMeetingDate(meeting.date)} • {formatDuration(meeting.duration_seconds)}</p>
        </div>
        <span className="rounded-full bg-accent-soft px-3 py-1 text-xs font-medium text-accent">{meeting.status}</span>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {meeting.tags.slice(0, 3).map((tag) => (
          <span key={tag.id} className="rounded-full border border-border bg-panel px-2.5 py-1 text-[11px] font-medium text-muted">
            #{tag.name}
          </span>
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between text-xs text-muted">
        <div className="flex -space-x-2">
          {meeting.participants.slice(0, 4).map((participant) => (
            <div key={participant.id} className="flex h-8 w-8 items-center justify-center rounded-full border border-panel bg-accent-soft text-[11px] font-semibold text-accent">
              {participant.name
                .split(' ')
                .map((part) => part[0])
                .join('')
                .slice(0, 2)}
            </div>
          ))}
        </div>
        <span>{meeting.participants.length} participants</span>
      </div>
    </Link>
  );
}
