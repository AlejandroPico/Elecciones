"""Recoge el archivo oficial de la Asamblea. Caché local; no publica datos de contacto.

La web principal protege las consultas automatizadas. Se utiliza el portal oficial
de datos abiertos, con TLS verificado por curl/Schannel, sin desactivar certificados.
"""
import concurrent.futures, hashlib, json, pathlib, re, subprocess, sys
from urllib.parse import urlencode, urlparse, parse_qs, urljoin
sys.path.insert(0, 'test-results/libraries')
from bs4 import BeautifulSoup

CACHE = pathlib.Path('test-results/madrid')
CACHE.mkdir(parents=True, exist_ok=True)
BASE = 'https://ctyp.asambleamadrid.es/web/guest'
PORTLET = 'es_satec_liferay_asamblea_ComposicionPortlet_INSTANCE_MA3PIwEgvh0w'
NS = '_' + PORTLET + '_'
PARAMS = dict(p_p_id=PORTLET, p_p_lifecycle='0', p_p_state='normal', p_p_mode='view')
MONTHS = dict(zip(['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'], range(1,13)))
MONTHS.update(dict(zip(['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'],range(1,13))))

def fetch(url):
    path = CACHE / 'pages' / (hashlib.sha256(url.encode()).hexdigest() + '.html')
    if path.exists(): return path.read_text(encoding='utf-8')
    result = subprocess.run(['curl.exe','--fail','--silent','--show-error','--location','--max-time','45',url], capture_output=True, check=True)
    text = result.stdout.decode('utf-8')
    if 'Sucuri' in text or len(text)<1000: raise ValueError('Respuesta no documental: ' + url)
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding='utf-8')
    return text

def soup(url): return BeautifulSoup(fetch(url), 'html.parser')
def date(text):
    m = re.search(r'(\d{1,2})\s+(?:de\s+)?([a-z]+)\.?\s+(?:de\s+)?(\d{4})', text.lower())
    if not m: return None
    return f'{m[3]}-{MONTHS[m[2]]:02d}-{int(m[1]):02d}'
def interval(text):
    pieces = text.replace('\xa0',' ').split(' - ')
    return date(pieces[0]), date(pieces[1]) if len(pieces)>1 else None
