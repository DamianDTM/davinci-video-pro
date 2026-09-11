"""Local media inventory and persistent production choices. No uploads or generation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import uuid
from workflow import atomic, atomic_bytes, digest, metadata, now, require_production, write_json

VIDEO = {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.mxf', '.m4v', '.mts', '.m2ts'}
AUDIO = {'.wav', '.mp3', '.m4a', '.aac', '.flac', '.aiff', '.ogg'}


def inventory(directory, recursive=False):
    directory = Path(directory).expanduser().resolve(strict=True)
    if not directory.is_dir():
        raise ValueError('Indica una carpeta de materiales.')
    candidates = directory.rglob('*') if recursive else directory.iterdir()
    files = []
    for path in candidates:
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(directory):
            continue
        kind = 'video' if path.suffix.lower() in VIDEO else 'audio' if path.suffix.lower() in AUDIO else None
        if kind:
            files.append({'path': str(path.resolve()), 'kind': kind, 'bytes': path.stat().st_size})
    files.sort(key=lambda item: item['path'].casefold())
    return {'directory': str(directory), 'recursive': recursive,
            'files': [{'number': i, **item} for i, item in enumerate(files, 1)],
            'next': 'Preguntar si se usaran todos los videos encontrados o solo cuales. Inventariar no autoriza usarlos ni subirlos.'}


def selected_files(values, allowed):
    if not isinstance(values, list):
        raise ValueError('La seleccion debe ser una lista explicita de rutas.')
    result = []
    for value in values:
        path = Path(value).expanduser()
        if not path.is_absolute():
            raise ValueError('Usa rutas absolutas en la seleccion de materiales.')
        path = path.resolve(strict=True)
        if not path.is_file() or path.suffix.lower() not in allowed:
            raise ValueError('La seleccion contiene un archivo que no es del tipo esperado.')
        if str(path) in result:
            raise ValueError('La seleccion contiene un archivo repetido.')
        result.append(str(path))
    return result


def save_intake(project, answers):
    script = require_production(project)
    videos = selected_files(answers.get('videos'), VIDEO)
    audios = selected_files(answers.get('audios', []), AUDIO)
    if not videos:
        raise ValueError('Selecciona al menos un video del usuario.')
    count = answers.get('output_count')
    if type(count) is not int or count < 1:
        raise ValueError('Pregunta cuantos videos finales desea; debe ser un entero positivo.')
    if type(answers.get('omni')) is not bool:
        raise ValueError('Falta la eleccion sobre escenas Omni.')
    mode = answers.get('images')
    if mode not in ('none', 'provided', 'native', 'openai-api'):
        raise ValueError('Elegir imagenes: none, provided, native u openai-api segun herramientas disponibles.')
    responses = answers.get('user_responses')
    if not isinstance(responses, list) or not responses or not all(isinstance(r, str) and r.strip() for r in responses):
        raise ValueError('Registra las respuestas reales del usuario; no inventes selecciones.')
    outputs = answers.get('outputs')
    if outputs is None and count == 1:
        outputs = [{'id': 'video-01', 'purpose': 'Montaje completo segun el guion elegido', 'videos': videos}]
    if not isinstance(outputs, list) or len(outputs) != count:
        raise ValueError('Define cada video final y que materiales usa; la cantidad debe coincidir con output_count.')
    planned = []
    ids = set()
    for output in outputs:
        name = output.get('id', '')
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', name) or name in ids:
            raise ValueError('Cada salida necesita un id unico sin rutas.')
        ids.add(name)
        sources = selected_files(output.get('videos'), VIDEO)
        if not sources or not set(sources).issubset(videos):
            raise ValueError('Una salida usa videos no incluidos en la seleccion del usuario.')
        purpose = output.get('purpose', '')
        if not isinstance(purpose, str) or not purpose.strip():
            raise ValueError('Explica el objetivo o diferencia de cada video final.')
        planned.append({'id': name, 'purpose': purpose, 'videos': sources})
    if set(videos) != {path for output in planned for path in output['videos']}:
        raise ValueError('Quedan videos seleccionados sin asignar; acuerda su uso o retiralos de la seleccion.')
    record = {'version': 1, 'at': now(), 'videos': videos, 'audios': audios,
              'output_count': count, 'outputs': planned, 'omni': answers['omni'], 'images': mode,
              'image_style': str(answers.get('image_style', 'por acordar')),
              'user_responses': responses, 'script_sha256': digest(script),
              'brief_sha256': digest(script.parent / 'BRIEF-TECNICO.md'),
              'note': 'La seleccion local no autoriza subidas ni generaciones ilimitadas. Omni: un resultado y coste para revisar antes de otra generacion, sin pedir presupuesto.'}
    path = metadata(project) / 'intake.json'
    if path.exists():
        atomic_bytes(metadata(project) / 'intake-history' / (uuid.uuid4().hex + '.json'), path.read_bytes())
    write_json(path, record)
    lines = ['# Encargo de edicion', '', f'Videos finales solicitados: {count}', '',
             f'Guion: {script}', f'Brief tecnico obligatorio: {script.parent / "BRIEF-TECNICO.md"}', '',
             f'Escenas Omni: {"si" if record["omni"] else "no"}', f'Imagenes: {mode}',
             f'Estilo de imagen: {record["image_style"]}', '', '## Materiales seleccionados', '']
    lines += ['- ' + value for value in videos + audios]
    lines += ['', '## Salidas previstas', '']
    for output in planned:
        lines += [f'- [ ] {output["id"]}: {output["purpose"]}',
                  '  Fuentes: ' + ', '.join(output['videos'])]
    lines += ['', 'Actualizar TAREAS.md con revision, export y evidencia para cada salida.',
              'No marcar el encargo completo hasta entregar todos los videos solicitados.',
              'Si cambian guion o brief, revisar este plan sin repetir preguntas ya respondidas.', '', record['note'], '']
    atomic(Path(project) / 'ENCARGO.md', '\n'.join(lines))
    return {'status': 'intake_saved', 'path': str(path), 'summary': str(Path(project).resolve() / 'ENCARGO.md'),
            'output_count': count}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    scan = sub.add_parser('inventory'); scan.add_argument('--directory', type=Path, default=Path.cwd())
    scan.add_argument('--recursive', action='store_true')
    save = sub.add_parser('save'); save.add_argument('--project-dir', type=Path, required=True)
    save.add_argument('--answers', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = inventory(args.directory, args.recursive) if args.command == 'inventory' else save_intake(
            args.project_dir, json.loads(args.answers.read_text(encoding='utf-8-sig')))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, TypeError, AttributeError) as exc:
        print(json.dumps({'success': False, 'error': str(exc)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
