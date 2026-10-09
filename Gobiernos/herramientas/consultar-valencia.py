"""Consulta las fuentes públicas valencianas con caché y TLS verificado.

La caché de documentos no forma parte del catálogo publicado. No recopilar
contactos personales ni declaraciones patrimoniales.
"""
import concurrent.futures, datetime, hashlib, json, pathlib, re, subprocess, sys
from urllib.parse import urljoin
sys.path.insert(0, 'test-results/libraries')
from bs4 import BeautifulSoup

CACHE = pathlib.Path('test-results/valencia')
BASE = 'https://www.cortsvalencianes.es'
CHECKED = '2026-10-09'

def fetch(url, suffix='.html'):
    path = CACHE/'documents'/(hashlib.sha256(url.encode()).hexdigest()+suffix)
    if not path.exists():
        result = subprocess.run(['curl.exe','--fail','--silent','--show-error','--location','--max-time','60',url],capture_output=True,check=True)
        if not result.stdout: raise ValueError('Documento vacío: '+url)
        path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(result.stdout)
    return path.read_bytes()

def soup(url): return BeautifulSoup(fetch(url).decode('utf-8'),'html.parser')
def write(path,data):
    path=pathlib.Path(path); text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if path.exists() and path.read_text(encoding='utf-8')==text:return
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')

ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI']
def date(text):
    m=re.search(r'(\d{2})-(\d{2})-(\d{4})',text)
    return f'{m[3]}-{m[2]}-{m[1]}' if m else None

def members(roman, historic=True):
    url=BASE+'/es/composicion/diputados?legislature='+roman+('&historic=1' if historic else '')
    s=soup(url);rows=[]
    for tr in s.select('table tbody tr'):
        td=tr.select('td')
        if len(td)<4: continue
        a=td[1].select_one('a[href]');gp=td[2].select_one('img');link=td[2].select_one('a[href]')
        if not a:continue
        url_person=urljoin(BASE,a['href']);key=url_person.rsplit('/',1)[1]
        rows.append({'key':key,'legislature':roman,'nameInList':a.get_text(' ',strip=True),'source':url_person,'listSource':url,'constituency':td[3].get_text(' ',strip=True),'group':(gp.get('alt','').removeprefix('Foto de ') if gp else td[2].get_text(' ',strip=True)),'groupSource':urljoin(BASE,link['href']) if link else url,'start':date(td[4].get_text()) if len(td)>4 else None,'endInclusive':date(td[5].get_text()) if len(td)>5 else None,'image':urljoin(BASE,tr.select_one('img')['src']) if tr.select_one('img') else None})
    if not rows:raise ValueError('Lista sin registros: '+url)
    return rows

def profile(item):
    s=soup(item['source']);main=s.select_one('.deputy-main-info')
    if not main:raise ValueError('Ficha sin identidad: '+item['source'])
    name=main.select_one('h2').get_text(' ',strip=True);birth=main.select_one('.deputy-birth');birthText=birth.get_text(' ',strip=True) if birth else ''
    birthPlace=re.split(r'\s+en\s+',birthText,maxsplit=1)[1].strip() if re.search(r'\s+en\s+',birthText) else None
    if birthPlace and not re.search(r'\w',birthPlace):birthPlace=None
    image=main.select_one('img');education=[];politicalText='';committees=[]
    # Extraer titulaciones breves, no copiar biografías ni información privada.
    for heading in s.find_all(['h2','h3','h4']):
        if 'Formación y actividad profesional' not in heading.get_text():continue
        container=heading.parent
        for line in container.get_text('\n',strip=True).splitlines():
            if re.search(r'licenciad|llicenciat|licenciat|licenciatura|diplomad|diplomat|diplomatura|graduad|graduat|grau en|grado en|doctorad|doctorat|ingenier|enginyer|máster|màster|master|bachiller|batxiller|formación profesional|formació professional',line,re.I) and 12<len(line)<240:
                if line not in education:education.append(line)
    for h in s.find_all(['h2','h3','h4']):
        if 'Trayectoria política e institucional' in h.get_text():politicalText=h.parent.get_text(' ',strip=True)
        if 'Listado de comisiones' in h.get_text():committees=list(dict.fromkeys(a.get_text(' ',strip=True) for a in h.parent.select('a[href]') if a.get_text(' ',strip=True).startswith('Comis')))
    return {'key':item['key'],'legislature':item['legislature'],'name':name,'source':item['source'],'birthDate':date(birthText),'birthPlace':birthPlace,'education':education[:6],'image':urljoin(BASE,image['src']) if image else None,'politicalText':politicalText,'committees':committees,'checkedAt':CHECKED}

def collect():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        lists=list(pool.map(members,ROMANS))
    current=members('XI',False);write(CACHE/'lists.json',lists);write(CACHE/'current-members.json',current)
    latest={}
    for rows in lists:
        for row in rows:latest[row['key']]=row
    good=[];errors=[]
    def safe(item):
        try:return profile(item)
        except Exception as e:return {'key':item['key'],'name':item['nameInList'],'source':item['source'],'error':str(e)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for i,result in enumerate(pool.map(safe,latest.values()),1):
            (errors if 'error' in result else good).append(result)
            if i%50==0:print('Fichas consultadas',i,'/',len(latest),flush=True)
    write(CACHE/'profiles.json',good);write(CACHE/'errors.json',errors)
    print('Registros',sum(map(len,lists)),'identidades',len(latest),'fichas',len(good),'vigentes',len(current),'errores',len(errors),flush=True)

if __name__=='__main__':
    collect()
