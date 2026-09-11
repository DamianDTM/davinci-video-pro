"""Create a new four-second reference clip after the script gate, preserving the source."""
import argparse
import json
from pathlib import Path
import subprocess
from workflow import require_script, digest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-dir', type=Path, required=True)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--start', type=float, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require_script(a.project_dir)
    import av
    import imageio_ffmpeg
    source = a.source.expanduser().resolve(strict=True)
    target = a.output.expanduser().resolve()
    if target.exists() or target.with_suffix('.source.json').exists() or target.suffix.lower() != '.mp4':
        raise ValueError('Elige un MP4 nuevo; se preservan los archivos existentes.')
    with av.open(str(source)) as media:
        video = media.streams.video[0]
        duration = media.duration / av.time_base if media.duration else None
        if a.start < 0 or duration is None or a.start + 4 > duration + 0.01:
            raise ValueError('Selecciona cuatro segundos completos dentro del video.')
        scale = 'scale=720:-2:out_range=tv' if video.width <= video.height else 'scale=-2:720:out_range=tv'
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
               '-i', str(source), '-ss', str(a.start), '-t', '4', '-map', '0:v:0', '-map', '0:a:0?',
               '-vf', scale, '-r', '30', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
               '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(target)]
    subprocess.run(command, check=True, capture_output=True, timeout=180)
    record = {'source': str(source), 'source_sha256': digest(source), 'start_seconds': a.start,
              'duration_seconds': 4, 'output': str(target), 'note': 'Restore this original audio after Omni generation.'}
    target.with_suffix('.source.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
