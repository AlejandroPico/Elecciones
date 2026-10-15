"""Gobiernos y Mesas: fuentes nominales, decretos presidenciales y cuadros históricos."""
import importlib.util,io,json,re,sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
spec=importlib.util.spec_from_file_location('consulta','Gobiernos/herramientas/consultar-castillas.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
from bs4 import BeautifulSoup
from pypdf import PdfReader
MONTHS=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
def spanish(text):
    m=re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',text,re.I)
    return f'{m[3]}-{MONTHS.index(m[2].lower())+1:02}-{int(m[1]):02}'if m and m[2].lower()in MONTHS else None
def text(url):
    raw=c.fetch(url)
    if raw.startswith(b'%PDF'):return ' '.join(p.extract_text()or''for p in PdfReader(io.BytesIO(raw)).pages)
    return c.soup(url).get_text(' ',strip=True)
def presidencies(region,number):
    url=f'https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_{number}'
    page=c.soup(url);rows=[]
    for h in page.select('h3'):
        name=re.sub(r'\s*\([^)]*\)','',c.clean(h.get_text(' ',strip=True))).strip()
        p=h.find_next('p')
        if p is None or 'Nombramiento:' not in p.get_text():continue
        a=p.find('a',href=True)
        if a is None:continue
        date=spanish(p.get_text(' ',strip=True))
        if not date:raise ValueError(p.get_text())
        source=urljoin(url,a['href']);original=text(source)
        if not re.search(r'nombra[r]?\s+President',original,re.I):raise ValueError('No es nombramiento '+source)
        rows.append({'name':name,'date':date,'source':source,'dossier':url,'title':c.clean(p.get_text(' ',strip=True))})
    c.write(c.CACHE/f'{region}-presidencias.json',sorted(rows,key=lambda r:r['date']));print(region,'presidencias',len(rows),flush=True)
def current_clm():
    url='https://castillalamancha.es/gobierno';p=c.soup(url);main=p.select_one('main') or p
    rows=[]
    # Cada tarjeta del directorio contiene una foto nominal, un encabezado y sus enlaces.
    for image in main.select('img[data-src]'):
        parent=image
        for _ in range(8):
            parent=parent.parent
            if parent is None:break
            links=[a for a in parent.select('a[href]')if '/gobierno/'in a['href']]
            if links and len(parent.select('img[data-src]'))==1:
                txt=c.clean(parent.get_text(' ',strip=True));head=parent.select_one('h2,h3,h4')
                if head and ('Consejer' in txt or 'Vicepresid' in txt or 'Presidente' in txt):
                    rows.append({'text':txt,'heading':head.get_text(' ',strip=True),'image':urljoin(url,image['data-src']),'source':urljoin(url,links[0]['href'])});break
    c.write(c.CACHE/'clm-gobierno-vigente.json',rows);print('clm gobierno',len(rows),flush=True)
def current_cyl():
    records=[]
    for offset in [0,100]:
        url=f'https://analisis.datosabiertos.jcyl.es/api/explore/v2.1/catalog/datasets/altos-cargos/records?limit=100&offset={offset}'
        data=json.loads(c.fetch(url));records.extend(data['results'])
    wanted=[r for r in records if re.match(r'^(?:Presidente de la Junta|Vicepresident[ae]|Consejer[oa]\b)',r['titulo']or'')and 'Consultivo'not in (r['titulo']or'')]
    # Campos públicos de trayectoria y formación; no se copian retribuciones ni contactos.
    out=[{k:r.get(k)for k in ['titulo','nombre','directorio','fotografia','experienciaprofesional','fechaposesion','formacionacademica','lugarnacimiento','identificador','enlace_al_contenido']}for r in wanted]
    c.write(c.CACHE/'cyl-gobierno-vigente.json',out);print('cyl gobierno',[(r['titulo'],r['nombre'])for r in out],flush=True)
def boards_clm():
    rows=[]
    for url in ['https://www.cortesclm.es/web2/paginas/mesa.php','https://www.cortesclm.es/web2/paginas/mesas_anteriores.php']:
        p=c.soup(url)
        for table in p.select('table.TABLE-entera'):
            heading=table.find_previous('h2');leg=re.search(r'\b([IVX]+)\s+Legislatura',heading.get_text(' ',strip=True)if heading else'')
            if not leg:continue
            for tr in table.find_all('tr'):
                cells=tr.find_all('td',recursive=False)
                if len(cells)!=3:continue
                a=cells[1].find('a',href=True)
                if not a:continue
                key=re.search(r'(?:mostrar|abrirventana)\([\'\"]?(\d+)',a['href'])
                rows.append({'legislature':leg[1],'key':key[1]if key else None,'role':c.clean(cells[0].get_text(' ',strip=True)),'name':re.sub(r'^(?:Dña\.|D\.)\s*','',c.clean(a.get_text(' ',strip=True))),'source':url})
    c.write(c.CACHE/'clm-mesas.json',rows);print('clm mesas',len(rows),flush=True)
def discover_history():
    urls=['https://es.wikipedia.org/wiki/Anexo:Composici%C3%B3n_del_Consejo_de_Gobierno_de_la_Junta_de_Comunidades_de_Castilla-La_Mancha','https://es.wikipedia.org/wiki/Junta_de_Castilla_y_Le%C3%B3n']
    for i,url in enumerate(urls):
        p=c.soup(url);main=p.select_one('.mw-parser-output')or p
        out={'source':url,'headings':[x.get_text(' ',strip=True)for x in main.select('h2,h3,h4')],'tables':[[[c.clean(td.get_text(' ',strip=True))for td in tr.find_all(['td','th'],recursive=False)]for tr in t.select('tr')]for t in main.select('table.wikitable')],'links':[{'text':a.get_text(' ',strip=True),'url':urljoin(url,a['href'])}for a in main.select('a[href]')if 'Gobierno_'in a['href']or 'boe.es'in a['href']or 'jcyl.es'in a['href']or 'docm.'in a['href']]}
        c.write(c.CACHE/f'historia-descubrimiento-{i}.json',out);print('Historia',i,'tables',len(out['tables']),'headings',out['headings'][:8],flush=True)
if __name__=='__main__':
    with ThreadPoolExecutor(4)as pool:
        tasks=[pool.submit(presidencies,'clm',11),pool.submit(presidencies,'cyl',17),pool.submit(current_clm),pool.submit(current_cyl)]
        for task in tasks:task.result()
    boards_clm();discover_history()
