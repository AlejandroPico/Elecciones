"""Recupera retratos documentados; nunca reemplaza imágenes anteriores ni genera caras."""
import importlib.util,pathlib,json,io,sys,collections,concurrent.futures,time,hashlib
from urllib.parse import urlencode
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-extremadura-balears.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
from PIL import Image
CACHE=c.CACHE;REV='2026-10-16-extremadura-balears'
people={row['id']:(pathlib.Path(row['folder']),row['meta'])for row in json.loads((CACHE/'catalogo-base.json').read_text('utf8'))}
def read(p):return json.loads(pathlib.Path(p).read_text('utf8'))
def photo(id,info):
 folder,meta=people[id]
 if(folder/'retrato.json').exists():return False
 raw=c.fetch(info['original']);image=Image.open(io.BytesIO(raw));fmt=image.format;image.verify();assert image.width>20 and image.height>20
 suffix={'JPEG':'jpg','PNG':'png','WEBP':'webp'}[fmt];file='retrato-complementario.'+suffix;(folder/file).write_bytes(raw);c.write(folder/'retrato.json',dict(file=file,reviewedAt=c.CHECKED,**info));return True
needed={}
for region in ['Extremadura','Illes Balears']:
 root=pathlib.Path('Gobiernos/Autonomías')/region
 for section in ['Gobierno','Parlamento']:
  stage=read(sorted(root.glob(section+'/*/composicion.json'))[-1])
  for member in stage.get('records',stage.get('terms',[])):
   id=member['person'];folder,meta=people[id]
   if not(folder/'retrato.json').exists():needed[id]=member['name']
if '--buscar'in sys.argv:
 candidates=[];rows=list(needed.items())
 for offset in range(0,len(rows),45):
  batch=rows[offset:offset+45];url='https://es.wikipedia.org/w/api.php?'+urlencode(dict(action='query',titles='|'.join(n for id,n in batch),prop='pageimages|extracts',piprop='name',exintro=1,explaintext=1,format='json',redirects=1));query=json.loads(c.fetch(url))['query'];redirects={p['from']:p['to']for p in query.get('redirects',[])};normalized={p['from']:p['to']for p in query.get('normalized',[])};pages={p['title']:p for p in query['pages'].values()}
  for id,name in batch:
   title=normalized.get(name,name);page=pages.get(redirects.get(title,title),{});
   if page.get('pageimage'):candidates.append(dict(person=id,name=name,title=page['title'],image=page['pageimage'],extract=page.get('extract','')[:1200]))
 c.write(CACHE/'retratos-candidatos.json',candidates);print(json.dumps(candidates,ensure_ascii=False,indent=2),flush=True)
if '--guardar'in sys.argv:
 candidates=read(CACHE/'retratos-candidatos-revisados.json');filenames=[p['image']for p in candidates];url='https://commons.wikimedia.org/w/api.php?'+urlencode(dict(action='query',titles='|'.join('File:'+n for n in filenames),prop='imageinfo',iiprop='url|extmetadata',format='json'));pages=json.loads(c.fetch(url))['query']['pages'];infos={p['title'].removeprefix('File:'):p['imageinfo'][0]for p in pages.values()if p.get('imageinfo')};results=[]
 for row in candidates:
  try:
   info=infos[row['image'].replace('_',' ')];ext=info['extmetadata']
   def val(k):return c.clean(r.c.BeautifulSoup(ext.get(k,{}).get('value',''),'html.parser').get_text(' ',strip=True))
   artist=val('Artist');license=val('LicenseShortName');licenseUrl=val('LicenseUrl');assert artist and license and licenseUrl
   added=photo(row['person'],dict(source=info['descriptionurl'],original=info['url'],credit=artist,license=license,licenseUrl=licenseUrl,identitySource='https://es.wikipedia.org/wiki/'+row['title'].replace(' ','_')));results.append(dict(person=row['person'],source=info['descriptionurl'],added=added))
  except Exception as error:results.append(dict(person=row['person'],error=str(error)))
 c.write(pathlib.Path('Gobiernos/revisiones')/REV/'retratos-complementarios.json',results);print(json.dumps(results,ensure_ascii=False,indent=2),flush=True)

