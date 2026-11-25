# AntiDeepFake

## Backend offline

Requires Python 3.12 and `ffmpeg`/`ffprobe` on PATH.

```sh
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements-dev.txt
python -m backend.smoke_test --inspect
python -m backend.smoke_test --offline
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Upload with `curl -N -F 'file=@path/to/video.mp4' http://127.0.0.1:8000/api/v1/analyze`.
The default app does not call external providers and cannot classify real uploads;
missing provider results are reported as incomplete. Tests inject synthetic provider
results; these are not transcripts verified against the clips.

## Provider and storage configuration

Copy `.env.example` to `.env`, supply real provider credentials and set
`PROVIDER_MODE=live` only when you intend to send frames and audio out of the local environment.
Run `uvicorn backend.main:app --env-file .env` to load the file. Gemini uses
`generate_content`; the application falls back to the configured model on a 404.
Provider response formats and model availability must be verified with the bounded probe:

```sh
python -m backend.smoke_test --live --max-image 1 --max-audio 1 --max-state 1
```

The probe uploads one sample audio chunk, requests transcription, then attempts to delete the remote file.
Memory storage is the default. For SQLite set `REPOSITORY_BACKEND=sqlite` and optionally
`SQLITE_PATH`. For PostgreSQL set `REPOSITORY_BACKEND=postgres` and `DATABASE_URL`, and apply
`backend/db/schema.sql` first (the optional Compose service applies it to a new volume).
Demo cases appear only after the database is seeded. Live service availability and formal
Gate 1/2 sign-off require separate verification.
