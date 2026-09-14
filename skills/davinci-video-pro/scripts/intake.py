"""Local video, audio and visual-source inventory. No rendering, uploads or generation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import uuid
from workflow import atomic, atomic_bytes, digest, metadata, now, require_production, write_json

VIDEO = {'.mp4', '.mov', '.mkv', '.avi', '.webm', '.mxf', '.m4v', '.mts', '.m2ts'}
AUDIO = {'.wav', '.mp3', '.m4a', '.aac', '.flac', '.aiff', '.ogg'}
IMAGE = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.tif', '.tiff', '.bmp', '.svg'}
HTML = {'.html', '.htm', '.xhtml'}
PDF = {'.pdf'}
DOCUMENT = {'.doc', '.docx', '.odt', '.rtf', '.txt', '.md', '.ppt', '.pptx', '.odp'}
SUPPORT = IMAGE | HTML | PDF | DOCUMENT


def file_kind(path):
    suffix = Path(path).suffix.lower()
    for kind, extensions in (('video', VIDEO), ('audio', AUDIO), ('image', IMAGE),
                             ('html', HTML), ('pdf', PDF), ('document', DOCUMENT)):
        if suffix in extensions:
            return kind
    return None


def inventory(directory, recursive=False):
    directory = Path(directory).expanduser().resolve(strict=True)
    if not directory.is_dir():
        raise ValueError('Indica una carpeta de materiales.')
    candidates = directory.rglob('*') if recursive else directory.iterdir()
    files = []
    for path in candidates:
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(directory):
            continue
        kind = file_kind(path)
        if kind:
            files.append({'path': str(path.resolve()), 'kind': kind, 'bytes': path.stat().st_size})
    files.sort(key=lambda item: item['path'].casefold())
    return {'directory': str(directory), 'recursive': recursive,
            'files': [{'number': i, **item} for i, item in enumerate(files, 1)],
            'next': 'Preguntar todos o cuales videos y recursos de apoyo se usaran. HTML/PDF/documentos son candidatos visuales; inventariar no los abre, selecciona ni sube.'}


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
    support_files = selected_files(answers.get('support_files', []), SUPPORT)
    music = answers.get('music', {'mode': 'undecided', 'files': []})
    if not isinstance(music, dict) or music.get('mode') not in ('none', 'provided', 'undecided'):
        raise ValueError('Elegir musica: none, provided o undecided si falta la respuesta.')
    music_files = selected_files(music.get('files', []), AUDIO)
    if bool(music_files) != (music['mode'] == 'provided'):
        raise ValueError('Musica provided requiere pistas elegidas; none/undecided no pueden incluirlas.')
    music = {'mode': music['mode'], 'files': music_files}
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
        publication = output.get('publication', {})
        if (not isinstance(publication, dict) or set(publication) - {'title', 'description'}
                or not all(isinstance(value, str) for value in publication.values())):
            raise ValueError('publication admite title y description de texto del usuario; no es una autorizacion.')
        planned.append({'id': name, 'purpose': purpose, 'videos': sources, 'publication': publication})
    if set(videos) != {path for output in planned for path in output['videos']}:
        raise ValueError('Quedan videos seleccionados sin asignar; acuerda su uso o retiralos de la seleccion.')
    record = {'version': 2, 'at': now(), 'videos': videos, 'audios': audios, 'support_files': support_files,
              'output_count': count, 'outputs': planned, 'omni': answers['omni'], 'images': mode, 'music': music,
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
    lines += ['', '## Recursos de apoyo aportados', '']
    lines += [f'- [{file_kind(value)}] {value}' for value in support_files] or ['Sin archivos de apoyo seleccionados.']
    if support_files:
        lines += ['', 'Abrir y revisar informacion y apariencia; HTML con su CSS real y captura visual.',
                  'Registrar en RECURSOS.md la fuente, pagina/seccion, captura, frase y tiempos del montaje corregido.',
                  'Insertar lo pertinente con diseno fiel y resaltado legible. Esta lista no demuestra revision ni obliga a usarlo todo.']
    lines += ['', '## Musica opcional', '', 'Eleccion: ' + music['mode']]
    lines += ['- ' + value for value in music_files]
    if music['mode'] == 'undecided':
        lines += ['Preguntar si quiere aportar un MP3/carpeta de canciones o seguir sin musica.']
    lines += ['', 'La voz corregida puede continuar en off sobre documentos e imagenes.']
    lines += ['', '## Salidas previstas', '']
    for output in planned:
        lines += [f'- [ ] {output["id"]}: {output["purpose"]}',
                  '  Fuentes: ' + ', '.join(output['videos'])]
        if output['publication']:
            lines += ['', 'Textos aportados para publicacion (sin permiso de envio implicito):',
                      'Titulo:', output['publication'].get('title', '(pendiente si se publica)'),
                      'Descripcion:', output['publication'].get('description', '(pendiente si se publica)'), '']
    lines += ['', 'Actualizar TAREAS.md con revision, export y evidencia para cada salida.',
              'Mostrar como reproducir cada montaje y esperar validacion antes del export final.',
              'Al cerrar preguntar si desea publicar en redes. Pedir solo titulos/descripciones que falten.',
              'Registrar cuentas, textos, autorizacion y estado remoto en PUBLICACION.md; no publicar por este registro.',
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
