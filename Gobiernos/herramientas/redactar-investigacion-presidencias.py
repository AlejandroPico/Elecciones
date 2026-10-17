"""Valida el expediente interno y genera su cronología legible, sin acceder a la red."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1] / 'investigacion' / 'presidencias-centrales'


def read(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def indexed(items: list[dict], kind: str) -> dict[str, dict]:
    result = {}
    for item in items:
        identity = item['id']
        if identity in result:
            raise ValueError(f'{kind}: ID duplicado {identity}')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identity):
            raise ValueError(f'{kind}: ID inválido {identity}')
        result[identity] = item
    return result


def validate_date(value: str, precision: str) -> None:
    lengths = {'day': 10, 'month': 7, 'year': 4}
    if precision not in lengths or len(value) != lengths[precision]:
        raise ValueError(f'Fecha/precisión incoherentes: {value} / {precision}')
    date.fromisoformat(value + {'day': '', 'month': '-01', 'year': '-01-01'}[precision])


def render() -> str:
    source_file, event_file, stage_file = read('fuentes.json'), read('eventos.json'), read('etapas.json')
    sources = indexed(source_file['sources'], 'fuentes')
    events = indexed(event_file['events'], 'eventos')
    stages = indexed(stage_file['stages'], 'etapas')
    norm_file = read('normativa.json')
    norms = indexed([{**norm, 'id': norm['id'].lower()} for norm in norm_file['norms']], 'normativa')
    cutoff = event_file['checkedAt']
    date.fromisoformat(cutoff)
    used_sources = set()
    for source in sources.values():
        parsed = urlsplit(source['url'])
        if parsed.scheme != 'https' or not parsed.netloc:
            raise ValueError(f'URL no válida: {source["id"]}')
        for field in ('title', 'supports', 'limits', 'consultedAt', 'kind'):
            if not source.get(field):
                raise ValueError(f'Fuente sin {field}: {source["id"]}')
        if source['kind'] not in {'primary', 'secondary', 'agency'}:
            raise ValueError(f'Tipo de fuente desconocido: {source["id"]}')
        date.fromisoformat(source['consultedAt'])
        if source['consultedAt'] > cutoff:
            raise ValueError(f'Consulta posterior al corte: {source["id"]}')
    for stage in stages.values():
        for source in stage['sources']:
            if source not in sources:
                raise ValueError(f'Etapa con fuente inexistente: {stage["id"]}/{source}')
            used_sources.add(source)
    for event in events.values():
        validate_date(event['date'], event['datePrecision'])
        if event['date'] > cutoff:
            raise ValueError(f'Evento futuro: {event["id"]}')
        for field in ('title', 'summary', 'attribution', 'category', 'verification', 'reviewedAt'):
            if not event.get(field):
                raise ValueError(f'Evento sin {field}: {event["id"]}')
        date.fromisoformat(event['reviewedAt'])
        if event['reviewedAt'] > cutoff:
            raise ValueError(f'Revisión posterior al corte: {event["id"]}')
        stage_ids = [event['stage'], *event.get('relatedStages', [])]
        for link in event.get('displayStages', []):
            if not link.get('reason'):
                raise ValueError(f'Vínculo sin explicación: {event["id"]}')
            stage_ids.append(link['stage'])
        if event.get('stageAtMilestone'):
            stage_ids.append(event['stageAtMilestone'])
        for stage in stage_ids:
            if stage not in stages:
                raise ValueError(f'Etapa inexistente: {event["id"]}/{stage}')
        if not event['sources']:
            raise ValueError(f'Evento sin fuentes: {event["id"]}')
        for source in event['sources']:
            if source not in sources:
                raise ValueError(f'Fuente inexistente: {event["id"]}/{source}')
            used_sources.add(source)
        if event.get('judicialStatus') and not event.get('statusAtSource'):
            raise ValueError(f'Estado judicial sin fecha: {event["id"]}')
    kinds = Counter(source['kind'] for source in sources.values())
    for norm in norms.values():
        validate_date(norm['date'], 'day')
        if norm['stage'] not in stages or norm['date'] > cutoff or norm['id'] in events:
            raise ValueError(f'Registro normativo inválido: {norm["id"]}')
        if not norm['title'] or not norm['officialTitle'] or not norm['topics']:
            raise ValueError(f'Registro normativo incompleto: {norm["id"]}')
    weeks = read('cobertura-semanal.json')['weeks']
    previous = date(1975, 11, 19)
    weekly_norms = []
    for week in weeks:
        start, end = date.fromisoformat(week['from']), date.fromisoformat(week['until'])
        if start != previous + timedelta(days=1) or end < start or (end-start).days > 6:
            raise ValueError('Hueco o solapamiento en el registro semanal')
        previous = end
        for ref in week['norms']:
            if ref.lower() not in norms or not week['from'] <= norms[ref.lower()]['date'] <= week['until']:
                raise ValueError(f'Referencia semanal normativa incoherente: {ref}')
            weekly_norms.append(ref.lower())
        for ref in week['events']:
            if ref not in events or not week['from'] <= events[ref]['date'] <= week['until']:
                raise ValueError(f'Referencia semanal editorial incoherente: {ref}')
    if previous.isoformat() != cutoff or sorted(weekly_norms) != sorted(norms):
        raise ValueError('Registro semanal incompleto o duplicado')
    lines = [
        '# Presidencias centrales: cronología documentada', '',
        f'Corte de consulta: **{cutoff}**. **Investigación ampliada; cobertura hemerográfica parcial.**', '',
        f'Este expediente reúne **{len(events)} hechos**, **{len(sources)} referencias** '
        f'({kinds["primary"]} primarias, {kinds["agency"]} de agencia y {kinds["secondary"]} periodísticas) '
        f'y un índice de **{len(stages)} etapas**. Se añade un catálogo separado de **{len(norms)} disposiciones** '
        'identificadas por sus metadatos del BOE. Las cifras describen cobertura, no una valoración política.', '',
        'Los hechos se agrupan por la administración de origen. Cuando una sentencia o actualización llega después, '
        'se muestra también la etapa de resolución. Los rótulos anuales no son intervalos jurídicos ni duraciones exactas. '
        'Una fecha de consulta reciente no convierte una resolución antigua en el estado judicial vigente.', '',
        'Criterios: [investigacion.md](investigacion.md). Lagunas y siguiente revisión: [pendientes.md](pendientes.md). '
        'Los registros normativos no son acontecimientos analizados en profundidad ni éxitos acreditados. '
        'El registro `cobertura-semanal.json` documenta las semanas con entradas y las lagunas de revisión de prensa. '
        'No se declara completado un barrido hemerográfico semanal de cincuenta años.', '',
        '## Índice de etapas y cobertura', '',
        '| Etapa | Presidencia | Periodo orientativo | Hechos vinculados |',
        '| --- | --- | --- | ---: |',
    ]
    for stage in stages.values():
        count = sum(stage['id'] in {event['stage'], event.get('stageAtMilestone'), *event.get('relatedStages', []), *(link['stage'] for link in event.get('displayStages', []))} for event in events.values())
        label = stage['legislature'] or 'Contexto'
        lines.append(f'| {label} | {stage["president"]} | {stage["periodLabel"]} | {count} |')
    lines.extend(['', 'Las etapas sin entradas específicas siguen pendientes; no significan ausencia de hechos relevantes.', ''])
    index_sources = dict.fromkeys(source for stage in stages.values() for source in stage['sources'])
    lines.extend(['Base del índice: ' + '; '.join(f'[{sources[s]["title"]}]({sources[s]["url"]})' for s in index_sources) + '.', ''])
    for stage in stages.values():
        label = stage['legislature'] or 'Contexto'
        lines.extend([f'## {label} · {stage["president"]} · {stage["periodLabel"]}', '', stage['note'], ''])
        local_events = sorted((event for event in events.values() if event['stage'] == stage['id']), key=lambda event: (event['date'], event['id']), reverse=True)
        if not local_events:
            lines.extend(['Sin entradas propias contrastadas en esta primera pasada. Véase el plan de investigación pendiente.', ''])
        for event in local_events:
            lines.extend([f'### {event["date"]} · {event["title"]}', '', f'**Tipo:** {event["category"]}. **ID:** `{event["id"]}`.', '', event['summary'], '', '**Atribución y alcance.** ' + event['attribution'], ''])
            if event.get('factsPeriod'):
                lines.extend(['**Periodo de los hechos:** ' + event['factsPeriod'] + '.', ''])
            for link in event.get('displayStages', []):
                target = stages[link['stage']]
                lines.extend(['**También visible en:** ' + target['president'] + ' · ' + str(target['legislature'] or 'Contexto') + '. ' + link['reason'], ''])
            if event.get('stageAtMilestone'):
                resolution = stages[event['stageAtMilestone']]
                lines.extend(['**Etapa en la fecha del hito:** ' + str(resolution['legislature'] or 'Contexto') + ' · ' + resolution['president'] + '.', ''])
            if event.get('judicialStatus'):
                lines.extend([f'**Estado documentado a {event["statusAtSource"]}:** {event["judicialStatus"]}.', ''])
            if event.get('caseId'):
                lines.extend([f'**Expediente relacionado:** `{event["caseId"]}`.', ''])
            for source_id in event['sources']:
                source = sources[source_id]
                lines.extend([f'**Fuente:** [{source["title"]}]({source["url"]}). ' + source['limits'], ''])
            if event['pending']:
                lines.extend(['**Por completar:** ' + ' '.join(event['pending']), ''])
        references = [event for event in events.values() if stage['id'] in event.get('relatedStages', [])]
        if references:
            lines.extend(['Hechos de alcance compartido, desarrollados en otra etapa: ' + '; '.join(f'{event["title"]} (`{event["id"]}`)' for event in references) + '.', ''])
    unused = sorted(set(sources) - used_sources)
    lines.extend(['## Catálogo normativo separado', '',
        'Procedencia, consultas reproducibles y exclusiones: `catalogos-boe.json`, `normativa.json` y `revision-normativa.json`. '
        'Las disposiciones ya desarrolladas se excluyen mediante sus identificadores BOE o ELI. '
        'Se conserva la fecha de publicación y el título oficial, sin deducir eficacia, autoría exclusiva del Gobierno ni vigencia actual.', '',
        '| Etapa | Presidencia | Disposiciones en el índice |', '| --- | --- | ---: |'])
    for stage in stages.values():
        lines.append(f'| {stage["legislature"] or "Contexto"} | {stage["president"]} | {sum(n["stage"] == stage["id"] for n in norms.values())} |')
    lines.append('')
    lines.extend(['## Fuentes de ampliación todavía sin entrada', ''])
    if unused:
        for source_id in unused:
            source = sources[source_id]
            lines.extend([f'- [{source["title"]}]({source["url"]}): {source["supports"]} Límite: {source["limits"]}'])
    else:
        lines.append('Todas las referencias registradas están vinculadas al índice o a un hecho.')
    lines.extend(['', 'Este documento se regenera desde `etapas.json`, `eventos.json` y `fuentes.json` mediante '
                  '`Gobiernos/herramientas/redactar-investigacion-presidencias.py`. Corregir primero los registros; '
                  'la validación comprueba estructura y referencias, no sustituye la lectura histórica ni jurídica.', ''])
    return '\n'.join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Valida los registros y comprueba que la cronología esté actualizada.')
    args = parser.parse_args()
    content = render()
    target = ROOT / 'cronologia.md'
    if args.check:
        if not target.exists() or target.read_text(encoding='utf-8') != content:
            raise SystemExit('La cronología no coincide con los registros. Regenerarla antes de publicar.')
        print('Expediente válido; cronología actualizada.')
    else:
        target.write_text(content, encoding='utf-8', newline='\n')
        print(f'Cronología generada: {target}')


if __name__ == '__main__':
    main()
