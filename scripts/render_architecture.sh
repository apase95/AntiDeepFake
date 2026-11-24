#!/usr/bin/env bash
# ==============================================================================
# AntiDeepFake - Production Architecture Blueprint for Draw.io
# Run: bash scripts/render_architecture.sh
# ==============================================================================

cat << 'EOF'

========================================================================================================================
                              ANTIDEEPFAKE - CLOUD PRODUCTION ARCHITECTURE (DRAW.IO BLUEPRINT)
========================================================================================================================

    [ACTOR: JUDGE / USER]                                                                   [ACTOR: DEVOPS / DEV]
            |                                                                                         |
     (1) Select / Stream Video                                                               (Git Push to Repo)
     (5) Receive 5s Live Timeline Verdict                                                             |
            |                                                                                         v
            v                                                                              [GitHub Actions CI/CD]
+----------------------------------------------------------------------------------------------------------------------+
|  TIER 1: FRONTEND & EDGE TIER (Vercel & Cloudflare)                                                                  |
|  +----------------------------------------------------------------------------------------------------------------+  |
|  |  [Cloudflare Edge]                [Vercel Global Edge Network]              [Next.js 14 App Router]             | |
|  |  - Free DNS Management            - Zero-config CI/CD Deployment            - Video Player (Stream from Bucket) | |
|  |  - SSL/TLS Termination            - Serverless Edge Middleware              - Live 5s Risk Timeline Component   | |
|  |  - DDoS Shield & Edge Cache       - Auto Preview & Production URLs          - Real-time Alert Badges & Modal    | |
|  +----------------------------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------------------------+
                                           |
                                  (2) Send 5s Stream Chunk (Video/Audio)
                                           |
                                           v
+----------------------------------------------------------------------------------------------------------------------+
|  TIER 2: BACKEND SERVERLESS COMPUTE (Render / Docker)                                                                |
|  +----------------------------------------------------------------------------------------------------------------+  |
|  |  [Render Web Service]             [Docker Container]                        [FastAPI Orchestrator]              | |
|  |  - Free Web Service Tier          - Base: python:3.11-slim                  - Async non-blocking endpoints      | |
|  |  - Auto HTTPS: /api/v1/analyze    - System: ffmpeg (audio & frames)         - asyncio.gather() parallel dispatch| |
|  |  - Port: 8000                     - Python: aiohttp, pydantic, moviepy      - Pydantic schema validation        | |
|  +----------------------------------------------------------------------------------------------------------------+  |
+----------------------------------------------------------------------------------------------------------------------+
                         |                                                     |
            (3) Parallel AI Dispatch                                (4) Cache & Log Storage
                         |                                                     |
                         v                                                     v
+------------------------------------------------------+     +-------------------------------------------------+
|  TIER 4: EXTERNAL SERVERLESS AI TIER                 |     |  TIER 3: DATA & STORAGE TIER (Supabase)         |
|  +------------------------------------------------+  |     |  +-------------------------------------------+  |
|  | [1. Sightengine REST API]                      |  |     |  | [Supabase Storage (Object Storage)]       |  |
|  | - Endpoint: models=deepfake                    |  |     |  | - Bucket: "sample-videos" (Public)        |  |
|  | - Detects: Face-swap & GAN synthetic artifacts |  |     |  | - Stores: case1, case2, case3 MP4 videos  |  |
|  | - Output: cv_score (prob 0.0 - 1.0)            |  |     |  | - Zero egress fees for fast streaming     |  |
|  +------------------------------------------------+  |     |  +-------------------------------------------+  |
|  | [2. Google Gemini 3.5 Transcribe]              |  |     |  | [Supabase PostgreSQL Database]            |  |
|  | - Serverless Low-latency Audio Model           |  |     |  | - Table: "analysis_logs" (History)        |  |
|  | - Language: Vietnamese (with timestamps)       |  |     |  | - Table: "test_cases" (Pre-computed cache)|  |
|  | - Output: text transcript chunk                |  |     |  | - Table: "user_sessions" (Auth & tracking)|  |
|  +------------------------------------------------+  |     |  +-------------------------------------------+  |
|  | [3. OpenRouter: pplx-decider-flash-v1.3:free]   |  |     +-------------------------------------------------+
|  | - Perplexity System One Decision Model         |  |
|  | - Input: State (Transcript + CV Score)         |  |
|  | - Primitive: Choice Question (calibrated prob) |  |
|  | - Verdict: normal | visual | verbal | scam     |  |
|  +------------------------------------------------+  |
+------------------------------------------------------+

========================================================================================================================
                                             SUMMARY OF DRAW.IO BLOCKS
========================================================================================================================
1. Top Actors: User / Judge (Left), DevOps (Right).
2. Tier 1 (Blue Box): Vercel + Cloudflare (Frontend, DNS, CDN, Next.js).
3. Tier 2 (Orange Box): Render + Docker (FastAPI, Python, ffmpeg, Async Orchestrator).
4. Tier 3 (Green Box): Supabase (Storage Bucket for sample MP4 videos + PostgreSQL database).
5. Tier 4 (Purple Box): External Serverless AI (Sightengine CV + Google STT + OpenRouter Decider).
6. Numbered Arrows (1 -> 5): Trace the complete request-response lifecycle every 5 seconds.
========================================================================================================================

EOF
