"""Consulta fuentes públicas; conserva fechas desconocidas y omite contactos y bienes."""
import concurrent.futures, hashlib, json, pathlib, re, sys, urllib.request
from urllib.parse import urljoin
sys.path.insert(0, 'test-results/libraries')
from bs4 import BeautifulSoup

CACHE = pathlib.Path('test-results/atlantico')
CHECKED = '2026-10-12'
MONTHS = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']

def write(path, data):
    path = pathlib.Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    value = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if not path.exists() or path.read_text('utf8') != value: path.write_text(value, 'utf8')

def fetch(url):
    path = CACHE/'documents'/hashlib.sha256(url.encode()).hexdigest()
    if not path.exists():
        request = urllib.request.Request(url, headers={'User-Agent':'Elecciones/1.0 (consulta de fuentes institucionales)'})
        raw = urllib.request.urlopen(request, timeout=35).read()
        path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
    return path.read_bytes()

def soup(url):
    raw = fetch(url)
    try: text = raw.decode('utf8')
    except UnicodeDecodeError: text = raw.decode('latin1')
    return BeautifulSoup(text, 'html.parser')

def date(text):
    match = re.search(r'(\d{1,2}) de ([a-z]+) de (\d{4})', text.lower())
    return f'{match[3]}-{MONTHS.index(match[2])+1:02}-{int(match[1]):02}' if match and match[2] in MONTHS else None

def canary_list(leg):
    url = f'https://www.parcan.es/composicion/diputados/busqueda_alfabetico/{leg}/'
    page = soup(url); main = page.select_one('main') or page
    rows = {}
    for link in main.select('a[href]'):
        match = re.fullmatch(r'/composicion/diputados/diputado/(\d+)/',link['href'])
        if not match: continue
        parent = link.find_parent('tr'); cells = parent.select('td') if parent else []
        rows[match[1]] = {'key':match[1], 'legislature':leg, 'nameInList':link.get_text(' ',strip=True), 'source':urljoin(url,link['href']), 'groupInList':cells[-1].get_text(' ',strip=True) if cells else None, 'listSource':url}
    return list(rows.values())

def canary_profile(row):
    main = soup(row['source']).select_one('main')
    if main is None: raise ValueError('Ficha sin contenido: '+row['source'])
    heading = main.select_one('h1'); name = re.sub(r'^(?:Excmo\.|Excma\.|Ilmo\.|Ilma\.)\s+(?:Sr\.|Sra\.)\s*','',heading.get_text(' ',strip=True)).strip()
    text = main.get_text(' ',strip=True)
    place = re.search(r'Circunscripción de:\s*(.+?)\s+Grupo parlamentario:',text)
    group = re.search(r'Grupo parlamentario:\s*(.+?)(?=\s+(?:Alta|Baja) en el cargo:|\s+&nbsp|\s+Escribir)',text)
    start = re.search(r'Alta en el cargo:\s*(\d+ de \w+ de \d{4})',text)
    end = re.search(r'Baja en el cargo:\s*(\d+ de \w+ de \d{4})',text)
    image = next((i for i in main.select('img[src]') if '/diputados/images/' in i['src']), None)
    role = main.select_one('h2')
    bio = row['source']+'biografia/'
    result = {**row,'name':name,'role':role.get_text(' ',strip=True) if role else 'Diputado/a', 'start':date(start[1]) if start else None,'endInSource':date(end[1]) if end else None,'group':group[1].strip() if group else None,'constituency':place[1].strip() if place else None,'image':urljoin(row['source'], image['src']) if image else None,'checkedAt':CHECKED,'biographySource':bio}
    # Solo se conservan hechos académicos breves, no una biografía entera.
    try:
        b = soup(bio).select_one('main'); academic=[]
        for node in b.select('p,li'):
            line=node.get_text(' ',strip=True)
            if re.search(r'^(?:Licenciad[oa]|Licenciatura|Diplomad[oa]|Diplomatura|Graduad[oa]|Grado en|Doctor[ao]? en|Ingenier[oa]|Arquitect[oa]|Máster|Master|Maestr[oa]|Técnic[oa])\b',line,re.I) and len(line)<220:academic.append(line)
        result['education']=list(dict.fromkeys(academic))[:5]
    except Exception as error: result['biographyError']=str(error)
    return result

def collect_canarias():
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        rows=[item for result in pool.map(canary_list,range(4,12)) for item in result]
    write(CACHE/'canarias-listas.json',rows)
    def safe(row):
        try: return canary_profile(row)
        except Exception as error: return {**row,'error':str(error)}
    with concurrent.futures.ThreadPoolExecutor(6) as pool:
        records=[]
        for index,row in enumerate(pool.map(safe,rows),1):
            records.append(row)
            if index%100==0:write(CACHE/'canarias-perfiles.json',records);print('Canarias',index,'/',len(rows),flush=True)
    write(CACHE/'canarias-perfiles.json',records)
    print('Canarias, errores:',sum('error' in r for r in records),flush=True)

if __name__=='__main__':collect_canarias()
