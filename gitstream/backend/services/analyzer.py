
from __future__ import annotations

import os
import re
import textwrap

import google.generativeai as genai

from backend.models import VideoMetadata


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def _get_client() -> genai.GenerativeModel:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise AnalyzerError("GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=512,
        ),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_github_url(meta: VideoMetadata) -> str:
    """
    Given TikTok VideoMetadata, ask Gemini to identify the GitHub repo URL
    referenced in the video. Returns a clean https://github.com/owner/repo
    string, or raises AnalyzerError if none can be found.
    """
    prompt = _build_prompt(meta)
    model = _get_client()

    # Prepare multi-modal content: prompt string + Base64 image parts
    contents = [prompt]
    for frame_b64 in meta.frames:
        contents.append({"mime_type": "image/jpeg", "data": frame_b64})

    try:
        response = model.generate_content(contents)
        raw_text = response.text.strip()
    except Exception as exc:
        raise AnalyzerError(f"Gemini API call failed: {exc}") from exc

    return _parse_github_url(raw_text)


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

def _build_prompt(meta: VideoMetadata) -> str:
    transcript_section = (
        f"TRANSCRIPT:\n{meta.transcript[:3000]}"
        if meta.transcript
        else "TRANSCRIPT: (none available)"
    )

    return textwrap.dedent(f"""
        You are a precise data-extraction assistant. 
        I have provided text metadata and up to 3 screenshots from a TikTok video.

        TASK
        ----
        1. Look at the SCREENSHOTS provided. Check for:
           - GitHub URLs in the browser address bar.
           - Repository names in the page header (e.g., "owner / repo").
           - Code or terminal outputs that mention a library name.
        
        2. Read the TRANSCRIPT and METADATA:
           {transcript_section}
        
        3. Cross-reference: If the transcript mentions a tool and the image shows a matching GitHub page, extract that URL.

        Return ONLY the canonical URL in this exact format:
            https://github.com/owner/repo
        Do NOT include sub-paths like /blob/main/README.md -- strip to owner/repo.
        Do NOT include any explanation, punctuation, or extra text.

        If no GitHub repository can be identified with confidence, return exactly:
            NOT_FOUND

        Your response:
    """).strip()


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

_GITHUB_URL_PATTERN = re.compile(
    r"https://github\.com/[\w.\-]+/[\w.\-]+"
)

_SPOKEN_PATTERN = re.compile(
    r"github\s+dot\s+com\s+(?:slash\s+)?([\w.\-]+)\s+slash\s+([\w.\-]+)",
    re.IGNORECASE,
)


def _parse_github_url(raw: str) -> str:
    if "NOT_FOUND" in raw.upper():
        raise AnalyzerError(
            "Gemini could not identify a GitHub repository in this video."
        )

    match = _GITHUB_URL_PATTERN.search(raw)
    if match:
        url = match.group(0).rstrip(".,;)")
        return _normalise_github_url(url)

    spoken = _SPOKEN_PATTERN.search(raw)
    if spoken:
        owner, repo = spoken.group(1), spoken.group(2)
        return f"https://github.com/{owner}/{repo}"

    raise AnalyzerError(
        f"Could not parse a valid GitHub URL from Gemini response: {raw!r}"
    )


def _normalise_github_url(url: str) -> str:
    """Strip trailing slashes, .git suffix, and any sub-path after owner/repo."""
    url = url.rstrip("/").removesuffix(".git")
    parts = url.replace("https://github.com/", "").split("/")
    if len(parts) < 2:
        raise AnalyzerError(f"URL is missing owner or repo segment: {url!r}")
    return f"https://github.com/{parts[0]}/{parts[1]}"


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class AnalyzerError(RuntimeError):
    """Raised when Gemini fails or returns an unusable response."""
