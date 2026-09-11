"""Read-only portable diagnostics. No credentials, uploads or config mutations."""
from __future__ import annotations
import argparse,json,os,platform,shutil,sys
from pathlib import Path

def inspect_clients(client, project, codex_root, claude_config):
    """Report registrations only; never start commands or echo env/arguments."""
    project = Path(project).expanduser().resolve()
    result = {}

    def inspect(sources):
        configs = []
        servers = []
        for scope, path, project_local in sources:
            item = {'scope': scope, 'path': str(path), 'exists': path.is_file()}
            configs.append(item)
            if not path.is_file():
                continue
            try:
                if path.suffix == '.toml':
                    import tomllib
                    parsed = tomllib.loads(path.read_text(encoding='utf-8-sig'))
                    entries = parsed.get('mcp_servers', {})
                else:
                    parsed = json.loads(path.read_text(encoding='utf-8-sig'))
                    if project_local:
                        parsed = next((v for k, v in parsed.get('projects', {}).items()
                                       if Path(k).expanduser().resolve() == project), {})
                    entries = parsed.get('mcpServers', {})
                for name, entry in entries.items():
                    if 'resolve' not in name.lower() or not isinstance(entry, dict):
                        continue
                    row = {'name': name, 'scope': scope, 'enabled': entry.get('enabled', True),
                           'repo_candidate': None, 'repo_found': False}
                    for arg in entry.get('args', []):
                        if not isinstance(arg, str):
                            continue
                        script = Path(arg)
                        if script.is_absolute() and script.name == 'server.py' and script.parent.name == 'src':
                            row.update(repo_candidate=str(script.parent.parent), repo_found=script.is_file())
                            break
                    servers.append(row)
            except (OSError, ValueError, TypeError, AttributeError) as exc:
                item['parse_error'] = type(exc).__name__
        return {'mcp_config_present': bool(servers), 'configs': configs,
                'servers': servers, 'mcp_transport': {'tested': False},
                'note': 'Registro local; no demuestra que el servidor arranque ni que Resolve responda.'}

    if client in ('codex', 'both'):
        result['codex'] = inspect([('user', Path(codex_root) / 'config.toml', False)])
    if client in ('claude-code', 'both'):
        result['claude-code'] = inspect([('user', Path(claude_config), False),
                                        ('local', Path(claude_config), True),
                                        ('project', project / '.mcp.json', False)])
    return result


def ffmpeg_status():
    path = shutil.which('ffmpeg')
    bundled = None
    try:
        import imageio_ffmpeg
        candidate = imageio_ffmpeg.get_ffmpeg_exe()
        if Path(candidate).is_file():
            bundled = candidate
    except (ImportError, RuntimeError, OSError):
        pass
    return {'available': bool(path or bundled), 'path_executable': path,
            'imageio_executable': bundled}


def key_present():
    if os.name == 'nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Environment') as key:
                value,_=winreg.QueryValueEx(key,'GEMINI_API_KEY')
            if str(value).strip():
                return True
        except OSError:
            pass
    return bool(os.environ.get('GEMINI_API_KEY','').strip())

def windows_resolve():
    import winreg
    installed=[]
    for hive in [winreg.HKEY_LOCAL_MACHINE,winreg.HKEY_CURRENT_USER]:
        for branch in [r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
                       r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall']:
            try:
                with winreg.OpenKey(hive,branch) as root:
                    for i in range(winreg.QueryInfoKey(root)[0]):
                        try:
                            with winreg.OpenKey(root,winreg.EnumKey(root,i)) as app:
                                def field(name):
                                    try:return winreg.QueryValueEx(app,name)[0]
                                    except OSError:return ''
                                name=field('DisplayName')
                                if name in ['DaVinci Resolve','DaVinci Resolve Studio']:
                                    installed.append({'name':name,'version':field('DisplayVersion'),
                                                      'location':field('InstallLocation')})
                        except OSError:
                            pass
            except OSError:
                pass
    exe=Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Blackmagic Design/DaVinci Resolve/Resolve.exe'
    return {'installed_entries':installed,'default_executable_exists':exe.is_file(),
            'default_executable':str(exe) if exe.is_file() else None,
            'edition_note':'Confirm edition in About or the live API if the registry name is ambiguous.'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path)
    parser.add_argument('--client', choices=('codex', 'claude-code', 'both'), default='both')
    parser.add_argument('--claude-config', type=Path, help='Ruta explicita a .claude.json si se usa otro perfil.')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--skip-connection',action='store_true')
    parser.add_argument('--check-connection',action='store_true',help='Prueba tecnica de Resolve, sin editar ni requerir guion.')
    parser.add_argument('--project-dir',type=Path)
    args=parser.parse_args()
    codex_root=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
    claude_config = args.claude_config or (Path(os.environ['CLAUDE_CONFIG_DIR']) / '.claude.json'
                    if os.environ.get('CLAUDE_CONFIG_DIR') else Path.home() / '.claude.json')
    clients = inspect_clients(args.client, args.project_dir or Path.cwd(), codex_root, claude_config)
    repos = {s['repo_candidate'] for c in clients.values() for s in c['servers'] if s['repo_found']}
    repo = args.repo or (Path(next(iter(repos))) if len(repos) == 1 else None)
    report={'system':platform.system(),'python':sys.version.split()[0],
            'python_path':sys.executable,'executables':{n:shutil.which(n) for n in ['git','node','ffmpeg','codex','claude']},
            'gemini_key_present':key_present(),'selected_client':args.client, 'clients':clients,
            'repo_candidate':str(repo) if repo else None,
            'repo_found':bool(repo and (repo/'src/server.py').is_file()),
            'ffmpeg':ffmpeg_status(),'bridge_config_present':False}
    bridge_config=Path(os.environ.get('DAVINCI_RESOLVE_BRIDGE_CONFIG',str(Path.home()/'.config/davinci-resolve-mcp/bridge.json')))
    report['bridge_config_present']=bridge_config.is_file()
    report['resolve']=windows_resolve() if os.name=='nt' else {'note':'Inspect the installed app with platform-specific tools.'}
    report['connection']={'tested':False}
    if args.check_connection and not repo:
        report['connection']['next'] = 'Indica --repo: no se encontro un checkout unico para el cliente elegido.'
    if report['repo_found'] and args.check_connection and not args.skip_connection:
        try:
            sys.path.insert(0,str(repo))
            from src.utils.resolve_bridge_client import connect
            resolve=connect(require_enabled=False,timeout=15)
            project=resolve.GetProjectManager().GetCurrentProject()
            report['connection']={'tested':True,'transport':'in-app bridge','connected':True,
                                  'version':resolve.GetVersionString(),'project_open':bool(project)}
        except Exception as exc:
            report['connection']={'tested':True,'transport':'in-app bridge','connected':False,
                                  'error_type':type(exc).__name__,
                                  'next':'Read the MCP remediation; a bridge failure does not test Studio external scripting.'}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf-8') as stream:json.dump(report,stream,ensure_ascii=False,indent=2)
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
    main()
