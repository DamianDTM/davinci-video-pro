"""Local media QC and explicit agent review. Never edits or approves a video automatically."""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import subprocess
import sys

from workflow import digest, now, require_production


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def create_json(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def binding(path):
    path = Path(path).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError('La evidencia debe ser un archivo.')
    return {'path': str(path), 'sha256': digest(path)}


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError('Se esperaba un entero valido en el plan de revision.')
    return value


def validate_plan(plan):
    if not isinstance(plan, dict) or plan.get('version') != 1:
        raise ValueError('El plan necesita version: 1.')
    expected = plan['expected']
    for key in ('frames', 'width', 'height'): integer(expected[key], 1)
    if isinstance(expected['fps'], bool): raise ValueError('FPS invalido.')
    try: fps = Fraction(str(expected['fps']))
    except (ValueError, ZeroDivisionError): raise ValueError('FPS invalido.') from None
    if not 0 < fps <= 240 or type(expected['audio']) is not bool:
        raise ValueError('FPS o presencia de audio invalidos.')
    if type(expected.get('speech', expected['audio'])) is not bool:
        raise ValueError('speech debe ser booleano.')
    if expected.get('speech', expected['audio']) and not expected['audio']:
        raise ValueError('No puede haber discurso sin audio.')
    cuts = plan['cuts']
    if not isinstance(cuts, list): raise ValueError('cuts debe ser una lista, incluso si esta vacia.')
    for cut in cuts:
        integer(cut, 1)
        if cut >= expected['frames']: raise ValueError('Corte fuera de la salida.')
    if len(set(cuts)) != len(cuts): raise ValueError('Hay cortes duplicados.')
    # These are half-open DESTINATION ranges read back from Resolve, not source endFrame.
    spans = plan.get('primary_video_spans')
    if spans is not None:
        if not isinstance(spans, list): raise ValueError('primary_video_spans debe ser una lista.')
        for span in spans:
            integer(span['start']); integer(span['end'], 1)
            if not span['start'] < span['end'] <= expected['frames']:
                raise ValueError('Rango de destino invalido.')
    return fps


def gaps(spans, total):
    """Union of all intended visible video lanes; intentional overlaps are allowed."""
    cursor = 0
    missing = []
    for span in sorted(spans, key=lambda s: (s['start'], s['end'])):
        if span['start'] > cursor: missing.append([cursor, span['start']])
        cursor = max(cursor, span['end'])
    if cursor < total: missing.append([cursor, total])
    return missing


def validate_srt(path, duration):
    text = Path(path).read_text(encoding='utf-8-sig').strip()
    if not text: raise ValueError('SRT vacio.')
    stamp = r'(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})'
    cues, previous_end = [], -1.0
    for block in re.split(r'\n\s*\n', text.replace('\r\n', '\n')):
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit(): raise ValueError('Bloque SRT invalido.')
        match = re.fullmatch(stamp + r'\s+-->\s+' + stamp, lines[1].strip())
        if not match or not ''.join(lines[2:]).strip(): raise ValueError('Tiempo o texto SRT invalido.')
        nums = list(map(int, match.groups()))
        for offset in (0, 4):
            if nums[offset + 1] >= 60 or nums[offset + 2] >= 60: raise ValueError('Reloj SRT invalido.')
        start = nums[0]*3600 + nums[1]*60 + nums[2] + nums[3]/1000
        end = nums[4]*3600 + nums[5]*60 + nums[6] + nums[7]/1000
        if not 0 <= start < end <= duration + 0.05: raise ValueError('Subtitulo fuera de la duracion.')
        if start < previous_end - 0.001: raise ValueError('Subtitulos superpuestos o desordenados.')
        cues.append({'start': start, 'end': end})
        previous_end = end
    return {'cues': len(cues), 'first': cues[0]['start'], 'last': cues[-1]['end'],
            'note': 'Estructura solamente; la IA debe comprobar texto, cobertura de voz y sincronizacion.'}


def ffmpeg_run(executable, args, timeout=900):
    result = subprocess.run([executable, '-hide_banner', '-nostdin', *args],
                            capture_output=True, text=True, errors='replace', timeout=timeout)
    if result.returncode:
        raise RuntimeError('FFmpeg fallo: ' + result.stderr[-1800:])
    return result.stderr


def loudness_summary(log):
    summary = log.rsplit('Summary:', 1)[-1]
    result = {}
    for name, pattern in (
            ('integrated_lufs', r'\bI:\s*([-+\w.]+)\s+LUFS'),
            ('range_lu', r'\bLRA:\s*([-+\w.]+)\s+LU'),
            ('true_peak_dbtp', r'\bPeak:\s*([-+\w.]+)\s+dBFS')):
        match = re.search(pattern, summary)
        if not match: raise ValueError('No se pudo leer la medicion ebur128: ' + name)
        value = float(match[1])
        result[name] = value if math.isfinite(value) else None
    return result


def intervals(indices):
    result = []
    for index in indices:
        if result and result[-1][1] == index: result[-1][1] = index + 1
        else: result.append([index, index + 1])
    return result


def audio_fingerprint(executable, path):
    """Exact decoded PCM identity for reusing neutral review after visual-only changes."""
    import av
    with av.open(str(path)) as media:
        if len(media.streams.audio) != 1: raise ValueError('La comparacion necesita una sola pista de audio.')
        stream = media.streams.audio[0]
        rate, channels = stream.codec_context.sample_rate, len(stream.codec_context.layout.channels)
        start = float(stream.start_time * stream.time_base) if stream.start_time is not None else None
        duration = float(stream.duration * stream.time_base) if stream.duration is not None else None
        layout = stream.codec_context.layout.name
    result = subprocess.run([executable, '-hide_banner', '-nostdin', '-loglevel', 'error', '-i', str(path),
                             '-map', '0:a:0', '-c:a', 'pcm_s32le', '-f', 'hash', '-hash', 'sha256', '-'],
                            capture_output=True, text=True, errors='replace', timeout=900)
    if result.returncode or not re.fullmatch(r'SHA256=[a-fA-F0-9]{64}\s*', result.stdout):
        raise ValueError('No se pudo comprobar la identidad del audio de la revision neutra.')
    return {'sample_rate': rate, 'channels': channels, 'layout': layout,
            'start_seconds': start, 'duration_seconds': duration,
            'pcm_sha256': result.stdout.strip().split('=')[1]}


def scan(project, source, plan_file, output_dir, subtitles=None, evidence=(), neutral_report=None):
    script = require_production(project)
    project = Path(project).expanduser().resolve()
    source = Path(source).expanduser().resolve(strict=True)
    plan_file = Path(plan_file).expanduser().resolve(strict=True)
    plan = load(plan_file)
    fps = validate_plan(plan)
    expected = plan['expected']
    inputs = {'media': binding(source), 'plan': binding(plan_file),
              'script': binding(script), 'brief': binding(script.parent / 'BRIEF-TECNICO.md')}
    if subtitles: inputs['subtitles'] = binding(subtitles)
    if neutral_report: inputs['neutral-report'] = binding(neutral_report)
    for i, path in enumerate(evidence): inputs[f'automation-{i+1}'] = binding(path)
    import av
    import imageio_ffmpeg
    import numpy as np
    # Each run has its own directory. Never reuse stale results or overwrite a source.
    destination = Path(output_dir).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=False)
    findings, artifacts, items = [], [], []

    def finding(kind, severity, detail):
        record = {'id': f'finding-{len(findings)+1}', 'kind': kind,
                  'severity': severity, 'detail': detail}
        findings.append(record)

    def artifact(path):
        artifacts.append(binding(path))

    def item(key, task, paths):
        items.append({'id': key, 'task': task, 'evidence': [str(Path(p).resolve()) for p in paths]})

    # A low-resolution preview can hide typography errors; evidence frames retain full resolution.
    targets = {0, expected['frames']-1}
    targets.update(range(0, expected['frames'], max(1, round(float(fps)*10))))
    for cut in plan['cuts']:
        targets.update((cut-1, cut, min(expected['frames']-1, cut+1)))
    black, missing_pts, pts_errors, count = [], 0, 0, 0
    first_time, previous_time = None, None
    captured = []
    try:
        with av.open(str(source)) as media:
            if len(media.streams.video) != 1:
                raise ValueError('La salida de revision necesita exactamente una pista de video.')
            video = media.streams.video[0]
            width, height = video.width, video.height
            actual_fps = str(video.average_rate) if video.average_rate else None
            audio_count = len(media.streams.audio)
            for frame in media.decode(video=0):
                stamp = float(frame.time) if frame.time is not None else None
                if stamp is None: missing_pts += 1
                else:
                    if first_time is None: first_time = stamp
                    if previous_time is not None and (stamp <= previous_time or abs(stamp-previous_time-1/float(fps)) > max(0.001, 0.1/float(fps))):
                        pts_errors += 1
                    previous_time = stamp
                gray = frame.to_ndarray(format='gray')
                if float(np.mean(gray <= 16)) >= 0.98: black.append(count)
                if count in targets:
                    path = destination / f'frame-{count:08d}.png'
                    frame.to_image().save(path)
                    artifact(path); captured.append(str(path))
                count += 1
                if count % max(1, round(float(fps)*30)) == 0:
                    print(f'QA: {count} fotogramas decodificados...', flush=True)
    except Exception as exc:
        create_json(destination / 'FAILED.json', {'status': 'incomplete', 'error_type': type(exc).__name__})
        raise
    if count != expected['frames']: finding('frame_count', 'blocker', {'expected': expected['frames'], 'actual': count})
    if (width, height) != (expected['width'], expected['height']): finding('dimensions', 'blocker', {'actual': [width, height]})
    if actual_fps is None or abs(float(Fraction(actual_fps))-float(fps)) > 0.001:
        finding('fps', 'blocker', {'expected': str(fps), 'actual': actual_fps})
    if missing_pts or pts_errors: finding('timestamps', 'blocker', {'missing': missing_pts, 'irregular': pts_errors})
    if bool(audio_count) != expected['audio'] or audio_count > 1:
        finding('audio_streams', 'blocker', {'expected_audio': expected['audio'], 'actual': audio_count})
    if black: finding('black_frames', 'warning', {'ranges': intervals(black), 'pixel_threshold': 16, 'ratio': 0.98})
    spans = plan.get('primary_video_spans')
    if spans is None:
        finding('timeline_not_measured', 'blocker', 'Falta primary_video_spans: leer la cobertura de la timeline real.')
    else:
        missing = gaps(spans, expected['frames'])
        if missing: finding('timeline_gaps', 'warning', {'ranges': missing})
    if not count: raise ValueError('No se decodificaron fotogramas.')
    duration = count/float(fps)
    measured, srt = None, None
    if subtitles:
        try: srt = validate_srt(subtitles, duration)
        except ValueError as exc: finding('subtitles_structure', 'blocker', str(exc))
    else:
        finding('srt_not_supplied', 'warning', 'Sin SRT auxiliar; verificar cobertura y texto en el render.')
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    speech = expected.get('speech', expected['audio'])
    if speech:
        if neutral_report is None:
            finding('neutral_review_missing', 'blocker', 'Falta la observacion neutra de Gemini del discurso completo (--neutral-report).')
        else:
            try:
                from gemini_video import VERIFY_SCHEMA, validate_response
                neutral = load(neutral_report)
                if neutral.get('mode') != 'verify' or neutral.get('editorial_context_sent') is not False:
                    raise ValueError('Se necesita verify, no un analisis con guion/brief.')
                validate_response(neutral['analysis'], VERIFY_SCHEMA)
                original = binding(neutral['source_path'])
                if original['sha256'] != neutral['source_sha256']:
                    raise ValueError('El medio enviado a Gemini cambio despues de la verificacion.')
                if original['sha256'] != inputs['media']['sha256']:
                    if audio_fingerprint(ffmpeg, original['path']) != audio_fingerprint(ffmpeg, source):
                        raise ValueError('La verificacion neutra no corresponde al audio completo actual.')
                inputs['neutral-source'] = original
            except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
                finding('neutral_review_invalid', 'blocker', str(exc))
    if audio_count:
        # Decode all audio, measure true peak; a quiet interval is not automatically a speech error.
        log = ffmpeg_run(ffmpeg, ['-i', str(source), '-map', '0:a:0', '-af', 'ebur128=peak=true', '-f', 'null', '-'])
        log_path = destination / 'audio-ebur128.txt'
        log_path.write_text(log, encoding='utf-8')
        artifact(log_path)
        measured = loudness_summary(log)
        if measured['integrated_lufs'] is None:
            finding('silent_audio', 'warning', 'Sonoridad no finita: escuchar y confirmar si el silencio es intencional.')
        if measured['true_peak_dbtp'] is not None and measured['true_peak_dbtp'] >= -0.1:
            finding('true_peak', 'warning', measured)
    units = [('opening', 0), *[(f'cut-{cut}', cut/float(fps)) for cut in sorted(plan['cuts'])], ('ending', duration)]
    for name, center in units:
        start, end = max(0, center-1.5), min(duration, center+1.5)
        path = destination / f'{name}.mp4'
        ffmpeg_run(ffmpeg, ['-loglevel', 'error', '-n', '-i', str(source), '-ss', str(start), '-t', str(end-start),
                            '-map', '0:v:0', '-map', '0:a:0?', '-c:v', 'libx264', '-crf', '18',
                            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', str(path)], timeout=180)
        artifact(path)
        item(name, f'Escuchar y ver {start:.3f}–{end:.3f}s: palabras completas, continuidad, suavidad y sincronizacion. Comparar con la fuente si hay dudas.', [path, source])
    item('full-playback', 'Reproducir TODO el archivo final, incluyendo lo que no aparece en las muestras.', [source])
    item('speech', 'Comprobar tartamudeos, repeticiones, ruido y prosodia por escucha; una transcripcion no basta.', [source])
    if speech:
        item('gemini-and-agent', 'Leer la observacion neutra de Gemini y contrastarla personalmente con todo el audio; resolver discrepancias por escucha.',
             [source, *([neutral_report] if neutral_report else [])])
    item('visuals', 'Verificar encuadres, fundidos sin flashes/doble rostro, texto legible, imagenes unicas y CTA despejada.', [source, *captured])
    item('subtitles', 'Comprobar literalidad, cobertura del discurso, sincronizacion, enfasis y animacion.', [source, *([subtitles] if subtitles else [])])
    item('brief-and-script', 'Contrastar montaje y duracion con guion y brief vigentes; revisar decisiones automaticas.', [source, script, script.parent/'BRIEF-TECNICO.md', plan_file])
    for key, record in inputs.items():
        if key.startswith('automation-'):
            item(key, 'Abrir y revisar este resultado automatico y su aplicacion en el video. No aprobar por el estado del programa.', [record['path'], source])
    for record in findings:
        item(record['id'], f"Resolver {record['kind']}: {record['detail']}", [source])
    # Detect in-place edits during processing, including changes to editorial requirements.
    for record in inputs.values():
        if digest(record['path']) != record['sha256']: raise ValueError('Una entrada cambio durante QA; repetir en otra carpeta.')
    require_production(project)
    report = {'version': 1, 'project_dir': str(project), 'created_at': now(),
              'status': 'blocked' if any(f['severity'] == 'blocker' for f in findings) else 'needs_ai_review',
              'inputs': inputs, 'artifacts': artifacts, 'findings': findings, 'review_items': items,
              'measured': {'frames': count, 'width': width, 'height': height, 'fps': actual_fps,
                           'audio_streams': audio_count, 'duration_seconds': duration, 'first_video_pts': first_time,
                           'audio': measured, 'subtitles': srt},
              'limits': ['No detecta por si solo palabras mutiladas, tartamudeos, ruido molesto ni contenido correcto.',
                         'Las muestras complementan la reproduccion completa; el agente debe observar todos los resultados.',
                         'Los rangos del plan deben provenir de Resolve, no de una estimacion del agente.']}
    report_path = destination / 'report.json'
    create_json(report_path, report)
    template = {'version': 1, 'report_sha256': digest(report_path), 'agent': '', 'model': '',
                'viewed_entire_video': False, 'listened_entire_audio': False,
                'items': [{'id': i['id'], 'verdict': 'pending', 'observation': '', 'evidence': []} for i in items]}
    create_json(destination / 'AI-REVIEW.json', template)
    return report


def gate(project, report_file, review_file, media=None):
    script = require_production(project)
    report_path = Path(report_file).expanduser().resolve(strict=True)
    review_path = Path(review_file).expanduser().resolve(strict=True)
    report, review = load(report_path), load(review_path)
    if report.get('version') != 1 or review.get('version') != 1:
        raise ValueError('Version QA no compatible.')
    if report.get('status') != 'needs_ai_review' or any(f['severity'] == 'blocker' for f in report['findings']):
        raise ValueError('Hay comprobaciones automaticas bloqueadas; corregir y repetir QA.')
    if Path(report['project_dir']).resolve() != Path(project).resolve(): raise ValueError('QA de otro proyecto.')
    if Path(report['inputs']['script']['path']).resolve() != script or Path(report['inputs']['brief']['path']).resolve() != script.parent/'BRIEF-TECNICO.md':
        raise ValueError('Documentos QA ajenos al encargo.')
    if media is not None and Path(report['inputs']['media']['path']).resolve() != Path(media).resolve():
        raise ValueError('QA de otro video.')
    if review.get('report_sha256') != digest(report_path): raise ValueError('La revision corresponde a otro informe QA.')
    bindings = [*report['inputs'].values(), *report['artifacts']]
    allowed = {str(Path(b['path']).resolve()) for b in bindings}
    for record in bindings:
        if digest(record['path']) != record['sha256']:
            raise ValueError('QA desactualizado: cambio medio, documentos o evidencia.')
    if not str(review.get('agent', '')).strip() or not str(review.get('model', '')).strip():
        raise ValueError('Identificar al agente/modelo que realmente reviso.')
    if review.get('viewed_entire_video') is not True or (report['measured']['audio_streams'] and review.get('listened_entire_audio') is not True):
        raise ValueError('Falta reproducir y revisar el video/audio completo.')
    records = review.get('items', [])
    if not isinstance(records, list): raise ValueError('Revision sin items validos.')
    required = {i['id'] for i in report['review_items']}
    if len(records) != len(required) or {r.get('id') for r in records} != required:
        raise ValueError('Faltan revisiones o hay IDs duplicados/ajenos.')
    warnings = {f['id'] for f in report['findings'] if f['severity'] == 'warning'}
    for record in records:
        permitted = ('intentional',) if record['id'] in warnings else ('pass',)
        if record.get('verdict') not in permitted:
            raise ValueError('Revision pendiente o rechazada: ' + record['id'])
        if len(str(record.get('observation', '')).strip()) < 20:
            raise ValueError('Falta una observacion concreta: ' + record['id'])
        evidence = record.get('evidence')
        if not isinstance(evidence, list) or not evidence or any(not isinstance(p, str) or str(Path(p).resolve()) not in allowed for p in evidence):
            raise ValueError('Falta evidencia vinculada: ' + record['id'])
    return {'status': 'agent_review_recorded', 'media': report['inputs']['media'],
            'report_sha256': digest(report_path), 'review_sha256': digest(review_path),
            'note': 'Trazabilidad de la revision, no garantia de cero errores ni aprobacion del usuario para exportar/publicar.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-dir', type=Path, required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('scan')
    check.add_argument('--file', type=Path, required=True)
    check.add_argument('--plan', type=Path, required=True)
    check.add_argument('--output-dir', type=Path, required=True)
    check.add_argument('--subtitles', type=Path)
    check.add_argument('--evidence', type=Path, action='append', default=[])
    check.add_argument('--neutral-report', type=Path)
    ready = sub.add_parser('gate')
    ready.add_argument('--report', type=Path, required=True)
    ready.add_argument('--ai-review', type=Path, required=True)
    ready.add_argument('--file', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'scan':
            result = scan(args.project_dir, args.file, args.plan, args.output_dir, args.subtitles, args.evidence, args.neutral_report)
            print(json.dumps({'status': result['status'], 'report': str(args.output_dir.resolve()/'report.json')}))
            return 2 if result['status'] == 'blocked' else 0
        print(json.dumps(gate(args.project_dir, args.report, args.ai_review, args.file)))
        return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'incomplete', 'error': str(exc)[:1600]}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
