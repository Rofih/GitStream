"use client";

import { useState } from "react";
import { HeroInput } from "@/components/HeroInput";
import { LoadingState } from "@/components/LoadingState";
import { RepoCard } from "@/components/RepoCard";
import type { Repository } from "@/lib/types";

type AppState =
  | { phase: "idle" }
  | { phase: "loading"; url: string }
  | { phase: "result"; url: string; repo: Repository }
  | { phase: "error"; message: string };

export default function Home() {
  const [state, setState] = useState<AppState>({ phase: "idle" });

  const handleSubmit = async (url: string) => {
    setState({ phase: "loading", url });
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tiktok_url: url }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.detail ?? data.error ?? "Analysis failed.");
      }
      setState({ phase: "result", url, repo: data.repository });
    } catch (err) {
      setState({
        phase: "error",
        message: err instanceof Error ? err.message : "Something went wrong.",
      });
    }
  };

  const handleReset = () => setState({ phase: "idle" });

  return (
    <main className="min-h-screen bg-background text-foreground">
      {state.phase === "idle" && (
        <HeroInput onSubmit={handleSubmit} isLoading={false} />
      )}
      {state.phase === "loading" && <LoadingState />}
      {state.phase === "result" && (
        <>
          <RepoCard repo={state.repo} tiktokUrl={state.url} />
          <div className="flex justify-center pb-12">
            <button onClick={handleReset} className="text-sm text-muted-foreground hover:text-foreground underline transition-colors">
              &larr; Analyze another video
            </button>
          </div>
        </>
      )}
      {state.phase === "error" && (
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4 px-4">
          <p className="text-destructive font-medium text-center max-w-md">{state.message}</p>
          <button onClick={handleReset} className="text-sm text-muted-foreground hover:text-foreground underline transition-colors">
            &larr; Try again
          </button>
        </div>
      )}
    </main>
  );
}
