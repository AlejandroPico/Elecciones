"""Completa retratos tras contrastar el nombre con etiquetas y alias de Wikidata.
Requiere las búsquedas de completar-retratos-catalunya.py; conserva fotos previas.
Guarda autor, licencia, URL y metadatos del archivo de Wikimedia Commons.
"""
import concurrent.futures, io, json, pathlib, re, sys, time, unicodedata, urllib.request
from urllib.parse import urlencode
sys.path.insert(0,'test-results/libraries')
from bs4 import BeautifulSoup
from PIL import Image
ROOT=pathlib.Path('.');CACHE=ROOT/'test-results/catalunya'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(v):return ' '.join(w for w in re.sub('[^a-z0-9]+',' ',''.join(c for c in unicodedata.normalize('NFD',v.lower()) if not unicodedata.combining(c))).split() if w!='i')
def request(url):
 for attempt in range(3):
  try:return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Elecciones (public archive; github.com/AlejandroPico/Elecciones)'}),timeout=45).read()
  except Exception:
   if attempt==2:raise
   time.sleep(3+attempt)
def plain(v):return BeautifulSoup(v,'html.parser').get_text(' ',strip=True) if '<' in v else v
def photo(item):
 row,folder,meta=item
 if (folder/'retrato.json').exists() or not row.get('results'):return None
 q=row['results'][0]['id'];cached=CACHE/f'{q}.json'
 try:
  if not cached.exists():cached.write_bytes(request(f'https://www.wikidata.org/wiki/Special:EntityData/{q}.json'))
  e=read(cached)['entities'][q]
  variants=[v['value'] for v in e.get('labels',{}).values()]+[v['value'] for vals in e.get('aliases',{}).values() for v in vals]
  expected=[meta['name'],meta.get('fullName',''),*meta.get('knownAs',[])]
  if not {norm(v) for v in variants}&{norm(v) for v in expected}:return {'id':meta['id'],'status':'identity-not-matched'}
  pictures=e.get('claims',{}).get('P18',[])
  if not pictures:return {'id':meta['id'],'status':'no-image'}
  filename=pictures[0]['mainsnak']['datavalue']['value']
  url='https://commons.wikimedia.org/w/api.php?'+urlencode({'action':'query','titles':'File:'+filename,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':250,'format':'json'})
  data=json.loads(request(url));info=next(iter(data['query']['pages'].values()))['imageinfo'][0];ext=info.get('extmetadata',{})
  def value(k):return plain(ext.get(k,{}).get('value',''))
  author=value('Artist');license=value('LicenseShortName');license_url=value('LicenseUrl') or (info['descriptionurl']+'#Licensing' if license else '')
  if not author or not license or not license_url:return {'id':meta['id'],'status':'incomplete-credit'}
  imageurl=info.get('thumburl') or info['url']
  try:raw=request(imageurl)
  except Exception:raw=request(info['url'])
  with Image.open(io.BytesIO(raw)) as image:
   image=image.convert('RGB');image.thumbnail((500,650));image.save(folder/'retrato.webp',quality=87)
  write(folder/'retrato.json',{'file':'retrato.webp','source':info['descriptionurl'],'credit':author,'license':license,'licenseUrl':license_url,'original':info['url'],'description':filename,'dateNote':value('DateTimeOriginal')})
  return {'id':meta['id'],'status':'added','entity':q,'source':info['descriptionurl']}
 except Exception as exc:return {'id':meta['id'],'status':'error','error':str(exc)}
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8');folders={}
 for p in (ROOT/'Políticos').glob('*/ficha.json'):
  m=read(p);folders[m['id']]=(p.parent,m)
 rows=read(CACHE/'photo-candidates.json');jobs=[(r,*folders[r['id']]) for r in rows if r['id'] in folders]
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
  results=[r for r in pool.map(photo,jobs) if r]
 write(CACHE/'commons-results.json',results)
 print({status:sum(r['status']==status for r in results) for status in set(r['status'] for r in results)},flush=True)