if '--recuperar'in sys.argv:
 audit=read(pathlib.Path('Políticos/revisiones')/REV/'informe.json');jobs=sorted(audit['portraitErrors'],key=lambda row:row['person']not in needed);results=[]
 def recover(row):
  if not(people[row['person']][0]/'retrato.json').exists():time.sleep(1.7)
  try:
   added=photo(row['person'],dict(source=row['source'],original=row['resource'],credit='Retrato institucional de la ficha individual de '+('la Asamblea de Extremadura'if'asambleaex.es'in row['source']else'el Parlament de les Illes Balears')));return dict(person=row['person'],added=added)
  except Exception as error:return dict(person=row['person'],error=str(error))
 with concurrent.futures.ThreadPoolExecutor(1)as pool:
  for i,result in enumerate(pool.map(recover,jobs)):
   results.append(result)
   if(i+1)%25==0:print('REINTENTADOS',i+1,'/',len(jobs),'RECUPERADOS',sum(p.get('added',False)for p in results),flush=True)
 c.write(CACHE/'retratos-recuperados.json',results)

if '--pdf'in sys.argv:
 import pymupdf
 source='https://contingutsweb.parlamentib.es/comunicacio/11/HemicicleParlamentariperdiputatsagost2023_reduit.pdf';raw=c.fetch(source);assert hashlib.sha256(raw).hexdigest()=='03dbef5bf453c182755b7ab9d4ac03d5c2e07c73e5778d98b92ef3cda59bf825','La edición del PDF ha cambiado: revisar las correspondencias antes de extraer retratos';doc=pymupdf.open(stream=raw,filetype='pdf');rows=[('baleares-pedro-m-alvarez-i-gelabert',332,4),('baleares-maria-de-lluc-fornas-i-munar',333,4),('baleares-veronica-llufriu-i-vidal',392,5),('baleares-teresa-suarez-i-genovard',391,5),('baleares-jose-maria-garcia-i-garcia',417,6)];results=[]
 for id,xref,page in rows:
  folder,meta=people[id]
  if(folder/'retrato.json').exists():continue
  resource=doc.extract_image(xref);file='retrato-parlament-publicacion.'+resource['ext'];(folder/file).write_bytes(resource['image']);c.write(folder/'retrato.json',dict(file=file,source=source,original=source,credit='Parlament de les Illes Balears · publicación institucional «L’hemicicle parlamentari»',page=page,resource=xref,reviewedAt=c.CHECKED,note='Recurso individual incrustado en el PDF oficial y contrastado visualmente con su nombre. Resolución original conservada; no se amplía artificialmente.'));results.append(dict(person=id,page=page,resource=xref,source=source))
 c.write(pathlib.Path('Gobiernos/Autonomías/Illes Balears/fuentes/retratos-publicacion.json'),results);print('RETRATOS DEL PDF',len(results),flush=True)

if '--auditar'in sys.argv:
 path=pathlib.Path('Políticos/revisiones')/REV/'informe.json';audit=read(path);identities=read(pathlib.Path('Gobiernos/revisiones')/REV/'identidades.json');reviewed={r['person']for r in identities};missing=sorted(id for id in reviewed if not(people[id][0]/'retrato.json').exists());audit['missingPortraits']=missing;audit['allMissingPortraits']=sorted(id for id,(folder,meta)in people.items()if not(folder/'retrato.json').exists());audit['portraitErrors']=[dict(person=row['person'],source=row['source'],resource=row['resource'],error='No se pudo recuperar el recurso institucional; la conexión de la fuente se cerró o el recurso no respondió.')for row in audit['portraitErrors']if row['person']in missing];c.write(path,audit)
 rows=[dict(person=id,name=people[id][1]['fullName'],reason='No hay retrato individual contrastado en las fuentes consultadas.',source=next((r['source']for r in identities if r['person']==id),None))for id in missing];c.write(pathlib.Path('Gobiernos/revisiones')/REV/'retratos-pendientes.json',rows);print('RETRATOS PENDIENTES',len(missing),'ERRORES DE DESCARGA',len(audit['portraitErrors']),flush=True)
