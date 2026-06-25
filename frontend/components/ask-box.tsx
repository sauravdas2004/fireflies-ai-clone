"use client";

import { useState } from 'react';
import { askQuestion } from '@/lib/api';
import { useToasts } from '@/components/toast-provider';

export function AskBox({ meetingId }: { meetingId: number | null }) {
  const { showToast } = useToasts();
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);

  async function handleAsk() {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await askQuestion(meetingId, question.trim());
      setAnswer(res.answer);
      showToast({ kind: 'success', title: 'Answer ready' });
    } catch (err) {
      showToast({ kind: 'error', title: 'Ask failed', description: err instanceof Error ? err.message : String(err) });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mt-4 space-y-3">
      <textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask something about this meeting..." className="w-full rounded-lg border border-border bg-panel-strong p-3 text-sm" rows={3} />
      <div className="flex items-center gap-2">
        <button onClick={handleAsk} disabled={loading} className="rounded-2xl bg-accent px-4 py-2 text-sm font-medium text-white shadow-soft">
          {loading ? 'Thinking...' : 'Ask'}
        </button>
        <button onClick={() => { setQuestion(''); setAnswer(null); }} className="rounded-2xl border border-border px-4 py-2 text-sm">Clear</button>
      </div>

      {answer ? (
        <div className="mt-3 rounded-lg border border-border bg-panel-strong p-3 text-sm">
          <div className="font-medium">Answer</div>
          <div className="mt-2 whitespace-pre-wrap">{answer}</div>
        </div>
      ) : null}
    </div>
  );
}

export default AskBox;
