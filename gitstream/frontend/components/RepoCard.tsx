"use client";

import type { Repository } from "@/lib/types";

export function RepoCard({ repo, tiktokUrl }: { repo: Repository; tiktokUrl: string }) {
  const tiktokVideoId = tiktokUrl.match(/video\/(\d+)/)?.[1];
  const embedUrl = tiktokVideoId ? `https://www.tiktok.com/embed/v2/${tiktokVideoId}` : null;

  return (
    <div className="max-w-7xl mx-auto p-6 grid grid-cols-12 gap-4">
      {/* Tile 1: Repository Hero */}
      <div className="col-span-12 md:col-span-8 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-8 flex flex-col justify-between min-h-[300px]">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <span className="px-2 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-[10px] font-mono text-zinc-500">
              {repo.primary_language || "Detecting..."}
            </span>
          </div>
          <h2 className="text-3xl font-semibold tracking-tight mb-2">{repo.repo_name}</h2>
          <p className="text-zinc-500 dark:text-zinc-400 max-w-lg leading-relaxed">
            {repo.description || "No description provided by the author."}
          </p>
        </div>
        <div className="flex items-center gap-6 mt-8">
          <div className="flex flex-col">
            <span className="text-2xl font-medium">{repo.star_count.toLocaleString()}</span>
            <span className="text-[10px] uppercase text-zinc-400">Stars</span>
          </div>
          <div className="flex flex-col">
            <span className="text-2xl font-medium">{repo.fork_count.toLocaleString()}</span>
            <span className="text-[10px] uppercase text-zinc-400">Forks</span>
          </div>
          <a href={repo.github_url} target="_blank" className="ml-auto bg-zinc-900 dark:bg-zinc-100 text-white dark:text-zinc-900 px-5 py-2 rounded-lg text-sm transition-all hover:ring-4 hover:ring-zinc-500/10">
            Open Repository
          </a>
        </div>
      </div>

      {/* Tile 2: TikTok Embed (Vertical Tile) */}
      <div className="col-span-12 md:col-span-4 row-span-2 bg-black rounded-2xl overflow-hidden border border-zinc-200 dark:border-zinc-800 shadow-sm">
        {embedUrl && (
          <iframe src={embedUrl} className="w-full h-full aspect-[9/16]" allowFullScreen />
        )}
      </div>

      {/* Tile 3: AI Visual Evidence (The "Frames") */}
      <div className="col-span-12 md:col-span-8 bg-zinc-50 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6">
        <h3 className="text-xs font-mono text-zinc-400 mb-4 uppercase tracking-widest">Visual Evidence (OCR)</h3>
        <div className="grid grid-cols-3 gap-3">
          {repo.frames?.map((frame, idx) => (
            <div key={idx} className="aspect-video rounded-lg overflow-hidden border border-zinc-200 dark:border-zinc-800 grayscale hover:grayscale-0 transition-all cursor-crosshair">
              <img src={`data:image/jpeg;base64,${frame}`} className="w-full h-full object-cover" alt="AI Context" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}