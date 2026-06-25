"use client";

import { Play, Pause, Volume2 } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

export function MediaPlayer({
  src,
  currentTime,
  onTimeUpdate,
  onSeek,
}: {
  src?: string | null;
  currentTime: number;
  onTimeUpdate: (time: number) => void;
  onSeek: (time: number) => void;
}) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [playing, setPlaying] = useState(false);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    audio.currentTime = currentTime;
  }, [currentTime]);

  const togglePlayback = async () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) {
      await audio.play();
      setPlaying(true);
    } else {
      audio.pause();
      setPlaying(false);
    }
  };

  return (
    <div className="rounded-[28px] border border-border bg-panel p-4 shadow-soft">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold">Meeting playback</h3>
          <p className="text-sm text-muted">Placeholder audio player styled like the Fireflies control bar.</p>
        </div>
        <button type="button" onClick={togglePlayback} className="inline-flex items-center gap-2 rounded-2xl bg-accent px-4 py-3 text-sm font-medium text-white shadow-soft">
          {playing ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
          {playing ? 'Pause' : 'Play'}
        </button>
      </div>

      <div className="mt-5 rounded-2xl border border-border bg-panel-strong p-4">
        <audio
          ref={audioRef}
          src={src ?? undefined}
          onTimeUpdate={(event) => onTimeUpdate(event.currentTarget.currentTime)}
          onLoadedMetadata={(event) => setDuration(event.currentTarget.duration || 0)}
          onEnded={() => setPlaying(false)}
        />
        <input
          type="range"
          min={0}
          max={duration || 1}
          value={currentTime}
          onChange={(event) => onSeek(Number(event.target.value))}
          className="h-2 w-full cursor-pointer appearance-none rounded-full bg-border accent-[rgb(var(--color-accent))]"
        />
        <div className="mt-3 flex items-center justify-between text-xs text-muted">
          <span>{formatTimestamp(currentTime)}</span>
          <span className="inline-flex items-center gap-1"><Volume2 className="h-3.5 w-3.5" /> Placeholder media</span>
          <span>{formatTimestamp(duration)}</span>
        </div>
      </div>
    </div>
  );
}

function formatTimestamp(seconds: number) {
  const totalSeconds = Math.max(0, Math.floor(seconds));
  const minutes = Math.floor(totalSeconds / 60);
  const remaining = totalSeconds % 60;
  return `${minutes}:${String(remaining).padStart(2, '0')}`;
}
