# AntiDeepFake - Sprint Planning (Agile/Scrum)

## 1. Team Overview & Agile Setup
- **Team Size**: 3 Engineers
  - **1 AI Engineer**: Owns prompt/criteria design, Sightengine (`1 frame/5s` + Semaphore + optional HF fallback), Google `gemini-3.5-transcribe` (`google-genai` Interactions + `files.delete()`), OpenRouter `POST /api/alpha/decisions` integration, and 3 official demo clips.
  - **Backend Engineer 1 (Pipeline Lead)**: Owns pure `ffmpeg` 5-second slicing subprocess (zero `moviepy`), async orchestration (`aiohttp`), rolling context (`prev + curr`), PII masking, quote grounding, and dual ephemeral cleanup.
  - **Backend Engineer 2 (Platform & Integration Lead)**: Owns FastAPI SSE streaming routes (`spec-api-contract.md`), Supabase (IPv4 Pooler port `6543` / `supabase-py` + Storage), pre-computed cache, non-root Docker, Render + Vercel direct-CORS integration, and warm-up ping.
- **Target Milestone**: MoMo TechDay '26 Preliminary Submission Deadline (**December 03, 2026**).
- **Reference Baseline**: Governed by `docs/specs/spec-api-contract.md` and `docs/validation/validation-plan.md`.

---

## 2. Sprint Roadmap & Exit Gates

| Sprint | Timeline | Primary Focus | Required Exit Gate |
|---|---|---|---|
| **Sprint 1** | Nov 25 - Nov 28 | Core Pipeline, Guardrails & API Setup | **Gate 1 + Gate 2**: Offline mocked tests pass 100%; Bounded `--live` probe passes across Sightengine, `google-genai`, and `/api/alpha/decisions` |
| **Sprint 2** | Nov 29 - Dec 01 | SSE Streaming, Pre-Cache & Cloud Deploy | **Gate 3 (Partial)**: Direct CORS Render + Vercel URLs live; 3 pre-cached cases stream at 0ms; live MP4 upload emits 5s SSE events |
| **Sprint 3** | Dec 02 - Dec 03 | Stress Testing, Video Demo & Final Submission | **Gate 3 (Full)**: 12-case Validation Matrix passes (`T01`–`T12`); 3-min video MP4, 10-page PDF slide, and 1-page A4 guide submitted |

---

## 3. Detailed Sprint Breakdown

### Sprint 1: Core Pipeline, Guardrails & AI Connectors (Nov 25 - Nov 28)
- **Sprint Goal**: Build and verify pure `ffmpeg` 5-second slicing, compliant AI connectors, rolling context, PII masking, quote grounding, and Supabase IPv4 tables.
- **Key Deliverables**:
  - Pure `ffmpeg` subprocess module (`asyncio.create_subprocess_exec`) outputting 5-second `.mp3` audio and 1 sharp `.jpg` keyframe in `/tmp/adf_<uuid>/` with automatic `finally` cleanup.
  - Connectors for Sightengine (`1 frame/5s` + `Semaphore(1)` `1.1s` spacing), Google `gemini-3.5-transcribe` (`files.upload` + `interactions.create` + `files.delete()`), and OpenRouter `POST /api/alpha/decisions` (`questions` dict).
  - Rolling context builder (`prev + curr` transcript) + PII regex masking (`[REDACTED_NUM]`) + Quote Grounding verifier (`R05`, `R06`).
  - Supabase PostgreSQL tables (`test_cases`, `analysis_logs`) accessed via IPv4 Pooler (`6543`) / HTTPS and `sample-videos` public bucket.
  - Offline unit test suite + bounded `--live` smoke script.
- **Sprint 1 Exit Gate**: All offline unit tests (`unittest`) pass without calling live APIs; bounded `--live` probe verifies Sightengine `models=deepfake` eligibility, `google-genai` delete cleanup, and `/api/alpha/decisions`.

### Sprint 2: SSE API Packaging, Pre-Caching & Cloud Deployment (Nov 29 - Dec 01)
- **Sprint Goal**: Expose SSE streaming endpoint matching `spec-api-contract.md`, deploy Docker container to Render (`<512MB` RAM), connect Supabase, and wire Next.js timeline UI on Vercel.
- **Key Deliverables**:
  - FastAPI endpoints: `/health` (warm-up ping), `/ready` (IPv4 DB probe), `/api/v1/cases`, `/api/v1/analyze` (`text/event-stream` SSE, direct CORS bypassing Vercel 4.5 MB cap, 15 MB / 30s limits), and `/api/v1/logs`.
  - Pre-computed `cached_analysis` JSON stored in Supabase `test_cases` table for the 3 official test cases (`0ms` delay).
  - Non-root `Dockerfile` (`python:3.11-slim` + `ffmpeg`, zero `moviepy`) deployed cleanly to Render Web Service.
  - Next.js Video Player + Live 5-second SSE Risk Timeline deployed to Vercel (firing `GET /health` warm-up on mount) and routed via Cloudflare.
- **Sprint 2 Exit Gate**: Judges can open the live Vercel URL, play Case 1–3 smoothly from Supabase Storage, and upload an MP4 directly to Render watching live 5s SSE badges appear.

### Sprint 3: Hardening, Benchmark Metrics & Submission Bundle (Dec 02 - Dec 03)
- **Sprint Goal**: Execute full 12-case Validation Matrix (`T01`–`T12`), measure real latency/RAM benchmarks, and finalize all MoMo TechDay '26 deliverables.
- **Key Deliverables**:
  - Execute and record results for all 12 validation matrix scenarios (including rolling context `T11` and dual local+cloud cleanup `T12`).
  - Measure real `p50`/`p95` per-window processing latencies and verify Render RAM stays under 400 MB.
  - Record 3-minute live demo MP4 video showcasing real deployed product behavior.
  - Finalize 10-page presentation slide PDF, 1-page A4 judge guide PDF, and clean `.zip` source archive with accurate `README.md`.
- **Sprint 3 Exit Gate**: Complete submission package uploaded to TechDay '26 portal before December 03 deadline.
