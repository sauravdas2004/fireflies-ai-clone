"use client";

import { CheckSquare2, ListChecks, Sparkles } from 'lucide-react';
import type { ActionItem, KeyTopic, Summary } from '@/lib/types';
import { cn } from './cn';

export function SummaryPanel({ summary, topics, actionItems }: { summary?: Summary | null; topics: KeyTopic[]; actionItems: ActionItem[] }) {
  return (
    <div className="rounded-[28px] border border-border bg-panel p-4 shadow-soft">
      <div className="flex items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h3 className="text-lg font-semibold">AI summary</h3>
          <p className="text-sm text-muted">Overview, key topics, and action items in a Fireflies-style panel.</p>
        </div>
        <Sparkles className="h-5 w-5 text-accent" />
      </div>

      <div className="mt-4 space-y-4">
        <div className="rounded-2xl bg-panel-strong p-4">
          <p className="text-xs font-medium uppercase tracking-[0.24em] text-muted">Overview</p>
          <p className="mt-3 text-sm leading-6 text-text">{summary?.overview_text ?? 'No summary is available yet.'}</p>
        </div>

        <section className="rounded-2xl border border-border bg-panel-strong p-4">
          <div className="flex items-center gap-2">
            <ListChecks className="h-4 w-4 text-accent" />
            <h4 className="text-sm font-semibold">Key topics</h4>
          </div>
          <ul className="mt-3 space-y-2">
            {topics.length ? topics.map((topic) => (
              <li key={topic.id} className="rounded-xl border border-border bg-panel px-3 py-2 text-sm text-text">
                {topic.topic_text}
              </li>
            )) : <li className="text-sm text-muted">No topics yet.</li>}
          </ul>
        </section>

        <section className="rounded-2xl border border-border bg-panel-strong p-4">
          <div className="flex items-center gap-2">
            <CheckSquare2 className="h-4 w-4 text-accent" />
            <h4 className="text-sm font-semibold">Action items</h4>
          </div>
          <div className="mt-3 space-y-2">
            {actionItems.length ? actionItems.map((item) => (
              <div key={item.id} className={cn('rounded-xl border px-3 py-3 text-sm', item.is_completed ? 'border-emerald-200 bg-emerald-50/70' : 'border-border bg-panel')}>
                <p className={cn('font-medium', item.is_completed && 'line-through text-muted')}>{item.text}</p>
                <div className="mt-1 flex items-center justify-between text-xs text-muted">
                  <span>{item.assignee ?? 'Unassigned'}</span>
                  <span>{item.due_date ? `Due ${item.due_date}` : 'No due date'}</span>
                </div>
              </div>
            )) : <p className="text-sm text-muted">No action items yet.</p>}
          </div>
        </section>
      </div>
    </div>
  );
}
