import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
from fastapi.testclient import TestClient

from backend.main import create_app
from backend.policy import Decision
from backend.providers import LiveProviders, Settings
from backend.repository import SqliteRepository


class ConnectorTests(unittest.IsolatedAsyncioTestCase):
    async def test_sightengine_429(self):
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(429))) as http:
            providers = LiveProviders(Settings(), http=http)
            with tempfile.TemporaryDirectory() as directory:
                frame = Path(directory) / 'frame.jpg'
                frame.write_bytes(b'image')
                self.assertEqual(await providers.evaluate(frame), ('provider_error', None))

    async def test_gemini_deletes_on_failure(self):
        google = AsyncMock()
        google.files.upload.return_value = SimpleNamespace(name='files/test')
        google.models.generate_content.side_effect = RuntimeError('test')
        providers = LiveProviders(Settings(), google=google)
        try:
            self.assertIsNone(await providers.transcribe(Path('audio.mp3')))
            google.files.delete.assert_awaited_once_with(name='files/test')
        finally:
            await providers.aclose()

    async def test_sqlite_reopens(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.db'
            repository = SqliteRepository(path)
            await repository.start()
            await repository.insert(dict(analysis_id='test', source_type='user_upload', duration_seconds=4,
                                         window_count=1, overall_risk_level='HIGH', max_cv_score=None,
                                         processing_time_ms=20))
            reopened = SqliteRepository(path)
            self.assertTrue(await reopened.ready())
            self.assertEqual((await reopened.logs())[0]['analysis_id'], 'test')


class RollingTests(unittest.TestCase):
    def test_previous_window_is_redacted_and_grounds_quote(self):
        providers = AsyncMock()
        providers.evaluate.return_value = ('evaluated', .92)
        providers.transcribe.side_effect = ['Do not call your bank. OTP 123456', 'Transfer the money now.']
        providers.decide.side_effect = [Decision(), Decision('coercive', 'Do not call your bank')]
        with patch('backend.main.probe', return_value=(10, True, ())), \
             patch('backend.main.slice_window', return_value=(Path('frame'), Path('audio'))), \
             TestClient(create_app(providers)) as client:
            result = client.post('/api/v1/analyze', files={'file': b'mock'})
        self.assertIn('confirmed_scam', result.text)
        self.assertIn('"trigger_quote": "Do not call your bank"', result.text)
        self.assertEqual(providers.decide.await_args.args[0], 'Do not call your bank. OTP [REDACTED_NUM]')
