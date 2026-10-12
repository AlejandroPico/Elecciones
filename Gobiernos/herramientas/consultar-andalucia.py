"""Consulta el archivo público del Parlamento andaluz, sin declaraciones privadas.

Conserva originales en la caché ignorada. No confunde listas de participantes de
una legislatura con composiciones simultáneas ni grupo parlamentario con partido.
"""
import concurrent.futures, hashlib, json, pathlib, re, subprocess, sys
from urllib.parse import urljoin, quote, parse_qs, urlsplit
sys.path.insert(0, 'test-results/libraries')
from bs4 import BeautifulSoup

BASE = 'https://www.parlamentodeandalucia.es'
PATH = '/webdinamica/portal-web-parlamento/composicionyfuncionamiento/'
CACHE = pathlib.Path('test-results/andalucia')
CHECKED = '2026-10-12'

def write(path, data):
    path = pathlib.Path(path)
    text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text('utf8') != text: path.write_text(text, 'utf8')

def fetch(url, suffix='.html'):
    path = CACHE / 'documents' / (hashlib.sha256(url.encode()).hexdigest() + suffix)
    if not path.exists():
        raw = subprocess.check_output(['curl.exe', '--fail', '--silent', '--show-error', '--location', '--max-time', '30', '--retry', '1', '--retry-delay', '1', quote(url, safe=':/?=%&+;#')])
        if not raw: raise ValueError('Documento vacío: ' + url)
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    return path.read_bytes()

def soup(url):
    # El portal anuncia UTF-8, pero sus páginas dinámicas envían bytes Latin-1.
    raw = fetch(url)
    try: text = raw.decode('utf8')
    except UnicodeDecodeError: text = raw.decode('latin1')
    return BeautifulSoup(text, 'html.parser')

def date(text):
    m = re.search(r'(\d{2})/(\d{2})/(\d{4})', text)
    return f'{m[3]}-{m[2]}-{m[1]}' if m else None

def members(leg):
    url = BASE + PATH + f'memoriadecomposiciones.do?accion=Ver+resultados&grupo=3&legislatura={leg}&modo=confoto&organo=1001&seleccion=diputadosydiputadas&subseleccion=grupo&subsubseleccion=364'
    s = soup(url); rows = {}
    for a in s.select('a[href]'):
        label = a.get_text(' ', strip=True)
        if 'codmie=' not in a['href'] or not label: continue
        query = parse_qs(urlsplit(a['href']).query); key = query['codmie'][0]
        if 'nlegis' not in query or int(query['nlegis'][0]) != leg: continue
        group = re.search(r'\[([^]]+)\]', label)
        rows.setdefault(key, {'key': key, 'legislature': leg, 'nameInList': label.split('[')[0].strip(), 'listSource': url, 'source': urljoin(url, a['href']), 'groupsInList': []})
        if group and group[1] not in rows[key]['groupsInList']: rows[key]['groupsInList'].append(group[1])
    if len(rows) < 100: raise ValueError(f'Lista incompleta de la legislatura {leg}: {len(rows)}')
    return list(rows.values())

def profile(item):
    s = soup(item['source']); main = s.select_one('#interior-pa') or s
    heading = next((h for h in main.select('h1,h2') if ',' not in h.get_text() and len(h.get_text(' ',strip=True).split()) >= 3), None)
    # La fotografía aporta un identificador y un nombre explícitos.
    image = next((img for img in main.select('img') if 'fotografia.do?' in img.get('src', '') and 'codmie=' + item['key'] in img['src']), None)
    names = [h.get_text(' ', strip=True) for h in main.select('h1,h2,h3,h4') if len(h.get_text(' ',strip=True).split()) >= 3 and not any(w in h.get_text() for w in ['Pertenencia', 'Enlaces', 'Documentación', 'Órganos', 'actualidad'])]
    name = names[0] if names else item['nameInList']
    if not main.select_one('h1') or name == item['nameInList']: raise ValueError('Ficha sin identidad institucional: ' + item['source'])
    text = main.get_text(' ', strip=True)
    place = re.search(r'Circunscripción:\s*([^\n]+?)(?=\s+(?:Datos personales|Intervenciones|Perfiles en|Contactar|Pertenencia|Documentación))', text)
    organs = []
    for table in main.select('table'):
        headers = [h.get_text(' ',strip=True) for h in table.select('thead th')]
        if 'Órgano' not in headers or 'Cargo ocupado' not in headers: continue
        for tr in table.select('tbody tr'):
            cells = tr.select('th,td')
            if len(cells) < 3: continue
            link = cells[0].select_one('a[href]')
            organs.append({'organ': cells[0].get_text(' ',strip=True), 'role': cells[1].get_text(' ',strip=True), 'start': date(cells[2].get_text()), 'endInSource': date(cells[3].get_text()) if len(cells)>3 else None, 'source': item['source'], 'organSource': urljoin(BASE, link['href']) if link else item['source']})
    group = next((h.get_text(' ',strip=True) for h in main.select('h2') if h.get_text(' ',strip=True).startswith(('G.P.', 'Grupo Parlamentario'))), None)
    return {**item, 'name': name, 'constituency': place[1].strip() if place else None, 'groupInProfile': group, 'image': urljoin(BASE, image['src']) if image else None, 'organs': organs, 'checkedAt': CHECKED}

def collect():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        lists = list(pool.map(members, range(1,14)))
    write(CACHE / 'lists.json', lists)
    records = [r for rows in lists for r in rows]
    def safe(item):
        try: return profile(item)
        except Exception as e: return {**item, 'error': str(e)}
    good, errors = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for i, result in enumerate(pool.map(safe, records), 1):
            (errors if 'error' in result else good).append(result)
            if i % 100 == 0:
                write(CACHE/'profiles.json', good); write(CACHE/'errors.json', errors)
                print('Fichas contrastadas', i, '/', len(records), flush=True)
    write(CACHE/'profiles.json',good); write(CACHE/'errors.json',errors)
    print('Legislaturas', len(lists), 'registros', len(records), 'identidades', len({r['key'] for r in records}), 'incidencias', len(errors), flush=True)

if __name__ == '__main__': collect()
