"""
api/index.py
------------
FastAPI application entry point. Vercel auto-detects this file and
serves it as a serverless function for all routes under /api/*.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

from backend.models import AnalyzeRequest, AnalyzeResponse, Repository
from backend.services.processor import fetch_video_metadata, ProcessorError
from backend.services.analyzer import extract_github_url, AnalyzerError
from backend.services.github_api import fetch_repo_data, GitHubAPIError


# ---------------------------------------------------------------------------
# Supabase client (lazy-initialised at startup)
# ---------------------------------------------------------------------------

_supabase: Client | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _supabase
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_ANON_KEY", "")
    if url and key:
        _supabase = create_client(url, key)
    yield


app = FastAPI(
    title="GitStream API",
    description="Convert TikTok URLs into structured GitHub repo data.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production to your Vercel domain
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(body: AnalyzeRequest) -> AnalyzeResponse:
    """
    Full pipeline: TikTok URL -> metadata -> Gemini -> GitHub stats -> DB write.
    """
    try:
        # 1. Fetch TikTok metadata & transcript (no video download)
        video_meta = fetch_video_metadata(body.tiktok_url)

        # 2. Ask Gemini to find the GitHub URL in the caption/transcript
        github_url = extract_github_url(video_meta)

        # 3. Pull repo stats from GitHub REST API
        repo: Repository = fetch_repo_data(
            github_url=github_url,
            tiktok_url=body.tiktok_url,
            tiktok_author=video_meta.uploader,
        )

        # 4. Persist to Supabase (upsert so re-analysis refreshes the record)
        if _supabase:
            _supabase.table("discovered_repos").upsert(
                {
                    "tiktok_url": repo.tiktok_url,
                    "github_url": repo.github_url,
                    "repo_name": repo.repo_full_name,
                    "star_count": repo.star_count,
                    "ai_summary": repo.ai_summary,
                    "author_name": repo.tiktok_author,
                },
                on_conflict="tiktok_url",
            ).execute()

        return AnalyzeResponse(success=True, repository=repo)

    except ValueError as exc:
        print(f"DEBUG ValueError: {exc}")
        raise HTTPException(status_code=422, detail=str(exc))
    except ProcessorError as exc:
        raise HTTPException(status_code=502, detail=f"Video fetch failed: {exc}")
    except AnalyzerError as exc:
        print(f"DEBUG AnalyzerError: {exc}")
        raise HTTPException(status_code=422, detail=f"AI analysis failed: {exc}")
    except GitHubAPIError as exc:
        raise HTTPException(status_code=502, detail=f"GitHub API failed: {exc}")
