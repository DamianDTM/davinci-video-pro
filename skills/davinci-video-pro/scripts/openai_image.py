"""Optional single OpenAI image generation for hosts without native ImageGen."""
import argparse
import base64
import json
import math
import os
from pathlib import Path
import urllib.request
from workflow import require_script, digest, write_json, now


def read_key():
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not key and os.name == 'nt':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as reg:
                key = str(winreg.QueryValueEx(reg, 'OPENAI_API_KEY')[0]).strip()
        except OSError:
            pass
    if not key:
        raise ValueError('Configura OPENAI_API_KEY localmente; no pegues la clave en el chat.')
    return key


def generate(args):
    script = require_script(args.project_dir)
    if not args.confirmation.strip() or not all(math.isfinite(x) for x in (args.estimated_usd, args.max_usd)) or not 0 < args.estimated_usd <= args.max_usd:
        raise ValueError('Falta autorizacion real de esta imagen o su estimacion excede el tope acordado.')
    prompt = args.prompt_file.read_text(encoding='utf-8-sig').strip()
    if len(prompt) < 30:
        raise ValueError('Prepara un prompt de la escena basado en el guion.')
    target = args.output.expanduser().resolve()
    state_path = target.with_suffix('.request.json')
    if target.suffix.lower() != '.png' or target.exists() or state_path.exists():
        raise ValueError('Elige una imagen nueva. Si existe un intento, revisalo antes de volver a generar.')
    key = read_key()
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {'status': 'requested', 'created_at': now(), 'script_sha256': digest(script),
              'model': args.model, 'prompt': prompt, 'estimated_usd': args.estimated_usd,
              'max_usd_for_this_image': args.max_usd, 'confirmation': args.confirmation}
    with state_path.open('x', encoding='utf-8') as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
    payload = {'model': args.model, 'prompt': prompt, 'n': 1, 'size': args.size,
               'quality': args.quality, 'output_format': 'png'}
    request = urllib.request.Request('https://api.openai.com/v1/images/generations',
        data=json.dumps(payload).encode(), headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'})
    try:
        # urllib has no application-level automatic retry here.
        with urllib.request.urlopen(request, timeout=300) as response:
            data = json.load(response)
        content = base64.b64decode(data['data'][0]['b64_json'], validate=True)
        if not content.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('La respuesta no es un PNG.')
        with target.open('xb') as stream:
            stream.write(content)
        record.update(status='completed_needs_review', output=str(target), usage=data.get('usage'))
        write_json(state_path, record)
        return {'status': record['status'], 'file': str(target)}
    except Exception as exc:
        record.update(status='failed_or_uncertain', error_type=type(exc).__name__)
        write_json(state_path, record)
        raise RuntimeError(f'La imagen no se completo ({type(exc).__name__}). No se reintentara automaticamente.') from None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-dir', type=Path, required=True)
    p.add_argument('--prompt-file', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--model', required=True, help='Modelo GPT Image elegido y disponible en la cuenta.')
    p.add_argument('--size', default='1024x1536')
    p.add_argument('--quality', choices=('low', 'medium', 'high'), default='medium')
    p.add_argument('--confirmation', required=True)
    p.add_argument('--estimated-usd', type=float, required=True)
    p.add_argument('--max-usd', type=float, required=True)
    a = p.parse_args()
    try:
        print(json.dumps(generate(a))); return 0
    except Exception as exc:
        print(json.dumps({'success': False, 'error': str(exc)})); return 1


if __name__ == '__main__':
    raise SystemExit(main())
