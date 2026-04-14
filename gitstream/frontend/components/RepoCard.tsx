"use client";

import type { Repository } from "@/lib/types";

interface RepoCardProps {
  repo: Repository;
  tiktokUrl: string;
}

export function RepoCard({ repo, tiktokUrl }: RepoCardProps) {
  const tiktokVideoId = tiktokUrl.match(/video\/(\d+)/)?.[1];
  const embedUrl = tiktokVideoId
    ? `https://www.tiktok.com/embed/v2/${tiktokVideoId}`
    : null;

  return (
    <div className="w-full max-w-5xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Left: GitHub repo card */}
      <div className="rounded-xl border border-border bg-background shadow-sm p-6 flex flex-col gap-4">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-xs text-muted-foreground mb-1">{repo.owner}</p>
            <h2 className="text-xl font-semibold leading-tight">{repo.repo_name}</h2>
          </div>
          <a
            href={repo.github_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-md border border-border hover:bg-muted transition-colors flex-shrink-0"
          >
            View on GitHub
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
            </svg>
          </a>
        </div>

        {repo.description && (
          <p className="text-sm text-muted-foreground leading-relaxed">{repo.description}</p>
        )}

        {/* Stats row */}
        <div className="flex items-center gap-4 text-sm flex-wrap">
          <span className="flex items-center gap-1.5 font-medium">
            <svg className="w-4 h-4 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
            {repo.star_count.toLocaleString()}
          </span>
          <span className="flex items-center gap-1.5 text-muted-foreground">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/>
            </svg>
            {repo.fork_count.toLocaleString()}
          </span>
          {repo.primary_language && (
            <span className="flex items-center gap-1.5 text-muted-foreground">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
              </svg>
              {repo.primary_language}
            </span>
          )}
          {repo.homepage && (
            <a href={repo.homepage} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
              </svg>
              Site
            </a>
          )}
        </div>

        {/* Topics */}
        {repo.topics.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {repo.topics.slice(0, 8).map((topic) => (
              <span key={topic} className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                {topic}
              </span>
            ))}
          </div>
        )}

        {/* AI Summary */}
        {repo.ai_summary && (
          <div className="rounded-lg bg-violet-50 dark:bg-violet-950/30 border border-violet-200 dark:border-violet-800 p-3">
            <p className="text-xs font-medium text-violet-700 dark:text-violet-400 mb-1">AI Summary</p>
            <p className="text-sm text-violet-900 dark:text-violet-200 leading-relaxed">{repo.ai_summary}</p>
          </div>
        )}
      </div>

      {/* Right: TikTok embed */}
      <div className="flex flex-col gap-3">
        <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">Source video</p>
        {embedUrl ? (
          <div className="rounded-xl overflow-hidden border border-border shadow-sm" style={{ aspectRatio: "9/16", maxHeight: "600px" }}>
            <iframe
              src={embedUrl}
              className="w-full h-full"
              allowFullScreen
              allow="encrypted-media"
              title="TikTok video"
            />
          </div>
        ) : (
          <div className="rounded-xl border border-dashed border-border flex items-center justify-center text-muted-foreground text-sm p-8" style={{ aspectRatio: "9/16", maxHeight: "600px" }}>
            Embed unavailable —{" "}
            <a href={tiktokUrl} target="_blank" rel="noopener noreferrer" className="ml-1 underline hover:text-foreground transition-colors">
              watch on TikTok
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
