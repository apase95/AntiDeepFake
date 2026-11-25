import asyncio
import json
import math
import re
from pathlib import Path


async def run(*args):
    process = await asyncio.create_subprocess_exec(
        *args, stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), 20)
    finally:
        if process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            await process.wait()
    if process.returncode:
        raise ValueError('Media processing failed')
    return stdout, stderr.decode(errors='replace')


async def probe(path: Path):
    # Force a supported demuxer and disallow network protocols and MP4 external tracks.
    with path.open('rb') as stream:
        header = stream.read(12)
    if header[4:8] == b'ftyp':
        options = ('-f', 'mov', '-enable_drefs', '0')
    elif header.startswith(b'\x1a\x45\xdf\xa3'):
        options = ('-f', 'matroska')
    else:
        raise ValueError('Unsupported media')
    options = ('-protocol_whitelist', 'file', *options)
    stdout, _ = await run('ffprobe', '-v', 'error', *options, '-show_format',
                          '-show_streams', '-of', 'json', str(path))
    info = json.loads(stdout)
    duration = float(info.get('format', {}).get('duration', 'nan'))
    tracks = {stream['codec_type'] for stream in info.get('streams', [])}
    if not math.isfinite(duration) or duration <= 0 or 'video' not in tracks:
        raise ValueError('Invalid video')
    return duration, 'audio' in tracks, options


async def slice_window(source, directory, start, length, has_audio, options):
    prefix = ('ffmpeg', '-hide_banner', '-nostdin', '-y', '-ss', str(start),
              '-t', str(length), *options, '-i', str(source))
    frame = directory / 'frame.jpg'
    _, report = await run(*prefix, '-an', '-vf',
                          "scale='min(640,iw)':-2,signalstats,metadata=print",
                          '-frames:v', '1', str(frame))
    brightness = re.search(r'lavfi.signalstats.YAVG=([\d.]+)', report)
    audio = None
    if has_audio:
        audio = directory / 'audio.mp3'
        _, report = await run(*prefix, '-vn', '-af', 'volumedetect', '-ac', '1',
                              '-ar', '16000', '-b:a', '64k', str(audio))
        volume = re.search(r'mean_volume: (-?[\d.]+) dB', report)
        if not volume or float(volume[1]) < -60:
            audio = None
    return frame if brightness and float(brightness[1]) >= 30 else None, audio
