"""Read-only portable diagnostics. No credentials, uploads or config mutations."""
from __future__ import annotations
import argparse,json,os,platform,shutil,subprocess,sys
from pathlib import Path

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
    parser.add_argument('--output',type=Path)
    parser.add_argument('--skip-connection',action='store_true')
    parser.add_argument('--check-connection',action='store_true',help='Consulta Resolve solo con guion confirmado.')
    parser.add_argument('--project-dir',type=Path)
    args=parser.parse_args()
    codex_root=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
    repo=args.repo or codex_root/'integrations/davinci-resolve-mcp'
    report={'system':platform.system(),'python':sys.version.split()[0],
            'python_path':sys.executable,'executables':{n:shutil.which(n) for n in ['git','node','ffmpeg','codex','claude']},
            'gemini_key_present':key_present(),'codex_root':str(codex_root),
            'repo_candidate':str(repo),'repo_found':(repo/'src/server.py').is_file(),
            'mcp_config_present':False,'bridge_config_present':False}
    config=codex_root/'config.toml'
    if config.is_file():
        try:
            import tomllib
            with config.open('rb') as stream:parsed=tomllib.load(stream)
            names=[name for name in parsed.get('mcp_servers',{}) if 'resolve' in name.lower()]
            report['mcp_config_present']=bool(names)
            report['resolve_mcp_names']=names
        except Exception as exc:
            report['config_parse_error']=type(exc).__name__
    bridge_config=Path(os.environ.get('DAVINCI_RESOLVE_BRIDGE_CONFIG',str(Path.home()/'.config/davinci-resolve-mcp/bridge.json')))
    report['bridge_config_present']=bridge_config.is_file()
    report['resolve']=windows_resolve() if os.name=='nt' else {'note':'Inspect the installed app with platform-specific tools.'}
    report['connection']={'tested':False}
    if args.check_connection and not args.skip_connection:
        from workflow import require_script
        if not args.project_dir:
            parser.error('--project-dir es obligatorio para consultar la API de Resolve.')
        require_script(args.project_dir)
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
