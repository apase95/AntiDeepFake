# AntiDeepFake - Local Setup & Development Guide

This guide explains how the 3 engineers (and MoMo TechDay '26 judges reviewing the source code) can set up, run, and test AntiDeepFake locally.

---

## 1. Prerequisites
- **Python**: 3.11 or 3.12 (recommended for FastAPI, `aiohttp`, `asyncpg`, and `google-genai`)
- **Node.js**: 20+ and `npm` (for Next.js 14 Frontend)
- **System Tool**: `ffmpeg` installed and available in system PATH (used as pure subprocess; `moviepy` is not used)
- **Docker**: Docker Engine + Compose v2+ (optional for container testing)

Verify `ffmpeg` installation on Linux/macOS:
```bash
ffmpeg -version
```

---

## 2. Environment Configuration

1. Copy the template file (never commit your private `.env`):
   ```bash
   cp .env.example .env
   ```
2. Fill in the required credentials in `.env`:
   - `SIGHTENGINE_API_USER` and `SIGHTENGINE_API_SECRET`
   - `GOOGLE_API_KEY` (Google AI Studio key for `gemini-3.5-transcribe` via `google-genai` Interactions API)
   - `OPENROUTER_API_KEY` (OpenRouter key for `pplx-decider-flash-v1.3:free` on `/api/alpha/decisions`)
   - `DATABASE_URL` (Supabase Supavisor IPv4 Pooler URI on port `6543`) and `SUPABASE_URL` / `SUPABASE_SERVICE_KEY`
   - Optional: `HF_TOKEN` (Hugging Face fallback for deepfake vision)

---

## 3. Running Backend & Frontend Locally

### Backend (FastAPI)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start FastAPI dev server on port 8000
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Verify health check
curl http://127.0.0.1:8000/health
```

### Frontend (Next.js)
```bash
cd frontend
npm ci
# Ensure NEXT_PUBLIC_API_BASE_URL points directly to Backend (http://127.0.0.1:8000)
npm run dev
# Open http://127.0.0.1:3000
```

---

## 4. Testing Strategy (Offline First, Bounded Live Second)

### 4.1. Offline Unit & Contract Tests (Zero API Cost)
All automated tests mock Sightengine, Google `google-genai`, and OpenRouter HTTP responses. Run these freely during development:
```bash
# Run offline pipeline, SSE serialization, PII redaction, quote grounding, and rolling context checks
python -m unittest discover -s tests -p "test_*.py"
```

### 4.2. Bounded Live Provider Smoke Probe
To verify real API keys and Sightengine `models=deepfake` eligibility without burning monthly quota, run the bounded smoke test (sends max 1 image, 1 audio chunk, and 1 text state, and calls `files.delete()`):
```bash
python -m backend.smoke_test --live
```

---

## 5. Docker Production Simulation

Build and test the production container image locally (verifies non-root execution, `ffmpeg` binary, and under 512 MB RAM footprint):
```bash
docker build -t antideepfake-api -f Dockerfile .
docker run --rm -p 8000:8000 --env-file .env antideepfake-api
```
