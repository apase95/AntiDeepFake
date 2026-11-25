import argparse
import asyncio
from pathlib import Path

from .media import probe


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--offline', action='store_true')
    mode.add_argument('--inspect', action='store_true')
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

    asyncio.run(inspect())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
