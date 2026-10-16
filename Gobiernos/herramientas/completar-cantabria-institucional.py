"""Retratos del gabinete: enlaces nominales del Portal de Transparencia.

No se sustituyen recursos personales existentes. Se conserva el original y la
licencia que declara el portal. Los documentos de intereses no se descargan.
"""
import importlib.util,pathlib,sys,urllib.parse
sys.path.insert(0,'test-results/libraries')
s=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).with_name('catalogo-regional.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.c.CACHE=pathlib.Path('test-results/cantabrico')
directory='https://transparencia.cantabria.es/altos-cargos-informacion-individualizada'
rows=m.load(m.c.CACHE/'cantabria-gobierno-vigente.json')
links={}
for a in m.c.soup(directory).select('a[href]'):
 name=m.c.clean(a.get_text(' ',strip=True))
 if name not in links:links[name]=a['href'].replace('http://www.cantabria.es/web/transparencia/','https://transparencia.cantabria.es/')
audit=[]
for row in rows:
 url=links.get(row['name'])
 if not url:continue
 soup=m.c.soup(url)
 # Los retratos pertenecen al contenido nominal; los logos del portal se excluyen.
 images=[im for im in soup.select('img[src]')if '/documents/'in im['src'] and any(word in urllib.parse.unquote(im['src']).lower()for word in ['consejer','agüeros','arasti','pascual','martínez','silva'])]
 if not images:continue
 image=urllib.parse.urljoin(url,images[0]['src'])
 row.update(image=image,portraitSource=url,portraitCredit='Gobierno de Cantabria · Portal de Transparencia',portraitLicense='CC BY 3.0 ES',portraitLicenseUrl='https://creativecommons.org/licenses/by/3.0/es/')
 audit.append(dict(name=row['name'],source=url,image=image,license='https://creativecommons.org/licenses/by/3.0/es/'))
m.c.write(m.c.CACHE/'cantabria-gobierno-vigente.json',rows)
m.c.write('Gobiernos/Autonomías/Cantabria/fuentes/retratos-gabinete.json',audit)
print('Retratos nominales localizados:',len(audit))
