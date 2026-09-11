"""Local project state, script gate and confirmed revisions. No network calls."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import re
from pathlib import Path
import shutil
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
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(content, encoding='utf-8')
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
        raise ValueError('Inicializa el proyecto y pide el guion al usuario antes de llamar APIs o editar.')
    return json.loads(path.read_text(encoding='utf-8'))


def profile_root(override=None):
    return Path(override or os.environ.get('DAVINCI_VIDEO_PRO_HOME', Path.home() / '.davinci-video-pro')).expanduser().resolve()


def meaningful(text):
    if len(text.strip()) < 30 or '{{' in text or 'PENDIENTE_DE_GUION' in text:
        raise ValueError('Falta un guion concreto. Completa el borrador con el usuario; una plantilla vacia no habilita APIs.')


def require_script(project):
    project = Path(project).expanduser().resolve()
    state = read_state(project)
    if (metadata(project) / 'transaction.json').exists():
        raise ValueError('Revision interrumpida: revisa transaction.json y recupera los documentos antes de continuar.')
    script = project / DOCS[0]
    approved = state.get('script_approval') or {}
    if not script.is_file() or not approved.get('confirmation') or approved.get('sha256') != digest(script):
        raise ValueError('No hay guion vigente confirmado. Pidelo al usuario o confirma el borrador; no llames APIs ni edites.')
    meaningful(script.read_text(encoding='utf-8-sig'))
    return script


def update_status(project, state, phase):
    block = ('<!-- davinci-status:start -->\n' +
           f'Fase: {phase}\n\nRevision: {state.get("revision", 0)}\n\n' +
           f'Perfil compartido local: {state["profile_home"]}\n\n' +
           'Leer GUION-CREATIVO.md, BRIEF-TECNICO.md, TAREAS.md y CAMBIOS-PENDIENTES.md al retomar.\n' +
           'Comprobar workflow.py gate antes de editar o consultar servicios.\n<!-- davinci-status:end -->')
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
    for name in DOCS + ('TAREAS.md', 'ESTADO.md', 'CAMBIOS-PENDIENTES.md', 'AGENTS.md', 'CLAUDE.md'):
        if (project / name).exists():
            raise ValueError(f'Ya existe {name}. Conserva su contenido y elige una carpeta nueva para inicializar.')
    shared = profile_root(profile)
    templates = shared / 'templates'
    templates.mkdir(parents=True, exist_ok=True)
    for name in DOCS:
        if not (templates / name).exists():
            shutil.copyfile(ASSETS / name, templates / name)
        shutil.copyfile(templates / name, project / name)
    for folder in ('materiales/videos', 'materiales/audios', 'materiales/marca-y-referencias',
                   'generados/imagenes', 'generados/angulos-omni', 'analisis', 'proyecto-resolve', 'exportaciones'):
        (project / folder).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ASSETS / 'TAREAS.md', project / 'TAREAS.md')
    atomic(project / 'CAMBIOS-PENDIENTES.md', '# Comentarios pendientes\n\nSin comentarios pendientes.\n')
    routing = ('# Edicion con DaVinci Video Pro\n\nPara editar videos usa la skill davinci-video-pro si esta disponible.\n'
               'Primero lee ESTADO.md, GUION-CREATIVO.md, BRIEF-TECNICO.md, TAREAS.md y CAMBIOS-PENDIENTES.md.\n'
               'Antes de editar o llamar cualquier API del flujo, pide el guion y comprueba su confirmacion vigente.\n'
               'El guion es la fuente principal; no reemplaces sus decisiones con el estilo predeterminado.\n'
               'Las revisiones de los dos documentos y las preferencias para futuros videos requieren un resumen confirmado.\n')
    for name in ('AGENTS.md', 'CLAUDE.md'):
        atomic(project / name, routing)
    state = {'version': 2, 'created_at': now(), 'profile_home': str(shared), 'revision': 0,
             'analysis_model': 'gemini-3.8-flash', 'angle_model': 'gemini-omni-1.1-flash',
             'script_approval': None, 'omni_plan': None}
    write_json(metadata(project) / 'project.json', state)
    update_status(project, state, 'Esperando guion del usuario; APIs y edicion pendientes.')
    return {'status': 'initialized', 'project': str(project), 'profile_home': str(shared)}


def confirm_script(project, confirmation):
    if not confirmation.strip():
        raise ValueError('Registra la respuesta real del usuario que entrega o confirma este guion.')
    state = read_state(project)
    path = Path(project) / DOCS[0]
    meaningful(path.read_text(encoding='utf-8-sig'))
    state['script_approval'] = {'sha256': digest(path), 'confirmation': confirmation, 'at': now()}
    write_json(metadata(project) / 'project.json', state)
    update_status(project, state, 'Guion confirmado; comprobar instalacion y preparar el plan de edicion.')
    return {'status': 'script_confirmed', 'sha256': digest(path)}


def stage_revision(project, creative, technical, summary, profile_creative=None, profile_technical=None):
    state = read_state(project)
    if bool(profile_creative) != bool(profile_technical):
        raise ValueError('Para actualizar preferencias generales proporciona ambas plantillas.')
    candidates = [Path(creative), Path(technical)]
    texts = [p.read_text(encoding='utf-8-sig') for p in candidates]
    meaningful(texts[0])
    if not texts[1].strip() or not summary.strip():
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
    history = meta / 'history' / (pending['id'] + '-' + uuid.uuid4().hex[:8])
    history.mkdir(parents=True, exist_ok=False)
    originals = [(target, target.read_text(encoding='utf-8')) for target, _ in targets]
    for index, (target, content) in enumerate(originals):
        atomic(history / f'{index}-{target.name}', content)
    saved_state = json.loads(json.dumps(state))
    write_json(history / 'project-before.json', saved_state)
    write_json(meta / 'transaction.json', {'history': str(history), 'targets': [str(p) for p, _ in targets]})
    try:
        for (target, _), content in zip(targets, texts):
            atomic(target, content)
        state['revision'] += 1
        state['script_approval'] = {'sha256': digest(Path(project) / DOCS[0]), 'confirmation': confirmation, 'at': now()}
        state['last_revision'] = {'id': pending['id'], 'summary': pending['summary'], 'confirmation': confirmation, 'at': now()}
        write_json(meta / 'project.json', state)
        write_json(history / 'confirmed.json', {**pending, 'confirmation': confirmation})
    except Exception:
        for target, content in originals:
            atomic(target, content)
        write_json(meta / 'project.json', saved_state)
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


def set_omni_plan(project, scenes, cost, confirmation):
    require_script(project)
    if scenes < 1 or not math.isfinite(cost) or cost <= 0 or not confirmation.strip():
        raise ValueError('Indica escenas, tope de presupuesto y la autorizacion real del usuario.')
    state = read_state(project)
    state['omni_plan'] = {'max_attempts': scenes, 'budget_usd': cost, 'confirmation': confirmation, 'at': now()}
    write_json(metadata(project) / 'project.json', state)
    return {'status': 'omni_plan_saved', 'plan': state['omni_plan']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-dir', type=Path, required=True)
    sub = p.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init'); init.add_argument('--profile-home', type=Path)
    sub.add_parser('gate'); sub.add_parser('status')
    accept = sub.add_parser('confirm-script'); accept.add_argument('--confirmation', required=True)
    stage = sub.add_parser('stage-revision')
    stage.add_argument('--creative', required=True); stage.add_argument('--technical', required=True)
    stage.add_argument('--summary-file', required=True)
    stage.add_argument('--profile-creative'); stage.add_argument('--profile-technical')
    apply = sub.add_parser('apply-revision'); apply.add_argument('--confirmation', required=True)
    omni = sub.add_parser('omni-plan'); omni.add_argument('--max-attempts', type=int, required=True)
    omni.add_argument('--budget-usd', type=float, required=True); omni.add_argument('--confirmation', required=True)
    a = p.parse_args(); project = a.project_dir.expanduser().resolve()
    try:
        if a.command == 'init': result = init_project(project, a.profile_home)
        elif a.command == 'gate': result = {'script': str(require_script(project)), 'gate': 'passed'}
        elif a.command == 'status': result = read_state(project)
        elif a.command == 'confirm-script': result = confirm_script(project, a.confirmation)
        elif a.command == 'stage-revision':
            result = stage_revision(project, a.creative, a.technical, Path(a.summary_file).read_text(encoding='utf-8-sig'), a.profile_creative, a.profile_technical)
        elif a.command == 'apply-revision': result = apply_revision(project, a.confirmation)
        else: result = set_omni_plan(project, a.max_attempts, a.budget_usd, a.confirmation)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except Exception as exc:
        print(json.dumps({'success': False, 'error': str(exc)}, ensure_ascii=False)); return 1


if __name__ == '__main__':
    sys.exit(main())
