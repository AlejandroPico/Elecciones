"""Localiza nombramientos y cambios en ventanas documentadas del BOJA.

Los índices se obtienen del calendario público. Los resultados requieren lectura
del articulado; la fecha del índice no sustituye la entrada en vigor.
"""
import concurrent.futures, datetime, importlib.util, re
from urllib.parse import urljoin
spec = importlib.util.spec_from_file_location('andalucia', __file__.replace('consultar-gobierno-andalucia.py','consultar-andalucia.py'))
ad = importlib.util.module_from_spec(spec); spec.loader.exec_module(ad)
BASE = 'https://www.juntadeandalucia.es'
MONTHS = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
WINDOWS = [
 ('1982-07-20','1982-08-05'), ('1984-03-08','1984-03-24'), ('1986-07-25','1986-08-05'),
 ('1988-02-29','1988-03-08'), ('1990-07-24','1990-08-05'), ('1992-01-10','1992-01-25'),
 ('1993-07-01','1993-07-25'), ('1994-08-01','1994-08-10'), ('1995-03-01','1995-03-15'),
 ('1996-04-12','1996-04-22'), ('2000-04-26','2000-05-04'), ('2002-03-01','2002-03-20'),
 ('2004-02-05','2004-02-15'), ('2004-04-22','2004-05-03'), ('2007-07-01','2007-07-20'),
 ('2008-03-01','2008-03-15'), ('2008-04-18','2008-04-26'), ('2008-07-07','2008-07-18'),
 ('2009-04-07','2009-04-29'), ('2010-03-20','2010-03-31'), ('2010-10-20','2010-10-29'),
 ('2011-04-04','2011-04-15'), ('2012-05-04','2012-05-12'), ('2013-09-05','2013-09-16'),
 ('2015-01-25','2015-02-02'), ('2015-06-11','2015-06-23'), ('2017-06-07','2017-06-16'),
 ('2018-06-05','2018-06-14'), ('2019-01-17','2019-01-27'), ('2019-02-09','2019-02-18'),
 ('2020-09-02','2020-09-14'), ('2022-03-28','2022-04-08'), ('2022-07-22','2022-08-01'),
 ('2023-04-01','2023-04-10'), ('2024-05-01','2024-05-14'), ('2024-07-28','2024-08-04'),
 ('2025-10-13','2025-10-23'), ('2026-07-03','2026-07-17')
]

def year(y):
    s = ad.soup(BASE + f'/boja/{y}/'); issues = []
    for table in s.select('table.calendario_tabla'):
        month = MONTHS.index(table.select_one('caption').get_text().strip().lower()) + 1
        for a in table.select('a[href]'):
            day = f'{y}-{month:02d}-{int(a.get_text()):02d}'
            if any(start <= day <= end for start,end in WINDOWS):
                issues.append({'date':day,'url':urljoin(BASE,a['href'])})
    return issues

def issue(row):
    s = ad.soup(row['url']); pages = [s]
    # Hay índices antiguos s2.1, modernos s2 y días con varios boletines.
    if re.search(r'/boja/\d{8}\.html$',row['url']):
        links = {urljoin(row['url'],a['href']).replace('http://','https://')
                 for a in s.select('a[href]') if re.search(r'(?:boja/)?\d{4}/\d+/(?:index\.html)?$',a['href'])}
        links = {u + 'index.html' if u.endswith('/') else u for u in links}
        return [r for u in sorted(links) for r in issue({**row,'url':u})]
    sections = {urljoin(row['url'],a['href']) for a in s.select('a[href]') if re.search(r's2(?:\.1)?$',a['href']) or 'Nombramientos' in a.get_text()}
    for u in sections: pages.append(ad.soup(u))
    found = {}
    for page in pages:
        for a in page.select('a[href]'):
            label = a.get_text(' ',strip=True)
            if 'item_html' in a.get('class', []):
                container = a.find_parent('div')
                heading = container.select_one('p') if container else None
                if heading: label = heading.get_text(' ',strip=True)
            if not re.match(r'(?:REAL )?DECRETO',label,re.I): continue
            if not re.search(r'(?:nombra|ces[ae]|designa|reestructura|reasigna|suplencia|suplir|asigna|vicepresiden)',label,re.I): continue
            if not re.search(r'\bconsejer[oa]s?\b|\bvicepresiden|presidente de la Junta|miembros del Consejo|Consejerías',label,re.I): continue
            u = urljoin(row['url'],a['href']); found[u] = {'label':label,'source':u,'published':row['date']}
    return list(found.values())

def norm(row):
    s = ad.soup(row['source'])
    # El articulado aparece dentro del bloque específico del histórico.
    candidates = s.select('[id*=disposicion], [class*=disposicion], [id*=texto], [class*=texto]')
    main = next((c for c in candidates if len(c.get_text())>300 and row['label'][:30] in c.get_text(' ',strip=True)), None)
    if main is None: main = s.select_one('#main-content') or s
    text = main.get_text('\n',strip=True)
    start = text.find(row['label'])
    if start>=0: text = text[start:]
    text = re.split(r'\n(?:Descargar PDF|Disposición anterior|Disposición siguiente|BOJA (?:Extraordinario )?nº)',text)[0]
    return {**row,'text':text}

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(3) as pool: issues = [r for rows in pool.map(year,sorted({int(start[:4]) for start,_ in WINDOWS})) for r in rows]
    print('Índices BOJA',len(issues),flush=True)
    with concurrent.futures.ThreadPoolExecutor(4) as pool: rows = [r for group in pool.map(issue,issues) for r in group]
    rows = list({r['source']:r for r in rows}.values())
    with concurrent.futures.ThreadPoolExecutor(4) as pool: norms = list(pool.map(norm,rows))
    ad.write(ad.CACHE/'normas-gobierno.json',norms)
    print('Disposiciones recuperadas',len(norms),flush=True)
