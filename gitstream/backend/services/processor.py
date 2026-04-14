"""
processor.py
------------
Fetches TikTok video metadata and transcript/caption data using yt-dlp
in --dump-json mode. No video bytes are written to disk — only JSON
metadata and subtitle text, keeping us well within Vercel's 500 MB limit.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from backend.models import VideoMetadata


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fetch_video_metadata(tiktok_url: str) -> VideoMetadata:
    """
    Given a TikTok URL, return structured metadata including the caption
    text, description, and any auto-generated subtitles (transcript).

    Strategy
    --------
    1.  Run `yt-dlp --dump-json` to get the full JSON info dict without
        touching the video stream.
    2.  Optionally run a second pass with `--write-auto-subs --skip-download`
        into a temp directory to capture the VTT/SRT transcript, then read
        and delete that file immediately. The total I/O never approaches
        the Vercel 500 MB limit.

    Raises
    ------
    ProcessorError   -- on yt-dlp failure or unexpected output.
    ValueError       -- if the URL is not a recognisable TikTok URL.
    """
    _validate_tiktok_url(tiktok_url)

    raw_info = _dump_json(tiktok_url)
    transcript = _fetch_transcript(tiktok_url)

    return _build_metadata(raw_info, transcript)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_TIKTOK_PATTERN = re.compile(
    r"https?://(www\.|vm\.|vt\.)?tiktok\.com/", re.IGNORECASE
)


def _validate_tiktok_url(url: str) -> None:
    if not _TIKTOK_PATTERN.match(url):
        raise ValueError(
            f"URL does not appear to be a TikTok link: {url!r}"
        )


# ---------------------------------------------------------------------------
# yt-dlp helpers
# ---------------------------------------------------------------------------

import sys

_YTDLP_BASE_ARGS: list[str] = [
    sys.executable, "-m", "yt_dlp",
    "--no-warnings",
    "--quiet",
    "--add-header", "User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36",
    "--no-playlist",
]

_YTDLP_TIMEOUT_SECONDS = 30


def _run_ytdlp(args: list[str]) -> subprocess.CompletedProcess:
    """Thin wrapper that enforces a hard timeout and captures output."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=_YTDLP_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise ProcessorError(
            f"yt-dlp timed out after {_YTDLP_TIMEOUT_SECONDS}s"
        ) from exc
    except FileNotFoundError as exc:
        raise ProcessorError(
            "yt-dlp is not installed or not on PATH"
        ) from exc

    return result


def _dump_json(url: str) -> dict[str, Any]:
    """
    Run `yt-dlp --dump-json <url>` and parse the resulting JSON blob.
    --dump-json prints the info dict to stdout and exits without
    downloading any media.
    """
    args = [*_YTDLP_BASE_ARGS, "--dump-json", url]
    result = _run_ytdlp(args)

    if result.returncode != 0:
        raise ProcessorError(
            f"yt-dlp --dump-json failed (exit {result.returncode}): "
            f"{result.stderr.strip()}"
        )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ProcessorError(
            f"yt-dlp returned invalid JSON: {exc}"
        ) from exc


def _fetch_transcript(url: str) -> str:
    """
    Attempt to download auto-generated subtitles into a NamedTemporaryFile
    directory, read the resulting .vtt file, strip the WebVTT markup, and
    return clean plain text. Returns an empty string if no subtitles exist.

    The temp directory is removed immediately after reading — zero persistent
    disk usage on Vercel's ephemeral filesystem.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        subtitle_path_template = str(Path(tmpdir) / "subtitle")

        args = [
            *_YTDLP_BASE_ARGS,
            "--skip-download",
            "--write-auto-subs",
            "--sub-langs", "en",
            "--sub-format", "vtt",
            "--output", subtitle_path_template,
            url,
        ]

        _run_ytdlp(args)

        vtt_files = list(Path(tmpdir).glob("*.vtt"))

        if not vtt_files:
            return ""

        raw_vtt = vtt_files[0].read_text(encoding="utf-8", errors="replace")
        return _strip_vtt_markup(raw_vtt)


# ---------------------------------------------------------------------------
# VTT -> plain text
# ---------------------------------------------------------------------------

_VTT_TIMESTAMP = re.compile(
    r"\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}"
)
_VTT_TAG = re.compile(r"<[^>]+>")


def _strip_vtt_markup(vtt: str) -> str:
    """
    Convert raw WebVTT content to clean, deduplicated plain text.

    VTT files from TikTok typically repeat many cue blocks for the same
    phrase. We dedup consecutive identical lines so Gemini gets a concise
    transcript.
    """
    lines: list[str] = []
    for line in vtt.splitlines():
        line = line.strip()
        if line in ("", "WEBVTT") or line.isdigit():
            continue
        if _VTT_TIMESTAMP.match(line):
            continue
        line = _VTT_TAG.sub("", line).strip()
        if not line:
            continue
        if lines and lines[-1] == line:
            continue
        lines.append(line)

    return " ".join(lines)


# ---------------------------------------------------------------------------
# Model construction
# ---------------------------------------------------------------------------

def _build_metadata(info: dict[str, Any], transcript: str) -> VideoMetadata:
    return VideoMetadata(
        video_id=info.get("id", ""),
        title=info.get("title") or info.get("description", "")[:200],
        description=info.get("description", ""),
        uploader=info.get("uploader", ""),
        uploader_handle=info.get("uploader_id", ""),
        duration_seconds=int(info.get("duration") or 0),
        view_count=info.get("view_count"),
        like_count=info.get("like_count"),
        canonical_url=info.get("webpage_url", ""),
        thumbnail_url=info.get("thumbnail", ""),
        tags=info.get("tags") or [],
        transcript=transcript,
    )


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class ProcessorError(RuntimeError):
    """Raised when yt-dlp fails or returns unexpected output."""
