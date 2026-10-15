"""Gobierno de Aragón: nombramientos, directorio vigente y organigramas históricos."""
import importlib.util,json,re,collections
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
s=importlib.util.spec_from_file_location('a','Gobiernos/herramientas/consultar-aragon.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
s=importlib.util.spec_from_file_location('g','Gobiernos/herramientas/consultar-gobiernos-castillas.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g);g.c=c
def collect():
 g.presidencies('aragon',10)
 rows=json.loads((c.CACHE/'aragon-presidencias.json').read_text('utf8'))
 for row in rows:
  match=re.search(r'Decreto\s+\d+/(\d{4}),?\s*de\s*(\d{1,2})\s+de\s+(\w+)',row['title'],re.I)
  if match and match[3].lower()in g.MONTHS:row['date']=f'{match[1]}-{g.MONTHS.index(match[3].lower())+1:02}-{int(match[2]):02}'
 rows.append({'name':'Jorge Antonio Azcón Navarro','date':'2026-04-29','source':'https://www.boe.es/buscar/doc.php?id=BOE-A-2026-9361','title':'Real Decreto 367/2026, de 29 de abril','dossier':'https://www.boe.es/buscar/doc.php?id=BOE-A-2026-9361'})
 assert 'Jorge Antonio Azcón Navarro'in g.text(rows[-1]['source'])
 # El portal oficial distingue expresamente la presidencia interina de 1995.
 periods=json.loads((c.CACHE/'organigrama-158.json').read_text('utf8'))
 entities={r['id_entidad']:r for r in json.loads((c.CACHE/'organigrama-159.json').read_text('utf8'))}
 cargos=json.loads((c.CACHE/'organigrama-160.json').read_text('utf8'))
 history=[]
 for row in cargos:
  entity=entities.get(row['id_entidad'],{});period=next((p for p in periods if p['id_legislatura']==entity.get('id_legislatura')),None)
  if not period or not period.get('fecha_ini')or period['fecha_ini']<'1983':continue
  role=c.clean(row.get('cargo')or'');name=c.clean(row.get('nombre')or'')
  if not name or not re.match(r'^(?:CONSEJER[OA]\b|VICEPRESIDENT[EA]\b|PRESIDENT[EA] (?:DE ARAGÓN|DEL GOBIERNO|DE LA DIPUTACIÓN))',role,re.I):continue
  if 'CONSEJO'in role.upper()and not role.upper().startswith('CONSEJER'):continue
  history.append({'name':name,'role':role.capitalize(),'period':period['nombre'],'periodStart':period['fecha_ini'][:10],'periodEnd':(period.get('fecha_fin')or'')[:10]or None,'start':(row.get('fecha_ini')or'')[:10]or None,'endInSource':(row.get('fecha_fin')or'')[:10]or None,'entity':entity['nombre'],'legislatureKey':period['id_legislatura'],'source':'https://opendata.aragon.es/GA_OD_Core/download?resource_id=160&formato=json'})
 interim=next(r for r in history if 'Tejedor'in r['name']and r['periodStart'].startswith('1995'))
 rows.append({'name':interim['name'],'date':interim['periodStart'],'source':interim['source'],'title':'Presidencia interina · periodo publicado en el organigrama histórico','interim':True})
 c.write(c.CACHE/'presidencias.json',sorted(rows,key=lambda r:r['date']))
 c.write(c.CACHE/'consejerias-historicas.json',history)
 url='https://www.aragon.es/transparencia/gobierno';p=c.soup(url);current=[]
 for link in p.select('a[data-lfr-editable-id="Enlace ficha"]'):
  box=link
  while box and not(box.select_one('h3[data-lfr-editable-id="Nombre"]')and box.select_one('img')):box=box.parent
  if not box:continue
  name=c.clean(box.select_one('h3[data-lfr-editable-id="Nombre"]').get_text());role=c.clean(box.select_one('[data-lfr-editable-id="Cargo"]').get_text());image=box.select_one('img[src]')
  current.append({'name':name,'role':role,'image':urljoin(url,image['src']),'source':link['href'],'directory':url})
 c.write(c.CACHE/'gobierno-vigente.json',current)
 print('Gobiernos',len(rows),'Cargos históricos',len(history),'Vigentes',len(current),flush=True)
 # Complemento enciclopédico: filas factuales, sin convertir sus cuadros en composiciones diarias.
 url='https://es.wikipedia.org/wiki/Anexo:Composición_del_Gobierno_de_Aragón';p=c.soup(url);tables=[]
 for table in p.select('table.wikitable'):
  for x in table.select('sup.reference,.sortkey,.sorttext,[style*="display:none"],[style*="display: none"]'):x.decompose()
  tables.append({'heading':table.find_previous('h2').get_text(' ',strip=True),'rows':[[c.clean(td.get_text(' ',strip=True))for td in tr.find_all(['td','th'],recursive=False)]for tr in table.select('tr')],'source':url})
 c.write(c.CACHE/'cuadros-complementarios.json',tables)
if __name__=='__main__':collect()
