# AntiDeepFake - Technical Architecture Specification

> **Status Note**: Updated Production-Ready MVP Architecture. Performance targets are benchmarks to measure during Sprint 2/3, not guaranteed SLAs.

## 1. Production Architecture Overview (Draw.io Blueprint)

The system applies a 4-tier Serverless architecture optimized for Free Tier constraints (Vercel 4.5 MB proxy limit, Render 512 MB RAM, Sightengine 1 req/s, and Supabase IPv4 networking):
1. **Frontend Tier (Cloudflare + Vercel Hobby)**: Global CDN, warm-up ping on load (`GET /health`), video streaming from Supabase, and live SSE 5-second timeline.
2. **Backend Compute Tier (Render Docker - 512 MB RAM)**: Non-root FastAPI + `uvicorn` using pure `ffmpeg` subprocesses (zero `moviepy` RAM bloat), SSE streaming (`text/event-stream`), rolling context, PII masking, and quote grounding.
3. **Data & Storage Tier (Supabase)**: PostgreSQL via **IPv4 Supavisor Pooler (port 6543)** or `supabase-py` HTTPS, plus `sample-videos` storage bucket.
4. **External Serverless AI Tier**: Sightengine (`1 keyframe/5s` + `Semaphore(1)` + optional Hugging Face fallback) + Google `gemini-3.5-transcribe` (Interactions API + `files.delete()` cleanup) + OpenRouter `pplx-decider-flash-v1.3:free` (`POST /api/alpha/decisions`).

```text
+---------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                               CLOUD ARCHITECTURE OVERVIEW                                                         |
+---------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                                                                                                   |
|  [User / Judge Browser] --(1. Load UI & Stream Demo MP4)--> [Frontend Tier: Cloudflare + Vercel]                                                  |
|  [User / Judge Browser] --(2. Direct CORS Upload <=15MB)--> [Backend Tier: Render Docker (Bypass Vercel 4.5MB limit)]                             |
|  [User / Judge Browser] <-(5. SSE Event Stream / 5s)------- [Backend Tier: FastAPI StreamingResponse]                                             |
|                                                                          |                                                                        |
|  +-------------------------------------+   +------------------------------------------------------+   +----------------------------------------+  |
|  |           FRONTEND TIER             |   |               BACKEND COMPUTE TIER                   |   |         DATA & STORAGE TIER            |  |
|  |       (Cloudflare + Vercel)         |   |            (Render Free Tier 512MB RAM)              |   |              (Supabase)                |  |
|  +-------------------------------------+   +------------------------------------------------------+   +----------------------------------------+  |
|  | - Cloudflare (DNS + SSL + CDN)      |   | - FastAPI + Uvicorn (Port 8000, Non-root user)       |   | - Supabase Storage:                    |  |
|  | - Vercel Edge (Next.js 14 App):     |   | - Pure ffmpeg Subprocess (No moviepy RAM overhead)   |   |   Bucket: sample-videos (3 demo MP4s)  |  |
|  |   * Warm-up GET /health on mount    |   | - Progressive 5s SSE Pipeline:                       |   | - Supabase PostgreSQL (IPv4 Pooler):   |  |
|  |   * Video Player (from Supabase)    |   |   * Slice 5s .mp3 & 1 sharp keyframe (.jpg)          |   |   * Library: asyncpg / supabase-py     |  |
|  |   * Live SSE 5s Risk Timeline       |   |   * Rolling Context (prev 5s + curr 5s transcript)   |   |   * Port: 6543 (Avoid IPv6 port 5432)  |  |
|  |   * Red/Yellow Alert Badges         |   |   * PII Redaction & Quote Grounding Verifier         |   |   * Tables: test_cases, analysis_logs  |  |
|  +-------------------------------------+   +---------------------------+--------------------------+   +----------------------------------------+  |
|                                                                        |                                                  ^                       |
|                                                               (3. Parallel AI Inference)                        (4. Fetch Cache / Save Meta)      |
|                                                                        |                                                  |                       |
|                                                                        v                                                  |                       |
|                                            +------------------------------------------------------+                       |                       |
|                                            |             EXTERNAL SERVERLESS AI TIER              |                       |                       |
|                                            +------------------------------------------------------+                       |                       |
|                                            | - Sightengine CV: 1 frame/5s + Semaphore(1) 1.1s     | ----------------------+                       |
|                                            |   (Optional Fallback: HuggingFace SigLIP2)           |                                               |
|                                            | - Gemini 3.5 Transcribe: Interactions + Files API    |                                               |
|                                            |   (Explicit files.delete() in finally block)         |                                               |
|                                            | - OpenRouter Decider: POST /api/alpha/decisions      |                                               |
|                                            +------------------------------------------------------+                                               |
+---------------------------------------------------------------------------------------------------------------------------------------------------+
```

---

## 2. Component Stack & Production Guardrails

