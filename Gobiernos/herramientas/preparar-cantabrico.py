"""Normaliza hechos breves; conserva las incertidumbres de los archivos históricos."""
import importlib.util,pathlib,json,re
from urllib.parse import urljoin
s=importlib.util.spec_from_file_location('x',pathlib.Path(__file__).with_name('consultar-cantabrico.py'));x=importlib.util.module_from_spec(s);s.loader.exec_module(x);c=x.c
def read(file):return json.loads((c.CACHE/file).read_text('utf8'))

def governments():
 for region in ['asturias','cantabria']:
  # El dosier contiene dos erratas: se contrastan con el decreto enlazado.
  apps=read(region+'-presidencias.json')
  if region=='cantabria':
   for a in apps:
    if '/1999/07/26/'in a['source']:a.update(date='1999-07-23',correction='El PDF del BOE es Real Decreto 1285/1999; el dosier escribe por error 1285/1995.')
    if 'BOE-A-2023-15471'in a['source']:a.update(name='María José Sáenz de Buruaga Gómez',correction='Nombre completo contrastado en el decreto del BOE; el encabezado del dosier dice Sanz de Buruaga.')
  c.write(c.CACHE/(region+'-presidencias-revisadas.json'),sorted(apps,key=lambda r:r['date']))
  url=read('investigacion/'+region+'-senado.json')['source'];p=c.soup(url);rows=[];role='Presidencia';name=None
  for h in p.select('h3'):
   text=c.clean(h.get_text(' ',strip=True))
   if 'Consejería'in text or 'Vicepresidencia'in text:role=text;continue
   if not re.match(r'^[A-ZÁÉÍÓÚÑ]',text)or text in ['Menú','Idiomas','Síguenos']:continue
   source=url;nextp=h.find_next('p')
   if nextp and 'Nombramiento'in nextp.get_text():
    a=nextp.find('a',href=True)
    if a:source=urljoin(url,a['href'])
   rows.append(dict(name=text,role=role,source=source,directory=url))
  if region=='asturias':
   # El directorio actualizado del Principado prevalece sobre las erratas/omisiones del resumen del Senado.
   rows=[]
   for r in read('asturias-directorio-gobierno.json'):
    match=re.search(r'Cargo:\s*\n([^\n]+)',r['text']);assert match,r['label']
    rows.append(dict(name=r['label'],role=match[1],source=r['source'],directory='https://transparencia.asturias.es/gobierno/equipo-gobierno',image=r['images'][0]['image']if r['images']else None))
  assert len(rows)==(11 if region=='asturias'else 10),(region,rows)
  c.write(c.CACHE/(region+'-gobierno-vigente.json'),rows)
  history=read('investigacion/'+('asturias-anexo.json'if region=='asturias'else'cantabria-historia-gobierno.json'));out=[]
  for table in history['tables']:
   heading=table['heading'];year=re.search(r'(19\d{2}|20\d{2})',heading)
   if not year or int(year[0])<1982:continue
   enabled=False;role=None
   for cells in table['rows']:
    if cells and cells[0]in ['Cargo','Consejería']:
     enabled=True;continue
    if not enabled or not cells:continue
    first=cells[0]
    if first:role=first
    if not role:continue
    values=[v for v in cells[1:]if v and not re.fullmatch(r'\[.*\]|\d+',v)]
    if not values:continue
    value=values[0]
    name=re.split(r'\s+\d{1,2} de |\s*\(',value)[0].strip()
    if any(k in name.lower()for k in ['encargado','asumid','suprimid','funciones','vacante','no existe'])or len(name.split())<2:continue
    out.append(dict(name=name,role=role,period=heading,detail=value,source=history['source'],kind='secondary'))
  c.write(c.CACHE/(region+'-consejerias-historicas.json'),out);print(region,'actual',len(rows),'historico',len(out),flush=True)
if __name__=='__main__':governments()
