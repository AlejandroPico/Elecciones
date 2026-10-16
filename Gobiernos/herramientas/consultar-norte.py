"""Fuentes institucionales de País Vasco y Navarra; caché original no publicada."""
import importlib.util, pathlib, re, json, sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
spec=importlib.util.spec_from_file_location('consulta_base',pathlib.Path(__file__).with_name('consultar-castillas.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
c.CACHE=pathlib.Path('test-results/norte');c.CHECKED='2026-10-16'
PV='https://www.legebiltzarra.eus'
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII']

def date(value):
    m=re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})',value)
    if not m:return None
    year=int(m[3]);year+=2000 if year<70 else 1900 if year<100 else 0
    import datetime
    return datetime.date(year,int(m[2]),int(m[1])).isoformat()

def basque_rows(url):
    p=c.soup(url);rows=[]
    for table in p.select('table.parlamentarios'):
        section=None
        for tr in table.select('tr'):
            head=tr.select_one('th.nivelx')
            if head:section=c.clean(head.get_text(' ',strip=True))
            name=tr.select_one('.miembro_persona a[href]')
            if not name:continue
            cells=tr.select('td');span=tr.select_one('.miembro_cargo');group=tr.select_one('.miembro_grupo')
            ds=re.findall(r'\d{1,2}\.\d{1,2}\.\d{4}',span.get_text(' ',strip=True)if span else'')
            source=urljoin(url,name['href']);key=re.search(r'c_(\d+)\.html',source)[1]
            ordered=c.clean(name.get_text(' ',strip=True));surname,first=ordered.split(',',1)
            rows.append({'key':key,'name':c.clean(first+' '+surname),'source':source,'group':c.clean(group.get_text(' ',strip=True))if group else None,'start':date(ds[0])if ds else None,'end':date(ds[1])if len(ds)>1 else None,'section':section,'listSource':url})
    assert rows,'Sin filas parlamentarias: '+url
    return rows

def basque_profile(row):
    p=c.soup(row['source']);box=p.select_one('.ficha-personal-int');assert box,row['source']
    name=box.select_one('.ficha_datos strong');ordered=c.clean(name.get_text(' ',strip=True))
    surname,first=ordered.split(',',1);im=box.select_one('.ficha_foto img[src]');details={}
    for dt in box.select('dt'):
        dd=dt.find_next_sibling('dd');key=c.clean(dt.get_text()).strip(' :')
        if dd and key in ['Titulación','Profesión','Idiomas']:details[key]=c.clean(dd.get_text(' ',strip=True))
    return {**row,'name':c.clean(first+' '+surname),'image':urljoin(row['source'],im['src'])if im else None,'details':details}

def collect_basque():
    lists=[];todo={}
    for i in range(1,14):
        code='LGA'if i==13 else f'L{i:02}'
        url=f'{PV}/comparla/c_comparla_alf_{code}.html';board=f'{PV}/comorga/c_comorga_mes_{code}.html'
        rows=basque_rows(url);mesa=basque_rows(board)
        lists.append({'legislature':i,'source':url,'records':rows,'boardSource':board,'board':mesa})
        for row in [*rows,*mesa]:todo[row['key']]=row
        print('EUSKADI',i,len(rows),'Mesa',len(mesa),flush=True)
    current=basque_rows(PV+'/comparla/c_comparla_alf_ACT.html');assert len(current)==75
    c.write(c.CACHE/'pais-vasco-listas.json',lists);c.write(c.CACHE/'pais-vasco-actual.json',current)
    profiles=[]
    def profile(row):
        try:return basque_profile(row)
        except Exception as error:return {**row,'error':str(error)}
    with ThreadPoolExecutor(4)as pool:
        for i,row in enumerate(pool.map(profile,todo.values())):
            profiles.append(row)
            if(i+1)%50==0:c.write(c.CACHE/'pais-vasco-perfiles.json',profiles);print('PERFILES EUSKADI',i+1,flush=True)
    c.write(c.CACHE/'pais-vasco-perfiles.json',profiles);print('PERFILES EUSKADI',len(profiles),'errores',sum('error'in p for p in profiles),flush=True)

def collect_basque_territories():
    """Sigue las áreas del mapa oficial; no asigna territorios a partir del partido."""
    def collect(code):
        url=PV+'/c_comparla_ter_'+code+'.html';page=c.soup(url);rows=[]
        for area in page.select('map[name="Territorios"] area[href]'):
            source=urljoin(url,area['href']);territory=area['alt']
            for row in basque_rows(source):rows.append({**row,'territory':territory,'territorySource':source})
        assert rows,(code,'Sin circunscripciones')
        return code,rows
    codes=['ACT','LGA',*[f'L{i:02}'for i in range(1,13)]]
    with ThreadPoolExecutor(4)as pool:data=dict(pool.map(collect,codes))
    lists=json.loads((c.CACHE/'pais-vasco-listas.json').read_text('utf8'))
    for li in lists:
        code='LGA'if li['legislature']==13 else f"L{li['legislature']:02}"
        by_key={r['key']:r for r in data[code]}
        for row in li['records']:
            if row['key']in by_key:
                row.update({k:by_key[row['key']][k]for k in ['territory','territorySource']})
    c.write(c.CACHE/'pais-vasco-listas.json',lists)
    c.write(c.CACHE/'pais-vasco-circunscripciones.json',data)
    print('CIRCUNSCRIPCIONES',len(data),'relaciones territoriales',flush=True)

