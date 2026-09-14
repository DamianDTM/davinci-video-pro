"""Bind an Omni input to a reviewed audiovisual edit; no provider calls."""
from pathlib import Path
import json
from workflow import require_production, digest, now


def corrected_input_record(project, source, output, review_file, start):
    script = require_production(project)
    review = Path(review_file).expanduser().resolve(strict=True)
    if not review.read_text(encoding='utf-8-sig').strip():
        raise ValueError('El informe debe describir la revision real de imagen, voz y cortes ya corregidos.')
    return {'version': 1, 'source_kind': 'reviewed_corrected_audiovisual_edit',
            'project_dir': str(Path(project).resolve()),
            'source': str(Path(source).resolve()), 'source_sha256': digest(source),
            'start_seconds': start, 'duration_seconds': 4,
            'output': str(Path(output).resolve()), 'output_sha256': digest(output),
            'review_file': str(review), 'review_sha256': digest(review),
            'script_sha256': digest(script),
            'brief_sha256': digest(script.parent / 'BRIEF-TECNICO.md'),
            'created_at': now(),
            'audio_to_restore': 'corrected_audio_from_this_input',
            'note': 'Revision del agente; los hashes verifican trazabilidad, no calidad perceptiva.'}


def require_corrected_input(project, clip):
    script = require_production(project)
    clip = Path(clip).expanduser().resolve(strict=True)
    message = ('Omni requiere imagen y audio ya corregidos y revisados. Prepara el fragmento '
               'desde ese montaje con prepare_clip.py --review-file <informe-de-revision>; '
               'no uses el clip bruto ni recuperes su audio sin corregir.')
    try:
        record = json.loads(clip.with_suffix('.source.json').read_text(encoding='utf-8-sig'))
        valid = (isinstance(record, dict) and record.get('version') == 1
                 and record.get('source_kind') == 'reviewed_corrected_audiovisual_edit'
                 and record.get('audio_to_restore') == 'corrected_audio_from_this_input'
                 and Path(record['project_dir']).resolve() == Path(project).resolve()
                 and Path(record['output']).resolve() == clip
                 and record['output_sha256'] == digest(clip)
                 and record['source_sha256'] == digest(Path(record['source']))
                 and record['review_sha256'] == digest(Path(record['review_file']))
                 and bool(Path(record['review_file']).read_text(encoding='utf-8-sig').strip())
                 and record['script_sha256'] == digest(script)
                 and record['brief_sha256'] == digest(script.parent / 'BRIEF-TECNICO.md'))
    except (OSError, ValueError, KeyError, TypeError):
        raise ValueError(message) from None
    if not valid:
        raise ValueError(message + ' El archivo o su revision no coincide con el registro vigente.')
    return record
