# AntiDeepFake - Role-Based Tasklist

This tasklist maps concrete tasks across the 3 roles, aligned with `docs/specs/spec-api-contract.md` (v1.1 SSE) and `docs/validation/validation-plan.md`.

---

## 1. Summary of Roles

```text
+-----------------------+----------------------------------+----------------------------------+
|      AI ENGINEER      |   BACKEND ENGINEER 1 (PIPELINE)  |   BACKEND ENGINEER 2 (PLATFORM)  |
+-----------------------+----------------------------------+----------------------------------+
| - Sightengine + Sem(1)| - Pure ffmpeg slicing (no moviepy| - FastAPI SSE & Direct CORS      |
| - google-genai STT    | - Rolling context + PII masking  | - Supabase IPv4 Pooler & Storage |
| - OpenRouter Decisions| - Quote grounding & temp cleanup | - Pre-computed cache layer       |
| - 3 Demo video clips  | - Offline T01-T12 mocked tests   | - Non-root Docker & Warm-up ping |
+-----------------------+----------------------------------+----------------------------------+
```

---

## 2. AI Engineer Tasklist

| Task ID | Task Description | Sprint | Priority | Deliverable / Acceptance Criteria | Status |
|---|---|---|---|---|---|
| **AI-101** | Connect Sightengine API + Rate Limiter + HF Fallback | Sprint 1 | P0 | Async connector sending 1 sharp frame/5s guarded by `Semaphore(1)` (`1.1s` delay), returning `cv_score` (`[0.0, 1.0]`) or `insufficient_visual_data`, plus optional HF `SigLIP2` fallback | To Do |
| **AI-102** | Connect `gemini-3.5-transcribe` (`google-genai`) | Sprint 1 | P0 | Async wrapper using `files.upload()` + `interactions.create()` (`v1beta`), strictly calling `files.delete()` inside `finally` (`R08`) | To Do |
| **AI-103** | Integrate OpenRouter Decisions API | Sprint 1 | P0 | Connector calling `POST https://openrouter.ai/api/alpha/decisions` with `questions` dict (`choice` type) and isolating untrusted speech (`R07`) | To Do |
| **AI-104** | Prepare 3 Official Demo Video Clips | Sprint 1 | P0 | 3 MP4 clips: Case 1 (Face-swap scam), Case 2 (Genuine scam), Case 3 (Low-quality network safe) | To Do |
| **AI-105** | Bounded `--live` Smoke Probe (`backend/smoke_test.py`) | Sprint 1 | P0 | CLI probe testing max 1 image, 1 audio, 1 state; confirms Sightengine `models=deepfake` free-tier access and Google `files.delete()` cleanup | To Do |
| **AI-106** | Tune Thresholds & Rolling Context Accuracy | Sprint 2 | P1 | Calibrate `CV_DEEPFAKE_THRESHOLD` (0.60) and `VERBAL_PRESSURE_THRESHOLD` (0.70); pass T01–T04 and T11 | To Do |
| **AI-107** | Measure Actual Latency & Record Demo Script | Sprint 3 | P0 | Document real `p50`/`p95` latencies per provider and draft 3-minute demo voiceover script | To Do |

---

## 3. Backend Engineer 1 Tasklist (Pipeline & Video Processing Lead)

| Task ID | Task Description | Sprint | Priority | Deliverable / Acceptance Criteria | Status |
|---|---|---|---|---|---|
| **BE1-201** | Implement Pure `ffmpeg` 5s Slicer + Cleanup | Sprint 1 | P0 | Subprocess `ffmpeg` (`asyncio.create_subprocess_exec`, zero `moviepy`) slicing 5s `.mp3` + 1 `.jpg` in `/tmp/adf_<uuid>/`, cleaned in `finally` (`R08`) | To Do |
| **BE1-202** | Implement PII Redaction Filter (`R05`) | Sprint 1 | P0 | Regex redaction replacing phone numbers, bank accounts, CCCD, and OTPs with `[REDACTED_NUM]` before Decider call | To Do |
| **BE1-203** | Implement Rolling Context & Quote Grounding (`R01`, `R06`) | Sprint 1 | P0 | Combine redacted `previous_transcript + current_transcript` for Decider state; verify `trigger_quote` substring match (`T07`, `T11`) | To Do |
| **BE1-204** | Build Async Streaming Generator Pipeline | Sprint 1 | P0 | Async generator yielding `WindowEvaluation` objects sequentially per 5s window while running CV and STT concurrently per chunk | To Do |
| **BE1-205** | Timeout, Rate-Limit & Fallback Handling | Sprint 2 | P1 | 10s HTTP timeout caps, bounded retries, returning `evaluation_incomplete` / `provider_error` safely (`T10`) | To Do |
| **BE1-206** | Offline Mocked Unit Test Suite (Gate 1) | Sprint 2 | P0 | Complete `unittest` suite covering `T01`–`T12` mocked scenarios (including `files.delete()` mock assertion) at zero cost | To Do |
| **BE1-207** | Render 512MB RAM & Latency Profiling | Sprint 3 | P1 | Profile container memory under concurrent 15 MB uploads to verify RAM stays comfortably below 400 MB | To Do |

---

## 4. Backend Engineer 2 Tasklist (Platform, Storage & Deployment Lead)

| Task ID | Task Description | Sprint | Priority | Deliverable / Acceptance Criteria | Status |
|---|---|---|---|---|---|
| **BE2-301** | Initialize Supabase DB (IPv4 Pooler `6543`) | Sprint 1 | P0 | Run DDL (`test_cases`, `analysis_logs`); configure `asyncpg` via Supavisor IPv4 pooler (port `6543`) or `supabase-py` HTTPS | To Do |
| **BE2-302** | Configure Supabase Storage Bucket | Sprint 1 | P0 | Public `sample-videos` bucket hosting 3 test MP4 clips with verified range-request streaming & CORS | To Do |
| **BE2-303** | Build FastAPI Server & Pre-Stream Validators | Sprint 1 | P0 | Setup `/health`, `/ready`, explicit CORS (`APP_ORIGIN`), and uniform JSON error responses (`400`, `413` > 15MB, `422` > 30s, `429`, `503`) | To Do |
| **BE2-304** | Implement SSE `/analyze` & Demo Endpoints | Sprint 2 | P0 | Implement `POST /api/v1/analyze` (`StreamingResponse` `text/event-stream` emitting `window` + `summary` events), `GET /api/v1/cases`, `GET /api/v1/logs` | To Do |
| **BE2-305** | Populate Pre-computed Demo Cache | Sprint 2 | P0 | Pre-compute analysis JSON for the 3 official MP4s and store in `test_cases` for 0ms demo speed | To Do |
| **BE2-306** | Non-root `Dockerfile` & Render Deployment | Sprint 2 | P0 | Build slim `Dockerfile` (`python:3.11-slim` + `ffmpeg`, no `moviepy`, non-root user), deploy to Render HTTPS | To Do |
| **BE2-307** | Frontend Vercel Direct-CORS & SSE UI | Sprint 2 | P1 | Wire Video Player + SSE EventSource/Fetch stream consumer + `GET /health` warm-up ping on mount; bypass Vercel 4.5MB limit completely | To Do |
| **BE2-308** | Final Contest Packaging & `README.md` | Sprint 3 | P0 | Generate clean `.zip` code archive, complete `README.md` declaring all AI tools/libs, submit by Dec 03 | To Do |