NAV='https://parlamentodenavarra.es'
NAV_YEARS=[1979,1983,1987,1991,1995,1999,2003,2007,2011,2015,2019,2023]
def navarra_publications(year):
    files={}
    for month in ([4,5,6]if year==1979 else[6,7]):
        url=f'{NAV}/es/calendar-details/calendario_boletines_parlamento/{year}-{month:02}/undefined'
        data=json.loads(c.fetch(url));p=c.BeautifulSoup(data.get('view',''),'html.parser')
        for box in p.select('.lista-publicaciones'):
            link=next((a for a in box.select('a[href]')if '/boletines/'in a['href']and a['href'].endswith('.pdf')),None)
            if link:
                d=box.select_one('[content]');files[link['href']]={'source':link['href'],'publishedAt':d['content'][:10]if d else None}
    return {'year':year,'files':list(files.values())}

def navarra_profile(row):
    p=c.soup(row['source']);image=p.select_one('img[src*="fichas-personas"]');details=[]
    for tr in p.select('table.views-table tbody tr'):
        cells=tr.find_all('td',recursive=False)
        if len(cells)not in [3,4]:continue
        dates=cells[2].select('[content]');start=dates[0]['content'][:10]if dates else None
        end=dates[-1]['content'][:10]if len(dates)>1 else None
        if len(cells)==4:
            last=cells[3].select_one('[content]');end=last['content'][:10]if last else end
        details.append({'role':c.clean(cells[0].get_text(' ',strip=True)),'organ':c.clean(cells[1].get_text(' ',strip=True)),'start':start,'end':end})
    # Solamente formación breve y atributos profesionales; nunca declaraciones ni contactos.
    education=[]
    for paragraph in p.select('.region-content p'):
        text=c.clean(paragraph.get_text(' ',strip=True))
        if len(text)<650 and re.search(r'licenciad|graduad|diplomad|doctorad|ingenier|universidad|máster|formación profesional',text,re.I)and not re.search(r'declaracion|@|\d{9}',text,re.I):education.append(text)
    src=urljoin(row['source'],image['src'])if image else None
    if src:src=re.sub(r'/styles/[^/]+/public/','/',src).split('?')[0]
    return {**row,'name':image.get('alt')if image and image.get('alt')else row['name'],'image':src,'roles':details,'education':education}

def collect_navarra():
    url=NAV+'/composicion-organos/parlamentarios-forales';p=c.soup(url);rows={}
    for a in p.select('a[href*="/persona/"]'):
        label=c.clean(a.get_text(' ',strip=True))
        if not label:continue
        surname,first=label.split(',',1);source=urljoin(url,a['href']);rows[source]={'source':source,'name':c.clean(first+' '+surname)}
    assert len(rows)==50,len(rows)
    with ThreadPoolExecutor(4)as pool:profiles=list(pool.map(navarra_profile,rows.values()))
    c.write(c.CACHE/'navarra-perfiles-actuales.json',profiles)
    with ThreadPoolExecutor(3)as pool:documents=list(pool.map(navarra_publications,NAV_YEARS))
    c.write(c.CACHE/'navarra-boletines-indice.json',documents)
    import pymupdf
    selected=[]
    for i,year in enumerate(NAV_YEARS):
        li=next(r for r in documents if r['year']==year)
        pattern=rf'B{year}{i}0+1\.pdf$'
        choices=[r for r in li['files']if re.search(pattern,r['source'])]
        if year==1979:choices=[{'source':NAV+'/sites/default/files/memorias-actividad/Memoria%201979-1981.pdf','publishedAt':None}]
        for row in choices:
            doc=pymupdf.open(stream=c.fetch(row['source']),filetype='pdf');text='\n'.join(p.get_text(sort=True)for p in doc)
            c.write(c.CACHE/'boletines'/f'{year}-{i}.json',{**row,'legislature':i,'text':text,'pages':[p.get_text(sort=True)for p in doc]})
            selected.append({**row,'legislature':i,'pages':len(doc)})
        print('NAVARRA BOLETINES',year,len(li['files']),'seleccionados',len(choices),flush=True)
    c.write(c.CACHE/'navarra-boletines-seleccionados.json',selected);print('NAVARRA PERFILES ACTUALES',len(profiles),flush=True)

def inspect(url):
    p=c.soup(url);main=p.select_one('main')or p.select_one('#content')or p
    links=[{'text':c.clean(a.get_text(' ',strip=True)),'url':urljoin(url,a['href'])}for a in main.select('a[href]')]
    out={'source':url,'text':main.get_text('\n',strip=True),'links':links}
    c.write(c.CACHE/'inspeccion'/(c.hashlib.sha256(url.encode()).hexdigest()+'.json'),out)
    return {'source':url,'text':out['text'][:3000],'links':[r for r in links if re.search(r'parlam|legis|mesa|gobierno|presiden|diputad|composi|miembro|anterior|pleno',r['text']+' '+r['url'],re.I)][:110]}

if __name__=='__main__':
    if '--territorios'in sys.argv:collect_basque_territories();sys.exit()
    if '--pais-vasco'in sys.argv:collect_basque();sys.exit()
    if '--navarra'in sys.argv:collect_navarra();sys.exit()
    for url in sys.argv[1:]:
        try:print(json.dumps(inspect(url),ensure_ascii=False),flush=True)
        except Exception as error:print(json.dumps({'source':url,'error':str(error)},ensure_ascii=False),flush=True)
