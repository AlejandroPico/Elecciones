"""Retratos de consejeros sin fotografía institucional disponible.

La identidad procede del enlace personal del cuadro de composición consultado.
Commons debe publicar autor y licencia. Nunca sustituir un retrato previo.
"""
import concurrent.futures, hashlib, importlib.util, io, json, pathlib, re, sys, urllib.request
from urllib.parse import urlencode, unquote, urljoin
sys.path.insert(0, 'test-results/libraries')
from bs4 import BeautifulSoup
from PIL import Image
ROOT=pathlib.Path('.'); CACHE=ROOT/'test-results/madrid'; DEST=ROOT/'Gobiernos/Autonomías/Madrid'
def read(p,default=None):return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def request(url):
 p=CACHE/'photo-api'/hashlib.sha256(url.encode()).hexdigest()
 if p.exists():return p.read_bytes()
 data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Elecciones (public institutional archive; github.com/AlejandroPico/Elecciones)'}),timeout=35).read()
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return data
spec=importlib.util.spec_from_file_location('transcription',ROOT/'Gobiernos/herramientas/transcribir-gobierno-madrid.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
people={read(p)['id']:(p.parent,read(p)) for p in (ROOT/'Políticos').glob('*/ficha.json')}
needed={r['person'] for p in (DEST/'Gobierno').glob('*/composicion.json') for g in [read(p)] for r in g['terms']+g.get('archiveTerms',[]) if not (people[r['person']][0]/'retrato.json').exists()}
by_name={t.norm(m.get('fullName') or m['name']):id for id,(f,m) in people.items() if id in needed}
pages=[('https://es.wikipedia.org',(CACHE/'cache/gobiernos-wiki.html').read_text(encoding='utf-8'))]+[(url,table) for _,url,tables in read(CACHE/'cabinets-en.json',[]) for table in tables[:1]]
jobs={}
for base,html in pages:
 for a in BeautifulSoup(html,'html.parser').select('table a[href], a[href]'):
  label=a.get_text(' ',strip=True);id=by_name.get(t.norm(t.full_name(label)))
  if not id or '/wiki/' not in a['href'] or 'redlink=1' in a['href']:continue
  url=urljoin(base,a['href'])
  # El cuadro español se procesa primero y prevalece si hay dos idiomas.
  jobs.setdefault(id,url)
pagefiles={};errors={}
# Consultas agrupadas para respetar los límites de las APIs públicas.
for domain in sorted({url.split('/')[2] for url in jobs.values()}):
 urls=[url for url in jobs.values() if url.split('/')[2]==domain]
 titles=[unquote(url.split('/wiki/')[1]) for url in urls]
 try:
  api=f'https://{domain}/w/api.php?'+urlencode({'action':'query','titles':'|'.join(titles),'prop':'pageimages','piprop':'name','redirects':1,'format':'json'})
  query=json.loads(request(api))['query'];redirects={r['from']:r['to'] for r in query.get('redirects',[])};pages={p['title']:p for p in query['pages'].values()}
  for url,title in zip(urls,titles):
   title=title.replace('_',' ');pagefiles[url]=pages.get(redirects.get(title,title),{}).get('pageimage')
 except Exception as e:
  for url in urls:errors[url]=str(e)
infos={};filenames=sorted({f for f in pagefiles.values() if f})
if filenames:
 try:
  api='https://commons.wikimedia.org/w/api.php?'+urlencode({'action':'query','titles':'|'.join('File:'+f for f in filenames),'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':350,'format':'json'})
  for p in json.loads(request(api))['query']['pages'].values():
   if p.get('imageinfo'):infos[p['title'].removeprefix('File:')]=p['imageinfo'][0]
 except Exception as e:
  for url in jobs.values():errors[url]=str(e)
def photo(job):
 id,url=job;folder,meta=people[id]
 try:
  if url in errors:raise ValueError(errors[url])
  filename=pagefiles.get(url)
  if not filename:return {'id':id,'status':'no-image','source':url}
  info=infos[filename.replace('_',' ')];ext=info.get('extmetadata',{})
  def value(k):
   v=ext.get(k,{}).get('value','');return BeautifulSoup(v,'html.parser').get_text(' ',strip=True) if '<' in v else v
  credit=value('Artist');license=value('LicenseShortName');license_url=value('LicenseUrl')
  if not credit or not license or not license_url:return {'id':id,'status':'incomplete-credit','source':url}
  imageurl=info.get('thumburl') or info['url']
  try:raw=request(imageurl)
  except Exception:raw=request(info['url'])
  with Image.open(io.BytesIO(raw)) as im:
   im=im.convert('RGB');im.thumbnail((500,650));im.save(folder/'retrato.webp',quality=88)
  write(folder/'retrato.json',{'file':'retrato.webp','source':info['descriptionurl'],'credit':credit,'license':license,'licenseUrl':license_url,'original':info['url'],'description':filename,'dateNote':value('DateTimeOriginal'),'identitySource':url})
  return {'id':id,'status':'added','source':info['descriptionurl'],'file':filename}
 except Exception as e:return {'id':id,'status':'error','source':url,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(photo,jobs.items()))
previous=read(DEST/'fuentes/retratos-complementarios.json',[])
write(DEST/'fuentes/retratos-complementarios.json',list({r['id']:r for r in previous+results}.values()))
print('Fotografías complementarias:',{s:sum(r['status']==s for r in results) for s in {r['status'] for r in results}},flush=True)
