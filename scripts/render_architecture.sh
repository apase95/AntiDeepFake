#!/usr/bin/env bash
# ==============================================================================
# AntiDeepFake - Production Architecture Blueprint for Draw.io
# Run: bash scripts/render_architecture.sh
# ==============================================================================

cat << 'EOF'

========================================================================================================================
                              ANTIDEEPFAKE - CLOUD PRODUCTION ARCHITECTURE (DRAW.IO BLUEPRINT)
========================================================================================================================

    [ACTOR: JUDGE / USER (BROWSER)]                                                          [ACTOR: DEVOPS / DEV]
       |                       |                                                                       |
 (1) Load UI &                 +---(2) Direct CORS Upload (<=15MB MP4)                         (Git Push to Repo)
     Stream Demo MP4                   (Bypasses Vercel 4.5MB limit!)                                  |
       |                               |                                                               v
       v                               |                                                    [GitHub Actions CI/CD]
+----------------------------------+   |
| TIER 1: FRONTEND & EDGE TIER     |   |
| (Cloudflare + Vercel Hobby)      |   |
+----------------------------------+   |
| - Cloudflare (DNS + SSL + CDN)   |   |
| - Vercel Edge (Next.js 14 App)   |   |
|   * Warm-up GET /health on load  |   |
|   * Video Player (from Supabase) |   |
|   * Live 5s SSE Risk Timeline    |   |
|   * Red / Yellow Alert Badges    |   |
+----------------------------------+   |
       ^                               |
       | (5) SSE Event Stream          |
       |     (1 WindowEvaluation / 5s) |
       |                               v
+----------------------------------------------------------------------------------------------------------------------+
|  TIER 2: BACKEND COMPUTE TIER (Render Docker - 512MB RAM Free Tier)                                                  |
|  +----------------------------------------------------------------------------------------------------------------+  |
|  | [FastAPI + Uvicorn (Non-root)]     [Pure ffmpeg Subprocess]            [Guardrails & Ephemeral Cleanup]        |  |
|  | - Direct CORS HTTPS Endpoints      - No moviepy (saves >250MB RAM)     - PII Regex Masking ([REDACTED_NUM])    |  |
|  | - POST /api/v1/analyze (SSE)       - Slices 5s .mp3 + 1 keyframe .jpg  - Rolling Context (prev + curr 5s text) |  |
|  | - GET  /api/v1/cases (0ms Cache)   - Stored in /tmp/adf_<uuid>/        - Quote Grounding + finally() cleanup   |  |
|  +----------------------------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------------------------+
                         |                                                     |
            (3) Parallel AI Inference                                (4) IPv4 Pooler / HTTPS DB
                         |                                                     |
                         v                                                     v
+------------------------------------------------------+     +-------------------------------------------------+
|  TIER 4: EXTERNAL SERVERLESS AI TIER                 |     |  TIER 3: DATA & STORAGE TIER (Supabase)         |
|  +------------------------------------------------+  |     |  +-------------------------------------------+  |
|  | [1. Sightengine REST API (models=deepfake)]    |  |     |  | [Supabase Storage (Object Storage)]       |  |
|  | - 1 keyframe / 5s + Semaphore(1) (1.1s spacing)|  |     |  | - Public Bucket: "sample-videos"          |  |
|  | - Optional Fallback: HuggingFace SigLIP2       |  |     |  | - Hosts 3 MP4 demo clips (0ms egress)     |  |
|  +------------------------------------------------+  |     |  +-------------------------------------------+  |
|  | [2. Google Gemini 3.5 Transcribe]              |  |     |  | [Supabase PostgreSQL (IPv4 Pooler :6543)] |  |
|  | - Interactions API + Files API (google-genai)  |  |     |  | - Library: asyncpg or supabase-py HTTPS   |  |
|  | - Explicit files.delete() in finally() block   |  |     |  | - Table: "test_cases" (Pre-cached JSON)   |  |
|  +------------------------------------------------+  |     |  | - Table: "analysis_logs" (Redacted meta)  |  |
|  | [3. OpenRouter: pplx-decider-flash-v1.3:free]  |  |     |  +-------------------------------------------+  |
|  | - Endpoint: POST /api/alpha/decisions          |  |     +-------------------------------------------------+
|  | - Payload: state + questions (choice criteria) |  |
|  | - Output: answers["risk_verdict"] + prob       |  |
|  +------------------------------------------------+  |
+------------------------------------------------------+

========================================================================================================================
                                             SUMMARY OF DRAW.IO BLOCKS
========================================================================================================================
1. Top Actors: Judge Browser (Left - splits traffic: static UI to Vercel, >4.5MB MP4 direct to Render), DevOps (Right).
2. Tier 1 (Blue Box): Cloudflare + Vercel (Next.js 14 UI, Warm-up ping, SSE Timeline Consumer).
3. Tier 2 (Orange Box): Render Docker (FastAPI SSE, pure ffmpeg subprocess, PII masking, Rolling Context, Quote Grounding).
4. Tier 3 (Green Box): Supabase (Storage "sample-videos" + PostgreSQL IPv4 Pooler port 6543: test_cases, analysis_logs).
5. Tier 4 (Purple Box): Sightengine (1 req/s Semaphore + HF fallback), Gemini 3.5 Transcribe (Interactions + delete),
                        OpenRouter /api/alpha/decisions (pplx-decider-flash-v1.3:free).
========================================================================================================================

EOF
