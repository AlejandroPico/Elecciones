"""Fuentes institucionales de Extremadura e Illes Balears; caché fuera del catálogo."""
import importlib.util,pathlib,re,sys,json,concurrent.futures,hashlib,subprocess,shutil
from urllib.parse import urljoin,parse_qs,urlparse
s=importlib.util.spec_from_file_location('c',pathlib.Path(__file__).with_name('consultar-castillas.py'));c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.CACHE=pathlib.Path('test-results/extremadura-balears');c.CHECKED='2026-10-16'
original_fetch=c.fetch
def fetch(url):
 # El cliente del sistema valida la cadena TLS que no completa urllib en
 # algunos servidores del Parlament. No se desactiva la validación TLS.
 if 'parlamentib.'not in url:return original_fetch(url)
 file=c.CACHE/'documents'/hashlib.sha256(url.encode()).hexdigest();file.parent.mkdir(parents=True,exist_ok=True)
 if not file.exists():
  subprocess.run([shutil.which('pwsh'),' -NoProfile'.strip(),'-File',str(pathlib.Path(__file__).with_name('consultar-fuente-windows.ps1')),url,str(file)],check=True,capture_output=True)
 return file.read_bytes()
c.fetch=fetch
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
def forward_name(label):
 surname,given=label.split(',',1);return c.clean(given+' '+surname)
def extremadura_list(n,ceased=False):
 url=f'https://www.asambleaex.es/dipslegis-{n}'+('-BAJA'if ceased else'');pending=[url];seen=set();rows=[]
 while pending:
  link=pending.pop(0)
  if link in seen:continue
  seen.add(link);p=c.soup(link)
  for a in p.select('ul.listaitems > li > a.pn-title[href]'):
   if not re.fullmatch(r'verdiputado-\d+',a['href']):continue
   text=c.clean(a.parent.get_text(' ',strip=True));label=c.clean(a.get_text(' ',strip=True));tail=text[len(label):].strip();province='Badajoz'if tail.endswith('BADAJOZ')else'Cáceres'if tail.endswith('CÁCERES')else None
   group=re.sub(r'\s*(?:BADAJOZ|CÁCERES)$','',tail).strip()
   rows.append(dict(name=forward_name(label),key=a['href'].split('-')[-1],source=urljoin(link,a['href']),group=group,constituency=province,ceased=ceased))
  pending.extend(urljoin(link,a['href'])for a in p.select('a[href]')if re.fullmatch(fr'dipslegis-{n}-(?:TODO|BAJA|ALTA)-\d+',a['href']))
 rows=list({(row['key'],row['group'],row['constituency']):row for row in rows}.values())
 result=dict(legislature=n,source=url,pages=sorted(seen),members=rows);c.write(c.CACHE/f'extremadura/listas/{n}{"-bajas"if ceased else""}.json',result);print('EXT LISTA',n,len(rows),flush=True);return result
def extremadura_profile(row):
 p=c.soup(row['source']);body=p.select_one('#contenido');h=body.select_one('h2');image=body.select_one('img[src*="func=viewfoto"]')
 result=dict(name=forward_name(c.clean(h.get_text())),key=row['key'],source=row['source'],image=urljoin(row['source'],image['src'])if image else None,legislatures=[c.clean(li.get_text(' ',strip=True))for li in body.select('#tab_legislaturas li')],roles=[c.clean(li.get_text(' ',strip=True))for li in body.select('#tab_cargos li')])
 c.write(c.CACHE/f'extremadura/perfiles/{row["key"]}.json',result);return result
def safe_extremadura_profile(row):
 try:return extremadura_profile(row)
 except Exception as error:
  print('EXT PERFIL NO DISPONIBLE',row['key'],row['name'],str(error),flush=True)
  c.write(c.CACHE/f'extremadura/perfiles/{row["key"]}.json',{**row,'error':str(error),'image':None,'roles':[],'legislatures':[]})
def extremadura():
 with concurrent.futures.ThreadPoolExecutor(3)as pool:lists=list(pool.map(extremadura_list,range(1,13)))
 lists.append(extremadura_list(12,True));profiles={r['key']:r for d in lists for r in d['members']}
 with concurrent.futures.ThreadPoolExecutor(4)as pool:
  for i,_ in enumerate(pool.map(safe_extremadura_profile,profiles.values())):
   if(i+1)%50==0:print('EXT PERFILES',i+1,'/',len(profiles),flush=True)
 import pymupdf
 extremadura_documents()
def extremadura_documents():
 import pymupdf
 for n in range(1,13):
  page=f'https://www.asambleaex.es/grupos-{n}';p=c.soup(page)
  links=[urljoin(page,a['href'])for a in p.select('a[href]')if 'gruposporlegis'in a['href']]
  if not links:continue
  url=links[0];raw=c.fetch(url);doc=pymupdf.open(stream=raw,filetype='pdf');text='\n'.join(page.get_text()for page in doc)
  c.write(c.CACHE/f'extremadura/grupos/{n}.json',dict(source=url,text=text));print('EXT PDF',n,len(text),flush=True)
