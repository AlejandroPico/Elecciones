"""Retratos complementarios de Commons, con identidad, autor y licencia.

Las correspondencias se revisan expresamente en la tabla de fuentes del dominio.
No sustituir retratos oficiales disponibles ni usar una imagen colectiva como
retrato. Las descargas pendientes quedan en el informe para revisión visual.
"""
import concurrent.futures, hashlib, io, json, pathlib, sys, urllib.request
from urllib.parse import urlencode
sys.path.insert(0,'test-results/libraries')
from bs4 import BeautifulSoup
from PIL import Image
ROOT=pathlib.Path('.');CACHE=ROOT/'test-results/valencia/photo-api';DEST=ROOT/'Gobiernos/Autonomías/Comunitat Valenciana'
def read(p,default=None):return json.loads(p.read_text('utf8')) if p.exists() else default
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def request(url):
 p=CACHE/hashlib.sha256(url.encode()).hexdigest()
 if p.exists():return p.read_bytes()
 raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Elecciones (public institutional archive; github.com/AlejandroPico/Elecciones)'}),timeout=40).read()
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);return raw
entries=read(DEST/'fuentes/identidades-retratos-complementarios.json',[])
needed=[r for r in entries if r.get('verifiedIdentity') and not (ROOT/'Políticos'/r['folder']/'retrato.json').exists()]
if not needed:print('No quedan retratos complementarios pendientes');sys.exit(0)
api='https://es.wikipedia.org/w/api.php?'+urlencode({'action':'query','titles':'|'.join(r['title'] for r in needed),'prop':'pageimages','piprop':'name','redirects':1,'format':'json'})
query=json.loads(request(api))['query'];redirects={r['from']:r['to'] for r in query.get('redirects',[])};pages={p['title']:p for p in query['pages'].values()}
for r in needed:r['filename']=pages.get(redirects.get(r['title'],r['title']),{}).get('pageimage')
names=sorted({r['filename'] for r in needed if r['filename']});infos={}
if names:
 api='https://commons.wikimedia.org/w/api.php?'+urlencode({'action':'query','titles':'|'.join('File:'+n for n in names),'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':350,'format':'json'})
 for page in json.loads(request(api))['query']['pages'].values():
  if page.get('imageinfo'):infos[page['title'].removeprefix('File:')]=page['imageinfo'][0]
def photo(r):
 folder=ROOT/'Políticos'/r['folder'];id=read(folder/'ficha.json')['id'];filename=r['filename']
 if not filename:return {'id':id,'status':'no-image','identitySource':r['source']}
 try:
  info=infos[filename.replace('_',' ')];ext=info.get('extmetadata',{})
  def v(k):return BeautifulSoup(ext.get(k,{}).get('value',''),'html.parser').get_text(' ',strip=True)
  if not all(v(k) for k in ['Artist','LicenseShortName','LicenseUrl']):raise ValueError('Autor o licencia incompletos')
  try:raw=request(info.get('thumburl') or info['url'])
  except Exception:raw=request(info['url'])
  with Image.open(io.BytesIO(raw)) as im:
   if min(im.size)<65:raise ValueError('Imagen demasiado pequeña')
   im=im.convert('RGB');im.thumbnail((500,650))
   pending=CACHE/'pending';pending.mkdir(parents=True,exist_ok=True);im.save(pending/(id+'.jpg'),quality=88)
  meta={'file':'retrato-valencia.jpg','source':info['descriptionurl'],'credit':v('Artist'),'license':v('LicenseShortName'),'licenseUrl':v('LicenseUrl'),'original':info['url'],'description':filename,'dateNote':v('DateTimeOriginal'),'identitySource':r['source']}
  write(CACHE/'pending'/(id+'.json'),meta)
  return {'id':id,'folder':r['folder'],'status':'pending-visual-review','file':filename,'source':info['descriptionurl']}
 except Exception as e:return {'id':id,'status':'error','error':str(e),'identitySource':r['source']}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(photo,needed))
previous=read(DEST/'fuentes/retratos-complementarios.json',[])
write(DEST/'fuentes/retratos-complementarios.json',list({r['id']:r for r in previous+results}.values()))
print('Retratos complementarios:',{s:sum(r['status']==s for r in results) for s in {r['status'] for r in results}})
