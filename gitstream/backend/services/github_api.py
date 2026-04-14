"""
github_api.py
-------------
Fetches repository metadata from the GitHub REST API v3.
"""

from __future__ import annotations

import os
import re
from typing import Optional

import httpx

from backend.models import Repository


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_GITHUB_API_BASE = "https://api.github.com"
_TIMEOUT = 10


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_repo_data(
    github_url: str,
    tiktok_url: str,
    tiktok_author: str,
) -> Repository:
    """
    Given a GitHub repo URL, fetch stars, forks, description, language,
    topics, and homepage from the GitHub REST API.

    Raises
    ------
    GitHubAPIError  -- on HTTP errors or unexpected response shapes.
    ValueError      -- if github_url cannot be parsed into owner/repo.
    """
    owner, repo_name = _parse_owner_repo(github_url)
    raw = _call_github_api(f"/repos/{owner}/{repo_name}")
    ai_summary = _build_ai_summary(raw)

    return Repository(
        tiktok_url=tiktok_url,
        tiktok_author=tiktok_author,
        github_url=github_url,
        repo_full_name=raw.get("full_name", f"{owner}/{repo_name}"),
        repo_name=raw.get("name", repo_name),
        owner=raw.get("owner", {}).get("login", owner),
        star_count=raw.get("stargazers_count", 0),
        fork_count=raw.get("forks_count", 0),
        description=raw.get("description"),
        primary_language=raw.get("language"),
        topics=raw.get("topics", []),
        homepage=raw.get("homepage") or None,
        ai_summary=ai_summary,
    )


# ---------------------------------------------------------------------------
# GitHub REST helpers
# ---------------------------------------------------------------------------

def _call_github_api(path: str) -> dict:
    """
    Make an authenticated GET request to the GitHub REST API.
    Uses GITHUB_TOKEN if available (5,000 req/hr vs 60 unauthenticated).
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{_GITHUB_API_BASE}{path}"

    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            response = client.get(url, headers=headers)
    except httpx.TimeoutException as exc:
        raise GitHubAPIError(f"GitHub API timed out for {path}") from exc
    except httpx.RequestError as exc:
        raise GitHubAPIError(f"GitHub API request failed: {exc}") from exc

    if response.status_code == 404:
        raise GitHubAPIError(
            f"Repository not found on GitHub (404): {path}"
        )
    if response.status_code == 403:
        raise GitHubAPIError(
            "GitHub API rate limit exceeded. Set GITHUB_TOKEN to increase quota."
        )
    if not response.is_success:
        raise GitHubAPIError(
            f"GitHub API returned {response.status_code} for {path}: "
            f"{response.text[:200]}"
        )

    return response.json()


# ---------------------------------------------------------------------------
# URL parsing
# ---------------------------------------------------------------------------

_GITHUB_REPO_RE = re.compile(
    r"https?://github\.com/([\w.\-]+)/([\w.\-]+)"
)


def _parse_owner_repo(github_url: str) -> tuple[str, str]:
    match = _GITHUB_REPO_RE.match(github_url)
    if not match:
        raise ValueError(f"Cannot parse owner/repo from URL: {github_url!r}")
    return match.group(1), match.group(2).removesuffix(".git")


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------

def _build_ai_summary(raw: dict) -> str:
    parts: list[str] = []

    name = raw.get("full_name", "")
    if name:
        parts.append(name)

    desc = raw.get("description", "")
    if desc:
        parts.append(desc)

    lang = raw.get("language")
    stars = raw.get("stargazers_count", 0)
    forks = raw.get("forks_count", 0)

    stats = []
    if lang:
        stats.append(f"Written in {lang}")
    if stars:
        stats.append(f"{stars:,} stars")
    if forks:
        stats.append(f"{forks:,} forks")

    if stats:
        parts.append(" · ".join(stats))

    topics = raw.get("topics", [])
    if topics:
        parts.append("Topics: " + ", ".join(topics[:8]))

    return " | ".join(parts)


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class GitHubAPIError(RuntimeError):
    """Raised on GitHub REST API failures."""
