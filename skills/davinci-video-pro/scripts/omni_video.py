"""One bounded Omni alternate-angle generation, gated by the user's script and plan."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time
from workflow import require_production, read_state, metadata, write_json, digest, now


def reserve(project, scene, source, prompt, estimate):
    script = require_production(project)
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', scene):
        raise ValueError('Usa un identificador de escena sencillo, sin rutas.')
    state = read_state(project)
    plan = state.get('omni_plan')
    if not plan or not plan.get('confirmation'):
        raise ValueError('Falta un plan de escenas y presupuesto autorizado para Omni.')
    if not math.isfinite(estimate) or estimate <= 0:
        raise ValueError('Indica una estimacion conservadora segun las tarifas vigentes.')
    ledger = metadata(project) / 'omni-attempts'
    ledger.mkdir(parents=True, exist_ok=True)
    existing = [json.loads(p.read_text(encoding='utf-8')) for p in ledger.glob('*.json')]
    fingerprint = hashlib.sha256((digest(source) + prompt + state['angle_model']).encode()).hexdigest()
    if any(x.get('fingerprint') == fingerprint or x['scene'] == scene for x in existing):
        raise ValueError('Esta escena ya tiene un intento. Revisa el resultado; no se reintenta automaticamente.')
    if len(existing) >= plan['max_attempts'] or sum(x['reserved_usd'] for x in existing) + estimate > plan['budget_usd'] + 1e-9:
        raise ValueError('El intento excede el plan autorizado. No se llamo a Google.')
    record = {'scene': scene, 'fingerprint': fingerprint, 'reserved_usd': estimate,
              'status': 'reserved', 'created_at': now(), 'model': state['angle_model'],
              'source_sha256': digest(source), 'script_sha256': digest(script),
              'brief_sha256': digest(script.parent / 'BRIEF-TECNICO.md')}
    path = ledger / (scene + '.json')
    with path.open('x', encoding='utf-8') as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
    return path, record


def generate(args):
    script = require_production(args.project_dir)
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', args.scene):
        raise ValueError('Identificador de escena no valido.')
    if not args.upload_to_google:
        raise ValueError('El usuario debe autorizar enviar este fragmento a Google; despues usa --upload-to-google.')
    source = args.file.expanduser().resolve(strict=True)
    if source.suffix.lower() != '.mp4':
        raise ValueError('Prepara un fragmento MP4 de cuatro segundos para esta ruta comprobada.')
    # Probe locally before spending or reserving an attempt.
    import av
    with av.open(str(source)) as media:
        if not media.streams.video or media.duration is None or not 3.8 <= media.duration / av.time_base <= 4.3:
            raise ValueError('Este helper requiere un fragmento de aproximadamente cuatro segundos.')
    prompt = args.prompt_file.read_text(encoding='utf-8-sig').strip()
    if len(prompt) < 30 or len(prompt) > 12000:
        raise ValueError('Prepara un prompt concreto, derivado del guion, de 30 a 12000 caracteres.')
    # The agent writes the scene prompt from the approved script; retain traceability.
    target = Path(args.project_dir).resolve() / 'generados' / 'angulos-omni' / (args.scene + '.mp4')
    if target.exists():
        raise ValueError('Ya existe el video destino. Se conserva.')
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = metadata(args.project_dir) / 'omni.lock'
    with lock.open('x', encoding='utf-8') as stream:
        stream.write('Un intento a la vez. Si se interrumpe, revisar su estado antes de retirar este bloqueo.')
    record_path = None; record = None; remote = None; key = ''
    try:
        from gemini_video import client_for, read_key, types, sdk_problem
        problem = sdk_problem()
        if problem:
            raise ValueError(problem)
        key = read_key()
        record_path, record = reserve(args.project_dir, args.scene, source, prompt, args.estimated_usd)
        target.with_suffix('.prompt.txt').write_text(prompt, encoding='utf-8')
        with client_for(key) as client:
            try:
                remote = client.files.upload(file=source, config=types.UploadFileConfig(mime_type='video/mp4', display_name='Authorized alternate-angle clip'))
                deadline = time.monotonic() + 300
                while not remote.state or remote.state.name != 'ACTIVE':
                    if remote.state and remote.state.name == 'FAILED': raise RuntimeError('Google no pudo procesar el fragmento.')
                    if time.monotonic() > deadline: raise TimeoutError('El fragmento no estuvo disponible en cinco minutos.')
                    time.sleep(5); remote = client.files.get(name=remote.name)
                require_production(args.project_dir)
                record['status'] = 'generation_requested'; write_json(record_path, record)
                response = client.interactions.create(model=record['model'], store=False, background=False,
                    input=[{'type': 'video', 'uri': remote.uri, 'mime_type': 'video/mp4'}, {'type': 'text', 'text': prompt}],
                    response_format={'type': 'video', 'aspect_ratio': args.aspect_ratio, 'resolution': '720p', 'duration': '4s'})
                record['interaction_id'] = getattr(response, 'id', None)
                record['usage'] = response.usage.model_dump(mode='json') if response.usage else None
                video = response.output_video
                if response.status != 'completed' or not video or not video.data:
                    raise RuntimeError('La respuesta no incluye un video completo. No se reintentara automaticamente.')
                content = base64.b64decode(video.data, validate=True)
                if b'ftyp' not in content[:48]: raise ValueError('La respuesta no parece un MP4.')
                with target.open('xb') as stream: stream.write(content)
                record.update(status='completed', output=str(target), bytes=len(content),
                              needs_visual_review=True, original_audio_must_be_restored=True)
                write_json(record_path, record)
            finally:
                if remote and remote.name:
                    try:
                        client.files.delete(name=remote.name)
                        record['remote_input_deleted'] = True
                    except Exception:
                        record['remote_input_deleted'] = False
                        record['cleanup_file_name'] = remote.name
                        print('No se pudo retirar la entrada temporal de Google. Revisa el registro.', file=sys.stderr)
                    write_json(record_path, record)
        return {'status': 'completed_needs_review', 'file': str(target), 'script': str(script), 'record': str(record_path)}
    except Exception as exc:
        if record_path:
            record.update(status='failed_or_uncertain', error_type=type(exc).__name__)
            write_json(record_path, record)
        # Do not echo arbitrary SDK errors, key material or base64 media.
        detail = sdk_problem() if 'sdk_problem' in locals() else None
        raise RuntimeError(detail or f'Omni no termino: {type(exc).__name__}. Revisa el intento guardado antes de otra generacion.') from None
    finally:
        lock.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-dir', type=Path, required=True)
    p.add_argument('--file', type=Path, required=True); p.add_argument('--scene', required=True)
    p.add_argument('--prompt-file', type=Path, required=True)
    p.add_argument('--estimated-usd', type=float, required=True)
    p.add_argument('--aspect-ratio', choices=('9:16', '16:9'), default='9:16')
    p.add_argument('--upload-to-google', action='store_true')
    a = p.parse_args()
    try:
        print(json.dumps(generate(a), ensure_ascii=False, indent=2)); return 0
    except Exception as exc:
        print(json.dumps({'success': False, 'error': str(exc)}, ensure_ascii=False)); return 1


if __name__ == '__main__':
    sys.exit(main())
