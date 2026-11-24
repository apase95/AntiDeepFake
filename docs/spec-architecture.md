# AntiDeepFake - Technical Architecture Specification

## 1. Production Architecture Overview (Draw.io Blueprint)

The system is designed with four clear tiers:
1. **Frontend Tier (Vercel & Cloudflare)**: Global Edge delivery, SSL termination, and real-time interactive UI.
2. **Backend Compute Tier (Render & Docker)**: Lightweight FastAPI container with ffmpeg for 5-second video windowing.
3. **Data & Storage Tier (Supabase)**: Cloud PostgreSQL database and Supabase Storage for sample video hosting.
4. **External Serverless AI Tier**: Tri-model pipeline (Sightengine CV + Google Gemini STT + OpenRouter PPLX Decider).

```text
+---------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                               CLOUD ARCHITECTURE OVERVIEW                                                         |
+---------------------------------------------------------------------------------------------------------------------------------------------------+
|                                                                                                                                                   |
|  [User / Judge] ---------(1. Select / Stream Video)--------> [Frontend Tier: Vercel + Cloudflare]                                                 |
|  [User / Judge] <--------(5. Real-time 5s Timeline)-------- [Frontend Tier: Next.js 14 App]                                                       |
|                                                                          |                                                                        |
|                                                                 (2. Process 5s Chunk)                                                             |
|                                                                          |                                                                        |
|                                                                          v                                                                        |
|  +-------------------------------------+   +------------------------------------------------------+   +----------------------------------------+  |
|  |           FRONTEND TIER             |   |               BACKEND COMPUTE TIER                   |   |         DATA & STORAGE TIER            |  |
|  |         (Vercel & Cloudflare)       |   |                 (Render & Docker)                    |   |              (Supabase)                |  |
|  +-------------------------------------+   +------------------------------------------------------+   +----------------------------------------+  |
|  | - Cloudflare (DNS + SSL + CDN)      |   | - FastAPI Web Service (Port 8000)                    |   | - Supabase Storage:                    |  |
|  | - Vercel Edge Network               |   | - Docker Image (python:3.11-slim + ffmpeg)           |   |   Bucket: sample-videos (MP4 files)    |  |
|  | - Next.js 14 App Router:            |   | - Async 5-Second Window Pipeline:                    |   | - Supabase PostgreSQL:                 |  |
|  |   * Video Player Component          |   |   * Video frame sampling via ffmpeg                  |   |   Table: analysis_logs (Verdict, quote)|  |
|  |   * Live 5s Risk Timeline           |   |   * Audio chunking via ffmpeg                        |   |   Table: test_cases (Pre-cached JSON)  |  |
|  |   * Alert Modal & Badges            |   |   * Concurrent Async Dispatcher (aiohttp)            |   |   Table: user_sessions                 |  |
|  +-------------------------------------+   +---------------------------+--------------------------+   +----------------------------------------+  |
|                                                                        |                                                  ^                       |
|                                                               (3. Parallel Inference)                          (4. Fetch / Persist Logs)          |
|                                                                        |                                                  |                       |
|                                                                        v                                                  |                       |
|                                            +------------------------------------------------------+                       |                       |
|                                            |             EXTERNAL SERVERLESS AI TIER              |                       |                       |
|                                            +------------------------------------------------------+                       |                       |
|                                            | - Sightengine Deepfake API: Face-swap score (0.0-1.0)| ----------------------+                       |
|                                            | - Google Gemini 3.5 Transcribe: Low-latency STT      |                                               |
|                                            | - OpenRouter pplx-decider-flash: Choice Decision     |                                               |
|                                            +------------------------------------------------------+                                               |
+---------------------------------------------------------------------------------------------------------------------------------------------------+
```

---

## 2. Component Breakdown

| Tier | Component | Technology / Service | Role & Responsibility |
|---|---|---|---|
| **Frontend** | DNS & CDN | Cloudflare Free Plan | DNS management, DDoS protection, SSL termination, and edge caching |
| **Frontend** | Web Hosting | Vercel (Hobby Tier) | Hosts Next.js 14 App Router, video player, and live risk timeline |
| **Backend** | Compute | Render / Docker | Python 3.11-slim container with ffmpeg for 5s audio and frame extraction |
| **Backend** | Orchestrator | FastAPI + aiohttp | Parallel async dispatching to AI APIs and result aggregation |
| **Storage** | Video Storage | Supabase Storage | Public bucket `sample-videos` hosting test MP4 clips with zero egress fees |
| **Database**| Database | Supabase PostgreSQL | Stores analysis logs, pre-computed cached results, and session data |
| **AI (CV)** | Face-swap CV | Sightengine REST API | Specialized deepfake detection returning calibrated `prob` (0.0 - 1.0) |
| **AI (STT)**| Speech-to-Text | Google Gemini 3.5 Transcribe | Fast Vietnamese speech recognition with word-level timestamps |
| **AI (Logic)**| Decision Model | OpenRouter pplx-decider-flash | Evaluates State against Choice Questions to output calibrated verdict |

---

## 3. Data Flow Steps (Detailed Sequential Flow)

1. **Step 1: Video Access**: The judge loads the Next.js web app. Pre-loaded demo videos stream directly from **Supabase Storage** (`sample-videos` bucket) with low latency.
2. **Step 2: 5-Second Windowing**: The frontend or backend slices the active video stream into 5-second chunks (extracting audio to `.mp3` and 2-3 keyframes to `.jpg` via ffmpeg).
3. **Step 3: Parallel AI Dispatch**:
   - Audio is dispatched to **Google Gemini 3.5 Transcribe** -> returns Vietnamese transcript.
   - Keyframe images are dispatched to **Sightengine API** -> returns `deepfake_score`.
4. **Step 4: Decision Synthesis**:
   - Transcript and visual score are packaged into a State string.
   - Dispatched to **OpenRouter (`pplx-decider-flash-v1.3:free`)** using the Choice Question primitive.
   - Decider returns calibrated probability and verdict label (`normal`, `visual_alert_only`, `verbal_pressure_only`, `confirmed_scam`).
5. **Step 5: Timeline Update**: Backend writes the evaluation result to **Supabase PostgreSQL** and streams JSON to the frontend to update the live timeline badge.

---

## 4. Draw.io Box Attributes Guide (For Manual Drawing)

When drawing this diagram in Draw.io:
- **Group 1 (Top Left)**: User Actor icon (Ban giám khảo / Người dùng).
- **Group 2 (Top Right)**: DevOps Actor icon (Developer with Git push to Vercel/Render).
- **Main Outer Box**: "AntiDeepFake Cloud Ecosystem".
- **Column 1**: "Frontend Tier" (Vercel Triangle logo, Cloudflare Cloud logo, Next.js logo).
- **Column 2**: "Backend Serverless Compute" (Render / Docker Whale logo, FastAPI logo, ffmpeg icon).
- **Column 3**: "Data & Video Storage Tier" (Supabase logo, Storage Bucket icon, PostgreSQL Elephant icon).
- **Bottom Box**: "Managed AI Services" (Sightengine, Google AI, OpenRouter / Perplexity logos).
- **Connectors**: Solid arrows for data flow (1 to 5), dashed arrows for CI/CD deployments.
