# AntiDeepFake - API & Data Contract Specification (v1.1 - SSE Streaming)

> **Shared Technical Baseline**: Authoritative contract between AI Engineer, Backend Pipeline, Backend Platform, and Next.js Frontend.

## 1. Endpoints Overview

| Method & Path | Intent & Access | Notes |
|---|---|---|
| `GET /health` | Liveness & Cold-Start Warm-up | Returns `200 {"status": "ok", "service": "api"}`. Fired by UI on page load to wake Render. |
| `GET /ready` | Bounded DB readiness check | Executes `SELECT 1` on Supabase via IPv4 Pooler (`6543`) / HTTPS. Returns `503` on failure. |
| `GET /api/v1/cases` | Fetch 3 official demo cases | Returns metadata, Supabase Storage video URLs, and pre-cached timeline JSON (`0ms`). |
| `POST /api/v1/analyze` | **Progressive SSE Video Analysis** | Called directly from Browser to Render CORS (`multipart/form-data`, max 15 MB / 30s). Returns `text/event-stream` emitting `window` events every 5s. |
| `GET /api/v1/logs` | Fetch recent anonymized logs | Returns the last 20 redacted `analysis_logs` records (no PII/raw video). |

> **Critical Routing Rule**: Browser **must** send `POST /api/v1/analyze` directly to Render HTTPS (`NEXT_PUBLIC_API_BASE_URL`), never through Vercel Next.js API Proxy, to avoid Vercel Hobby Tier's 4.5 MB payload cap.

---

## 2. SSE Streaming Contract (`POST /api/v1/analyze`)

Content-Type: `text/event-stream`

### 2.1. `event: window` (Emitted progressively as each 5s chunk finishes)
```text
event: window
data: {"window_id":2,"start_sec":5,"end_sec":10,"cv_status":"evaluated","cv_score":0.88,"transcript_redacted":"Chuyển ngay giúp em [REDACTED_NUM] triệu, đừng gọi cho mẹ.","rolling_context_used":true,"verdict":"confirmed_scam","probability":0.94,"trigger_quote":"đừng gọi cho mẹ","recommended_action":"Urgent Warning: Pause transfer and call your saved phone number to verify."}
```
- **Allowed `cv_status` values**: `"evaluated"`, `"insufficient_visual_data"`, `"provider_error"`.
- **Window `risk_level`**: `LOW`, `MEDIUM`, `HIGH`, or `UNKNOWN`. Coercive speech can produce `verbal_pressure_only` with `HIGH` risk independently of visual evidence. `confirmed_scam` requires both verbal and visual evidence.
- **Allowed `verdict` values**: `"normal"`, `"visual_alert_only"`, `"verbal_pressure_only"`, `"confirmed_scam"`, `"evaluation_incomplete"`.
- **Invariants**:
  - `trigger_quote` must be `null` or a verified normalized substring of `transcript_redacted` (or the previous window transcript).
  - `cv_score` is strictly bounded `[0.0, 1.0]` or `null` when `cv_status != "evaluated"`.

### 2.2. `event: summary` (Emitted once after all chunks complete)
```text
event: summary
data: {"schema_version":"1.1","analysis_id":"adf_a1b2c3d4e5f6","duration_seconds":15,"overall_risk_level":"HIGH","processing_time_ms":3420,"total_windows":3}
```

### 2.3. `event: error` (Emitted if an unrecoverable stream failure occurs mid-flight)
```text
event: error
data: {"schema_version":"1.1","code":"provider_unavailable","message":"External evaluation timed out.","request_id":"req_9f8e7d6c"}
```

---

## 3. Pre-Cached Demo Response (`GET /api/v1/cases`)

```json
{
  "case_id": "case_1_faceswap_scam",
  "title": "Case 1: Face-Swap Video + Urgent Transfer Pressure",
  "description": "Tests simultaneous visual tampering and psychological coercion.",
  "video_url": "https://<project>.supabase.co/storage/v1/object/public/sample-videos/case1-faceswap-scam.mp4",
  "cached_analysis": {
    "schema_version": "1.1",
    "analysis_id": "demo_case_1",
    "duration_seconds": 15,
    "overall_risk_level": "HIGH",
    "processing_time_ms": 0,
    "windows": [
      {
        "window_id": 1,
        "start_sec": 0,
        "end_sec": 5,
        "cv_status": "evaluated",
        "cv_score": 0.85,
        "transcript_redacted": "Alo mẹ à, con đang ở ngoài đường.",
        "rolling_context_used": false,
        "verdict": "visual_alert_only",
        "probability": 0.81,
        "trigger_quote": null,
        "recommended_action": "Visual tampering detected; do not use video alone to verify identity."
      }
    ]
  }
}
```

---

## 4. Pre-Stream Validation Errors (HTTP Status Codes)

Before opening the SSE stream, invalid uploads immediately return a JSON error envelope without stack traces or PII:

```json
{
  "schema_version": "1.1",
  "code": "file_too_large",
  "message": "Video file exceeds the maximum allowed size of 15 MB.",
  "request_id": "req_9f8e7d6c"
}
```

| HTTP Status | Stable `code` | Trigger Condition & Client Handling |
|---|---|---|
| **400** | `invalid_media_format` | Uploaded file is not valid MP4/WebM or corrupted header. |
| **413** | `file_too_large` | File exceeds 15 MB limit before processing starts. |
| **422** | `duration_exceeded` | Video duration exceeds 30 seconds or Pydantic validation fails. |
| **429** | `rate_limited` | External AI quota reached or client hits upload rate cap. |
| **503** | `provider_unavailable` | Upstream DB unreachable on `/ready`. |

---

## 5. Supabase PostgreSQL Database Schema

Connect from Render using the **Supavisor IPv4 Pooler (port `6543`)** with `asyncpg` (or `supabase-py` HTTPS):

```sql
-- Pre-computed official demo test cases (0ms demo latency)
CREATE TABLE IF NOT EXISTS test_cases (
    case_id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    video_url TEXT NOT NULL,
    cached_analysis JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Anonymized metadata logs (zero raw video, zero unredacted PII)
CREATE TABLE IF NOT EXISTS analysis_logs (
    analysis_id VARCHAR(64) PRIMARY KEY,
    source_type VARCHAR(32) NOT NULL CHECK (source_type IN ('demo_case', 'user_upload')),
    duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0),
    window_count INTEGER NOT NULL CHECK (window_count > 0),
    overall_risk_level VARCHAR(16) NOT NULL CHECK (overall_risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'UNKNOWN')),
    max_cv_score FLOAT,
    processing_time_ms INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```
