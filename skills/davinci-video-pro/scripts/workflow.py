"""Local project state, script/brief requirements and confirmed revisions. No network calls."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import sys
import uuid
from datetime import datetime, timezone

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
DOCS = ('GUION-CREATIVO.md', 'BRIEF-TECNICO.md')


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic(path, content):
    # New text has the same bytes on Windows and Unix.
    atomic_bytes(path, content.replace('\r\n', '\n').replace('\r', '\n').encode('utf-8'))


def atomic_bytes(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_bytes(content)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_json(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def metadata(project):
    return Path(project).expanduser().resolve() / '.davinci-video-pro'


def read_state(project):
    path = metadata(project) / 'project.json'
    if not path.is_file():
        raise ValueError('Inicializa el encargo y elige guion y brief tecnico antes de analizar, generar o editar.')
    return json.loads(path.read_text(encoding='utf-8'))


def profile_root(override=None):
    return Path(override or os.environ.get('DAVINCI_VIDEO_PRO_HOME', Path.home() / '.davinci-video-pro')).expanduser().resolve()


def meaningful(text):
    if len(text.strip()) < 30 or '{{' in text or 'PENDIENTE_DE_GUION' in text:
        raise ValueError('El documento esta vacio o incompleto. Completarlo o usar el predeterminado antes de producir.')


def require_script(project):
    project = Path(project).expanduser().resolve()
    state = read_state(project)
    if (metadata(project) / 'transaction.json').exists():
        raise ValueError('Revision interrumpida: revisa transaction.json y recupera los documentos antes de continuar.')
    script = project / DOCS[0]
    approved = state.get('script_approval') or {}
    if not script.is_file() or not approved.get('confirmation') or approved.get('sha256') != digest(script):
        raise ValueError('No hay guion vigente confirmado. Recibe el propio o usa use-default-script con la respuesta real (incluso no tengo guion) antes de producir.')
    meaningful(script.read_text(encoding='utf-8-sig'))
    return script


def require_brief(project):
    project = Path(project).expanduser().resolve()
    state = read_state(project)
    path = project / DOCS[1]
    approved = state.get('brief_approval') or {}
    if not path.is_file() or not approved.get('confirmation') or approved.get('sha256') != digest(path):
        raise ValueError('Falta elegir y leer un brief tecnico vigente. Muestra su ruta, recibe la eleccion del usuario y registra confirm-brief antes de producir.')
    meaningful(path.read_text(encoding='utf-8-sig'))
    return path


def require_production(project):
    script = require_script(project)
    require_brief(project)
    return script


def confirm_brief(project, confirmation, source='user'):
    if not confirmation.strip():
        raise ValueError('Registra la eleccion real del brief tecnico por el usuario.')
    state = read_state(project)
    path = Path(project) / DOCS[1]
    meaningful(path.read_text(encoding='utf-8-sig'))
    if (metadata(project) / 'transaction.json').exists():
        raise ValueError('Recupera la revision interrumpida antes de confirmar el brief.')
    state['brief_approval'] = {'sha256': digest(path), 'confirmation': confirmation, 'at': now(), 'source': source}
    write_json(metadata(project) / 'project.json', state)
    update_status(project, state, 'Brief tecnico elegido; completar el encargo y comprobar gate antes de producir.')
    return {'status': 'brief_confirmed', 'brief': str(path.resolve()), 'sha256': digest(path)}


def document_paths(project):
    project = Path(project).expanduser().resolve()
    state = read_state(project)
    preview = project / 'GUION-POR-DEFECTO.md'
    if not preview.exists():
        text = (ASSETS / preview.name).read_text(encoding='utf-8-sig')
        template = Path(state['profile_home']) / 'templates' / DOCS[0]
        preferences = re.search(r'^## Preferencias creativas reutilizables\s*\n(.*?)(?=^## |\Z)',
                                template.read_text(encoding='utf-8-sig'), re.M | re.S)
        if preferences and preferences.group(1).strip():
            text += '\n## Preferencias creativas del perfil\n\n' + preferences.group(1).strip() + '\n'
        atomic(preview, text)
    return {'script': str(project / DOCS[0]), 'default_script_editable': str(preview),
            'technical_brief_editable': str(project / DOCS[1])}


def update_status(project, state, phase):
    block = ('<!-- davinci-status:start -->\n' +
           f'Fase: {phase}\n\nRevision: {state.get("revision", 0)}\n\n' +
           f'Perfil compartido local: {state["profile_home"]}\n\n' +
           'Leer GUION-CREATIVO.md, BRIEF-TECNICO.md, TAREAS.md y CAMBIOS-PENDIENTES.md al retomar.\n' +
           'Leer ENCARGO.md si existe. Comprobar workflow.py gate antes de analizar, generar o editar.\n<!-- davinci-status:end -->')
    path = Path(project) / 'ESTADO.md'
    if path.exists():
        current = path.read_text(encoding='utf-8')
        pattern = r'<!-- davinci-status:start -->.*?<!-- davinci-status:end -->'
        content = re.sub(pattern, lambda _: block, current, flags=re.S) if re.search(pattern, current, re.S) else current + '\n\n' + block
    else:
        content = '# Estado del proyecto\n\n' + block + '\n\n## Registro de configuracion y avance\n\nGuardar aqui versiones, rutas, evidencias y siguiente paso sin secretos.\n'
    atomic(path, content)


def init_project(project, profile=None):
    project = Path(project).expanduser().resolve()
    if (metadata(project) / 'project.json').exists():
        return {'status': 'existing', 'project': str(project), 'state': read_state(project)}
    project.mkdir(parents=True, exist_ok=True)
    for name in DOCS + ('GUION-POR-DEFECTO.md', 'TAREAS.md', 'ESTADO.md', 'CAMBIOS-PENDIENTES.md', 'AGENTS.md', 'CLAUDE.md'):
        if (project / name).exists():
            raise ValueError(f'Ya existe {name}. Conserva su contenido y elige una carpeta nueva para inicializar.')
    shared = profile_root(profile)
    templates = shared / 'templates'
    templates.mkdir(parents=True, exist_ok=True)
    for name in DOCS:
        if not (templates / name).exists():
            atomic(templates / name, (ASSETS / name).read_text(encoding='utf-8-sig'))
        atomic(project / name, (templates / name).read_text(encoding='utf-8-sig'))
    for folder in ('materiales/videos', 'materiales/audios', 'materiales/marca-y-referencias',
                   'generados/imagenes', 'generados/angulos-omni', 'analisis', 'proyecto-resolve', 'exportaciones'):
        (project / folder).mkdir(parents=True, exist_ok=True)
    atomic(project / 'TAREAS.md', (ASSETS / 'TAREAS.md').read_text(encoding='utf-8-sig'))
    atomic(project / 'CAMBIOS-PENDIENTES.md', '# Comentarios pendientes\n\nSin comentarios pendientes.\n')
    routing = ('# Edicion con DaVinci Video Pro\n\nPara editar videos usa la skill davinci-video-pro si esta disponible.\n'
               'Primero lee ESTADO.md, GUION-CREATIVO.md, BRIEF-TECNICO.md, TAREAS.md y CAMBIOS-PENDIENTES.md.\n'
               'Primero instalacion/conexion; despues materiales, numero y duracion de salidas, brief, guion y recursos opcionales.\n'
               'Preguntar por HTML/CSS, PDF/documentos y musica MP3/carpeta; pueden omitirse.\n'
               'HTML: abrir, capturar su diseno real y sincronizar resaltados con la voz corregida.\n'
               'Las pruebas tecnicas de conexion no requieren guion. Producir requiere guion y brief tecnico vigente.\n'
               'El brief tecnico es obligatorio: leerlo y aplicar todos sus criterios durante montaje y QA.\n'
               'Mostrar siempre las rutas absolutas editables de guion y brief. Leer ENCARGO.md si existe.\n'
               'Si dice no tengo guion o hazlo con el de defecto, usar use-default-script sin preguntar otra vez.\n'
               'Registrar confirm-brief y comprobar workflow.py gate; si pasa, retomar sin repetir preguntas.\n'
               'El guion es la fuente principal; no reemplaces sus decisiones con el estilo predeterminado.\n'
               'Omni: limpiar y revisar imagen/voz antes de generar, tambien para muestras; no usar el clip bruto.\n'
               'Omni: no pedir presupuesto; generar uno, mostrar video y coste, esperar decision antes del siguiente.\n'
               'Mostrar proyecto/timeline y como reproducir cada montaje; esperar visto bueno antes del export final.\n'
               'Al cerrar preguntar por publicacion opcional en redes y usar titulo/descripcion del brief o pedirlos.\n'
               'Publicar solo el contenido y destinos autorizados con acceso real; leer PUBLICACION.md para no duplicar subidas.\n'
               'Las revisiones de los dos documentos y las preferencias para futuros videos requieren un resumen confirmado.\n')
    for name in ('AGENTS.md', 'CLAUDE.md'):
        atomic(project / name, routing)
    state = {'version': 2, 'created_at': now(), 'profile_home': str(shared), 'revision': 0,
             'analysis_model': 'gemini-3.8-flash', 'angle_model': 'gemini-omni-1.1-flash',
             'script_approval': None, 'brief_approval': None, 'omni_plan': None}
    write_json(metadata(project) / 'project.json', state)
    document_paths(project)
    update_status(project, state, 'Completar instalacion y recepcion: materiales, salidas, brief, guion y recursos.')
    return {'status': 'initialized', 'project': str(project), 'profile_home': str(shared)}


def confirm_script(project, confirmation, source='user'):
    if not confirmation.strip():
        raise ValueError('Registra la respuesta real del usuario que entrega o confirma este guion.')
    state = read_state(project)
    path = Path(project) / DOCS[0]
    meaningful(path.read_text(encoding='utf-8-sig'))
    state['script_approval'] = {'sha256': digest(path), 'confirmation': confirmation, 'at': now(), 'source': source}
    write_json(metadata(project) / 'project.json', state)
    update_status(project, state, 'Guion elegido; completar brief y encargo, comprobar gate y preparar el montaje.')
    return {'status': 'script_confirmed', 'sha256': digest(path)}


def use_default_script(project, confirmation):
    if not confirmation.strip():
        raise ValueError('Registra la peticion real de usar el guion por defecto.')
    project = Path(project).expanduser().resolve()
    state = read_state(project)
    meta = metadata(project)
    if (meta / 'transaction.json').exists() or (meta / 'pending').exists():
        raise ValueError('Hay una revision pendiente; resuelvela antes de seleccionar otro guion.')
    approval = state.get('script_approval') or {}
    if approval.get('source') == 'default':
        require_script(project)
        return {'status': 'default_already_selected', 'script': str(project / DOCS[0])}
    path = project / DOCS[0]
    original = path.read_bytes()
    if 'PENDIENTE_DE_GUION' not in original.decode('utf-8-sig') or approval:
        raise ValueError('Ya existe un guion propio. Conserva su contenido y prepara una revision para cambiarlo.')
    text = Path(document_paths(project)['default_script_editable']).read_text(encoding='utf-8-sig')
    meaningful(text)
    state_before = (meta / 'project.json').read_bytes()
    try:
        atomic(path, text)
        confirm_script(project, confirmation, source='default')
    except Exception:
        atomic_bytes(path, original)
        atomic_bytes(meta / 'project.json', state_before)
        raise
    return {'status': 'default_script_selected', 'script': str(path), 'sha256': digest(path)}


def stage_revision(project, creative, technical, summary, profile_creative=None, profile_technical=None):
    state = read_state(project)
    if bool(profile_creative) != bool(profile_technical):
        raise ValueError('Para actualizar preferencias generales proporciona ambas plantillas.')
    candidates = [Path(creative), Path(technical)]
    texts = [p.read_text(encoding='utf-8-sig') for p in candidates]
    meaningful(texts[0])
    meaningful(texts[1])
    if not summary.strip():
        raise ValueError('Faltan el brief tecnico o el resumen para el usuario.')
    revision = metadata(project) / 'pending'
    if revision.exists():
        raise ValueError('Ya hay una revision pendiente. Revisala o archivala antes de preparar otra.')
    profile_texts = None
    if profile_creative:
        profile_texts = [Path(p).read_text(encoding='utf-8-sig') for p in (profile_creative, profile_technical)]
        if 'PENDIENTE_DE_GUION' not in profile_texts[0]:
            raise ValueError('La plantilla general debe conservar PENDIENTE_DE_GUION; no heredar el contenido de este video.')
    revision.mkdir(parents=True)
    baseline = {name: digest(Path(project) / name) for name in DOCS}
    for name, content in zip(DOCS, texts):
        atomic(revision / name, content)
    shared = Path(state['profile_home']) / 'templates'
    profile_baseline = {name: digest(shared / name) for name in DOCS} if profile_texts else None
    if profile_texts:
        for name, content in zip(DOCS, profile_texts):
            atomic(revision / 'templates' / name, content)
    pending = {'id': uuid.uuid4().hex, 'summary': summary, 'baseline': baseline,
               'profile_baseline': profile_baseline, 'created_at': now()}
    write_json(revision / 'revision.json', pending)
    atomic(Path(project) / 'CAMBIOS-PENDIENTES.md', '# Resumen por confirmar\n\n' + summary + '\n\nEstado: pendiente de confirmacion del usuario.\n')
    return {'status': 'awaiting_confirmation', **pending}


def apply_revision(project, confirmation):
    if not confirmation.strip():
        raise ValueError('Se necesita la respuesta real que confirma el resumen; el silencio no es confirmacion.')
    state = read_state(project)
    meta = metadata(project)
    pending_dir = meta / 'pending'
    pending = json.loads((pending_dir / 'revision.json').read_text(encoding='utf-8'))
    targets = [(Path(project) / name, pending_dir / name) for name in DOCS]
    for target, _ in targets:
        if digest(target) != pending['baseline'][target.name]:
            raise ValueError('Los documentos cambiaron despues del resumen. Preparar un resumen actualizado.')
    if pending['profile_baseline']:
        for name in DOCS:
            target = Path(state['profile_home']) / 'templates' / name
            if digest(target) != pending['profile_baseline'][name]:
                raise ValueError('Otro proyecto actualizo las preferencias. Revisar los cambios antes de confirmar.')
            targets.append((target, pending_dir / 'templates' / name))
    texts = [source.read_text(encoding='utf-8-sig') for _, source in targets]
    meaningful(texts[0])
    meaningful(texts[1])
    history = meta / 'history' / (pending['id'] + '-' + uuid.uuid4().hex[:8])
    history.mkdir(parents=True, exist_ok=False)
    originals = [(target, target.read_bytes()) for target, _ in targets]
    for index, (target, content) in enumerate(originals):
        atomic_bytes(history / f'{index}-{target.name}', content)
    saved_state = (meta / 'project.json').read_bytes()
    atomic_bytes(history / 'project-before.json', saved_state)
    write_json(meta / 'transaction.json', {'history': str(history), 'targets': [str(p) for p, _ in targets]})
    try:
        for (target, _), content in zip(targets, texts):
            atomic(target, content)
        state['revision'] += 1
        state['script_approval'] = {'sha256': digest(Path(project) / DOCS[0]), 'confirmation': confirmation, 'at': now()}
        state['brief_approval'] = {'sha256': digest(Path(project) / DOCS[1]), 'confirmation': confirmation, 'at': now()}
        state['last_revision'] = {'id': pending['id'], 'summary': pending['summary'], 'confirmation': confirmation, 'at': now()}
        write_json(meta / 'project.json', state)
        write_json(history / 'confirmed.json', {**pending, 'confirmation': confirmation})
    except Exception:
        for target, content in originals:
            atomic_bytes(target, content)
        atomic_bytes(meta / 'project.json', saved_state)
        (meta / 'transaction.json').unlink(missing_ok=True)
        raise
    (meta / 'transaction.json').unlink()
    archive_target = history / 'proposed'
    if pending_dir.resolve().parent != meta.resolve() or archive_target.resolve().parent != history.resolve():
        raise ValueError('Las rutas de archivo no permanecen dentro del proyecto.')
    pending_dir.rename(archive_target)
    atomic(Path(project) / 'CAMBIOS-PENDIENTES.md', '# Comentarios pendientes\n\nRevision confirmada y aplicada.\n')
    update_status(project, state, 'Revision confirmada. Retomar las tareas de edicion y verificacion pendientes.')
    return {'status': 'revision_applied', 'revision': state['revision'], 'profile_updated': bool(pending['profile_baseline'])}


def omni_attempts(project):
    return [json.loads(p.read_text(encoding='utf-8'))
            for p in sorted((metadata(project) / 'omni-attempts').glob('*.json'))]


def authorize_omni_next(project, confirmation, reviewed_scene=None, retry_of=None):
    """Record an actual user choice for one attempt, without asking for a budget."""
    require_production(project)
    if not confirmation.strip():
        raise ValueError('Registra la respuesta real que pide usar Omni o continuar tras ver el resultado y coste.')
    if (metadata(project) / 'omni.lock').exists():
        raise ValueError('Hay un intento en curso o interrumpido. Revisarlo antes de continuar.')
    attempts = omni_attempts(project)
    previous = max(attempts, key=lambda x: x['created_at']) if attempts else None
    if previous:
        if previous['status'] not in ('completed', 'failed_or_uncertain'):
            raise ValueError('El intento anterior no esta resuelto. Consultar su estado sin volver a generarlo.')
        if reviewed_scene != previous['scene']:
            raise ValueError('Muestra el resultado y coste anterior, espera la decision y registra --reviewed-scene.')
    elif reviewed_scene:
        raise ValueError('No hay una escena anterior para revisar.')
    if retry_of and retry_of != reviewed_scene:
        raise ValueError('Un reintento debe referirse al resultado que acaba de revisar el usuario.')
    state = read_state(project)
    state['omni_approval'] = {'id': uuid.uuid4().hex, 'confirmation': confirmation, 'at': now(),
                              'reviewed_scene': reviewed_scene, 'retry_of': retry_of,
                              'previous_scenes': sorted(x['scene'] for x in attempts)}
    write_json(metadata(project) / 'project.json', state)
    return {'status': 'one_omni_attempt_authorized', 'approval': state['omni_approval']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-dir', type=Path, required=True)
    sub = p.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init'); init.add_argument('--profile-home', type=Path)
    sub.add_parser('gate'); sub.add_parser('status'); sub.add_parser('documents')
    accept = sub.add_parser('confirm-script'); accept.add_argument('--confirmation', required=True)
    default = sub.add_parser('use-default-script'); default.add_argument('--confirmation', required=True)
    brief = sub.add_parser('confirm-brief'); brief.add_argument('--confirmation', required=True)
    brief.add_argument('--source', choices=('user', 'default'), default='user')
    stage = sub.add_parser('stage-revision')
    stage.add_argument('--creative', required=True); stage.add_argument('--technical', required=True)
    stage.add_argument('--summary-file', required=True)
    stage.add_argument('--profile-creative'); stage.add_argument('--profile-technical')
    apply = sub.add_parser('apply-revision'); apply.add_argument('--confirmation', required=True)
    omni = sub.add_parser('omni-next'); omni.add_argument('--confirmation', required=True)
    omni.add_argument('--reviewed-scene'); omni.add_argument('--retry-of')
    a = p.parse_args(); project = a.project_dir.expanduser().resolve()
    try:
        if a.command == 'init': result = init_project(project, a.profile_home)
        elif a.command == 'gate': result = {'script': str(require_production(project)), 'brief': str(require_brief(project)), 'gate': 'passed'}
        elif a.command == 'status': result = read_state(project)
        elif a.command == 'documents': result = document_paths(project)
        elif a.command == 'confirm-script': result = confirm_script(project, a.confirmation)
        elif a.command == 'use-default-script': result = use_default_script(project, a.confirmation)
        elif a.command == 'confirm-brief': result = confirm_brief(project, a.confirmation, a.source)
        elif a.command == 'stage-revision':
            result = stage_revision(project, a.creative, a.technical, Path(a.summary_file).read_text(encoding='utf-8-sig'), a.profile_creative, a.profile_technical)
        elif a.command == 'apply-revision': result = apply_revision(project, a.confirmation)
        else: result = authorize_omni_next(project, a.confirmation, a.reviewed_scene, a.retry_of)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except Exception as exc:
        print(json.dumps({'success': False, 'error': str(exc)}, ensure_ascii=False)); return 1


if __name__ == '__main__':
    sys.exit(main())