def write(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def list_page(leg, page=1, historical=False):
    if historical and leg < 13:
        roman=['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii'][leg-1]
        url=BASE+'/la-asamblea/historia/legislatura-'+roman+'/diputados'
        first=soup(url)
        if page>1:
            link=next(a['href'] for a in first.select('a[href]') if any(k.endswith('paramNumeroDePagina') for k in parse_qs(urlparse(a['href']).query)))
            params=parse_qs(urlparse(link).query)
            pagekey=next(k for k in params if k.endswith('paramNumeroDePagina'))
            params[pagekey]=[str(page)]
            url=link.split('?')[0]+'?'+urlencode(params,doseq=True)
        s=first if page==1 else soup(url)
    else:
        if page==1: q = {**PARAMS,NS+'action':'search',NS+'legislatura':str(leg),NS+'fecha':'',NS+'condicion':'',NS+'isSearch':'true'}
        else: q = {**PARAMS, NS+'paramNumeroDePagina':str(page), NS+'paramFormValues':'SSSSPPPPparamLegislaturaSSSSVVVVPPPP'+str(leg)}
        url = BASE+'/composicion/diputados?'+urlencode(q)
        s = soup(url)
    members={}; pages=[1]
    for a in s.select('a[href]'):
        p=parse_qs(urlparse(a['href']).query)
        if 'diputado' in p:
            key=p['diputado'][0]
            if key not in members: members[key]={'key':key,'name':a.get_text(' ',strip=True),'legislature':leg}
        else:
            pagekey=next((k for k in p if k.endswith('paramNumeroDePagina')),None)
            if pagekey: pages.append(int(p[pagekey][0]))
    # Las primeras legislaturas tienen cobertura desigual en el buscador web.
    # Se conserva el vacío, y se contrasta con las tablas de datos abiertos.
    return list(members.values()), max(pages)

def profile(item):
    key=item['key']; leg=item['legislature']
    url=BASE+f'/composicion/diputados/ficha-del-diputado?diputado={key}&legislatura={leg}'
    s=soup(url); im=s.select_one('img.foto-detalle')
    if not im: raise ValueError('Ficha sin retrato ni identidad: '+key)
    name=im.get('alt') or item['name']
    details=im.parent.parent
    # Información básica: no se recorren los apartados de contactos ni declaraciones.
    info=details.get_text(' ',strip=True).split('Legislaturas')[0]
    birth=date(info)
    education=[]
    header=s.select_one('#formacion')
    if header:
        target=header.select_one('a[data-target]')
        body=s.select_one(target['data-target']) if target else None
        if body:
            text=body.get_text(' ',strip=True)
            for degree, center in re.findall(r'Descripción:\s*(.*?)\s*Centro:\s*(.*?)(?=FOR\.\d+|$)',text):
                education.append({'degree':degree.strip(),'center':center.strip()})
    legs=[]
    for header in s.select('.card-header[id^="legislatura"]'):
        anchor=header.select_one('a[data-target]')
        body=s.select_one(anchor['data-target']) if anchor else None
        if not body: continue
        label=header.get_text(' ',strip=True); roles=[]; groups=[]
        for heading in body.select('.encabezado'):
            title=heading.get_text(' ',strip=True)
            if title not in ['Grupos Parlamentarios','Cargos en la Asamblea']: continue
            entries=heading.find_next_sibling('ul')
            if not entries: continue
            for row in entries.find_all('li',recursive=False):
                r=row.select_one('.rango'); data=row.select_one('.lista-datos')
                if not r or not data: continue
                start,end=interval(r.get_text(' ',strip=True))
                for li in data.select('ul > li'):
                    text=li.get_text(' ',strip=True)
                    if title=='Grupos Parlamentarios': groups.append({'name':text,'start':start,'end':end})
                    else:
                        match=re.fullmatch(r'(.*?)\s*\((.*)\)',text)
                        roles.append({'role':match[1].strip() if match else text,'body':match[2].strip() if match else '', 'start':start,'end':end})
        legs.append({'label':label,'roles':roles,'groups':groups})
    if not legs: raise ValueError('Ficha sin histórico '+key)
    return {'key':key,'name':name,'source':f'https://www.asambleamadrid.es/composicion/diputados/ficha-del-diputado?diputado={key}&legislatura={leg}', 'fetchedFrom':url,'image':urljoin('https://ctyp.asambleamadrid.es',im['src']), 'birthDate':birth,'education':education,'legs':legs}

if __name__=='__main__':
    listed={}; coverage=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        entries=[(leg,historical) for leg in range(1,14) for historical in ([False,True] if leg<13 else [False])]
        first=dict(zip(entries,pool.map(lambda args:list_page(args[0],historical=args[1]),entries)))
        jobs=[(leg,page,historical) for (leg,historical),(members,last) in first.items() for page in range(2,last+1)]
        following=list(pool.map(lambda args:list_page(*args)[0],jobs))
    byleg={leg:[] for leg in range(1,14)}
    for (leg,historical),(members,last) in first.items():byleg[leg].extend(members)
    for (leg,page,historical),members in zip(jobs,following): byleg[leg].extend(members)
    for leg,members in byleg.items():
        unique={m['key']:m for m in members}; coverage.append({'legislature':leg,'profiles':len(unique)})
        for key,item in unique.items():
            if key not in listed or leg>listed[key]['legislature']: listed[key]=item
    write(CACHE/'lists.json',{'coverage':coverage,'people':list(listed.values())})
    print('Listas oficiales:',coverage,'identidades:',len(listed),flush=True)
    profiles=[]; errors=[]
    def safe(item):
        try:return profile(item)
        except Exception as e:return {'key':item['key'],'name':item['name'],'error':str(e)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for i,p in enumerate(pool.map(safe,listed.values()),1):
            (errors if 'error' in p else profiles).append(p)
            if i%50==0: print('Fichas',i,'/',len(listed),'errores',len(errors),flush=True)
    write(CACHE/'profiles.json',profiles);write(CACHE/'errors.json',errors)
    print('Fin:',len(profiles),'fichas;',len(errors),'errores',flush=True)
