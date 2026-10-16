"""Gobiernos vascos y navarros: nombramientos y directorios institucionales."""
import importlib.util,pathlib,json,re,sys
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
s=importlib.util.spec_from_file_location('n',pathlib.Path(__file__).with_name('consultar-norte.py'));n=importlib.util.module_from_spec(s);s.loader.exec_module(n);c=n.c
s=importlib.util.spec_from_file_location('g',pathlib.Path(__file__).with_name('consultar-gobiernos-castillas.py'));g=importlib.util.module_from_spec(s);s.loader.exec_module(g);g.c=c

def presidents(region,number):
    g.presidencies(region,number)
    rows=json.loads((c.CACHE/f'{region}-presidencias.json').read_text('utf8'))
    for row in rows:
        m=re.search(r'Decreto\s+\d+/(\d{4}),?\s*(?:de\s*)?(\d{1,2})\s+de\s+(\w+)',row['title'],re.I)
        if m and m[3].lower()in g.MONTHS:row['date']=f'{m[1]}-{g.MONTHS.index(m[3].lower())+1:02}-{int(m[2]):02}'
    c.write(c.CACHE/f'{region}-presidencias.json',rows)

def government_pages():
    sources={'pais-vasco-historico':'https://www.euskadi.eus/equipo-de-gobierno-de-la-legislatura-4/web01-s1ezaleh/es/','pais-vasco-actual':'https://www.euskadi.eus/miembros-del-consejo-de-gobierno/web01-s1ezaleh/es/','navarra-historico':'https://www.navarra.es/es/gobierno-de-navarra/gobiernos-anteriores','navarra-presidencias':'https://www.navarra.es/es/gobierno-de-navarra/presidencias-anteriores','navarra-actual':'https://gobiernoabierto.navarra.es/es/transparencia/gobierno'}
    for key,url in list(sources.items()):
        p=c.soup(url);main=p.select_one('main')or p
        if key=='pais-vasco-historico':
            for a in p.select('a[href]'):
                label=c.clean(a.get_text(' ',strip=True))
                if re.fullmatch('[IVX]+ Legislatura',label):sources['pais-vasco-'+label.split()[0]]=urljoin(url,a['href'])
    for key,url in sources.items():
        p=c.soup(url);main=p.select_one('main')or p
        out={'source':url,'text':main.get_text('\n',strip=True),'headings':[{ 'tag':h.name,'text':c.clean(h.get_text(' ',strip=True))}for h in main.select('h1,h2,h3,h4')],'links':[{'text':c.clean(a.get_text(' ',strip=True)),'url':urljoin(url,a['href'])}for a in main.select('a[href]')],'images':[{'src':urljoin(url,i['src']),'alt':i.get('alt','')}for i in main.select('img[src]')]}
        c.write(c.CACHE/'gobiernos'/(key+'.json'),out)
        print('GOBIERNO',key,len(out['text']),len(out['headings']),flush=True)

if __name__=='__main__':
    if '--paginas'in sys.argv:government_pages()
    else:
        presidents('pais-vasco','01');presidents('navarra',13);government_pages()
