"""Fuentes de Asturias y Cantabria. Originales de trabajo en caché ignorada."""
import importlib.util,pathlib,json,re,sys
from urllib.parse import urljoin,urlencode,urlparse,parse_qs
from concurrent.futures import ThreadPoolExecutor
s=importlib.util.spec_from_file_location('base',pathlib.Path(__file__).with_name('consultar-castillas.py'));c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.CACHE=pathlib.Path('test-results/cantabrico');c.CHECKED='2026-10-16'
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']

def dated(text):
 months=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
 m=re.search(r'(\d{1,2})\s+(?:de\s+)?('+'|'.join(months)+r')\s+(?:de\s+)?(\d{4})',text,re.I)
 return f'{m[3]}-{months.index(m[2].lower())+1:02}-{int(m[1]):02}'if m else None

def cantabria():
 root='https://parlamento-cantabria.es'
 def persons(p,url):
  rows=[]
  for cell in p.select('.views-view-responsive-grid__item-inner'):
   a=cell.select_one('.views-field-field-persona-nombre-completo a[href]')
   if not a:continue
   im=cell.select_one('.views-field-field-fotografia-1 img');logo=cell.select_one('.views-field-field-persona-nombre-completo img');role=cell.select_one('.label')
   rows.append(dict(name=c.clean(a.get_text(' ',strip=True)),source=urljoin(url,a['href']),image=urljoin(url,im['src'])if im else None,group=logo.get('alt')if logo else None,groupImage=logo.get('src')if logo else None,role=c.clean(role.get_text(' ',strip=True))if role else None))
  for table in p.select('table'):
   for tr in table.select('tr'):
    cell=tr.select_one('.views-field-field-persona-nombre-completo');a=cell.select_one('a[href]')if cell else None
    if not a:continue
    im=cell.select_one('img');group=tr.select_one('.views-field-field-partido-politico')
    image=group.select_one('img')if group else None
    rows.append(dict(name=c.clean(a.get_text(' ',strip=True)),source=urljoin(url,a['href']),image=urljoin(url,im['src'])if im else None,groupImage=image.get('src')if image else None))
  return rows
 def collect(leg):
  url=root+'/actividad/legislaturas/'+ROMANS[leg-1].lower()+'-legislatura';p=c.soup(url);orgs={};members={}
  fields={}
  for node in p.select('[class*=field--name-field-legis-]'):
   fields[' '.join(node.get('class',[]))]=c.clean(node.get_text(' ',strip=True))
  # El mismo paginador público actualiza las tres relaciones; basta recorrer las páginas de órganos.
  def page(u):
   pp=c.soup(u)
   for r in persons(pp,u):members[r['source']]=r
   for a in pp.select('a[href]'):
    href=urljoin(u,a['href']);label=c.clean(a.get_text(' ',strip=True))
    if f'/composicion/{leg}l-'in href and re.search(r'^(?:Pleno|Mesa del Parlamento|Mesa de la Asamblea|Grupo Parlamentario)',label,re.I):orgs[href]=label
  page(url)
  for pg in range(1,6):page(url+'?page='+str(pg))
  def organ(item):
   source,label=item;pp=c.soup(source);all_rows=[]
   # Las tablas de miembros tienen 12 filas por página, con altas y bajas.
   for pg in range(8):
    u=source+('?page='+str(pg)if pg else'');dom=c.soup(u)
    block=[{**r,'organ':label,'organSource':source}for r in persons(dom,u)]
    if not block or all(r in all_rows for r in block):break
    all_rows.extend(r for r in block if r not in all_rows)
    if len(block)<12:break
   return dict(name=label,source=source,members=all_rows)
  with ThreadPoolExecutor(3)as pool:organs=list(pool.map(organ,orgs.items()))
  for o in organs:
   for r in o['members']:members.setdefault(r['source'],r)
  result=dict(legislature=leg,source=url,fields=fields,text=p.get_text('\n',strip=True),members=list(members.values()),organs=organs)
  c.write(c.CACHE/f'cantabria-legislatura-{leg}.json',result);print('CANTABRIA',leg,len(members),[(o['name'],len(o['members']))for o in organs],flush=True)
  return result
 with ThreadPoolExecutor(3)as pool:lists=list(pool.map(collect,range(1,12)))
 refs={r['source']:r for li in lists for r in li['members']}
 def profile(row):
  p=c.soup(row['source']);title=p.select_one('h1');im=p.select_one('.field--name-field-fotografia img');bio=p.select_one('.field--name-field-persona-biografia');logo=p.select_one('.field--name-field-partido-politico img')
  roles=[]
  for table in p.select('table'):
   if table.select('th'):continue
   for tr in table.select('tr'):
    cells=tr.select('td')
    if len(cells)!=3:continue
    text=c.clean(cells[1].get_text(' ',strip=True));dates=re.findall(r'Fecha de (?:alta|baja):\s*([^:]+?)(?=Fecha de|$)',text)
    roles.append(dict(organ=c.clean(cells[0].get_text(' ',strip=True)),role=c.clean(cells[2].get_text(' ',strip=True)),start=dated(dates[0])if dates else None,end=dated(dates[1])if len(dates)>1 else None,rawDates=text))
  result={**row,'name':c.clean(title.get_text(' ',strip=True))if title else row['name'],'image':urljoin(row['source'],im['src'])if im else row.get('image'),'groupImage':logo.get('src')if logo else row.get('groupImage'),'biography':c.clean(bio.get_text(' ',strip=True))if bio else None,'roles':roles}
  c.write(c.CACHE/'cantabria-perfiles'/(c.hashlib.sha256(row['source'].encode()).hexdigest()+'.json'),result)
  return result
 with ThreadPoolExecutor(4)as pool:
  for i,result in enumerate(pool.map(profile,refs.values())):
   if i%40==0:print('PERFILES CANTABRIA',i,'/',len(refs),flush=True)

