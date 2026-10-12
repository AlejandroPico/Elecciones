"""Sigue referencias al BOE y contrasta cada nombramiento en el documento original."""
import importlib.util, io, re, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'test-results/libraries')
from pypdf import PdfReader
spec=importlib.util.spec_from_file_location('consulta','Gobiernos/herramientas/consultar-canarias-ceuta-melilla.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def collect(region, discovery):
    # La enciclopedia solo descubre enlaces; los hechos proceden del BOE enlazado.
    rows=[]
    for a in c.soup(discovery).select('a[href]'):
        title=a.get_text(' ',strip=True).strip('"')
        if 'boe.es' not in a['href'] or 'por el que se nombra Presidente' not in title:continue
        match=re.search(r'Decreto \d+/(\d{4}), de (\d+) de (\w+)',title)
        name=title.split(' a don ')[-1].rstrip('."')
        date=f'{match[1]}-{c.MONTHS.index(match[3])+1:02}-{int(match[2]):02}' if match else None
        rows.append({'name':name,'date':date,'source':a['href'],'title':title})
    def check(row):
        pdf=PdfReader(io.BytesIO(c.fetch(row['source'])));text=' '.join(page.extract_text() or '' for page in pdf.pages)
        if not re.search(r'nombra[r]?\s+Presidente',text,re.I):raise ValueError('Nombramiento no encontrado '+row['source'])
        return {**row,'text':text}
    with ThreadPoolExecutor(4) as pool: rows=list(pool.map(check,rows))
    c.write(c.CACHE/f'{region}-presidencias.json',rows)
    print(region,len(rows),[(r['date'],r['name']) for r in rows],flush=True)

if __name__=='__main__':
    collect('canarias','https://en.wikipedia.org/wiki/President_of_the_Canary_Islands')
    collect('ceuta','https://en.wikipedia.org/wiki/Mayor-President_of_Ceuta')
    collect('melilla','https://en.wikipedia.org/wiki/Mayor-President_of_Melilla')
