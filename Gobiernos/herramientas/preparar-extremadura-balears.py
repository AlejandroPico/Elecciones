"""Preparación y contraste de los archivos institucionales de ambas comunidades."""
import importlib.util,pathlib,re,json,sys,collections
from urllib.parse import urljoin
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-extremadura-balears.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
import pymupdf
MONTHS=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
CAT_MONTHS=['gener','febrer','març','abril','maig','juny','juliol','agost','setembre','octubre','novembre','desembre']
def presidencies():
 allurl='https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?lang=es_ES&lang=gl_ES&tuto_08='
 for region,title,url in [('extremadura','Presidentes del Gobierno de Extremadura',allurl),('baleares','Presidentes del Gobierno de Illes Balears','https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_15')]:
  p=c.soup(url);main=next(h.parent for h in p.select('h1')if c.clean(h.get_text())==title);rows=[]
  for h in main.select('h3'):
   paragraph=h.find_next('p');text=c.clean(paragraph.get_text(' ',strip=True))
   if not text.startswith('Nombramiento:'):continue
   match=re.search(r'Real Decreto\s+\d+/(\d{4}),?\s+de\s+(\d{1,2})\s+de\s+(\w+)',text,re.I);assert match,(region,text)
   head=c.clean(h.get_text(' ',strip=True));name=re.sub(r'\s*\([^)]*\)','',head).strip();date=f'{match[1]}-{MONTHS.index(match[3].lower())+1:02}-{int(match[2]):02}'
   leg=re.search(r'([IVX]+) Legislatura',h.find_previous('h2').get_text())[1];a=paragraph.select_one('a[href]');source=urljoin(url,a['href'])
   rows.append(dict(name=name,date=date,legislature=r.ROMANS.index(leg)+1,source=source,dossier=url,original=text))
  c.write(c.CACHE/region/'presidencias.json',sorted(rows,key=lambda d:d['date']));print('PRESIDENCIAS',region,len(rows),flush=True)
def grid(table):
 rows=[];spans={}
 for tr in table.select('tr'):
  cells=[];col=0
  for td in tr.find_all(['td','th'],recursive=False):
   while col in spans:
    text,left=spans[col];cells.append(text)
    if left==1:del spans[col]
    else:spans[col]=(text,left-1)
    col+=1
   text=c.clean(re.sub(r'\[[^]]*\]','',td.get_text(' ',strip=True)))
   for _ in range(int(td.get('colspan',1))):
    cells.append(text)
    if int(td.get('rowspan',1))>1:spans[col]=(text,int(td['rowspan'])-1)
    col+=1
  while col in spans:
   text,left=spans[col];cells.append(text)
   if left==1:del spans[col]
   else:spans[col]=(text,left-1)
   col+=1
  rows.append(cells)
 return rows
def cabinets():
 for region,url in [('extremadura','https://es.wikipedia.org/wiki/Anexo:Composici%C3%B3n_de_la_Junta_de_Extremadura'),('baleares','https://es.wikipedia.org/wiki/Gobierno_de_las_Islas_Baleares')]:
  p=c.soup(url);tables=[]
  for i,table in enumerate(p.select('.mw-parser-output table')):
   heading=table.find_previous(['h2','h3','h4']);data=dict(index=i,source=url,heading=c.clean(heading.get_text())if heading else'',rows=grid(table));tables.append(data)
   print('CUADRO',region,i,data['heading'],str(data['rows'][:2])[:320],flush=True)
  c.write(c.CACHE/region/'gabinetes-complementarios.json',tables)