def executives():
 s=importlib.util.spec_from_file_location('g',pathlib.Path(__file__).with_name('consultar-gobiernos-castillas.py'));g=importlib.util.module_from_spec(s);s.loader.exec_module(g);g.c=c
 for region,num in [('asturias','05'),('cantabria','06')]:
  g.presidencies(region,num);path=c.CACHE/f'{region}-presidencias.json';rows=json.loads(path.read_text('utf8'))
  for row in rows:
   m=re.search(r'Decreto\s+\d+/(\d{4}),?\s*(?:de\s*)?(\d{1,2})\s+de\s+(\w+)',row['title'],re.I)
   if m and m[3].lower()in g.MONTHS:row['date']=f'{m[1]}-{g.MONTHS.index(m[3].lower())+1:02}-{int(m[2]):02}'
  c.write(path,rows)
 sources={'asturias':'https://transparencia.asturias.es/gobierno/equipo-gobierno','cantabria':'https://www.cantabria.es/consejerias1'}
 for region,url in sources.items():
  p=c.soup(url);links={}
  for a in p.select('a[href]'):
   href=urljoin(url,a['href']);text=c.clean(a.get_text(' ',strip=True))
   if (region=='asturias'and'/-/gobierno/equipo-gobierno/'in href)or(region=='cantabria'and'/web/consejeria-'in href and not href.split('/web/')[1].count('/')):links[href]=text
  rows=[]
  for href,label in links.items():
   pp=c.soup(href);main=pp.select_one('main')or pp
   row=dict(label=label,source=href,text=main.get_text('\n',strip=True),headings=[c.clean(h.get_text(' ',strip=True))for h in main.select('h1,h2,h3,h4')],images=[dict(image=urljoin(href,i['src']),alt=i.get('alt'))for i in main.select('img[src]')],links=[dict(text=c.clean(a.get_text(' ',strip=True)),source=urljoin(href,a['href']))for a in main.select('a[href]')]);rows.append(row)
  c.write(c.CACHE/(region+'-directorio-gobierno.json'),rows);print('DIRECTORIO',region,len(rows),flush=True)

def inspect(url):
 p=c.soup(url);main=p.select_one('main')or p.select_one('#content')or p.select_one('#main-content')or p
 out={'source':url,'text':main.get_text('\n',strip=True),'links':[{'text':c.clean(a.get_text(' ',strip=True)),'source':urljoin(url,a['href'])}for a in main.select('a[href]')],
      'forms':[str(f)for f in p.select('form')],'images':[{'source':urljoin(url,i['src']),'alt':i.get('alt','')}for i in main.select('img[src]')]}
 c.write(c.CACHE/'inspeccion'/(c.hashlib.sha256(url.encode()).hexdigest()+'.json'),out)
 return {'source':url,'tail':out['text'][-5800:],'links':[a for a in out['links']if re.search('diputad|legislatura|mesa|gobierno|consej|presiden',a['text']+' '+a['source'],re.I)][-65:],
         'forms':[{'action':f.get('action'),'inputs':[(e.name,e.get('name'),e.get('value'),[(o.get('value'),c.clean(o.get_text()))for o in e.select('option')])for e in f.select('input,select')]}for f in p.select('form')if f.select('select')]}

if __name__=='__main__':
 if '--cantabria'in sys.argv:cantabria()
 elif '--gobiernos'in sys.argv:executives()
 else:
  with ThreadPoolExecutor(3)as pool:
   for result in pool.map(inspect,sys.argv[1:]):print(json.dumps(result,ensure_ascii=False),flush=True)
