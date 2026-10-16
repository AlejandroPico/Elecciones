"""Fuentes públicas de Galicia; originales de trabajo en caché ignorada."""
import importlib.util,pathlib,json,re,sys
from urllib.parse import urljoin,urlparse,quote
from concurrent.futures import ThreadPoolExecutor
s=importlib.util.spec_from_file_location('c',pathlib.Path(__file__).with_name('consultar-castillas.py'));c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.CACHE=pathlib.Path('test-results/galicia');c.CHECKED='2026-10-16'
def inspect(url):
 p=c.soup(url);main=p.select_one('main')or p.select_one('#content')or p
 result=dict(source=url,text=main.get_text('\n',strip=True),links=[dict(text=c.clean(a.get_text(' ',strip=True)),url=urljoin(url,a['href']))for a in main.select('a[href]')],images=[dict(alt=i.get('alt'),url=urljoin(url,i['src']))for i in main.select('img[src]')])
 c.write(c.CACHE/'inspeccion'/(c.hashlib.sha256(url.encode()).hexdigest()+'.json'),result)
 return result
if __name__=='__main__':
 for url in sys.argv[1:]:
  try:
   r=inspect(url);print(json.dumps(dict(source=url,text=r['text'][:3500],links=[a for a in r['links']if any(w in(a['text']+' '+a['url']).lower()for w in ['deput','diput','lexisl','legisl','hist','mesa','compos','consell','presiden'])],images=r['images'][:25]),ensure_ascii=False),flush=True)
  except Exception as e:print(url,type(e).__name__,str(e),flush=True)
