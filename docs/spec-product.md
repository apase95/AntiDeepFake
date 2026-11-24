# AntiDeepFake - Product Specification

## 1. Project Overview
- **Project Name**: AntiDeepFake (DeepCall Sentinel)
- **Product Category**: Multimodal Real-time AI Assistant for Video Scam and Deepfake Prevention.
- **Competition Track**: Anti-Scam / AI Assistant in Fintech (TechDay '26 - MoMo).
- **Core Goal**: Intervene and alert users immediately during video calls before they transfer money, share OTP codes, or disclose private credentials to scammers.

---

## 2. Target Audience
- Individual users of digital wallets (such as MoMo) and mobile banking apps.
- Elderly people, parents, and families whose children or relatives live far away and who often receive urgent video calls asking for financial help.

---

## 3. Urgent Problem (Pain Points)
- Scammers hijack social media accounts (Facebook, Zalo, Telegram) of friends or relatives. They use face-swap deepfakes or play back pre-recorded videos during a brief video call (5 to 10 seconds) to build trust.
- Social engineering tactics: Scammers create psychological pressure by saying urgent phrases like *"Please transfer money right now, do not call mom"* and claim that the network connection is bad to hang up quickly.
- Critical impact: Warning the victim after the call ends is usually too late because the money is already transferred. The product must detect suspicious signals while the call or video is running so the user can pause and verify.

---

## 4. Core AI Mechanisms & Independent Alert Philosophy

### 4.1. Computer Vision Module (Direct Visual Analysis)
- Samples video frames (keyframes) from the video stream every 5-second window.
- Calls the Sightengine REST API specialized in deepfake and face-swap detection to output a confidence score (`cv_score` from `0.0` to `1.0`).
- Edge-case handling: If the face is too small, out of focus, or degraded due to poor network bandwidth, the system marks the state as `insufficient_visual_data` instead of incorrectly labeling it as a fake video.

### 4.2. Natural Language Processing Module (Real-time Speech Analysis)
- Transcribes Vietnamese audio into text in 5-second chunks using Google's low-latency `gemini-3.5-transcribe` model.
- Automatically masks sensitive numbers (PII/OTP) before processing.
- Evaluates psychological pressure indicators: urgent transfer requests, asking for OTP, threats, asking to keep secrets, or discouraging verification calls to relatives.

### 4.3. Risk Synthesis & Independent Alert Philosophy
- **Both branches do not need to agree to trigger an alert**:
  1. **Verbal Scam Signals Detected**: If the conversation asks for urgent money and discourages verification, the web app triggers an urgent RED alert immediately without waiting for visual confirmation.
  2. **Visual Tampering Only**: If only the face shows deepfake artifacts but the speech is neutral, the system displays a YELLOW warning: *"Visual tampering detected; do not use this video to verify identity"*, without accusing the caller of fraud.
  3. **Both Signals Confirmed**: Triggers the highest priority RED alarm: *"Confirmed High-Risk Scam - Stop Transaction"*.
