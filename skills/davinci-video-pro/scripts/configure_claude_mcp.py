"""Merge an upstream Resolve MCP entry into a Claude Code project, preserving other servers."""
import argparse
import json
from pathlib import Path
import shutil
import uuid
from workflow import write_json


def configure(project, entry_path):
    project = Path(project).resolve()
    # Registration only writes local JSON. API/connection checks still need a script.
    data = json.loads(Path(entry_path).read_text(encoding='utf-8-sig'))
    servers = data.get('mcpServers', data)
    selected = {name: entry for name, entry in servers.items() if 'resolve' in name.lower()}
    if len(selected) != 1:
        raise ValueError('La entrada debe contener exactamente un servidor Resolve del instalador oficial.')
    name, entry = next(iter(selected.items()))
    command = Path(entry.get('command', ''))
    if not command.is_absolute() or not command.is_file():
        raise ValueError('El interprete del MCP debe existir con ruta absoluta en este equipo.')
    if not isinstance(entry.get('args', []), list) or not isinstance(entry.get('env', {}), dict):
        raise ValueError('La entrada MCP no tiene la estructura esperada.')
    config = project / '.mcp.json'
    current = json.loads(config.read_text(encoding='utf-8-sig')) if config.exists() else {}
    if not isinstance(current, dict) or not isinstance(current.get('mcpServers', {}), dict):
        raise ValueError('La configuracion existente no es valida; no se modifico.')
    all_servers = current.setdefault('mcpServers', {})
    if all_servers.get(name) == entry:
        return {'status': 'already_configured', 'path': str(config)}
    if name in all_servers:
        raise ValueError('Ya hay una entrada Resolve diferente. Revisar el cambio concreto antes de reemplazarla.')
    backup = None
    if config.exists():
        backup = project / ('.mcp.json.backup-' + uuid.uuid4().hex)
        shutil.copyfile(config, backup)
    all_servers[name] = entry
    write_json(config, current)
    return {'status': 'configured_needs_reload_and_connection_test', 'path': str(config),
            'backup': str(backup) if backup else None}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-dir', type=Path, required=True)
    p.add_argument('--entry', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(configure(a.project_dir, a.entry)))


if __name__ == '__main__':
    main()
