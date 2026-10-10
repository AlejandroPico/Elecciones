"""Verifica cobertura, recursos y referencias del complemento valenciano.

No modifica las composiciones ni depende de la caché de investigación.
"""
import concurrent.futures, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGION = ROOT / 'Gobiernos/Autonomías/Comunitat Valenciana'

def read(path, default=None):
    return json.loads(path.read_text('utf8')) if path.exists() else default

def main():
    def person(path):
        meta = read(path)
        photo = read(path.parent / 'retrato.json')
        return meta['id'], {'name': meta['name'], 'folder': path.parent,
                            'portrait': bool(photo and (path.parent / photo['file']).is_file()),
                            'sources': {r['url'] for r in read(path.parent / 'fuentes.json', [])}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
        people = dict(pool.map(person, (ROOT / 'Políticos').glob('*/ficha.json')))
    governments = [read(p) for p in (REGION / 'Gobierno').glob('*/composicion.json')]
    parliaments = [read(p) for p in (REGION / 'Parlamento').glob('*/composicion.json')]
    historical = [g for g in governments if g['start'] < '2023-07-17']
    errors = []
    for composition, terms in [(g, g['terms']) for g in governments] + [(p, p['board']) for p in parliaments]:
        for t in terms:
            if t['person'] not in people or t['source'] not in people[t['person']]['sources']:
                errors.append({'composition': composition['id'], 'person': t['person'], 'error': 'Identidad o fuente ausente'})
            if not t['start'] or (t['end'] and t['end'] <= t['start']):
                errors.append({'composition': composition['id'], 'person': t['person'], 'error': 'Intervalo no válido'})
    initial = read(ROOT / 'Gobiernos/revisiones/2026-10-09-valencia/informe.json')
    involved = {id for id in initial['identityMapping'].values()} | {t['person'] for g in governments for t in g['terms']}
    missing = [{'id': id, 'name': people[id]['name']} for id in sorted(involved) if not people[id]['portrait']]
    supplement = read(REGION / 'fuentes/retratos-complementados.json')
    for row in supplement:
        folder = ROOT / 'Políticos' / row['name']
        photo = read(folder / 'retrato.json')
        if not photo or not (folder / photo['file']).is_file():
            errors.append({'person': row['name'], 'error': 'Recurso gráfico ausente'})
    consell = read(REGION / 'fuentes/consell-historico.json')
    data = {
        'checkedAt': '2026-10-10', 'baselineAudit': '2026-10-09-valencia',
        'scope': 'Complemento del histórico del Consell, Mesas de Les Corts y retratos pendientes.',
        'governments': len(governments), 'datedHistoricalGovernments': len(historical),
        'undatedHistoricalGovernmentTerms': sum(len(g.get('archiveTerms', [])) for g in historical),
        'consellEvents': len(consell['events']), 'consellNorms': len(consell['norms']),
        'historicalConsellPeople': len({m['person'] for e in consell['events'] for m in e['members']}),
        'legislatures': len(parliaments), 'datedBoardIntervals': sum(len(p['board']) for p in parliaments),
        'boardPeople': len({t['person'] for p in parliaments for t in p['board']}),
        'portraitsCompleted': supplement, 'missingPortraits': missing,
        'allMissingPortraits': sorted(id for id, p in people.items() if not p['portrait']),
        'errors': errors,
        'limits': [
            'Las vacantes solo se representan cuando hay una fecha documentada; las notas identifican relevos cuyo día de renuncia no queda precisado.',
            'El cierre del Pleno no acredita el cese de la Diputación Permanente.',
            'Cuatro retratos históricos siguen pendientes de una imagen individual identificable; no se utilizan homónimos ni fotografías de grupo ambiguas.',
            'El hemiciclo es esquemático, no un plano de asientos físicos.'
        ]
    }
    output = ROOT / 'Gobiernos/revisiones/2026-10-10-valencia'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'informe.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps({k: data[k] for k in ['datedHistoricalGovernments', 'consellEvents', 'datedBoardIntervals', 'errors']}, ensure_ascii=False))
    print('Retratos completados:', len(supplement), 'pendientes:', len(missing))
    assert not errors, errors

if __name__ == '__main__': main()
