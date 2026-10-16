"""Transcribe fuentes murcianas conservando su alcance y sus discrepancias."""
import importlib.util,pathlib,re,io,json
from urllib.parse import urljoin
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-murcia.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
import pymupdf
MONTHS=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']

def presidencies():
 url='https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_08';p=c.soup(url);rows=[]
 for h in p.select('h3'):
  name=re.sub(r'\s*\([^)]*\)\)?','',c.clean(h.get_text(' ',strip=True))).strip();para=h.find_next('p')
  if not para or 'Nombramiento:'not in para.get_text():continue
  a=para.find('a',href=True);source=urljoin(url,a['href']);raw=c.fetch(source)
  text=c.clean(' '.join(pg.get_text()for pg in pymupdf.open(stream=raw,filetype='pdf')))
  number=re.search(r'Real Decreto\s+(\d+/\d{4})',para.get_text(),re.I)[1]
  match=re.search(r'Real Decreto\s+'+re.escape(number.split('/')[0])+r'/(\d{4})[.,]?\s*(?:de\s+)?(\d{1,2})\s+de\s+(\w+)',text,re.I)
  if not match or match[3].lower()not in MONTHS:
   # El PDF de un BOE antiguo contiene varios decretos en dos columnas; el
   # epígrafe del Senado identifica el decreto concreto, no el texto vecino.
   match=re.search(r'Real Decreto\s+'+re.escape(number.split('/')[0])+r'/(\d{4})[.,]?\s*(?:de\s+)?(\d{1,2})\s+de\s+(\w+)',para.get_text(),re.I)
  assert match,(name,source,text[:400]);date=f'{match[1]}-{MONTHS.index(match[3].lower())+1:02}-{int(match[2]):02}'
  rows.append(dict(name=name,date=date,source=source,dossier=url,title=c.clean(para.get_text(' ',strip=True)),originalText=text))
 c.write(c.CACHE/'presidencias.json',sorted(rows,key=lambda d:d['date']));print('PRESIDENCIAS',len(rows),flush=True)

def cabinets():
 url='https://es.wikipedia.org/wiki/Consejo_de_Gobierno_de_la_Regi%C3%B3n_de_Murcia';p=c.soup(url);out=[]
 for i,table in enumerate(p.select('.mw-parser-output table')):
  if not 5<=i<=22:continue
  grid=[];spans={}
  for tr in table.select('tr'):
   cells=[];col=0
   for td in tr.find_all(['td','th'],recursive=False):
    while col in spans:
     val,rest=spans[col];cells.append(val)
     if rest==1:del spans[col]
     else:spans[col]=(val,rest-1)
     col+=1
    text=c.clean(re.sub(r'\[[^]]*\]','',td.get_text(' ',strip=True)))
    for k in range(int(td.get('colspan',1))):
     cells.append(text)
     if int(td.get('rowspan',1))>1:spans[col]=(text,int(td['rowspan'])-1)
     col+=1
   while col in spans:
    val,rest=spans[col];cells.append(val)
    if rest==1:del spans[col]
    else:spans[col]=(val,rest-1)
    col+=1
   grid.append(cells)
  h=table.find_previous(['h2','h3','h4']);out.append(dict(index=i,source=url,heading=c.clean(h.get_text()),rows=grid))
 c.write(c.CACHE/'gabinetes-enciclopedicos.json',out)
 print('CUADROS',len(out),flush=True)

def assemblies():
 # El texto institucional distingue constitución, elección presidencial y
 # apertura. Se guarda completo para contrastar las fechas de cada etapa.
 directory=r.BASE+'/arm/elecciones';p=c.soup(directory);out=[]
 for a in p.select('a[href]'):
  if not re.search(r'/content/(?:[ivx]+-legislatura|periodo-provisional)',a['href']):continue
  url=urljoin(directory,a['href']);body=r.main(url);out.append(dict(source=url,text=body.get_text('\n',strip=True)))
 c.write(c.CACHE/'etapas-asamblea.json',out)

