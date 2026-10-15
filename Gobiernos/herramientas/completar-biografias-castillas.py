"""Contrasta individualmente variantes de los cuadros antiguos con su artículo biográfico.

El enlace explícito de persona en el cuadro, el nombre completo y la relación
territorial permiten resolver variantes. No busca ni une por parecido de apellidos.
"""
import importlib.util,json,pathlib,re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin,quote,urlparse,unquote,urlencode
spec=importlib.util.spec_from_file_location('d','Gobiernos/herramientas/documentar-historia-castillas.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
c=d.c
def collect():
    audit=json.loads(pathlib.Path('Políticos/revisiones/2026-10-15-castillas/informe.json').read_text('utf8'));entries=audit['unresolvedHistoricalNames']
    sources={r['source'].split('#')[0]for r in entries if 'wikipedia.org'in r['source']};links={}
    for source in sources:
        main=c.soup(source).select_one('.mw-parser-output')
        if main:
            for a in main.select('a[href]'):
                href=urljoin(source,a['href']);text=c.clean(a.get_text(' ',strip=True))
                if '/wiki/'in href and 'wikipedia.org'in href and '?'not in href and not any(k in href for k in ['/Archivo:','/File:','/Categoría:','/Anexo:']):links[source,d.normalize(text)]=href
    todo={}
    for row in entries:
        name=row['name']
        if '←'in name or ','in name or len(name.split())<2:continue
        source=row['source'].split('#')[0]
        link=links.get((source,d.normalize(name)),'https://es.wikipedia.org/wiki/'+quote(name.replace(' ','_')))
        todo[name]={'nameInSource':name,'discovery':row['source'],'source':link}
    def review(row):
        try:
            page=c.soup(row['source']);main=page.select_one('.mw-parser-output')
            if not main:raise ValueError('Sin artículo biográfico')
            paragraphs=[p for p in main.select('p')if p.find(['b','strong'])and len(p.get_text(' ',strip=True))>60]
            first=paragraphs[0]if paragraphs else None
            if first is None:raise ValueError('Sin identificación biográfica')
            context=main.get_text(' ',strip=True)
            if not any(k in context for k in ['Castilla-La Mancha','Castilla y León','Castilla la Mancha','castellanomancheg','castellano-mancheg']):raise ValueError('El artículo no acredita la relación territorial')
            full=c.clean(first.find(['b','strong']).get_text(' ',strip=True))
            if len(full.split())<3 or len(full)>100:raise ValueError('Nombre completo no publicado en la identificación inicial: '+full)
            box=main.select_one('table.infobox');birth=box.select_one('.bday')if box else None;death=box.select_one('.dday')if box else None
            if box:
                for tr in box.select('tr'):
                    th=tr.find('th');td=tr.find('td')
                    if th and td and c.clean(th.get_text(' ',strip=True)).lower()in ['nombre completo','nombre de nacimiento']:full=c.clean(td.get_text(' ',strip=True))
            photo=None
            image=box.select_one('a[href] img')if box else None
            if image:
                try:
                    link=urljoin(row['source'],image.find_parent('a')['href']);filename=unquote(link.split('/wiki/',1)[-1]);filename=re.sub(r'^(?:Archivo|File):','File:',filename)
                    if filename.startswith('File:'):
                        api='https://commons.wikimedia.org/w/api.php?'+urlencode({'action':'query','format':'json','prop':'imageinfo','iiprop':'url|extmetadata|size|mime','titles':filename})
                        response=json.loads(c.fetch(api));item=next(iter(response['query']['pages'].values()));info=item.get('imageinfo',[{}])[0];metadata=info.get('extmetadata',{})
                        license=metadata.get('LicenseShortName',{}).get('value');artist=metadata.get('Artist',{}).get('value');licenseUrl=metadata.get('LicenseUrl',{}).get('value')
                        if info.get('url')and license and artist and info.get('mime')in ['image/jpeg','image/png','image/webp']and info.get('width',1)/info.get('height',1)<1.5:
                            author=c.BeautifulSoup(artist,'html.parser').get_text(' ',strip=True)
                            photo={'image':info['url'],'source':info['descriptionurl'],'credit':author+' · '+license,'license':license,'licenseUrl':licenseUrl}
                except Exception:pass
            return {**row,'fullName':full,'birthDate':birth.get_text(strip=True)if birth else None,'deathDate':death.get_text(strip=True)if death else None,'photo':photo,'checkedAt':c.CHECKED,'kind':'encyclopedic'}
        except Exception as error:return {**row,'error':str(error)}
    with ThreadPoolExecutor(4)as pool:results=list(pool.map(review,todo.values()))
    c.write(c.CACHE/'biografias-historicas-revisadas.json',results)
    print('BIOGRAFIAS',sum('error'not in r for r in results),'PENDIENTES',[(r['nameInSource'],r['error'])for r in results if r.get('error')],flush=True)
if __name__=='__main__':collect()
