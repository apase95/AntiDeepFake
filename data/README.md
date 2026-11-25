# AntiDeepFake - Evaluation Sample Videos (`data/`)

This directory contains curated English-language `.mp4` sample videos mapped directly to the evaluation criteria in `docs/validation/validation-plan.md` and `docs/specs/spec-demo.md`.

All deepfake video tracks are sourced from MIT-licensed benchmark datasets (`luchaoqi/TalkingHeadBench`) and verified against **Sightengine Deepfake API**, while authentic video tracks are sourced from `KlingTeam/LivePortrait` driving clips.

---

## Folder & Evaluation Mapping

| Folder | Criterion ID | Video Visuals | Audio Content | Expected Verdict |
|---|---|---|---|---|
| `01_T01_deepfake_scam/` | **T01 (Case 1)** | Deepfake (`AniPortraitAudio`, Sightengine `0.93`) | Urgent transfer + anti-verification | `confirmed_scam` (RED) |
| `02_T02_genuine_face_scam/` | **T02 (Case 2)** | Genuine Human (`d14.mp4`, Sightengine `0.001`) | Urgent transfer + anti-verification | `verbal_pressure_only` (ORANGE) |
| `03_T03_low_quality_safe/` | **T03 (Case 3)** | Degraded/Blurred (`320x320`, `boxblur`, `100kbps`) | Casual benign conversation | `normal` / `insufficient_visual_data` (GREEN) |
| `04_T04_deepfake_benign_speech/` | **T04** | Deepfake (`Hallo`, Sightengine `0.92`) | Casual benign conversation | `visual_alert_only` (YELLOW) |
| `05_T05_silent_no_face/` | **T05** | Black blank frames (no human face) | Silent audio track | `insufficient_visual_data` + empty transcript |
| `06_T06_pii_redaction/` | **T06 (R05)** | Genuine Human (`d3.mp4`) | Contains bank account, phone, and OTP | `[REDACTED_NUM]` masking verified |
| `07_T08_prompt_injection/` | **T08 (R07)** | Deepfake (`EmoPortrait`, Sightengine `0.91`) | Adversarial override + scam request | `confirmed_scam` (injection blocked) |
| `08_T09_duration_limit_exceeded/` | **T09** | Genuine Human (`d6.mp4`, `33.6 seconds`) | Exceeds 30s limit | HTTP `422 duration_exceeded` |
| `09_T11_rolling_context_boundary/` | **T11 (R01)** | Deepfake (`Hallo2`) | Scam split across `00:05` boundary | Window 2 detects `confirmed_scam` |
