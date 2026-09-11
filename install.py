"""Install the portable skill locally for Codex or Claude Code. No APIs or downloads."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from datetime import datetime, timezone
import uuid

NAME = 'davinci-video-pro'
SOURCE = Path(__file__).resolve().parent / 'skills' / NAME


def files(root):
    result = {}
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('No se instalan arboles con enlaces simbolicos.')
        if path.is_file() and '__pycache__' not in path.parts and not path.name.endswith('.pyc'):
            result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def install(root, update=False):
    root = Path(root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    target = root / NAME
    if target.is_symlink():
        raise ValueError('El destino es un enlace. Revisa esa instalacion antes de actualizar.')
    source_files = files(SOURCE)
    if target.exists() and files(target) == source_files:
        return {'status': 'already_installed', 'path': str(target)}
    if target.exists() and not update:
        raise ValueError('Hay otra version. Revisa sus cambios y usa --update para conservar una copia y actualizar.')
    staging = root / ('.' + NAME + '-' + uuid.uuid4().hex)
    shutil.copytree(SOURCE, staging, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    if files(staging) != source_files:
        raise ValueError('La copia no coincide; se conserva el destino original.')
    backup = None
    if target.exists():
        backup_root = root.parent / 'davinci-video-pro-backups'
        backup_root.mkdir(parents=True, exist_ok=True)
        backup = backup_root / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8])
        if target.resolve().parent != root or backup.resolve().parent != backup_root.resolve():
            raise ValueError('El origen o respaldo no permanece en las carpetas de instalacion previstas.')
        target.rename(backup)
    try:
        if staging.resolve().parent != root or target.resolve().parent != root:
            raise ValueError('La copia temporal o destino salio de la carpeta de instalacion.')
        staging.rename(target)
    except Exception:
        if backup:
            backup.rename(target)
        raise
    return {'status': 'installed', 'path': str(target), 'backup': str(backup) if backup else None}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--client', choices=('codex', 'claude-code', 'both'), required=True)
    p.add_argument('--scope', choices=('user', 'project'), default='user')
    p.add_argument('--project-dir', type=Path)
    p.add_argument('--skills-dir', type=Path, help='Explicit single-client destination; useful for an existing installation.')
    p.add_argument('--update', action='store_true')
    a = p.parse_args()
    if a.skills_dir and a.client == 'both': p.error('--skills-dir requiere un solo cliente.')
    if a.scope == 'project' and not a.project_dir: p.error('--project-dir es obligatorio para scope project.')
    clients = ['codex', 'claude-code'] if a.client == 'both' else [a.client]
    results = []
    for client in clients:
        if a.skills_dir: root = a.skills_dir
        elif a.scope == 'project': root = a.project_dir / ('.agents' if client == 'codex' else '.claude') / 'skills'
        elif client == 'claude-code': root = Path.home() / '.claude' / 'skills'
        elif os.environ.get('CODEX_HOME'): root = Path(os.environ['CODEX_HOME']) / 'skills'
        else: root = Path.home() / '.agents' / 'skills'
        results.append({'client': client, **install(root, a.update)})
    print(json.dumps({'results': results, 'next': 'Invoca davinci-video-pro. Primero pide el guion; no llama APIs durante esta instalacion.'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
