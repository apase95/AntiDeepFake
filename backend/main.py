import asyncio
import json
import math
import shutil
import tempfile
import time
from contextlib import aclosing
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from starlette.datastructures import UploadFile
from starlette.responses import JSONResponse, StreamingResponse

from .media import probe, slice_window
from .policy import ACTIONS, INJECTION, derive, ground, redact

FILE_LIMIT = 15 * 1024**2
BODY_LIMIT = FILE_LIMIT + 64 * 1024


def error(status, code, message):
    return JSONResponse({'schema_version': '1.1', 'code': code, 'message': message,
                         'request_id': 'req_' + uuid4().hex}, status_code=status)


class BoundedUpload:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST' or scope['path'] != '/api/v1/analyze':
            return await self.app(scope, receive, send)
        with tempfile.SpooledTemporaryFile(max_size=1024**2) as body:
            size = 0
            while True:
                event = await receive()
                if event['type'] == 'http.disconnect':
                    return
                chunk = event.get('body', b'')
                size += len(chunk)
                if size > BODY_LIMIT:
                    return await error(413, 'file_too_large', 'Upload exceeds the size limit.')(scope, receive, send)
                body.write(chunk)
                if not event.get('more_body'):
                    break
            body.seek(0)
            left = size

            async def replay():
                nonlocal left
                if left < 0:
                    return await receive()
                chunk = body.read(64 * 1024)
                left -= len(chunk)
                more = left > 0
                if not more:
                    left = -1
                    body.close()
                return {'type': 'http.request', 'body': chunk, 'more_body': more}

            # Use ASGI 2.3 disconnect monitoring even on servers advertising 2.4+.
            scope = {**scope, 'asgi': {**scope.get('asgi', {}), 'spec_version': '2.3'}}
            return await self.app(scope, replay, send)


class OfflineProviders:
    async def evaluate(self, frame):
        return 'provider_error', None

    async def transcribe(self, audio):
        return None

    async def decide(self, previous, current, injection_detected):
        return None


async def bounded(call, fallback):
    try:
        return await asyncio.wait_for(call, 10)
    except Exception:
        return fallback


def sse(event, payload):
    return f'event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n'


def create_app(providers=None, temp_root=None):
    app = FastAPI()
    app.add_middleware(BoundedUpload)
    providers = providers or OfflineProviders()
    logs = []

    @app.get('/health')
    async def health():
        return {'status': 'ok', 'service': 'api'}

    @app.get('/ready')
    async def ready():
        if not all(shutil.which(tool) for tool in ('ffmpeg', 'ffprobe')):
            return error(503, 'not_ready', 'Media tools unavailable.')
        return {'status': 'ok', 'repository': 'memory'}

    @app.get('/api/v1/cases')
    async def cases():
        return []

    @app.get('/api/v1/logs')
    async def analysis_logs():
        return list(reversed(logs))

    @app.post('/api/v1/analyze')
    async def analyze(request: Request):
        workspace = tempfile.TemporaryDirectory(prefix='adf_', dir=temp_root)
        root = Path(workspace.name)
        source = root / 'upload'
        handed_off = False
        try:
            async with request.form(max_files=1, max_fields=0) as form:
                upload = form.get('file')
                if not isinstance(upload, UploadFile):
                    return error(400, 'invalid_file', 'Expected one video file.')
                if upload.size is not None and upload.size > FILE_LIMIT:
                    return error(413, 'file_too_large', 'Video exceeds 15 MB.')
                size = 0
                with source.open('wb') as target:
                    while chunk := await upload.read(1024**2):
                        size += len(chunk)
                        if size > FILE_LIMIT:
                            return error(413, 'file_too_large', 'Video exceeds 15 MB.')
                        target.write(chunk)
            duration, has_audio, options = await probe(source)
            if duration > 30:
                return error(422, 'duration_exceeded', 'Video exceeds 30 seconds.')
            handed_off = True
        except (ValueError, TimeoutError):
            return error(400, 'invalid_file', 'Video could not be read.')
        finally:
            if not handed_off:
                workspace.cleanup()

        async def events():
            previous = ''
            analysis_id = 'adf_' + uuid4().hex
            started = time.monotonic()
            risks = {'LOW': 0, 'UNKNOWN': 1, 'MEDIUM': 2, 'HIGH': 3}
            overall, count, max_cv = 'LOW', 0, None
            try:
                for index in range(math.ceil(duration / 5)):
                    start, end = index * 5, min(index * 5 + 5, duration)
                    with tempfile.TemporaryDirectory(prefix=f'w{index + 1}_', dir=root) as directory:
                        frame, audio = await slice_window(source, Path(directory), start,
                                                          end - start, has_audio, options)
                        async def cv():
                            if frame is None:
                                return 'insufficient_visual_data', None
                            return await bounded(providers.evaluate(frame), ('provider_error', None))

                        async def stt():
                            return '' if audio is None else await bounded(providers.transcribe(audio), None)

                        async with asyncio.TaskGroup() as group:
                            cv_task, stt_task = group.create_task(cv()), group.create_task(stt())
                        status, score = cv_task.result()
                        raw = stt_task.result()
                        text = redact(raw or '')
                        injection = bool(INJECTION.search(text) or INJECTION.search(previous))
                        decision = (None if raw is None else await bounded(
                            providers.decide(previous, text, injection), None))
                        # An injection flag is not evidence of coercion. Fail closed on
                        # untrusted model output for this pair rather than promote it.
                        if injection:
                            decision = None
                        verdict, probability, risk = derive(status, score, decision, text)
                        quote = ground(decision.quote, text, previous) if decision and verdict in {
                            'confirmed_scam', 'verbal_pressure_only'} else None
                    overall = max(overall, risk, key=risks.get)
                    count += 1
                    if score is not None:
                        max_cv = max(max_cv or 0, score)
                    rolling = bool(previous.strip())
                    previous = text
                    yield sse('window', dict(window_id=count, start_sec=start, end_sec=end,
                                             cv_status=status, cv_score=score, transcript_redacted=text,
                                             rolling_context_used=rolling, verdict=verdict,
                                             probability=probability, risk_level=risk,
                                             trigger_quote=quote, recommended_action=ACTIONS[verdict]))
                yield sse('summary', dict(schema_version='1.1', analysis_id=analysis_id,
                                          duration_seconds=duration, overall_risk_level=overall,
                                          processing_time_ms=int((time.monotonic()-started)*1000),
                                          total_windows=count))
            except Exception:
                yield sse('error', dict(schema_version='1.1', code='analysis_failed',
                                        message='Analysis could not finish.', request_id=analysis_id))
            finally:
                if count:
                    logs.append(dict(analysis_id=analysis_id, source_type='user_upload',
                                     window_count=count, overall_risk_level=overall, max_cv_score=max_cv))
                    del logs[:-100]

        class AnalysisResponse(StreamingResponse):
            async def __call__(self, scope, receive, send):
                try:
                    async with aclosing(self.body_iterator):
                        await super().__call__(scope, receive, send)
                finally:
                    workspace.cleanup()

        return AnalysisResponse(events(), media_type='text/event-stream',
                                headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

    return app


app = create_app()
