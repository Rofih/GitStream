"use client";

import { useState } from "react";

interface HeroInputProps {
  onSubmit: (url: string) => void;
  isLoading: boolean;
}

export function HeroInput({ onSubmit, isLoading }: HeroInputProps) {
  const [url, setUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) return;
    onSubmit(trimmed);
  };

  return (
    <section className="flex flex-col items-center justify-center min-h-[60vh] px-4 text-center gap-6">
      <div className="flex items-center gap-1 mb-2">
        <span className="text-5xl font-bold tracking-tight">Git</span>
        <span className="text-5xl font-bold tracking-tight text-violet-500">Stream</span>
      </div>

      <p className="text-muted-foreground text-lg max-w-md leading-relaxed">
        Paste a TikTok URL. Our AI watches the video and surfaces the GitHub
        repo being showcased — with live stats.
      </p>

      <form onSubmit={handleSubmit} className="flex w-full max-w-xl gap-2 mt-2">
        <div className="relative flex-1">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            type="url"
            placeholder="https://www.tiktok.com/@user/video/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
            className="w-full pl-9 pr-4 h-12 text-sm rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent disabled:opacity-50"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !url.trim()}
          className="h-12 px-5 rounded-lg bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Analyze
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6"/>
          </svg>
        </button>
      </form>

      <p className="text-xs text-muted-foreground">
        Works with TikTok videos that mention or link to a GitHub repository
      </p>
    </section>
  );
}
