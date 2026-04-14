# GitStream

> Paste a TikTok URL. Get the GitHub repo. Instantly.

GitStream uses AI to watch TikTok developer videos, extract the GitHub
repository being showcased, and surface live stats — stars, language,
topics — alongside the original video embed.

## How it works

1. **You paste a TikTok URL** into the search bar.
2. **Video Metadata Extraction**: `yt-dlp` fetches the title, transcript, and streaming URL.
3. **AI Vision (OCR)**: The system captures 3 frames from the video (at 20%, 50%, and 80%) using **FFmpeg** (with a Python **OpenCV** fallback).
4. **Multimodal Analysis**: **Google Gemini 1.5 Flash** analyzes the text (captions/description) *and* the visual frames to pinpoint the GitHub repository showcased in the video.
5. **Real-time Stats**: The GitHub REST API pulls live stars, forks, and language data.
6. **Tile-based UI**: The result is displayed in a modern, bento-style layout featuring a "Visual Evidence" gallery showing what the AI saw.

## Tech Stack

| Layer      | Technology                                              |
|------------|---------------------------------------------------------|
| Frontend   | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui         |
| Backend    | FastAPI (Python 3.11), deployed on Vercel               |
| AI         | Google Gemini 1.5 Flash (Multimodal: Text + Vision)     |
| Database   | Supabase (PostgreSQL + RLS)                             |
| Video meta | yt-dlp + FFmpeg/OpenCV (Frame extraction fallback)      |
| GitHub     | GitHub REST API v3                                      |

## Local Setup

### Prerequisites

- Node.js 18+ and pnpm
- Python 3.11+
- A Supabase project
- A Google AI Studio API key (Gemini 1.5 Flash)
- A GitHub fine-grained PAT (`read:repo` scope)

### 1. Clone and install

```bash
git clone https://github.com/yourname/gitstream.git
cd gitstream

# Backend dependencies
pip install -r requirements.txt

# System dependency (Optional but recommended for speed)
# On Windows: choco install ffmpeg
# On Mac: brew install ffmpeg

# Frontend dependencies
cd frontend && pnpm install
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in all four values
```

### 3. Bootstrap the database

Open the **Supabase SQL editor** in your project dashboard and run:
1. The full contents of `database/schema.sql`.
2. The RLS policies found in the `README` (if not already in schema.sql) to allow `anon` insert/update for the backend.

### 4. Run locally

```bash
# Terminal 1 — FastAPI (from repo root)
uvicorn api.index:app --reload --port 8000

# Terminal 2 — Next.js
cd frontend && pnpm dev
```

Open [http://localhost:3000](http://localhost:3000).

## Deploying to Vercel

```bash
vercel deploy
```

Set the four environment variables from `.env.example` in your Vercel project
settings under **Settings → Environment Variables**. The `vercel.json` file
routes all `/api/*` requests to the FastAPI serverless handler automatically.

## Project Structure

```
gitstream/
├── api/index.py              # FastAPI entry point (Vercel serverless)
├── backend/
│   ├── models.py             # Pydantic models
│   └── services/
│       ├── processor.py      # yt-dlp: TikTok metadata + captions
│       ├── analyzer.py       # Gemini 1.5 Flash: extract GitHub URL
│       └── github_api.py     # GitHub REST: stars, language, description
├── frontend/
│   ├── app/page.tsx          # Main page (state machine)
│   └── components/
│       ├── HeroInput.tsx     # URL input bar
│       ├── LoadingState.tsx  # Animated pipeline stages
│       └── RepoCard.tsx      # GitHub stats + TikTok embed
├── database/schema.sql       # Supabase table + indexes + RLS
├── vercel.json               # Routing config
└── .env.example              # Environment variable template
```

## License

MIT — see [LICENSE](./LICENSE).
