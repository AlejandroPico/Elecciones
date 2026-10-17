"""Regenera los hitos del SMI desde los artículos originales conservados en el expediente.

Los importes son nominales, no una evaluación del salario real ni del efecto sobre el empleo.
No accede a la red. Para ampliar la serie, contrastar y conservar primero el artículo original.
"""
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / 'investigacion' / 'presidencias-centrales'
def read(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))
def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    spec = importlib.util.spec_from_file_location('normas', Path(__file__).with_name('importar-normativa-presidencias.py'))
    normas = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(normas)
    records = read('salarios-minimos.json')
    eventfile, sourcefile = read('eventos.json'), read('fuentes.json')
    events = {event['id']: event for event in eventfile['events']}
    sources = {source['id']: source for source in sourcefile['sources']}
    years = set()
    for row in records['rows']:
        year = re.search(r'para (\d{4})', row['title'], re.I).group(1)
        amount = re.search(r'(\d[\d., ]*)\s+(pesetas|euros)/mes', row['article1'])
        if not amount or not re.fullmatch(r'BOE-A-\d{4}-\d+', row['id']):
            raise ValueError('Registro del SMI sin importe contrastado o referencia válida')
        years.add(int(year))
        value, currency = amount.groups()
        source_id = 'smi-' + row['id'].lower()
        sources[source_id] = {
            'id': source_id, 'title': 'BOE · ' + row['title'],
            'url': 'https://www.boe.es/diario_boe/txt.php?id=' + row['id'],
            'supports': 'Importe nominal mensual del artículo 1, contrastado en el XML de la publicación original.',
            'limits': 'Consulta dirigida del artículo 1. La cuantía mensual no equivale a salario neto, salario real ni remuneración con todas las pagas prorrateadas. Consultar periodo de efectos y reglas de compensación en el decreto.',
            'kind': 'primary', 'consultedAt': records['checkedAt'],
        }
        identity = row['date'] + '-smi-' + year
        events[identity] = {
            'id': identity, 'date': row['date'], 'datePrecision': 'day',
            'stage': normas.stage_for(row['date']),
            'title': f'Salario mínimo (SMI) para {year}: {value} {currency} mensuales',
            'category': 'economico',
            'summary': f'El artículo 1 fija el importe mensual nominal en {value} {currency}. La fecha de esta entrada es la publicación del decreto; el año del salario es {year}.',
            'attribution': 'Decisión reglamentaria del Gobierno. La cuantía nominal no demuestra por sí sola una mejora del poder adquisitivo: debe contrastarse con inflación, jornada, pagas y efectos sobre el empleo. No se utiliza la cuantía mensual como salario neto ni como importe con pagas extraordinarias prorrateadas.',
            'sources': [source_id], 'pending': [],
            'verification': 'articulo-primero-publicacion-original',
            'reviewedAt': records['checkedAt'], 'topics': ['trabajo', 'economia-y-presupuestos'],
        }
    if years != set(range(1999, 2027)):
        raise ValueError('La selección anual 1999–2026 tiene lagunas')
    eventfile['events'], sourcefile['sources'] = list(events.values()), list(sources.values())
    write('eventos.json', eventfile)
    write('fuentes.json', sourcefile)
    print(f'{len(records["rows"])} importes del SMI; {len(events)} acontecimientos desarrollados.')

if __name__ == '__main__':
    main()