def current_governments():
 for region,url,names in [('extremadura','https://www.juntaex.es/es/lajunta',['María Guardiola Martín','Abel Bautista Morán','Óscar Arturo Fernández Calle','Elena Manzano Silva','Mercedes Morán Álvarez','Guillermo Santamaría Galdón','Sara García Espada','Juan José García García','Laureano León Rodríguez','Sandra Victoria Valencia Ramos','Francisco José Ramírez González']),('baleares','https://www.caib.es/webgoib/es/govern',['Margalida Prohens Rigo','Antoni Costa Costa','Antònia Maria Estarellas Torrens','Manuela García Romero','Antoni Vera Alemany','Alejandro Sáenz de San Pedro García','Sandra Fernández Herranz','Jaume Bauzá Mayol','José Luís Mateo Hernández','Catalina Teresa Cabrer González','Joan Simonet Pons','Juan Manuel Lafuente Mir'])]:
  p=c.soup(url)
  for name in names[:2]:
   node=next((a for a in p.select('a,p,span,h2,h3,h4,div')if c.clean(a.get_text(' ',strip=True))==name),None)
   if node:print('CURRENT CARD',region,name,str(node.parent.parent)[:6000],flush=True)
def government_cards():
 for region,url in [('extremadura','https://www.juntaex.es/es/lajunta'),('baleares','https://www.caib.es/webgoib/es/govern')]:
  p=c.soup(url);rows=[]
  if region=='extremadura':
   for card in p.select('.informacionFichaGobierno'):
    a=card.select_one('a.descripcion[href]');title=card.select_one('a.title');image=card.parent.select_one('img')
    if not a or not title:continue
    role=c.clean(title.get_text(' ',strip=True));full=c.clean(a.get_text(' ',strip=True));source=urljoin(url,a['href']);row=dict(name=full,role=role,source=source,image=urljoin(url,image['src'])if image else None,portraitSource=url)
    profile=c.soup(source);body=profile.select_one('.journal-content-article')or profile;biog=body.get_text('\n',strip=True)
    row['biography']=biog;c.write(c.CACHE/region/'cargos'/f'{len(rows)}.json',row);rows.append(row)
  else:
   for card in p.select('.goib-unitat-admin-item'):
    full=card.select_one('.goib-transparencia-nolink .line-clamp-3');role=card.select_one('a.goib-multilink[target="_self"] .line-clamp-3');image=card.select_one('img[src]')
    if not full or not role:continue
    rows.append(dict(name=c.clean(full.get_text()),role=c.clean(role.get_text()),source=url,image=urljoin(url,image['src'])if image else None,portraitSource=url))
  c.write(c.CACHE/region/'gobierno-vigente.json',rows);print('GOBIERNO VIGENTE',region,len(rows),flush=True)
def electoral_documents():
 elections=[(1983,'mayo'),(1987,'junio'),(1991,'mayo'),(1995,'mayo'),(1999,'junio'),(2003,'mayo'),(2007,'mayo'),(2011,'mayo'),(2015,'mayo'),(2019,'mayo'),(2023,'mayo'),(2025,'diciembre')]
 for n,(year,month)in enumerate(elections,1):
  url=f'https://www.juntaelectoralcentral.es/cs/jec/elecciones/Extremadura-{month}{year}'+('%20'if year==1995 else'')+'?p=1392649722119'
  try:
   p=c.soup(url);links=[urljoin(url,a['href'])for a in p.select('a[href]')if re.search(r'Escrutinio|actas de escrutinio',a.get_text(),re.I)]
   documents=[]
   for link in list(dict.fromkeys(links)):
    raw=c.fetch(link);doc=pymupdf.open(stream=raw,filetype='pdf');pages=[page.get_text()for page in doc];documents.append(dict(source=link,pages=pages));print('EXT ELECTOS',n,len(pages),sum(len(t)for t in pages),flush=True)
   if documents:c.write(c.CACHE/f'extremadura/elecciones/{n}.json',dict(**documents[0],directory=url,additionalDocuments=documents[1:]))
  except Exception as error:print('EXT ELECTOS NO DISPONIBLE',n,str(error),flush=True)