def balear_stage(n):
 import pymupdf
 url='https://www.parlamentib.es/PageHandler/'+ROMANS[n-1]+'_legislatura';p=c.soup(url);text=c.clean(p.get_text(' ',strip=True));documents=[]
 for a in p.select('a[href]'):
  label=c.clean(a.get_text(' ',strip=True))
  if label not in ['Relació de diputats i senadors','Composició dels grups parlamentaris','Composició dels òrgans parlamentaris']:continue
  link=urljoin(url,a['href']).replace('http://','https://');raw=c.fetch(link);doc=pymupdf.open(stream=raw,filetype='pdf');pages=[page.get_text()for page in doc]
  documents.append(dict(label=label,source=link,pages=pages));print('BALEARS PDF',n,label,len(pages),flush=True)
 result=dict(legislature=n,source=url,text=text,documents=documents);c.write(c.CACHE/f'baleares/legislaturas/{n}.json',result);return result
def balear_profile(row):
 source='https://web.parlamentib.es/webgtp/scripts/UnRegPers.asp?CFautor='+row['key'];p=c.soup(source)
 for script in p.select('script,style'):script.decompose()
 text=p.get_text('\n',strip=True)
 images=[dict(src=urljoin(source,t['src']),alt=t.get('alt'))for t in p.select('img[src]')]
 result={**row,'source':source,'text':text,'images':images};c.write(c.CACHE/f'baleares/perfiles/{row["key"]}.json',result);return result
def balear_current():
 url='https://www.parlamentib.es/Representants/Diputats.aspx?criteria=0';p=c.soup(url);rows=[]
 for a in p.select('a[href*="showDiputado"]'):
  args=re.findall(r"'([^']*)'",a['href']);assert len(args)==4
  key,treatment,given,surname=args;name=c.clean(given+' '+surname.title());rows.append(dict(key=key,name=name))
 assert len(rows)==59
 c.write(c.CACHE/'baleares/vigente.json',dict(source=url,members=rows))
 with concurrent.futures.ThreadPoolExecutor(4)as pool:
  for i,_ in enumerate(pool.map(balear_profile,rows)):
   if(i+1)%20==0:print('BALEARS PERFILES',i+1,flush=True)
def baleares():
 with concurrent.futures.ThreadPoolExecutor(3)as pool:list(pool.map(balear_stage,range(1,11)))
 balear_current()
def balear_archive_profiles():
 url='https://web.parlamentib.es/webgtp/scripts/cconsexpn.asp';p=c.soup(url);rows=[]
 for option in p.select('#proponent option[value]'):
  key=option['value'];label=c.clean(next((str(t)for t in option.contents if isinstance(t,str)),''))
  if not key.isdigit()or','not in label:continue
  surname,given=label.split(',',1)
  if not surname.strip()or not given.strip():continue
  rows.append(dict(key=key,name=c.clean(given+' '+surname.title())))
 c.write(c.CACHE/'baleares/indice-personas.json',dict(source=url,members=rows));print('BALEARS INDICE',len(rows),flush=True)
 with concurrent.futures.ThreadPoolExecutor(4)as pool:
  for i,_ in enumerate(pool.map(balear_profile,rows)):
   if(i+1)%50==0:print('BALEARS ARCHIVO',i+1,'/',len(rows),flush=True)
def inspect(url):
 try:
  p=c.soup(url);main=p.select_one('main')or p.select_one('#content')or p
  links=[(c.clean(a.get_text(' ',strip=True)),urljoin(url,a['href']))for a in main.select('a[href]')]
  print(json.dumps(dict(url=url,text=c.clean(main.get_text(' ',strip=True))[-8000:],links=list(dict.fromkeys(r for r in links if re.search(r'diput|legisl|presiden|mesa|gov|govern|consell|hist|grupo|hist|compos|fitxa|membre',str(r),re.I)))[:95],controls=[dict(id=t.get('id'),options=[(o.get('value'),o.get_text())for o in t.select('option')])for t in p.select('select')]),ensure_ascii=False),flush=True)
 except Exception as e:print(url,type(e).__name__,str(e),flush=True)
if __name__=='__main__':
 if '--extremadura'in sys.argv:extremadura()
 elif '--baleares'in sys.argv:baleares()
 elif '--bal-perfiles'in sys.argv:balear_archive_profiles()
 elif '--ext-completar'in sys.argv:
  with concurrent.futures.ThreadPoolExecutor(3)as pool:list(pool.map(extremadura_list,range(1,13)))
  extremadura_list(12,True);extremadura_documents()
 else:
  with concurrent.futures.ThreadPoolExecutor(3)as pool:list(pool.map(inspect,sys.argv[1:]))
