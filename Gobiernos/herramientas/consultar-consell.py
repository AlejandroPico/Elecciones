"""Fuentes del Consell y de la Mesa: consultas de lectura, caché reproducible."""
import concurrent.futures, json, pathlib, subprocess, sys
from urllib.parse import quote, urljoin
import importlib.util
spec=importlib.util.spec_from_file_location('cv',pathlib.Path(__file__).with_name('consultar-valencia.py'))
cv=importlib.util.module_from_spec(spec);spec.loader.exec_module(cv)
from bs4 import BeautifulSoup
CACHE=cv.CACHE

def bureau(leg):
    url=cv.BASE+'/es/composicion/organos/mesa'
    dest=CACHE/('mesa-'+leg+'.html')
    if not dest.exists():
        jar=CACHE/('cookies-'+leg+'.txt')
        raw=cv.fetch(url)
        s=BeautifulSoup(raw,'html.parser');form=s.select_one('form.bureau-form')
        fields={e['name']:e.get('value','') for e in form.select('input[type=hidden]')}
        fields.update(legislature=leg,historic='1',search='Buscar')
        args=['curl.exe','--fail','--silent','--show-error','--location','--max-time','20']
        for k,v in fields.items():args+=['--data-urlencode',k+'='+v]
        raw=subprocess.run(args+[url],capture_output=True,check=True).stdout
        dest.write_bytes(raw)
    s=BeautifulSoup(dest.read_bytes(),'html.parser');rows=[]
    for tr in s.select('table tbody tr'):
        td=tr.select('td')
        if len(td)<4:continue
        a=td[2].select_one('a[href]');img=td[3].select_one('img')
        if not a:continue
        link=urljoin(cv.BASE,a['href'])
        actual=link.split('/diputados/')[1].split('/')[0].upper()
        if actual!=leg:
            raise ValueError('La Mesa devuelve '+actual+' al solicitar '+leg+'; no atribuir su composición a la legislatura solicitada.')
        rows.append({'key':link.rsplit('/',1)[1],'source':link,'listSource':url,'legislature':leg,'role':td[0].get_text(' ',strip=True),'name':a.get_text(' ',strip=True),'group':img.get('alt','').removeprefix('Foto de ') if img else td[3].get_text(' ',strip=True),'start':cv.date(td[4].get_text()) if len(td)>4 else None,'endInclusive':cv.date(td[5].get_text()) if len(td)>5 else None})
    return rows

if __name__=='__main__':
    if '--mesa' in sys.argv:
        mesas=[]
        for leg in cv.ROMANS:
            try:mesas.append(bureau(leg))
            except Exception as e:print('Mesa histórica no acreditada',leg,str(e),flush=True);mesas.append([])
        if len(mesas)==11:cv.write(CACHE/'mesas.json',mesas)
        print('Mesas',[(cv.ROMANS[i],len(r),r[0] if r else {}) for i,r in enumerate(mesas)],flush=True)
        sys.exit(0)
    pages=['Lerma_I','Zaplana_II','Olivas','Camps_I','Camps_II','Camps_III','Fabra','Puig_I','Puig_II','Mazón','Pérez_Llorca']
    def cabinet(name):
        url='https://fr.wikipedia.org/wiki/Gouvernement_'+quote(name)
        s=cv.soup(url);tables=[]
        for table in s.select('table.wikitable'):
            header=table.find_previous(['h2','h3','h4'])
            rows=[[td.get_text(' ',strip=True) for td in tr.select('th,td')] for tr in table.select('tr')]
            tables.append({'heading':header.get_text(' ',strip=True) if header else '', 'rows':rows})
        links=[a['href'] for a in s.select('a.external[href]') if 'dogv.gva.es' in a['href'] or 'boe.es' in a['href']]
        return {'name':name,'source':url,'tables':tables,'officialLinks':links}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        cv.write(CACHE/'cabinets.json',list(pool.map(cabinet,pages)))
    urls=[('https://dogv.gva.es/datos/2025/12/03/pdf/2025_49244_es.pdf','nombramientos-2025.pdf'),('https://roderic.uv.es/bitstream/10550/73197/1/1983%20Joan%20Lerma%20primer%20presidente%20GV.pdf','consell-1983.pdf')]
    for url,name in urls:
        try:(CACHE/name).write_bytes(cv.fetch(url,'.pdf'))
        except Exception as e:print('Error',url,str(e),flush=True)
