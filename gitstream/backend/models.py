"""
models.py
---------
Pydantic v2 models shared across all backend services.
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, field_validator


class VideoMetadata(BaseModel):
    """Raw data extracted from a TikTok video by processor.py."""

    video_id: str
    title: str
    description: str
    uploader: str
    uploader_handle: str
    duration_seconds: int
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    canonical_url: str
    thumbnail_url: str
    tags: list[str] = []
    transcript: str = ""
    frames: list[str] = []


class Repository(BaseModel):
    """A GitHub repository discovered from a TikTok video."""

    tiktok_url: str
    tiktok_author: str
    github_url: str
    repo_full_name: str
    repo_name: str
    owner: str
    star_count: int = 0
    fork_count: int = 0
    description: Optional[str] = None
    primary_language: Optional[str] = None
    topics: list[str] = []
    homepage: Optional[str] = None
    ai_summary: str = ""
    frames: list[str] = []

    @field_validator("github_url")
    @classmethod
    def normalise_github_url(cls, v: str) -> str:
        v = v.rstrip("/")
        if not v.startswith("https://github.com/"):
            raise ValueError(f"Not a valid GitHub URL: {v!r}")
        return v


class AnalyzeRequest(BaseModel):
    tiktok_url: str


class AnalyzeResponse(BaseModel):
    success: bool
    repository: Optional[Repository] = None
    error: Optional[str] = None