| Tier | Component | Service / Model | Implementation Guardrails |
|---|---|---|---|
| **Frontend** | Web Hosting | Vercel (Hobby Tier) | Direct CORS requests to Render for uploads > 4.5 MB; fires `GET /health` warm-up ping on mount to wake Render container. |
| **Backend** | Video Slicer | Pure `ffmpeg` Subprocess | Invoked via `asyncio.create_subprocess_exec` (`~20MB` RAM); `moviepy` is explicitly excluded to prevent Render 512MB OOM crashes. |
| **Backend** | Orchestrator | FastAPI (`StreamingResponse`) | Emits SSE `window` events sequentially every ~1.2s; 10s HTTP timeout per provider. |
| **Storage** | Video Storage | Supabase Storage | Public bucket `sample-videos` hosting 3 official MP4 demo clips with zero egress charges. |
| **Database**| Database | Supabase PostgreSQL | Connected via **IPv4 Supavisor Pooler (port `6543`)** with `asyncpg` or **`supabase-py` HTTPS** (avoids Render IPv6 unreachable errors). |
| **AI (CV)** | Deepfake CV | Sightengine (`models=deepfake`) | Sends **1 sharp keyframe per 5s window** throttled via `asyncio.Semaphore(1)` (`1.1s` spacing) to respect Free Tier `1 req/s` cap; optional HF `SigLIP2` fallback. |
| **AI (STT)**| Speech-to-Text | `gemini-3.5-transcribe` | Uses `google-genai` SDK (`v1beta`) `files.upload()` + `interactions.create()`; strictly calls `files.delete()` in `finally` (`R08`). |
| **AI (Logic)**| Decision Model | `pplx-decider-flash-v1.3:free` | Uses OpenRouter Decisions API (`POST /api/alpha/decisions`) with `"questions"` dict and `"answers"` calibrated probabilities. |

---

## 3. OpenRouter Decisions API Contract (`/api/alpha/decisions`)

Unlike standard chat completions, `perplexity/pplx-decider-flash-v1.3:free` operates on OpenRouter's structured Decisions endpoint (`https://openrouter.ai/api/alpha/decisions`):

```json
{
  "model": "perplexity/pplx-decider-flash-v1.3:free",
  "state": {
    "previous_transcript": "Alo mẹ à, con đang có việc gấp ở ngoài đường.",
    "current_transcript": "Chuyển ngay giúp em [REDACTED_NUM] triệu, đừng gọi cho mẹ.",
    "cv_status": "evaluated",
    "cv_score": 0.88
  },
  "questions": {
    "risk_verdict": {
      "type": "choice",
      "instructions": "Evaluate scam risk using current speech, previous context, and deepfake visual score.",
      "criteria": {
        "normal": "Normal casual conversation with no money requests, threats, or verification blocking",
        "visual_alert_only": "Face-swap visual tampering flagged while speech content remains benign",
        "verbal_pressure_only": "Urgent money demand, OTP request, or discouraging verification, even if visual is normal",
        "confirmed_scam": "Explicit scam combining coercive transfer demand and anti-verification, or combined visual+verbal risk"
      }
    }
  }
}
```

- **Parsed Output Path**: `response["answers"]["risk_verdict"]["choice"]` and `response["answers"]["risk_verdict"]["probabilities"][verdict]`.

---

## 4. Trust Boundaries, Rolling Context & Ephemeral Cleanup

1. **Direct Upload & Server-Side Secrets**:
   - Browser sends `POST /api/v1/analyze` directly to Render HTTPS using CORS (`APP_ORIGIN` allowlist), keeping all provider keys strictly server-side.
2. **Rolling Context & PII Masking (`R01`, `R05`)**:
   - Before calling OpenRouter, PII regex replaces numbers (`\b\d{9,16}\b`, phone/OTP sequences) with `[REDACTED_NUM]`.
   - `previous_transcript` (already redacted) is included alongside `current_transcript` in `state` so scams split across a 5-second boundary are detected.
3. **Quote Grounding (`R06`)**:
   - Extracted `trigger_quote` phrases are validated via normalized substring matching against `current_transcript` (or `previous_transcript`) before rendering on the UI.
4. **Dual Ephemeral Cleanup (`R08`)**:
   - Local temp slice directory (`/tmp/adf_<uuid>/`) and uploaded audio files on Google Files API (`client.files.delete()`) are both deleted inside `finally` blocks immediately after processing each window/request.
   - `analysis_logs` stores only anonymized metadata.

---

## 5. Performance Targets to Measure (Not SLAs)

- **Target Per-Window Latency**: `p50` under `1.5 seconds`, `p95` under `3.0 seconds` per 5-second window (reflecting sequential `1.1s` Sightengine free-tier rate guard and Files API upload/delete round-trip).
- **Measurements Required in Sprint 2/3**: Log actual latencies for `ffmpeg`, Sightengine, Gemini Interactions API, and OpenRouter Decisions API during Gate 2 and Gate 3 validation.