def ocr_electoral_documents():
 folder=c.CACHE/'tessdata';folder.mkdir(exist_ok=True);trained=folder/'spa.traineddata'
 if not trained.exists():trained.write_bytes(c.fetch('https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/spa.traineddata'))
 for n in range(1,5):
  file=c.CACHE/f'extremadura/elecciones/{n}.json';data=json.loads(file.read_text('utf8'))
  if sum(map(len,data['pages']))>100:continue
  doc=pymupdf.open(stream=c.fetch(data['source']),filetype='pdf');pages=[]
  for i,page in enumerate(doc):
   text=page.get_text(textpage=page.get_textpage_ocr(language='spa',dpi=220,tessdata=str(folder)));pages.append(text);print('OCR',n,i+1,len(text),flush=True)
  data.update(pages=pages,ocr=True);c.write(file,data)
def ocr_columns():
 file=c.CACHE/'extremadura/elecciones/1.json';data=json.loads(file.read_text('utf8'));doc=pymupdf.open(stream=c.fetch(data['source']),filetype='pdf');pages=[]
 for i,page in enumerate(doc):
  parts=[];rect=page.rect
  for x0,x1 in [(0,rect.width/2),(rect.width/2,rect.width)]:
   pix=page.get_pixmap(dpi=220,clip=pymupdf.Rect(x0,0,x1,rect.height));image=pymupdf.open(stream=pix.tobytes('png'),filetype='png');part=pymupdf.open(stream=image.convert_to_pdf(),filetype='pdf');partPage=part[0];tp=partPage.get_textpage_ocr(language='spa',dpi=220,full=True,tessdata=str(c.CACHE/'tessdata'));parts.append(partPage.get_text(textpage=tp))
  pages.append('\n'.join(parts));print('OCR COLUMNAS',i+1,len(pages[-1]),flush=True)
 data.update(pages=pages,ocr=True,ocrMethod='Lectura separada de las dos columnas del boletín.');c.write(file,data)
def jec():
 url='https://www.juntaelectoralcentral.es/cs/jec/elecciones/Extremadura-mayo2003?p=1392649722119';p=c.soup(url)
 for a in p.select('a[href]'):
  if c.clean(a.get_text())=='Elecciones Autonómicas':
   link=urljoin(url,a['href']);p=c.soup(link);print('JEC INDICE',link,[(c.clean(a.get_text()),urljoin(link,a['href']))for a in p.select('a[href]')if 'Extremadura'in a['href']or'1983'in a.get_text()][:20]);break
def explore():
 url='https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?lang=es_ES&lang=gl_ES&tuto_08=';p=c.soup(url)
 h=next(h for h in p.select('h1,h2')if c.clean(h.get_text())=='Presidentes del Gobierno de Extremadura')
 print('SENADO EXT',str(h.parent)[:1100]);print('PREV',str(h.find_previous('div',id=True))[:300])
 for region,url in [('extremadura','https://www.juntaex.es/es/lajunta'),('baleares','https://www.caib.es/webgoib/es/govern')]:
  p=c.soup(url)
  for h in p.select('h2,h3,h4'):
   if 'Guardiola'in h.get_text()or'Costa'in h.get_text():print('GOB',region,str(h.parent.parent)[:4200])
 for url in ['https://web.parlamentib.es/webgtp/statics/exptran.htm','https://web.parlamentib.es/webgtp/scripts/UnRegPers.asp?CFautor=338']:
  p=c.soup(url);print('SRC',url,[(a.name,a.get('src'))for a in p.select('frame,iframe,script[src]')]);print('IMAGES',[(i.get('src'),i.get('alt'))for i in p.select('img[src]')][:5])
  if 'UnRegPers'in url:
   print('TITLES',[c.clean(h.get_text())for h in p.select('b,strong')][:25]);print('TABLE',str(p.select('table')[0])[:4000])
if __name__=='__main__':
 if '--preparar'in sys.argv:presidencies();cabinets();current_governments();jec()
 elif '--cargos'in sys.argv:government_cards()
 elif '--electos'in sys.argv:electoral_documents()
 elif '--ocr'in sys.argv:ocr_electoral_documents()
 elif '--ocr-columnas'in sys.argv:ocr_columns()
 else:explore()
