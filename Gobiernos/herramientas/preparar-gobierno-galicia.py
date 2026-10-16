"""Directorio vigente, retratos y nombramientos originales de la Xunta."""
import importlib.util,pathlib,re,io,sys
s=importlib.util.spec_from_file_location('g',pathlib.Path(__file__).with_name('consultar-galicia.py'));g=importlib.util.module_from_spec(s);s.loader.exec_module(g);c=g.c
from pypdf import PdfReader
MONTHS=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
def presidencies():
 url='https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_03';p=c.soup(url);rows=[]
 for h in p.select('h3'):
  name=re.sub(r'\s*\([^)]*\)','',c.clean(h.get_text(' ',strip=True))).strip();para=h.find_next('p')
  if not para or 'Nombramiento:'not in para.get_text():continue
  a=para.find('a',href=True);source=g.urljoin(url,a['href']);raw=c.fetch(source)
  text=' '.join(pg.extract_text()or''for pg in PdfReader(io.BytesIO(raw)).pages)if raw.startswith(b'%PDF')else c.soup(source).get_text(' ',strip=True)
  text=c.clean(text);number=re.search(r'Real Decreto\s+(\d+/\d{4})',para.get_text(),re.I)[1];match=re.search(r'Real Decreto\s+'+re.escape(number.split('/')[0])+r'/(\d{4})[.,]?\s*(?:de\s+)?(\d{1,2})\s+de\s+(\w+)',text,re.I)
  if not match or match[3].lower()not in MONTHS:
   code=re.search(r'(\d{4,5})\s+REAL DECRETO\s+\d+/(\d{4})',text,re.I)
   assert code,(name,source,text[:400])
   source=f'https://www.boe.es/buscar/doc.php?id=BOE-A-{code[2]}-{int(code[1])}';text=c.soup(source).get_text(' ',strip=True)
   match=re.search(r'Real Decreto\s+\d+/(\d{4}),?\s*(?:de\s+)?(\d{1,2})\s+de\s+(\w+)',text,re.I)
  assert match,(name,source,text[:400]);date=f'{match[1]}-{MONTHS.index(match[3].lower())+1:02}-{int(match[2]):02}'
  rows.append(dict(name=name,date=date,source=source,dossier=url,title=c.clean(para.get_text(' ',strip=True))))
 c.write(c.CACHE/'presidencias.json',sorted(rows,key=lambda r:r['date']));print('Nombramientos presidenciales',len(rows),flush=True)
def current():
 directory='https://transparencia.xunta.gal/es/tema/transparencia-institucional/goberno-e-altos-cargos/composicion-do-goberno';p=c.soup(directory);bios='https://www.xunta.gal/es/conselleiros-do-goberno-galego';bp=c.soup(bios);portraits={}
 for row in bp.select('tr'):
  im=row.select_one('img.imaxenConselleiro');strong=row.select('td strong')
  if not im or not strong:continue
  heading=c.clean(' '.join(x.get_text(' ',strip=True)for x in strong));portraits[heading]=dict(image=g.urljoin(bios,im['src']),biography='\n'.join(c.clean(t.get_text(' ',strip=True))for t in row.select('td p')[1:]))
 rows=[]
 for a in p.select('a[href]'):
  if '/goberno/transparencia_'not in a['href']:continue
  name=c.clean(a.get_text(' ',strip=True));source=g.urljoin(directory,a['href']);profile=c.soup(source)
  dog=[dict(title=c.clean(x.get_text(' ',strip=True)),url=g.urljoin(source,x['href']))for x in profile.select('a[href]')if '/dog/'in x['href']]
  matches=[(h,v)for h,v in portraits.items()if h.endswith(name)];assert len(matches)<=1,name
  image=matches[0][1]if matches else{};role=matches[0][0][:-len(name)].strip().capitalize()if matches else'Presidente de la Xunta de Galicia';assert image or name=='Alfonso Rueda Valenzuela',name
  rows.append(dict(name=name,role=role,source=source,directory=directory,appointments=dog,**{k:v for k,v in image.items()if k!='role'}))
 assert len(rows)==13,rows
 c.write(c.CACHE/'gobierno-vigente.json',rows);print('Gobierno vigente',len(rows),flush=True)
 # Galería oficial de presidencias: fotos publicadas en el apartado nominal.
 url='https://www.xunta.gal/es/todos-os-presidentes';p=c.soup(url);gallery=[]
 for im in p.select('#audioContido img[src]'):
  if '/documents/'not in im['src']:continue
  gallery.append(dict(image=g.urljoin(url,im['src']),context=c.clean(im.parent.parent.get_text(' ',strip=True))[:500]))
 c.write(c.CACHE/'retratos-presidentes.json',dict(source=url,rows=gallery))
if __name__=='__main__':presidencies();current()
