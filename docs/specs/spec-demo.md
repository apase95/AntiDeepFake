# AntiDeepFake - Online Demo & Evaluation Guide

This document is formatted as a 1-page A4 guide for the MoMo TechDay '26 judges to test the product online quickly and smoothly.

---

## 1. Online Testing Access
- **Product URL**: `https://antideepfake.vercel.app` (or your active deployment domain)
- **Test Credentials**: Open access configured for judges (no registration or login required).
- **How to Test**: Judges can select any of the 3 pre-loaded test videos on the interface. The AI pipeline will evaluate the video stream in 5-second intervals and display risk badges along the live Timeline.

---

## 2. Three Test Scenarios (Evaluation Cases)

### Case 1: Primary Scam Case - Face-Swap Video with Suspicious Dialogue
- **Input Data**: A test video with face-swap synthesis where the caller urgently says: *"Chuyển ngay giúp em 15 triệu, đừng gọi cho mẹ nhé"* (*"Please transfer 15 million right now, do not call mom"*).
- **System Behavior**:
  - At 00:00 - 00:05: Sightengine flags face edge blending artifacts (`cv_score: 0.86`).
  - At 00:05 - 00:10: NLP captures the urgent money request and anti-verification phrase.
  - **Displayed Result**: Timeline badge at 00:10 turns **BRIGHT RED (Confirmed Scam - 95% Confidence)**.
  - **Evidence Provided**: Highlights the quote *"đừng gọi cho mẹ"* and displays the face tampering score.
  - **Recommended Action**: *"Urgent Scam Warning: Stop transaction immediately. Call your saved phone number directly to verify."*

### Case 2: Control Case - Genuine Webcam with Suspicious Dialogue
- **Input Data**: A normal webcam video of an authentic person speaking the exact same phrase: *"Chuyển ngay giúp em, đừng gọi cho mẹ"*.
- **System Behavior**:
  - CV returns a safe score (`cv_score: 0.08`, no visual flag).
  - NLP identifies psychological coercion and attempts to prevent verification.
  - **Displayed Result**: Timeline badge turns **ORANGE (Verbal Pressure Only - 88% Confidence)**.
  - **Key takeaway**: The system still alerts the user even when the video is genuine (guarding against situations where a compromised account forces a real person to speak).

### Case 3: Low-Quality Video Case - Degraded Network & Blurry Frames
- **Input Data**: A real user on a weak network connection with heavy blur and pixelation, having a normal, casual conversation.
- **System Behavior**:
  - CV avoids false alarms and marks the state as: *"Insufficient Visual Data"*.
  - NLP confirms the speech is safe and normal.
  - **Displayed Result**: Timeline badge remains **GREEN (Normal - Safe)**, noting weak video signal without triggering annoying false alarms.
