"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useSWR from 'swr';
import { createMeeting, getTags, createTag } from '@/lib/api';
import { useToasts } from '@/components/toast-provider';
import type { Tag } from '@/lib/types';

export default function NewMeetingPage() {
  const router = useRouter();
  const { showToast } = useToasts();
  const [loading, setLoading] = useState(false);
  const [tags, setTags] = useState<Tag[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState('');

  const { data: tagsData } = useSWR('tags', () => getTags());
  // populate local tags once when data arrives
  useEffect(() => {
    if (tagsData) setTags(tagsData);
  }, [tagsData]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    // ensure tags_json reflects selectedTags
    formData.set('tags_json', JSON.stringify(selectedTags));
    setLoading(true);
    try {
      const meeting = await createMeeting(formData);
      showToast({ kind: 'success', title: 'Meeting created', description: meeting.title });
      router.push(`/meetings/${meeting.id}`);
    } catch (error) {
      showToast({ kind: 'error', title: 'Could not create meeting', description: error instanceof Error ? error.message : 'Unexpected error' });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-muted">Create meeting</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">Upload or paste a transcript</h1>
        <p className="mt-2 text-sm text-muted">TXT, VTT, or JSON transcript files can be ingested into the meeting workspace.</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 rounded-[28px] border border-border bg-panel p-6 shadow-soft">
        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Title" name="title" placeholder="Client kickoff with Atlas" required />
          <Field label="Meeting date" name="date_value" type="datetime-local" required />
          <Field label="Duration (seconds)" name="duration_seconds" type="number" placeholder="1800" />
          <Field label="Audio URL" name="audio_url" placeholder="https://example.com/audio.mp3" />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Participants JSON" name="participants_json" textarea placeholder='[{"name":"Alex Morgan","email":"alex@example.com","role":"Host"}]' />
          <div className="space-y-2 text-sm font-medium">
            <span>Tags</span>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => {
                const active = selectedTags.includes(tag.name);
                return (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => setSelectedTags((prev) => (prev.includes(tag.name) ? prev.filter((t) => t !== tag.name) : [...prev, tag.name]))}
                    className={`rounded-full px-3 py-1 text-sm font-medium border ${active ? 'bg-accent text-white border-accent' : 'bg-panel border-border text-muted'}`}
                  >
                    #{tag.name}
                  </button>
                );
              })}
            </div>
            <div className="mt-2 flex gap-2">
              <input value={newTag} onChange={(e) => setNewTag(e.target.value)} placeholder="Create tag (e.g. client-call)" className="w-full rounded-2xl border border-border bg-panel-strong px-4 py-3 text-sm outline-none" />
              <button
                type="button"
                onClick={async () => {
                  const name = newTag.trim().toLowerCase();
                  if (!name) return;
                  try {
                    const created = await createTag(name);
                    setTags((prev) => (prev.find((t) => t.name === created.name) ? prev : [...prev, created]));
                    setSelectedTags((prev) => (prev.includes(created.name) ? prev : [...prev, created.name]));
                    setNewTag('');
                  } catch (err) {
                    // ignore for now
                  }
                }}
                className="rounded-2xl bg-accent px-4 py-3 text-sm font-medium text-white"
              >
                Add
              </button>
            </div>
          </div>
        </div>

        <Field label="Paste transcript" name="transcript_text" textarea placeholder="Alex Morgan: Welcome everyone..." />

        <div>
          <label className="text-sm font-medium">Or upload transcript</label>
          <input name="transcript_file" type="file" accept=".txt,.vtt,.json" className="mt-2 block w-full rounded-2xl border border-border bg-panel-strong px-4 py-3 text-sm" />
        </div>

        <button type="submit" disabled={loading} className="rounded-2xl bg-accent px-5 py-3 text-sm font-medium text-white shadow-soft transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60">
          {loading ? 'Creating...' : 'Create meeting'}
        </button>
      </form>
    </div>
  );
}

function Field({ label, textarea, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string; textarea?: boolean }) {
  return (
    <label className="space-y-2 text-sm font-medium">
      <span>{label}</span>
      {textarea ? (
        <textarea
          {...(props as React.TextareaHTMLAttributes<HTMLTextAreaElement>)}
          className="min-h-28 w-full rounded-2xl border border-border bg-panel-strong px-4 py-3 text-sm outline-none placeholder:text-muted"
        />
      ) : (
        <input
          {...props}
          className="w-full rounded-2xl border border-border bg-panel-strong px-4 py-3 text-sm outline-none placeholder:text-muted"
        />
      )}
    </label>
  );
}
