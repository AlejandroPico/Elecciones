"""Fuentes complementarias: composiciones actuales, Mesas y archivo enciclopédico explícito."""
import copy,importlib.util,json,re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin,parse_qs,urlparse
spec=importlib.util.spec_from_file_location('c','Gobiernos/herramientas/consultar-castillas.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def cyl_chambers():
    out=[]
    for leg in range(1,13):
        root='http://www.ccyl.es';url=f'{root}/Organizacion/VistaGeneralLegislatura?Legislatura={leg}'
        page=c.soup(url);text=page.get_text(' ',strip=True)
        chart=[(c.clean(a.get_text(' ',strip=True)),urljoin(url,a['href']))for a in page.select('a[href]')if 'DetalleGrupoHistorico?'in a['href']]
        capacity=sum(int(re.search(r'(\d+)$',name)[1])for name,_ in chart)if chart else None
        boardUrl=f'{root}/Organizacion/ComposicionCargos?Legislatura={leg}&CodigoOrgano=TS{leg}99'
        board=[];p=c.soup(boardUrl)
        for a in p.select('a[href]'):
            if 'Procurador?'not in a['href']:continue
            parent=a
            while parent and len(parent.select('.cc_org_Procurador'))!=1:parent=parent.parent
            if not parent:continue
            q=parse_qs(urlparse(urljoin(boardUrl,a['href'])).query)
            if q.get('Legislatura')!=[str(leg)]:raise ValueError('Mesa de otra legislatura')
            name=c.clean(parent.select_one('.cc_org_Procurador').get_text(' ',strip=True));tr=a.find_parent('tr')
            if tr:
                cells=tr.find_all('td',recursive=False);role=c.clean(cells[1].get_text(' ',strip=True))
            else:
                role=c.clean(parent.get_text(' ',strip=True)).removeprefix(name).removesuffix('Ver ficha').strip()
                for cls in ['.cc_org_ProcuradorGrupoParlamentario','.cc_org_ProcuradorGrupoProvincia']:
                    n=parent.select_one(cls)
                    if n:role=role.replace(c.clean(n.get_text(' ',strip=True)),'').strip()
            board.append({'name':name,'key':q['CodigoPersona'][0],'role':role,'source':boardUrl})
        out.append({'legislature':leg,'source':url,'capacity':capacity,'groupsInChart':chart,'board':board,'boardText':c.clean(p.get_text(' ',strip=True))[:1400]})
    url='http://www.ccyl.es/Organizacion/PlenoPorGrupos?Legislatura=12';p=c.soup(url);current=[]
    for a in p.select('a[href]'):
        if 'Procurador?'not in a['href']:continue
        q=parse_qs(urlparse(urljoin(url,a['href'])).query)
        if q.get('Legislatura')!=['12']:raise ValueError('Pleno devuelto de otra legislatura')
        current.append({'key':q['CodigoPersona'][0],'source':urljoin(url,a['href'])})
    assert len(current)==82,len(current)
    c.write(c.CACHE/'cyl-composiciones.json',out);c.write(c.CACHE/'cyl-pleno-vigente.json',{'source':url,'members':current});print('CYL composiciones',[(r['legislature'],r['capacity'],len(r['board']))for r in out],flush=True)
def historical():
    urls=['https://es.wikipedia.org/wiki/Gobierno_de_Demetrio_Madrid','https://es.wikipedia.org/wiki/Gobierno_de_José_Constantino_Nalda','https://es.wikipedia.org/wiki/Gobierno_de_José_María_Aznar_(Castilla_y_León)','https://es.wikipedia.org/wiki/Gobierno_de_Jesús_Posada','https://es.wikipedia.org/wiki/Gobierno_de_Juan_José_Lucas','https://es.wikipedia.org/wiki/Gobierno_de_Juan_Vicente_Herrera','https://es.wikipedia.org/wiki/Primer_Gobierno_Fernández_Mañueco','https://es.wikipedia.org/wiki/Segundo_Gobierno_Fernández_Mañueco','https://es.wikipedia.org/wiki/Gobierno_Cospedal','https://es.wikipedia.org/wiki/Primer_Gobierno_García-Page','https://es.wikipedia.org/wiki/Segundo_Gobierno_García-Page']
    urls=[u for u in urls if not u.endswith('Gobierno_de_Juan_José_Lucas') and not u.endswith('Gobierno_de_Juan_Vicente_Herrera')]
    urls += ['https://es.wikipedia.org/wiki/'+n+'_gobierno_de_Juan_José_Lucas'for n in ['Primer','Segundo','Tercer']]
    urls += ['https://es.wikipedia.org/wiki/'+n+'_gobierno_de_Juan_Vicente_Herrera'for n in ['Primer','Segundo','Tercer','Cuarto','Quinto']]
    def read(url):
        try:
            p=c.soup(url);main=p.select_one('.mw-parser-output')or p
            # Expandir celdas combinadas para no confundir nombres con fechas.
            tables=[]
            for table in main.select('table.wikitable'):
                occupied={};grid=[]
                for ri,tr in enumerate(table.select('tr')):
                    row=[];col=0
                    for td in tr.find_all(['td','th'],recursive=False):
                        while (ri,col)in occupied:row.append(occupied[(ri,col)]);col+=1
                        cell=copy.deepcopy(td)
                        for hidden in cell.select('.sortkey,.sorttext,sup.reference'):hidden.decompose()
                        for hidden in cell.select('[style]'):
                            if 'display:none' in hidden.get('style','').replace(' ',''):hidden.decompose()
                        value=c.clean(cell.get_text(' ',strip=True));span=int(td.get('colspan',1));height=int(td.get('rowspan',1))
                        for x in range(span):
                            row.append(value)
                            for y in range(1,height):occupied[(ri+y,col)]=value
                            col+=1
                    while (ri,col)in occupied:row.append(occupied[(ri,col)]);col+=1
                    grid.append(row)
                tables.append(grid)
            def official(link):
                host=urlparse(urljoin(url,link)).hostname or ''
                return any(host==domain or host.endswith('.'+domain)for domain in ['boe.es','jcyl.es','jccm.es','castillalamancha.es'])
            refs=[{'title':a.get_text(' ',strip=True),'url':urljoin(url,a['href'])}for a in main.select('.references a.external[href]')if official(a['href'])]
            return {'source':url,'tables':tables,'officialReferences':refs,'kind':'encyclopedic','checkedAt':c.CHECKED}
        except Exception as e:return {'source':url,'error':str(e)}
    with ThreadPoolExecutor(4)as pool:rows=list(pool.map(read,urls))
    c.write(c.CACHE/'gobiernos-historicos-consulta.json',rows)
    print('Historia',[(r['source'].split('/')[-1],len(r.get('tables',[])),r.get('error'))for r in rows],flush=True)
if __name__=='__main__':cyl_chambers();historical()
