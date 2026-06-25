"use client";

import { Search } from 'lucide-react';
import { useState } from 'react';
import useSWR from 'swr';
import { cn } from './cn';
import { searchWorkspace } from '@/lib/api';

export function GlobalSearchBar() {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const { data } = useSWR(query.trim().length > 1 ? ['global-search', query] : null, () => searchWorkspace(query));

  return (
    <div className="relative flex-1">
      <div className="flex items-center gap-2 rounded-2xl border border-border bg-panel-strong px-4 py-3">
        <Search className="h-4 w-4 text-muted" />
        <input
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          placeholder="Search meetings, speakers, and transcript text"
          className="w-full bg-transparent text-sm outline-none placeholder:text-muted"
        />
      </div>

      {open && query.trim().length > 1 ? (
        <div className="absolute left-0 top-[calc(100%+0.75rem)] z-40 w-full overflow-hidden rounded-2xl border border-border bg-panel shadow-soft">
          <div className="border-b border-border px-4 py-3 text-xs font-medium uppercase tracking-[0.2em] text-muted">
            Search Results
          </div>
          <div className="max-h-80 overflow-auto p-2">
            {data?.results?.length ? (
              data.results.slice(0, 5).map((result) => (
                <div key={result.meeting_id} className="rounded-xl px-3 py-2 transition hover:bg-panel-strong">
                  <p className="text-sm font-medium">{result.title}</p>
                  <p className="mt-1 text-xs text-muted line-clamp-2">{result.snippet}</p>
                </div>
              ))
            ) : (
              <div className="px-3 py-6 text-sm text-muted">No matches yet.</div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
