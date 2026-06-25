"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { CalendarDays, ChevronRight, Grid2x2, Settings, Sparkles } from 'lucide-react';
import { useEffect, useState } from 'react';
import { cn } from '@/components/cn';
import { GlobalSearchBar } from '@/components/global-search-bar';
import { useThemeMode } from '@/components/theme-mode';

const navItems = [
  { href: '/', label: 'Notes', icon: Sparkles },
  { href: '#', label: 'Calendar', icon: CalendarDays },
  { href: '#', label: 'Apps', icon: Grid2x2 },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function AppChrome({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);
  const { theme, toggleTheme } = useThemeMode();

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="min-h-screen bg-workspace-radial">
      <div className="mx-auto flex min-h-screen max-w-[1600px] gap-6 px-4 py-4 lg:px-6">
        <aside className="hidden w-72 shrink-0 rounded-[28px] border border-border bg-panel/90 p-4 shadow-soft backdrop-blur xl:flex xl:flex-col">
          <div className="flex items-center gap-3 rounded-2xl border border-border bg-panel-strong px-4 py-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-accent text-white shadow-soft">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <p className="text-sm font-semibold tracking-tight">Fireflies</p>
              <p className="text-xs text-muted">Meeting workspace</p>
            </div>
          </div>

          <nav className="mt-6 space-y-1">
            {navItems.map((item) => {
              const active = item.href !== '#' && pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.label}
                  href={item.href}
                  className={cn(
                    'flex items-center justify-between rounded-2xl px-4 py-3 text-sm transition',
                    active ? 'bg-accent text-white shadow-soft' : 'text-muted hover:bg-panel-strong hover:text-text'
                  )}
                >
                  <span className="flex items-center gap-3">
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </span>
                  <ChevronRight className="h-4 w-4 opacity-50" />
                </Link>
              );
            })}
          </nav>

          <div className="mt-6 rounded-2xl border border-dashed border-border bg-panel-strong p-4">
            <p className="text-sm font-medium">Coming Soon</p>
            <p className="mt-1 text-xs leading-5 text-muted">
              Live call bot, integrations, and team collaboration are intentionally left as placeholders.
            </p>
          </div>

          <div className="mt-auto pt-6">
            <button
              type="button"
              onClick={toggleTheme}
              className="w-full rounded-2xl border border-border bg-panel-strong px-4 py-3 text-left text-sm transition hover:bg-accent-soft"
            >
              {mounted ? `Theme: ${theme}` : 'Theme: system'}
            </button>
          </div>
        </aside>

        <main className="flex min-h-screen min-w-0 flex-1 flex-col gap-4">
          <header className="rounded-[28px] border border-border bg-panel/90 px-4 py-4 shadow-soft backdrop-blur">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs font-medium uppercase tracking-[0.24em] text-muted">Fireflies workspace</p>
                <h1 className="mt-1 text-2xl font-semibold tracking-tight">Notes, transcripts, and action items</h1>
              </div>

              <div className="flex flex-col gap-3 lg:min-w-[560px] lg:flex-row lg:items-center">
                <GlobalSearchBar />
                <div className="flex items-center gap-3 rounded-2xl border border-border bg-panel-strong px-3 py-2">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent text-sm font-semibold text-white">
                    AC
                  </div>
                  <div>
                    <p className="text-sm font-medium">Alex Morgan</p>
                    <p className="text-xs text-muted">Default user</p>
                  </div>
                </div>
              </div>
            </div>
          </header>

          <div className="flex-1 rounded-[32px] border border-border bg-panel/90 p-4 shadow-soft backdrop-blur lg:p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
