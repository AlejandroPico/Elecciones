"""Retratos institucionales del Govern y búsqueda enciclopédica de apoyo.
No sustituye fotos previas ni usa siluetas institucionales como retratos personales.
"""
import concurrent.futures, hashlib, io, json, pathlib, re, sys, time, unicodedata, urllib.request
from urllib.parse import urljoin, urlencode
sys.path.insert(0,'test-results/libraries')
from bs4 import BeautifulSoup
from PIL import Image
ROOT=pathlib.Path('.');CACHE=ROOT/'test-results/catalunya';CHECKED='2026-10-08'
def norm(v):return ' '.join(w for w in re.sub('[^a-z0-9]+',' ',''.join(c for c in unicodedata.normalize('NFD',v.lower()) if not unicodedata.combining(c))).split() if w!='i')
def read(p,default=None):return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def request(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Elecciones archive (public institutional biographies; https://github.com/AlejandroPico/Elecciones)'}),timeout=40).read()
people={};names={}
for p in (ROOT/'Políticos').glob('*/ficha.json'):
 m=read(p);people[m['id']]={'meta':m,'folder':p.parent}
 for n in [m['name'],m.get('fullName'),*m.get('knownAs',[])]:
  if n:names[norm(n)]=m['id']
def portrait(id,url,source,credit,extra=None):
 folder=people[id]['folder']
 if (folder/'retrato.json').exists():return
 raw=request(url)
 with Image.open(io.BytesIO(raw)) as image:
  image=image.convert('RGB');image.thumbnail((500,650));image.save(folder/'retrato.webp',quality=87)
 write(folder/'retrato.json',{'file':'retrato.webp','source':source,'credit':credit,'original':url,**(extra or {})})
 print('Foto',people[id]['meta']['name'],flush=True)
if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 source='https://web.gencat.cat/ca/generalitat/qui-som/institucions-generalitat/govern'
 b=BeautifulSoup((CACHE/'government.html').read_text(encoding='utf-8'),'html.parser')
 for card in b.select('li.gencat-card__manual-card'):
  name=card.select_one('.gencat-card__description');img=card.select_one('img');link=card.select_one('a[href]')
  if not name or not img:continue
  id=names.get(norm(name.get_text(' ',strip=True)))
  if id:
   try:portrait(id,img['src'],urljoin(source,link['href']) if link else source,'Generalitat de Catalunya · fotografía institucional')
   except Exception as e:print('Error institucional',id,str(e),flush=True)
 audit=read(ROOT/'Gobiernos/revisiones/2026-10-08-catalunya/informe.json')
 missing=[id for id in audit['newPeople'] if not (people[id]['folder']/'retrato.json').exists()]
 candidates=[]
 def search(id):
  name=people[id]['meta']['name'];cache=CACHE/('entity-'+id+'.json')
  try:
   if cache.exists():data=read(cache)
   else:
    url='https://www.wikidata.org/w/api.php?'+urlencode({'action':'wbsearchentities','search':name,'language':'ca','uselang':'ca','format':'json','limit':3})
    data=json.loads(request(url));write(cache,data)
   return {'id':id,'name':name,'results':data.get('search',[])}
  except Exception as e:return {'id':id,'name':name,'error':str(e)}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for item in pool.map(search,missing):
   candidates.append(item)
 (CACHE/'photo-candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Candidatos para contraste',len(candidates),flush=True)
