"""Transcribe nombramientos y recupera retratos identificados en páginas oficiales."""
import importlib.util, io, json, re, sys
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'test-results/libraries')
from pypdf import PdfReader
spec=importlib.util.spec_from_file_location('consulta','Gobiernos/herramientas/consultar-canarias-ceuta-melilla.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def main():
    urls={
      'ceuta-1999':'https://www.ceuta.es/ceuta/component/jdownloads/finish/485-agosto/3439-bocce-3830-31-08-1999?Itemid=0',
      'ceuta-2007':'https://www.ceuta.es/ceuta/component/jdownloads/finish/376-junio/2362-bocce-extra-9-21-06-2007?Itemid=0',
      'ceuta-2011':'https://www.ceuta.es/ceuta/component/jdownloads/finish/328-junio/1799-bocce-extra-12-17-06-2011?Itemid=0',
      'melilla-2019':'https://bomemelilla.es/bome/BOME-BX-2019-21/articulo/86',
      'melilla-2023':'https://bomemelilla.es/bome/descargar/BOME-BX-2023-45.pdf',
      'melilla-2026-cese':'https://bomemelilla.es/bome/BOME-BX-2026-34/articulo/85',
      'melilla-2026-nombramiento':'https://bomemelilla.es/bome/BOME-BX-2026-34/articulo/86',
    }
    for key,url in urls.items():
        raw=c.fetch(url)
        if raw.startswith(b'%PDF'):
            reader=PdfReader(io.BytesIO(raw));text='\n\n'.join(p.extract_text(extraction_mode='layout') or '' for p in reader.pages)
        else:text=c.soup(url).get_text(' ',strip=True)
        c.write(c.CACHE/(key+'-nombramientos.json'),{'source':url,'text':text})
    # Cada página temática identifica expresamente al titular de su fotografía.
    base='https://www.melilla.es/melillaportal/'
    current=c.soup(base+'contenedor.jsp?codMenu=253&codMenuPN=600&codResi=1&language=es&layout=contenedor.jsp&seccion=distribuidor_menus.jsp')
    links={urljoin(base,a['href']) for a in current.select('a[href]') if 'distribuidor_servicios_tema.jsp' in a['href']}
    photos=[]
    for url in sorted(links):
        for i in c.soup(url).select('img[src]'):
            alt=i.get('alt','')
            if alt.lower().startswith('foto '):photos.append({'caption':alt,'image':urljoin(base,i['src']),'source':url})
    c.write(c.CACHE/'melilla-retratos-oficiales.json',photos)
    print('Retratos Melilla',len(photos),[r['caption'] for r in photos],flush=True)
    print('Archivos de nombramientos',len(urls),flush=True)

if __name__=='__main__':main()
