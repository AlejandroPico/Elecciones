"""Consulta pública del Parlament y sus dossiers. Caché de trabajo fuera del catálogo.
No copia contactos, declaraciones patrimoniales ni agendas personales.
"""
import concurrent.futures, hashlib, json, pathlib, re, sys, time, urllib.request
from urllib.parse import urljoin, parse_qs, urlparse
sys.path.insert(0, 'test-results/libraries')
from bs4 import BeautifulSoup

ROOT = pathlib.Path('test-results/catalunya')
CACHE = ROOT / 'cache'
CACHE.mkdir(parents=True, exist_ok=True)
BASE = 'https://www.parlament.cat'
def fetch(url):
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.html')
    if path.exists(): return BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Elecciones institutional archive)'})
            response = urllib.request.urlopen(request, timeout=45)
            text = response.read().decode(response.headers.get_content_charset() or ('latin1' if 'parlament.cat' in url else 'utf-8'))
            path.write_text(text, encoding='utf-8')
            time.sleep(.08)
            return BeautifulSoup(text, 'html.parser')
        except Exception:
            if attempt == 2: raise
            time.sleep(1 + attempt)
def save(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def name(text):
    return re.sub(r'^(?:(?:M\.\s*H\.|H\.|I\.|Excm\.|Il·lm\.)\s*)?(?:Sra?\.\s*)?', '', text).strip()
def date(text):
    m = re.search(r'(\d{1,2})[/.](\d{1,2})[/.](\d{4})', text)
    return f'{m[3]}-{int(m[2]):02}-{int(m[1]):02}' if m else None
def records(b):
    output = []
    for a in b.select('li strong a[href*="diputats-fitxa"]'):
        li = a.find_parent('li'); text = li.get_text(' ', strip=True)
        dd = li.find_parent('dd'); dt = dd.find_previous_sibling('dt') if dd else None
        output.append({'name': name(a.get_text(' ',strip=True)), 'url': urljoin(BASE, a['href']),
          'key': parse_qs(urlparse(a['href']).query)['p_codi'][0],
          'role': dt.get_text(' ',strip=True) if dt else '',
          'start': date(text.split('Alta:',1)[-1]) if 'Alta:' in text else None,
          'end': date(text.split('Baixa:',1)[-1]) if 'Baixa:' in text else None})
    return output
def legislature(url):
    b = fetch(url); text = b.get_text(' ',strip=True)
    label = b.select_one('h1').get_text(' ',strip=True)
    start = date(text.split('Data de constitució:',1)[-1]); end = date(text.split('Data de dissolució:',1)[-1])
    ple_url = urljoin(BASE, next(a['href'] for a in b.select('a[href]') if a.get_text(' ',strip=True)=='Ple del Parlament'))
    members = records(fetch(ple_url))
    groups=[]
    for a in b.select('a[href*="historial-grups"]'):
        group_url=urljoin(BASE,a['href'])
        groups.append({'name':a.get_text(' ',strip=True), 'source':group_url, 'members':records(fetch(group_url))})
    print('Legislatura', label, 'registros', len(members), 'grupos',len(groups),flush=True)
    return {'label':label,'start':start,'end':end,'source':url,'plenarySource':ple_url,'records':members,'groups':groups}
def current():
    url=BASE+'/web/composicio/ple-parlament/index.html'; b=fetch(url)
    entries=[];groups={}
    for a in b.select('h2 a[href*="diputats-fitxa"]'):
        li=a.find_parent('li'); paragraphs=li.select('p'); texts=[p.get_text(' ',strip=True) for p in paragraphs]
        group=texts[-1] if texts else ''; image=li.select_one('img')
        item={'name':name(a.get_text(' ',strip=True)), 'url':urljoin(BASE,a['href']), 'key':parse_qs(urlparse(a['href']).query)['p_codi'][0], 'role':texts[1] if len(texts)>2 else 'Diputats','group':group,'image':image.get('src','').strip() if image else None}
        entries.append(item);groups.setdefault(group,[]).append(item)
    return {'label':'XV legislatura', 'start':'2024-06-10','end':None,'source':url,'plenarySource':url,'records':entries,'groups':[{'name':g,'source':url,'members':m} for g,m in groups.items()]}
def profile(url):
    b=fetch(url);h1=b.select_one('h1');image=b.select_one('img.foto_fitxa') or b.select_one('img')
    sections={}
    for h in b.select('h2,h3'):
        title=h.get_text(' ',strip=True)
        if not any(t in title.lower() for t in ['biografia','naixement','formació','trajectòria','filiació']):continue
        parts=[]
        for sibling in h.next_siblings:
            if getattr(sibling,'name',None) in ['h2','h3']:break
            if hasattr(sibling,'get_text'):parts.append(sibling.get_text(' ',strip=True))
        sections[title]=' '.join(parts)
    return {'name':name(h1.get_text(' ',strip=True)) if h1 else '', 'url':url, 'image':image.get('src','').strip() if image else None,'sections':sections}
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    mode=sys.argv[1] if len(sys.argv)>1 else 'legislatures'
    if mode=='legislatures':
        b=fetch(BASE+'/web/composicio/legislatures-anteriors/index.html')
        urls=[urljoin(BASE,a['href']) for a in b.select('h2 a[href]')]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: legs=list(pool.map(legislature,urls))
        legs.insert(0,current());save('parlament-raw.json',legs)
    elif mode=='profiles':
        legs=json.loads((ROOT/'parlament-raw.json').read_text(encoding='utf-8'))
        latest={}
        for leg in legs:
            for r in leg['records']: latest.setdefault(r['key'],r['url'])
        urls=list(latest.values())
        # Una ficha por identificador, de la legislatura más reciente de esa persona.
        # Los intervalos históricos proceden de los registros de cada legislatura.
        output=[]
        def read(url):
            try:return profile(url)
            except Exception as error:return {'url':url,'error':str(error)}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            for i,item in enumerate(pool.map(read,urls)):
                output.append(item)
                if i%100==0:save('profiles.json',output);print('Fichas',i+1,'/',len(urls),flush=True)
        save('profiles.json',output);print('Finalizado',len(output),flush=True)