def current_decrees():
 # Transcripción contrastada con la nota nominal de la CARM y los decretos
 # del suplemento S6 consultados en el índice público. La descarga directa
 # devuelve una página de verificación: no se interpreta como un decreto.
 source='https://www.carm.es/web/servlet/pagina?IDCONTENIDO=125172&IDTIPO=10&RASTRO=c%24m120%2C126%2C2166'
 rows=[dict(name=full,role=role,source=source)for full,role in [
  ('Concepción Ruiz Caballero','Consejera de Política Social, Familias e Igualdad'),
  ('María Isabel López Aragón','Consejera de Economía, Hacienda, Portavocía, Fondos Europeos y Transformación Digital'),
  ('Marcos Ortuño Soto','Consejero de Presidencia, Juventud, Acción Exterior y Emergencias'),
  ('Joaquín Buendía Gómez','Consejero de Agua, Agricultura, Ganadería y Pesca'),
  ('Luis Alberto Marín González','Consejero de Empresa, Empleo y Economía Social'),
  ('Juan María Vázquez Rojas','Consejero de Medio Ambiente, Industria, Universidades, Investigación y Mar Menor'),
  ('Carmen María Conesa Nieto','Consejera de Turismo, Cultura y Deportes'),
  ('Víctor Marín Navarro','Consejero de Educación y Formación Profesional'),
  ('Jorge García Montoro','Consejero de Infraestructuras y Desarrollo Territorial'),
  ('Isabel Ayala Vigueras','Consejera de Salud')]]
 decrees={'María Isabel López Aragón':(2489,843171),'Joaquín Buendía Gómez':(2491,843173),'Luis Alberto Marín González':(2492,843174),'Jorge García Montoro':(2495,843177),'Isabel Ayala Vigueras':(2495,843177)}
 for row in rows:
  if row['name']in decrees:
   number,record=decrees[row['name']];row.update(source=f'https://www.borm.es/services/anuncio/ano/2026/numero/{number}/pdf?id={record}',appointment='2026-05-29')
  if row['name']=='Joaquín Buendía Gómez':row.update(image='https://www.alcantarilla.es/wp-content/uploads/2022/03/alcalde1.jpg',credit='Ayuntamiento de Alcantarilla · retrato publicado en su ficha de alcalde (2019-2023)',portraitSource='https://www.alcantarilla.es/corporacion-municipal-legislatura-2019-2023/joaquin-buendia-gomez/',education=['Ingeniero técnico en Electrónica Industrial por la Escuela Universitaria Politécnica de Cartagena (1988-1992).'])
  if row['name']=='Jorge García Montoro':row.update(image='https://confebus.org/assets/uploads/img/1722241528_cfc4d5de319bbbf006f9.jpeg',portraitSource='https://confebus.org/publicaciones/ver/4506/jorge-garcia-montoro-asume-la-consejeria-de-fomento-e-infraestructuras-de-murcia',credit='Confebus · retrato individual identificado de Jorge García Montoro, julio de 2024',education=['Licenciado en Derecho por la Universidad de Murcia.','Máster en Banca y Mercados Financieros BSCH–Universidad de Cantabria.','Máster en Estudios sobre la Unión Europea por la UCAM.'])
  if row['name']=='Isabel Ayala Vigueras':row.update(image='https://doihojqqs770p.cloudfront.net/articulos/articulos-197755-1200x675.jpg',portraitSource='https://www.consalud.es/autonomias/murcia/isabel-ayala-vigueras-nueva-consejera-de-salud-de-la-region-de-murcia.html',credit='ConSalud · fotografía individual identificada en la información de su nombramiento, mayo de 2026',source='https://www.borm.es/services/anuncio/ano/2026/numero/2496/pdf?id=843178',education=['Licenciada en Medicina y Cirugía por la Universidad de Murcia. Especialista en Medicina Familiar y Comunitaria.'],educationSource='https://www.carm.es/web/pagina?IDCONTENIDO=54732&IDTIPO=11&RASTRO=c%24m22660')
  if row['name']=='Víctor Marín Navarro':row.update(image='https://www.mazarronnoticias.org/wp-content/uploads/2023/01/160120232115541.jpg',portraitSource='https://www.mazarronnoticias.org/2023/01/el-mazarronero-victor-marin-nuevo-consejero-de-educacion/',credit='Mazarrón Noticias · retrato identificado de Víctor Marín en su nombramiento de enero de 2023',education=['Licenciado en Geografía e Historia y doctor en Historia del Arte por la Universidad de Murcia.'],educationSource='https://www.carm.es/web/pagina?IDCONTENIDO=51268&IDTIPO=11&RASTRO=c%24m25987%2C121%2C50474')
  if row['name']=='María Isabel López Aragón':row.update(image='https://s1.elespanol.com/2024/07/15/actualidad/870673259_247786719_855x1140.jpg',portraitSource='https://www.elespanol.com/espana/murcia/20240715/lopez-miras-introduce-licenciados-derecho-gobierno-pasa-pagina-vox-murcia/870663017_0.html',credit='CARM · retrato de Marisa López Aragón publicado por El Español en julio de 2024',education=['Licenciada en Derecho por la Universidad de Murcia.'],educationSource='https://www.carm.es/web/pagina?IDCONTENIDO=51887&IDTIPO=11&RASTRO=c79%24m626')
 c.write(c.CACHE/'gobierno-vigente.json',list({row['name']:row for row in rows}.values()));print('CONSEJERÍAS',len(rows),flush=True)

if __name__=='__main__':
 import sys
 if '--vigente'in sys.argv:current_decrees()
 else:presidencies();cabinets();assemblies()
