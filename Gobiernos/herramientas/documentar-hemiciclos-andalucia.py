"""Recupera la composición archivada, separada de las bajas, sin inventar fechas.

El archivo nominal conserva también las sustituciones. La lista anterior al
epígrafe «que causaron baja» constituye otra referencia documental, no una
composición diaria reconstruida. Las posiciones no son asientos físicos.
"""
import collections, importlib.util, json, pathlib, re
from urllib.parse import parse_qs, urlsplit

spec = importlib.util.spec_from_file_location('consulta', pathlib.Path(__file__).with_name('consultar-andalucia.py'))
consulta = importlib.util.module_from_spec(spec)
spec.loader.exec_module(consulta)


def composition(period, rows, mapping):
    source = rows[0]['listSource']
    page = consulta.soup(source)
    main = page.select_one('#interior-pa') or page
    started = False
    seen = set()
    groups = collections.defaultdict(list)
    records = {m['person']: m for m in period['records']}
    for element in main.find_all(['h1', 'h2', 'a']):
        text = element.get_text(' ', strip=True)
        if element.name == 'h1' and text.startswith('Diputados de todos los grupos'):
            started = True
            continue
        if started and element.name == 'h2' and 'que causaron baja' in text:
            break
        if not started or element.name != 'a' or not text:
            continue
        query = parse_qs(urlsplit(element.get('href', '')).query)
        key = query.get('codmie', [None])[0]
        if key is None or key in seen:
            continue
        person = mapping[key]
        if person not in records:
            raise ValueError('Identidad fuera del registro: ' + person)
        seen.add(key)
        match = re.search(r'\[([^]]+)\]', text)
        # La ausencia de etiqueta no permite atribuir un grupo ni militancia.
        groups[match[1] if match else 'Sin grupo publicado'].append(records[person])
    if not started or not 100 <= sum(map(len, groups.values())) <= period['capacity']:
        raise ValueError('Composición incompleta o sobredimensionada: ' + period['label'])
    if len({m['person'] for members in groups.values() for m in members}) != len(seen):
        raise ValueError('Identidades repetidas en la composición: ' + period['label'])
    return {
        'source': source,
        'checkedAt': period['checkedAt'],
        'note': 'Composición archivada por el Parlamento, en el listado separado de quienes causaron baja. La fuente no fecha esta composición: sirve de referencia de la legislatura, no del día seleccionado. Los puntos sin identificar no implican una vacante. El archivo completo conserva todos los relevos.',
        'groups': [{'name': name, 'source': source, 'members': [m['person'] for m in members]} for name, members in groups.items()],
    }


if __name__ == '__main__':
    profiles = json.loads((consulta.CACHE / 'profiles.json').read_text('utf8'))
    mapping = json.loads(pathlib.Path('Gobiernos/revisiones/2026-10-12-andalucia/informe.json').read_text('utf8'))['identityMapping']
    root = pathlib.Path('Gobiernos/Autonomías/Andalucía/Parlamento')
    for file in sorted(root.glob('*/composicion.json')):
        period = json.loads(file.read_text('utf8'))
        if not period['nominalOnly']:
            continue
        leg = int(period['id'].rsplit('-', 1)[1])
        period['archivedComposition'] = composition(period, [p for p in profiles if p['legislature'] == leg], mapping)
        consulta.write(file, period)
        print(period['label'], sum(len(g['members']) for g in period['archivedComposition']['groups']), flush=True)
