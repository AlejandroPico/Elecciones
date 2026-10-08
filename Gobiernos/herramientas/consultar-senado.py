"""Consulta las composiciones y mandatos del Senado desde 1977.

Fuentes públicas, consultas espaciadas y reanudables. No recoge contactos,
declaraciones patrimoniales ni información familiar. Los HTML de trabajo son
ignorados por Git; las composiciones contrastadas se guardan en Gobiernos/Senado.
"""
import pathlib, sys, json, re, urllib.request, urllib.parse, time, threading
import concurrent.futures, hashlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'test-results/libraries'))
from bs4 import BeautifulSoup
CACHE = ROOT/'test-results/senado-estructura'
CACHE.mkdir(parents=True, exist_ok=True)
DATE = '2026-10-08'
HOST = 'https://www.senado.es'
lock = threading.Lock()
last = 0
stop = threading.Event()

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8', newline='\n')

def fetch(url):
    global last
    if stop.is_set(): raise RuntimeError('Fuente en pausa')
    with lock:
        time.sleep(max(0, .25-(time.monotonic()-last)))
        last=time.monotonic()
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read(3000000)
    except urllib.error.HTTPError as e:
        if e.code == 429: stop.set()
        raise

def page(url, name):
    path=CACHE/(name+'.html')
    if not path.exists(): path.write_bytes(fetch(url))
    return BeautifulSoup(path.read_text('utf8'), 'html.parser')

def dmy(text):
    m=re.search(r'(\d{2})/(\d{2})/(\d{4})', text)
    return '-'.join([m[3],m[2],m[1]]) if m else None

def identity(a):
    q=urllib.parse.parse_qs(urllib.parse.urlparse(a['href']).query)
    return q.get('id1',[''])[0]

jobs={}
legislatures=[]
for leg in range(15,-1,-1):
    rosterUrl=HOST+'/web/composicionorganizacion/senadores/composicionsenado/senadoresdesde1977/consultaorden/index.html?legis='+str(leg)+'&lang=es_ES'
    roster=page(rosterUrl, 'pleno-'+str(leg))
    option=roster.select_one('select[name="legis"] option[value="'+str(leg)+'"]')
    # La Mesa ofrece límites explícitos de la legislatura.
    mesaUrl=HOST+'/web/composicionorganizacion/organossenado/mesa/composicion/index.html?legis='+str(leg)+'&order=C'
    mesa=page(mesaUrl, 'mesa-'+str(leg))
    option=mesa.select_one('select[name="legis"] option[value="'+str(leg)+'"]')
    label=option.get_text(' ',strip=True)
    dates=re.findall(r'\d{2}/\d{2}/\d{4}', label)
    members={}
    for a in roster.select('a[href*="fichasenador/index.html"]'):
        sid=identity(a)
        if not sid:continue
        q=urllib.parse.parse_qs(urllib.parse.urlparse(a['href']).query)
        if str(leg)!=q.get('legis',[''])[0]:continue
        name=a.get_text(' ',strip=True)
        if not name or not ',' in name:continue
        members[sid]={'senateId':sid,'institutionalName':name}
        jobs[(sid,leg)]={'id':sid,'leg':leg,'name':name}
    if len(members)<100:raise ValueError('Lista de senadores incompleta: '+str(leg))
    board=[]
    for a in mesa.select('a[href*="fichasenador/index.html"]'):
        sid=identity(a)
        if not sid:continue
        block=a.find_parent('div').find_parent('div').find_parent('div')
        h=block.find(['h3','h4'])
        if h:board.append({'senateId':sid,'role':h.get_text(' ',strip=True)})
    groups=[]
    currentGroup=''
    for a in roster.select('a[href*="fichasenador/index.html"]'):
        sid=identity(a)
        if sid not in members:continue
        li=a.find_parent('li')
        text=li.get_text(' ',strip=True) if li else ''
        match=re.search(r'((?:G[A-ZÀ-Ü0-9_-]+)\s*\([^)]*\))', text)
        if match:members[sid]['group']=match[1]
    legislatures.append({'number':leg,'label':label.split('(')[0].strip(),'start':dmy(dates[0]),'end':dmy(dates[1]),'source':rosterUrl,'mesaSource':mesaUrl,'board':board,'members':list(members.values())})
    print('Legislatura',leg,len(members),'senadores',flush=True)
save(CACHE/'legislaturas.json',legislatures)

def senator(row):
    sid,leg=row['id'],row['leg'];path=CACHE/'mandatos'/f'{sid}-{leg}.json'
    if path.exists() and not json.loads(path.read_text('utf8')).get('error'):return
    url=HOST+'/web/composicionorganizacion/senadores/composicionsenado/fichasenador/index.html?id1='+sid+'&legis='+str(leg)+'&lang=es_ES'
    result={**row,'source':url,'checkedAt':DATE}
    try:
        raw=fetch(url);s=BeautifulSoup(raw.decode('utf8'),'html.parser')
        meta=s.find('meta',attrs={'name':'Nombre'})
        if not meta:raise ValueError('Identidad no localizada')
        result['institutionalName']=meta.get('content','')
        general=s.select_one('.caja5-4')
        if general:
            result['credential']=[li.get_text(' ',strip=True) for li in general.select('li')]
        result['offices']=[]
        for h in s.select('#panel1 h5'):
            text=h.get_text(' ',strip=True)
            match=re.search(r'\((\d{2}/\d{2}/\d{4})\s+al\s+(\d{2}/\d{2}/\d{4})\)',text)
            title=text[:match.start()].strip() if match else text
            if '.' not in title:continue
            role,organ=title.split('.',1)
            result['offices'].append({'role':role.strip(),'organ':organ.strip(),'start':dmy(match[1]) if match else None,'end':dmy(match[2]) if match else None,'current':not bool(match)})
        # Formatos históricos de tabla que también publica la cámara.
        for tr in s.select('#panel1 table tr'):
            cells=[td.get_text(' ',strip=True) for td in tr.find_all('td')]
            if len(cells)>=4:result['offices'].append({'organ':cells[0],'role':cells[1],'start':dmy(cells[2]),'end':dmy(cells[3]),'current':not dmy(cells[3])})
        party=s.find('meta',attrs={'name':'Partido politico'})
        result['party']=party.get('content','') if party else None
        result['sha256']=hashlib.sha256(raw).hexdigest()
    except Exception as e:result['error']=str(e)
    if not stop.is_set():save(path,result)

if len(sys.argv)>1:
    requested=set(sys.argv[1:])
    jobs={key:row for key,row in jobs.items() if str(key[0])+'-'+str(key[1]) in requested}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for i,_ in enumerate(pool.map(senator,jobs.values()),1):
        if i%200==0:print('Mandatos consultados',i,'/',len(jobs),flush=True)
        if stop.is_set():break
print('Consulta terminada; incidencias pendientes se pueden reintentar.',flush=True)
