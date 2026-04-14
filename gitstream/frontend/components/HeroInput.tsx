"use client";

import { useState } from "react";

export function HeroInput({ onSubmit, isLoading }: { onSubmit: (url: string) => void; isLoading: boolean }) {
  const [url, setUrl] = useState("");

  return (
    <section className="flex flex-col items-center justify-center min-h-[50vh] px-4 gap-8">
      <div className="space-y-2">
        <h1 className="text-4xl font-medium tracking-tight text-zinc-900 dark:text-zinc-100">
          Source the Stream
        </h1>
        <p className="text-zinc-500 text-sm max-w-sm mx-auto">
          Turn TikTok tutorials into actionable GitHub repositories.
        </p>
      </div>

      <form
        onSubmit={(e) => { e.preventDefault(); onSubmit(url); }}
        className="w-full max-w-2xl relative group"
      >
        <div className="absolute inset-0 bg-zinc-200 dark:bg-zinc-800 rounded-2xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity" />
        <div className="relative flex items-center bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-2 shadow-2xl">
          <input
            type="url"
            placeholder="Paste TikTok URL..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 bg-transparent border-none px-4 py-3 text-sm focus:ring-0 outline-none"
          />
          <button
            type="submit"
            disabled={isLoading || !url}
            className="bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 px-6 py-2.5 rounded-lg text-sm font-medium hover:scale-[0.98] transition-transform disabled:opacity-50"
          >
            Stream
          </button>
        </div>
      </form>
    </section>
  );
}