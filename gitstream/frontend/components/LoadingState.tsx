"use client";

import { useEffect, useState } from "react";

const STAGES = [
  { label: "Watching the video...",            duration: 3500 },
  { label: "Reading the caption & tags...",    duration: 2000 },
  { label: "Asking Gemini to find the repo...", duration: 3000 },
  { label: "Fetching GitHub stats...",          duration: 2000 },
];

export function LoadingState() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    let elapsed = 0;
    const timers = STAGES.map((stage, i) => {
      const timer = setTimeout(() => {
        setStageIndex(Math.min(i + 1, STAGES.length - 1));
      }, elapsed + stage.duration);
      elapsed += stage.duration;
      return timer;
    });
    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center gap-6 py-20 px-4">
      <div className="relative w-16 h-16">
        <div className="absolute inset-0 rounded-full bg-violet-500/20 animate-ping" />
        <div className="absolute inset-2 rounded-full bg-violet-500/40 animate-pulse" />
        <div className="absolute inset-4 rounded-full bg-violet-600" />
      </div>

      <p key={stageIndex} className="text-lg font-medium text-foreground">
        {STAGES[stageIndex].label}
      </p>

      <ol className="flex flex-col gap-2 text-sm text-muted-foreground w-full max-w-xs">
        {STAGES.map((stage, i) => (
          <li
            key={stage.label}
            className={`flex items-center gap-2 transition-opacity duration-500 ${
              i <= stageIndex ? "opacity-100" : "opacity-30"
            }`}
          >
            <span className={`w-2 h-2 rounded-full flex-shrink-0 transition-colors duration-300 ${
              i < stageIndex
                ? "bg-violet-500"
                : i === stageIndex
                ? "bg-violet-400 animate-pulse"
                : "bg-gray-300"
            }`} />
            {stage.label}
          </li>
        ))}
      </ol>
    </div>
  );
}
