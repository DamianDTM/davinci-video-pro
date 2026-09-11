"""Local Omni cost estimates from reported usage. This is not a billing API."""
from pathlib import Path
from workflow import atomic, omni_attempts

PRICING = {
    'model': 'gemini-omni-1.1-flash', 'tier': 'Standard', 'resolution': '720p',
    'verified_on': '2026-09-11',
    'source': 'https://ai.google.dev/gemini-api/docs/pricing#gemini-omni-flash',
    'input_per_million_usd': 1.50, 'text_per_million_usd': 9.00,
    'video_per_million_usd': 17.50, 'video_tokens_per_second': 5792,
}


def token_count(value):
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def estimate_cost(record):
    result = {'currency': 'USD', 'billed_usd': None, 'estimated_subtotal_usd': None,
              'estimated_total_usd': None, 'status': 'unknown', 'components': [],
              'pricing': dict(PRICING),
              'note': 'Estimacion con la tarifa indicada, no un importe facturado confirmado por Google.'}
    if record.get('model') != PRICING['model'] or record.get('resolution') != PRICING['resolution']:
        result['note'] += ' No hay tarifa verificada para este modelo/resolucion.'
        return result
    usage = record.get('usage') or {}
    counts = {}
    breakdown = usage.get('output_tokens_by_modality') or []
    for item in breakdown:
        tokens = token_count(item.get('tokens'))
        modality = str(item.get('modality', '')).lower()
        if tokens is not None:
            counts[modality] = counts.get(modality, 0) + tokens

    def add(name, tokens, rate, basis='reported_tokens'):
        if tokens is not None:
            result['components'].append({'name': name, 'tokens': tokens, 'basis': basis,
                                         'estimated_usd': round(tokens * rate / 1_000_000, 8)})

    add('input', token_count(usage.get('total_input_tokens')), PRICING['input_per_million_usd'])
    add('text_output', counts.get('text'), PRICING['text_per_million_usd'])
    if 'video' in counts:
        add('video_output', counts['video'], PRICING['video_per_million_usd'])
    elif record.get('status') == 'completed' and record.get('output_seconds') is not None:
        add('video_output', round(record['output_seconds'] * PRICING['video_tokens_per_second']),
            PRICING['video_per_million_usd'], 'output_duration_estimate')

    if result['components']:
        result['estimated_subtotal_usd'] = round(sum(x['estimated_usd'] for x in result['components']), 8)
        result['status'] = 'partial_estimate'
        # Missing metadata is not zero. Do not guess whether thought tokens are
        # included in output tokens or add them twice. Only label a total when
        # every reported component reconciles and there are no extra token types.
        complete = (token_count(usage.get('total_input_tokens')) is not None
                    and 'video' in counts and set(counts) <= {'video', 'text'}
                    and usage.get('total_output_tokens') == sum(counts.values())
                    and all(usage.get(k) == 0 for k in
                            ('total_thought_tokens', 'total_cached_tokens', 'total_tool_use_tokens'))
                    and not usage.get('grounding_tool_count'))
        if complete:
            result['status'] = 'usage_estimate'
            result['estimated_total_usd'] = result['estimated_subtotal_usd']
        else:
            result['note'] += ' Subtotal parcial: los componentes no informados o ambiguos quedan pendientes.'
    else:
        result['note'] += ' Sin uso suficiente: coste desconocido; no significa que el intento sea gratuito.'
    return result


def write_cost_report(project):
    """Regenerate a human-readable ledger after every attempt, including failures."""
    lines = ['# Generaciones y costes de Omni', '',
             'Mostrar cada video y este coste antes de esperar la decision sobre otra generacion.',
             'Los importes estimados no son cargos confirmados. Un coste desconocido no es cero.', '']
    known = 0.0; unknown = 0
    for record in sorted(omni_attempts(project), key=lambda x: x['created_at']):
        cost = record.get('cost') or estimate_cost(record)
        subtotal = cost['estimated_subtotal_usd']
        if subtotal is None:
            unknown += 1; label = 'desconocido / pendiente de verificar'
        else:
            known += subtotal
            label = f'USD {subtotal:.6f} estimados'
            if cost['estimated_total_usd'] is None: label += ' (subtotal parcial)'
        lines.extend([f"## {record['scene']}", '', f"Estado: {record['status']}", '', f'Coste: {label}.', ''])
        if record.get('output'):
            path = Path(record['output']).as_posix()
            lines.extend([f'[Abrir video](<{path}>)', ''])
        lines.extend([cost['note'], '', f"Tarifa consultada: {cost['pricing']['verified_on']}. "
                      f"[Fuente oficial]({cost['pricing']['source']}).", ''])
    lines.extend([f'Suma de componentes estimados disponibles: USD {known:.6f}; '
                  f'intentos sin coste conocido: {unknown}. No es un total facturado.', ''])
    path = Path(project).resolve() / 'GASTOS-OMNI.md'
    atomic(path, '\n'.join(lines))
    return str(path)
