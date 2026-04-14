

from __future__ import annotations

import base64
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional

from backend.models import VideoMetadata



def fetch_video_metadata(tiktok_url: str) -> VideoMetadata:
    
    _validate_tiktok_url(tiktok_url)

    raw_info = _dump_json(tiktok_url)
    transcript = _fetch_transcript(tiktok_url)
    frames = _extract_frames(raw_info.get("url"), raw_info.get("duration", 0))

    print(f"DEBUG: Found {len(frames)} frames. Transcript found: {bool(transcript)}")
    return _build_metadata(raw_info, transcript, frames)




_TIKTOK_PATTERN = re.compile(
    r"https?://(www\.|vm\.|vt\.)?tiktok\.com/", re.IGNORECASE
)


def _validate_tiktok_url(url: str) -> None:
    if not _TIKTOK_PATTERN.match(url):
        raise ValueError(
            f"URL does not appear to be a TikTok link: {url!r}"
        )




import sys

_YTDLP_BASE_ARGS: list[str] = [
    sys.executable, "-m", "yt_dlp",
    "--no-warnings",
    "--quiet",
    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "--no-playlist",
]

_YTDLP_TIMEOUT_SECONDS = 30


def _run_ytdlp(args: list[str]) -> subprocess.CompletedProcess:
    
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




_VTT_TIMESTAMP = re.compile(
    r"\d{2}:\d{2}:\d{2}\.\d{3}\s+-->\s+\d{2}:\d{2}:\d{2}\.\d{3}"
)
_VTT_TAG = re.compile(r"<[^>]+>")


def _strip_vtt_markup(vtt: str) -> str:
    
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



def _build_metadata(info: dict[str, Any], transcript: str, frames: list[str]) -> VideoMetadata:
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
        frames=frames,
    )


def _extract_frames(stream_url: Optional[str], duration: int) -> list[str]:
    
    if not stream_url or duration < 2:
        return []

    print(f"Extracting frames from: {stream_url[:50]}...")

    frame_data = []
   
    timestamps = [duration * 0.2, duration * 0.5, duration * 0.8]

    with tempfile.TemporaryDirectory() as tmpdir:
        
        for i, ts in enumerate(timestamps):
            out_path = Path(tmpdir) / f"frame_{i}.jpg"
            cmd = [
                "ffmpeg", "-ss", str(ts),
                "-reconnect", "1", "-reconnect_streamed", "1", "-reconnect_delay_max", "5",
                "-i", stream_url,
                "-frames:v", "1", "-q:v", "2", str(out_path),
                "-y", "-hide_banner", "-loglevel", "error"
            ]
            try:
                subprocess.run(cmd, capture_output=True, timeout=10)
            except Exception:
                pass

            if out_path.exists():
                with open(out_path, "rb") as f:
                    frame_data.append(base64.b64encode(f.read()).decode("utf-8"))

        
        if not frame_data:
            try:
                import cv2
                cap = cv2.VideoCapture(stream_url)
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS) or 30
                    for i, ts in enumerate(timestamps):
                        cap.set(cv2.CAP_PROP_POS_MSEC, ts * 1000)
                        success, frame = cap.read()
                        if success:
                            out_path = Path(tmpdir) / f"cv_frame_{i}.jpg"
                            cv2.imwrite(str(out_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                            if out_path.exists():
                                with open(out_path, "rb") as f:
                                    frame_data.append(base64.b64encode(f.read()).decode("utf-8"))
                    cap.release()
            except ImportError:
                pass
            except Exception:
                pass

    return frame_data




class ProcessorError(RuntimeError):
    """Raised when yt-dlp fails or returns unexpected output."""
