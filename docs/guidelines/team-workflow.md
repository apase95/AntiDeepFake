# AntiDeepFake - Team Workflow & Engineering Guidelines

This document outlines the development workflow, collaboration rules, and Definition of Done (DoD) for the 3-engineer team.

---

## 1. Git Branching & Commit Conventions

### 1.1. Branching Strategy
- **`main`**: Production branch. Every merge to `main` automatically triggers deployments on Render (Backend) and Vercel (Frontend). Direct push to `main` is restricted during integration sprints.
- **`feature/<role>-<short-description>`**: Working branches for individual features.
  - Examples:
    - `feature/ai-sightengine-connector`
    - `feature/be1-video-windowing`
    - `feature/be2-supabase-storage`
- **`fix/<issue-description>`**: Bug fix branches.

### 1.2. Commit Message Standards (Conventional Commits)
Each commit must follow the standard format: `<type>(<scope>): <short imperative description>`
- `feat`: A new feature (e.g., `feat(pipeline): add ffmpeg 5s chunking logic`).
- `fix`: A bug fix (e.g., `fix(auth): handle missing sightengine credentials gracefully`).
- `docs`: Documentation only changes (e.g., `docs(specs): update product specification`).
- `chore`: Configuration, tooling, or dependency updates (e.g., `chore(docker): optimize dockerfile build layers`).

---

## 2. Secrets & Security Policy

1. **Never Commit Secrets to Git**:
   - The `.env` file containing live API keys (Sightengine, Google, OpenRouter, Database passwords) is strictly ignored via `.gitignore`.
   - Never paste API keys into markdown files, commit messages, or pull requests.
2. **Environment Synchronization**:
   - Whenever a new environment variable is introduced, immediately update `.env.example` with placeholder values and clear comments.
3. **Production Secrets**:
   - Live production keys are entered manually in the **Render Environment Dashboard** and **Vercel Environment Settings**.

---

## 3. Definition of Done (DoD)

A task or feature branch is considered "Done" only when:
1. **Schema Validation**: All input and output JSON objects strictly validate against defined `Pydantic` models without raising runtime exceptions.
2. **Performance SLA**: Processing a 5-second video window (Audio STT + Vision Deepfake + Choice Decision) must complete within **1.5 seconds**.
3. **Graceful Fallback**: If an external API fails, times out, or returns an error, the pipeline must catch the exception, log the issue, and return a safe fallback verdict (`insufficient_visual_data` or `safe`) instead of crashing the server.
4. **Code Quality**: Code is formatted cleanly, typed with Python type hints, and includes clear function docstrings.

---

## 4. Team Daily Sync & Handoff Protocol

- **Daily Standup (15 Minutes)**:
  - What did you complete yesterday?
  - What are you working on today?
  - Are there any blocking dependencies between AI, Pipeline, and Platform?
- **Integration Handoffs**:
  - AI Engineer delivers tested prompt templates and API connectors to Backend Engineer 1.
  - Backend Engineer 1 delivers the packaged pipeline function to Backend Engineer 2.
  - Backend Engineer 2 exposes the endpoints and verifies full end-to-end integration with the Next.js UI.
