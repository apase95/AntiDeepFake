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
results; these are not transcripts verified against the clips. Analysis logs are
in memory; the demo case list is empty. Live connectors, persistent storage and
formal Gate 1/2 sign-off are not included in this increment.
