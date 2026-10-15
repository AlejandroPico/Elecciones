"""Consulta de fuentes públicas de Aragón; originales en caché de trabajo ignorada."""
import importlib.util,pathlib,json,re,datetime,collections
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin,urlparse,parse_qs
spec=importlib.util.spec_from_file_location('c','Gobiernos/herramientas/consultar-castillas.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
c.CACHE=pathlib.Path('test-results/aragon');c.CHECKED='2026-10-16'
ROOT='https://www.cortesaragon.es/'
_soup=c.soup
def aragon_soup(url):
    if 'cortesaragon.es/'in url:
        # Algunas biografías contienen un byte inválido, aunque la página es
        # UTF-8. No reinterpretar por ello todos los nombres como Windows-1252.
        return c.BeautifulSoup(c.fetch(url).decode('utf8',errors='replace'),'html.parser')
    return _soup(url)
c.soup=aragon_soup
CURRENT=ROOT+'Diputados-y-diputadas.2164.0.html?&no_cache=1'
HISTORY=ROOT+'Anteriores-legislaturas.2357.0.html?&no_cache=1'
def date(s):
    m=re.search(r'(\d{2})/(\d{2})/(\d{2,4})',s)
    if not m:return None
    y=int(m[3]);y=y+(2000 if y<77 else 1900)if y<100 else y
    return datetime.date(y,int(m[2]),int(m[1])).isoformat()
def cards(p,url):
    out=[]
    for box in p.select('#content .team'):
        anchor=box.select_one('.team-title h4 a[href]')
        if not anchor or 'uiddip'not in anchor['href']:continue
        source=urljoin(url,anchor['href']);key=parse_qs(urlparse(source).query)['tx_t3comunicacion_pi3[uiddip]'][0]
        span=box.select_one('.team-title span');h=span.find('h6')if span else None
        dates=re.findall(r'\d{2}/\d{2}/\d{2,4}',h.get_text(' ',strip=True))if h else[]
        if h:h.extract()
        image=box.select_one('.team-image img[src]')
        out.append({'key':key,'name':c.clean(anchor.get_text(' ',strip=True)),'group':c.clean(span.get_text(' ',strip=True))if span else None,'start':date(dates[0])if dates else None,'endInSource':date(dates[1])if len(dates)>1 else None,'source':source,'image':urljoin(url,image['src'])if image else None})
    return out
def listing(leg):
    url=CURRENT if leg==12 else HISTORY+'&tx_t3comunicacion_pi3%5Bnumleg%5D='+str(leg)
    p=c.soup(url);records=cards(p,url);main=p.select_one('#content');links=[]
    for a in main.select('a[href]'):
        href=urljoin(url,a['href']).split('#')[0];txt=c.clean(a.get_text(' ',strip=True))
        if any(k in href for k in ['uidcir','uidgru','uidcom%5D=0','Mesa.2261']):
            row={'label':txt,'source':href}
            if row not in links:links.append(row)
    return {'legislature':leg,'source':url,'records':records,'links':links}
def profile(row):
    try:
        p=c.soup(row['source']);main=p.select_one('#content');head=main.select_one('.promo h3');image=main.select_one('.team-image img[src]')
        header=head.find_next_sibling('span')if head else None
        province=re.search(r'Diputad[oa] por ([^\n]+)',header.get_text('\n',strip=True))if header else None
        bio=[c.clean(x.get_text(' ',strip=True))for x in main.select('.team-content p')if c.clean(x.get_text())]
        # Formación factual breve; no se publican teléfonos, direcciones ni la biografía completa.
        education=[s.strip()for b in bio for s in re.split(r'(?<=[.;])\s+',b)if re.search(r'licenciad|graduad|diplomad|doctorad|ingenier|universidad|bachiller|formación profesional',s,re.I)and len(s)<450 and not re.search(r'@|\d{9}',s)]
        roles=[{'legislature':int(tab['id'][5:]),'title':c.clean(a.get_text(' ',strip=True))}for tab in main.select('div.tab-pane[id^=legis]')for a in tab.select('.list-group-item')]
        return {**row,'nameInProfile':c.clean(head.get_text(' ',strip=True))if head else None,'constituency':c.clean(province[1])if province else None,'image':urljoin(row['source'],image['src'])if image else row.get('image'),'education':education,'roles':roles}
    except Exception as e:return {**row,'sourceError':str(e),'education':[],'roles':[]}
def collect():
    with ThreadPoolExecutor(3)as pool:lists=list(pool.map(listing,range(1,13)))
    c.write(c.CACHE/'listas.json',lists);print('LISTAS',[(r['legislature'],len(r['records']))for r in lists],flush=True)
    requests={link['source']for li in lists for link in li['links']}
    def read(url):
        try:return {'source':url,'records':cards(c.soup(url),url)}
        except Exception as e:return {'source':url,'records':[],'error':str(e)}
    with ThreadPoolExecutor(3)as pool:details=list(pool.map(read,sorted(requests)))
    c.write(c.CACHE/'desgloses.json',details);print('DESGLOSES',len(details),flush=True)
    todo={r['key']:r for li in lists for r in li['records']}
    for li in details:
        for r in li['records']:todo[r['key']]=r
    with ThreadPoolExecutor(3)as pool:profiles=list(pool.map(profile,todo.values()))
    c.write(c.CACHE/'perfiles.json',profiles);print('PERFILES',len(profiles),'ERRORES',sum(bool(p.get('sourceError'))for p in profiles),flush=True)
def inspect(url):
    try:
        p=c.soup(url);main=p.select_one('main')or p
        links=[{'text':c.clean(a.get_text(' ',strip=True)),'url':urljoin(url,a['href'])}for a in main.select('a[href]')]
        c.write(c.CACHE/'inspeccion'/(c.hashlib.sha256(url.encode()).hexdigest()+'.json'),{'source':url,'text':main.get_text(' ',strip=True),'links':links})
        return {'source':url,'text':c.clean(main.get_text(' ',strip=True))[:1800],'links':[a for a in links if re.search(r'legisl|diputad|compos|hist|grupo|mesa|parlament|Perfil|gobierno|presiden',a['text']+' '+a['url'],re.I)][:90]}
    except Exception as e:return {'source':url,'error':str(e)}
if __name__=='__main__':
    import sys
    if '--collect'in sys.argv:collect()
    else:
        for url in sys.argv[1:]:print(json.dumps(inspect(url),ensure_ascii=False),flush=True)
