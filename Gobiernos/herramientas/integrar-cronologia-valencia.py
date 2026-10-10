"""Integra transcripciones contrastadas, sin deducir fechas de tablas sin fechar.

Ejecutar desde la raíz. Consume fuentes/consell-historico.json y, si existe,
fuentes/mesa-cronologia.json. Conserva las identidades compartidas nacionales.
No consulta la red ni depende de la caché de investigación.
"""
import concurrent.futures, datetime, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DEST = ROOT / 'Gobiernos/Autonomías/Comunitat Valenciana'

def read(path, default=None):
    return json.loads(path.read_text('utf8')) if path.exists() else default

def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'utf8')

def ref(url, label='DOGV · nombramientos y ceses del Consell'):
    return {'label': label, 'url': url, 'kind': 'encyclopedic' if 'wikipedia.org' in url else 'institutional'}

def period(start, end):
    last = (datetime.date.fromisoformat(end) - datetime.timedelta(days=1)).isoformat() if end else 'actualidad'
    return start + ' — ' + last

def main():
    paths = list((ROOT / 'Políticos').glob('*/ficha.json'))
    def load(path):
        data = read(path)
        return data['id'], (path.parent, data)
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
        people = dict(pool.map(load, paths))
    sources = read(DEST / 'fuentes/consell-historico.json')
    terms, live = [], {}
    def close(person, event):
        if person in live:
            t = live.pop(person)
            t['end'] = event['date']
            t['endBasis'] = event['source']
            t['endNote'] = event['basis']
            if t['start'] < t['end']:
                terms.append(t)
    for event in sources['events']:
        assert event['date'] and event['source'].startswith('https://')
        if event['full']:
            for person in list(live):
                close(person, event)
        for person in event['cease']:
            close(person, event)
        for member in event['members']:
            close(member['person'], event)
            assert member['person'] in people, member['name']
            live[member['person']] = {
                **member, 'start': event['date'], 'end': None,
                'source': event['source'], 'startNote': event['basis'],
                'additionalSources': event.get('additionalSources', []),
                'constituency': 'Comunitat Valenciana',
            }
    assert not live, 'El último evento debe delimitar el relevo de julio de 2023.'
    governments = []
    for path in sorted((DEST / 'Gobierno').glob('*/composicion.json')):
        g = read(path)
        if g['start'] == '2023-07-17':
            # Conservar también el Consell saliente en el primer tramo de Mazón,
            # según el mismo criterio de efectos del DOGV utilizado en el visor.
            g['terms'] = [t for t in g['terms'] if not t.get('historicalCarryover')]
            for original in terms:
                if original['start'] < g['start'] < original['end']:
                    g['terms'].append({**original, 'start': g['start'],
                                       'appointmentStart': original['start'],
                                       'historicalCarryover': True,
                                       'periodNote': 'Consell saliente en funciones. El visor usa los efectos de los decretos, no la hora de la ceremonia de toma de posesión.'})
            write(path, g)
        if g['start'] < '2023-07-17':
            presidents = [t for t in g['terms'] if t['level'] == 'president']
            g['terms'] = presidents.copy()
            for original in terms:
                start = max(original['start'], g['start'])
                end = min(original['end'], g['end'])
                if start >= end or any(t['person'] == original['person'] for t in presidents):
                    continue
                t = {**original, 'start': start, 'end': end}
                if start != original['start'] or end != original['end']:
                    t['appointmentStart'] = original['start']
                    t['appointmentEnd'] = original['end']
                    t['periodNote'] = 'Intervalo mostrado dentro de esta etapa presidencial; el nombramiento individual puede comenzar antes o terminar después.'
                g['terms'].append(t)
            dated = {t['person'] for t in g['terms']}
            g['archiveTerms'] = [t for t in g.get('archiveTerms', []) if t['person'] not in dated]
            g['source'] = 'https://dogv.gva.es/dogv-portal-frontend/es/legislatiu'
            g['incidents'] = [
                'Nombramientos, ceses, cambios de cartera y asignaciones temporales contrastados con el articulado del DOGV. Se distingue la fecha del decreto de la entrada en vigor indicada en su disposición final.',
                'Los titulares salientes pueden continuar en funciones tras la toma de posesión del nuevo president. El cambio de etapa presidencial no se interpreta como cese individual.',
            ]
            g['checkedAt'] = sources['checkedAt']
            write(path, g)
        governments.append(g)
    # La transcripción queda sincronizada para las siguientes incorporaciones.
    write(DEST / 'Gobierno/transcripcion.json', sorted(governments, key=lambda g: g['start']))
    offices = {}
    for t in terms:
        offices.setdefault(t['person'], []).append({
            'title': t['role'] + ' · Generalitat Valenciana',
            'period': period(t['start'], t['end']),
            'start': t['start'], 'end': t['end'], 'source': ref(t['source']),
            'endSource': ref(t['endBasis'], 'DOGV · efectos del cese o reasignación'),
        })
    # Un antiguo conseller también puede haber sido president. Regenerar su
    # presidencia desde la composición canónica al sustituir sus carteras.
    for g in governments:
        for t in g['terms']:
            if t['level'] == 'president' and t['person'] in offices:
                offices[t['person']].append({
                    'title': t['role'] + ' · Generalitat Valenciana',
                    'period': period(t['start'], t['end']),
                    'start': t['start'], 'end': t['end'],
                    'source': ref(t['source'], 'Generalitat · etapa presidencial'),
                    'endSource': ref(t.get('endBasis') or g['source'], 'Generalitat · límite de la etapa presidencial'),
                })
    for person, rows in offices.items():
        folder, meta = people[person]
        previous = read(folder / 'cargos-valencia.json', [])
        # Se sustituyen las carteras históricas sin fechas y sus antiguas
        # reproducciones, conservando los cargos parlamentarios y posteriores.
        keep = [r for r in previous if 'Generalitat Valenciana' not in r['title']
                or (r.get('start') and r['start'] >= '2023-07-20')
                or r['source']['url'].startswith('https://dogv.gva.es/datos/2023/')
                or r['source']['url'].startswith('https://dogv.gva.es/datos/2024/')
                or r['source']['url'].startswith('https://dogv.gva.es/datos/2025/')]
        write(folder / 'cargos-valencia.json', keep + rows)
        refs = read(folder / 'fuentes.json', [])
        additions = [r[key] for r in rows for key in ['source', 'endSource']]
        additions += [ref(url, 'DOGV · competencias complementarias')
                      for t in terms if t['person'] == person
                      for url in t.get('additionalSources', [])]
        for r in additions:
            if not any(old['url'] == r['url'] for old in refs): refs.append(r)
        write(folder / 'fuentes.json', refs)
    print(f'Consell: {len(terms)} intervalos individuales, {len(offices)} titulares.')
    mesa = read(DEST / 'fuentes/mesa-cronologia.json')
    if mesa:
        indexed = {p['id']: p for p in mesa['legislatures']}
        board_offices = {}
        for path in (DEST / 'Parlamento').glob('*/composicion.json'):
            p = read(path)
            p['board'] = indexed[p['id']]['terms']
            p['archiveBoard'] = []
            p['boardNote'] = mesa['note']
            write(path, p)
            for t in p['board']:
                row = {'title': t['role'], 'period': period(t['start'], t['end']),
                       'start': t['start'], 'end': t['end'],
                       'source': ref(t['source'], 'Les Corts · composición y relevos de la Mesa')}
                if t.get('endBasis'):
                    row['endSource'] = ref(t['endBasis'], 'Les Corts · relevo o límite del Pleno')
                if t.get('endNote'): row['note'] = t['endNote']
                board_offices.setdefault(t['person'], []).append(row)
        for person, rows in board_offices.items():
            folder, _ = people[person]
            previous = read(folder / 'cargos-valencia.json', [])
            keep = [r for r in previous if ' de Les Corts' not in r['title']]
            write(folder / 'cargos-valencia.json', keep + rows)
            refs = read(folder / 'fuentes.json', [])
            for row in rows:
                for key in ['source', 'endSource']:
                    r = row.get(key)
                    if r and not any(old['url'] == r['url'] for old in refs): refs.append(r)
            write(folder / 'fuentes.json', refs)
        print(f'Mesas: {sum(len(p["terms"]) for p in mesa["legislatures"])} intervalos, {len(board_offices)} personas.')
    return people

if __name__ == '__main__': main()
