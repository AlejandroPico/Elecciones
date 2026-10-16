"""Consulta pública riojana; originales en caché, datos publicados sin contactos privados."""
import importlib.util,pathlib,re,concurrent.futures
from urllib.parse import urljoin
s=importlib.util.spec_from_file_location('c',pathlib.Path(__file__).with_name('consultar-castillas.py'));c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.CACHE=pathlib.Path('test-results/rioja');c.CHECKED='2026-10-16'
import pymupdf

def page(url):
 try:return c.soup(url)
 except Exception:
  if 'www.parlamento-larioja.org/'not in url:raise
  return c.soup(url.replace('www.parlamento-larioja.org/','adminweb.parlamento-larioja.org/'))

def main(url):
 p=page(url);return p.select_one('#content')or p.select_one('[itemprop=articleBody]')or p

def chamber(n):
 base='https://www.parlamento-larioja.org/'+('composicion-y-organos/legislatura-11'if n==11 else f'conoce-el-parlamento/legislaturas-anteriores/legislatura-{n}')
 listing='https://www.parlamento-larioja.org/composicion-y-organos/diputados'if n==11 else base+'/diputados'
 p=main(listing);members=[]
 for a in p.select('a[href]'):
  if '/diputados/'not in a['href']:continue
  group=a.find_parent(class_='grupo');h=group.find(['h2','h3'])if group else a.find_previous(['h2','h3'])
  members.append(dict(name=c.clean(a.get_text(' ',strip=True)),source=urljoin(listing,a['href']),group=c.clean(h.get_text(' ',strip=True))if h else None))
 mesa=base+'/organos/mesa';b=main(mesa);board=[]
 for item in b.select('.item'):
  a=item.select_one('a[href*="/diputados/"]');h=item.select_one('h3')
  if a and h:board.append(dict(name=c.clean(a.get_text()),role=c.clean(h.get_text()),source=mesa,text=c.clean(item.get_text(' ',strip=True))))
 text=main(base).get_text(' ',strip=True)
 result=dict(legislature=n,source=listing,stageSource=base,description=c.clean(text),members=members,board=board)
 c.write(c.CACHE/f'parlamentos/{n}.json',result);print('PARLAMENTO',n,len(members),len(board),flush=True);return result

def profile(row):
 url=row['source'];document=page(url);p=document.select_one('#content')or document;h=document.select_one('h1');name=c.clean(h.get_text())if h else row['name']
 image=next((urljoin(url,im['src'])for im in p.select('img[src]')if im['src'].rstrip('/').endswith('/image')),None)
 # Conservamos la biografía pública para transcribir solo formación, fechas y trayectoria.
 result={**row,'name':name,'image':image,'text':p.get_text('\n',strip=True)}
 key=re.search(r'legislatura-(\d+)/diputados/(.+)',url);c.write(c.CACHE/f'perfiles/{key[1]}-{key[2]}.json',result)
 return result

def safe_profile(row):
 key=re.search(r'legislatura-(\d+)/diputados/(.+)',row['source']);file=c.CACHE/f'perfiles/{key[1]}-{key[2]}.json'
 if file.exists():return
 try:return profile(row)
 except Exception as e:
  # Segundo dominio público de la misma institución, comprobado en su directorio.
  try:return profile({**row,'source':row['source'].replace('www.parlamento-larioja.org','adminweb.parlamento-larioja.org')})
  except Exception as fallback:print('ERROR PERFIL',row['source'],str(e),str(fallback),flush=True)

def cabinets():
 url='https://web.larioja.org/portal-transparencia/56-gobierno/consejo-de-gobierno/174-gobiernos-anteriores';p=main(url);rows=[]
 for a in p.select('a[href]'):
  if '/files/pdf/gobierno/anteriores/'not in a['href']:continue
  source=urljoin(url,a['href']);raw=c.fetch(source);key=re.search(r'/([0-9]{2})',source)[1]
  folder=c.CACHE/'gabinetes';folder.mkdir(parents=True,exist_ok=True);(folder/(key+'.pdf')).write_bytes(raw)
  text='\n'.join(pg.get_text()for pg in pymupdf.open(stream=raw,filetype='pdf'))
  (folder/(key+'.txt')).write_text(text,'utf8');rows.append(dict(key=key,label=c.clean(a.get_text()),source=source))
 c.write(c.CACHE/'gabinetes.json',rows)
 url='https://web.larioja.org/consejo-de-gobierno';p=c.soup(url)
 c.write(c.CACHE/'gobierno-actual.json',dict(source=url,text=p.get_text('\n',strip=True),images=[dict(name=im.get('alt'),url=urljoin(url,im['src']))for im in p.select('img[src]')if '/estructura/responsables/'in im['src']]))

def pleno(n):
 base='https://www.parlamento-larioja.org/'+('composicion-y-organos/legislatura-11'if n==11 else f'conoce-el-parlamento/legislaturas-anteriores/legislatura-{n}')
 url=base+'/organos/pleno';p=main(url);rows=[]
 for a in p.select('a[href*="/diputados/"]'):
  parent=a.parent;rows.append(dict(name=c.clean(a.get_text()),source=urljoin(url,a['href']),text=c.clean(parent.get_text(' ',strip=True))))
 c.write(c.CACHE/f'plenos/{n}.json',dict(source=url,text=p.get_text('\n',strip=True),members=rows));print('PLENO',n,len(rows),flush=True)

def safe_pleno(n):
 try:pleno(n)
 except Exception as e:
  # El directorio nominal de esa legislatura sigue siendo fuente primaria.
  print('PLENO NO DISPONIBLE',n,str(e),flush=True)

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(4)as pool:stages=list(pool.map(chamber,range(1,12)))
 rows={r['source']:r for stage in stages for r in stage['members']}
 with concurrent.futures.ThreadPoolExecutor(4)as pool:
  for i,r in enumerate(pool.map(safe_profile,rows.values())):
   if(i+1)%50==0:print('PERFILES',i+1,'/',len(rows),flush=True)
 with concurrent.futures.ThreadPoolExecutor(3)as pool:list(pool.map(safe_pleno,range(1,12)))
 cabinets()
