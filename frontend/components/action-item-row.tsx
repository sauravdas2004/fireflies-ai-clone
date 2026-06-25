"use client";

import { Check, Pencil, Trash2 } from 'lucide-react';
import type { ActionItem } from '@/lib/types';
import { cn } from './cn';

export function ActionItemRow({
  item,
  onToggle,
  onEdit,
  onDelete,
}: {
  item: ActionItem;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <div className={cn('flex items-start justify-between gap-3 rounded-2xl border px-4 py-3', item.is_completed ? 'border-emerald-200 bg-emerald-50/70' : 'border-border bg-panel-strong')}>
      <button type="button" onClick={onToggle} className="mt-0.5 inline-flex h-7 w-7 items-center justify-center rounded-full border border-border bg-panel text-muted transition hover:bg-accent hover:text-white" aria-label="Toggle completion">
        <Check className="h-4 w-4" />
      </button>
      <div className="min-w-0 flex-1">
        <p className={cn('text-sm font-medium', item.is_completed && 'line-through text-muted')}>{item.text}</p>
        <p className="mt-1 text-xs text-muted">{item.assignee ?? 'Unassigned'} {item.due_date ? `• Due ${item.due_date}` : ''}</p>
      </div>
      <div className="flex gap-1">
        <button type="button" onClick={onEdit} className="rounded-full p-2 text-muted transition hover:bg-panel hover:text-text" aria-label="Edit action item">
          <Pencil className="h-4 w-4" />
        </button>
        <button type="button" onClick={onDelete} className="rounded-full p-2 text-muted transition hover:bg-panel hover:text-text" aria-label="Delete action item">
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
