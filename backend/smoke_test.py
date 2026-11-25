import argparse
import asyncio
import os
import tempfile
from pathlib import Path

from .media import probe, slice_window
from .main import bounded
from .providers import LiveProviders, Settings
from dotenv import dotenv_values


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--offline', action='store_true')
    mode.add_argument('--inspect', action='store_true')
    mode.add_argument('--live', action='store_true')
    for name in ('image', 'audio', 'state'):
        parser.add_argument(f'--max-{name}', type=int, choices=(0, 1), default=1)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.offline:
        import unittest
        suite = unittest.defaultTestLoader.discover(str(root / 'tests'))
        return int(not unittest.TextTestRunner().run(suite).wasSuccessful())

    async def inspect():
        for path in sorted((root / 'data').glob('*/*.mp4')):
            duration, audio, _ = await probe(path)
            print(f'{path.parent.name}: {duration:.3f}s, audio={audio}')

    if args.live:
        cfg = Settings.from_env({**dotenv_values(root / '.env'), **os.environ})
        if ((args.max_image and not (cfg.sight_user and cfg.sight_secret)) or
                (args.max_audio and not cfg.google_key) or (args.max_state and not cfg.router_key)):
            parser.error('Missing credentials for one or more selected probes')

        async def live():
            from dataclasses import replace
            # No fallback requests in the quota-bounded probe.
            providers = LiveProviders(replace(cfg, hf_url='', gemini_fallback=cfg.gemini_model))
            checks = []
            try:
                if args.max_image or args.max_audio:
                    source = next((root / 'data').glob('01*/*.mp4'))
                    _, has_audio, options = await probe(source)
                    with tempfile.TemporaryDirectory() as directory:
                        frame, audio = await slice_window(source, Path(directory), 0, 5, has_audio, options)
                        if args.max_image:
                            result = await bounded(providers.evaluate(frame), ('provider_error', None), 10) if frame else ('provider_error', None)
                            checks.append(('vision', result[0] == 'evaluated'))
                        if args.max_audio:
                            result = await bounded(providers.transcribe(audio), None, 10) if audio else None
                            checks.append(('speech', bool(result)))
                if args.max_state:
                    result = await bounded(providers.decide('', 'Please call me tomorrow.', False), None, 10)
                    checks.append(('decision', result is not None))
            finally:
                await providers.aclose()
            for name, passed in checks:
                print(f'{name}: {"ok" if passed else "failed"}')
            return int(not checks or not all(passed for _, passed in checks))

        return asyncio.run(live())
    asyncio.run(inspect())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
