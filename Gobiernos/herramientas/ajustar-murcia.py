"""Correcciones finales contrastadas; conserva IDs y recursos anteriores."""
import importlib.util,pathlib,json,io,collections
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-murcia.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
from PIL import Image
root=pathlib.Path('Políticos').resolve();base=pathlib.Path('Gobiernos/Autonomías/Región de Murcia');changes=[]
def load(file):return json.loads(pathlib.Path(file).read_text('utf8'))

def parliamentary_group():
 file=base/'Parlamento/2023 Legislatura XI/composicion.json';data=load(file)
 person=root/'María Marín Martínez';meta=load(person/'ficha.json');id=meta['id'];source='https://www.asambleamurcia.es/diputado/11021/maria-marin-martinez'
 for row in data['records']:
  if row['person']==id:row['formationLabel']='Mixto'
 groups=collections.defaultdict(list)
 for row in data['records']:groups[row['formationLabel']].append(row)
 data['groups']=[dict(name=n,source=rows[0]['source'],members=rows)for n,rows in groups.items()];c.write(file,data)
 file=person/'grupos-autonomias.json';rows=load(file)
 for row in rows:
  if row.get('territory')=='murcia'and row.get('period')=='Legislatura XI':row['title']='Región de Murcia · Mixto'
 c.write(file,rows)
 file=person/'afiliaciones.json';rows=load(file);rows=[row for row in rows if not(row.get('territory')=='murcia'and row.get('period')=='Legislatura XI')]
 for label,organization,period in [('Mixto',None,'Legislatura XI'),('Podemos','podemos','Dirección regional documentada en la biografía de la XI legislatura')]:
  row=dict(organization=organization,name=label,period=period,kind='association',source=dict(label='Trayectoria publicada por la Asamblea Regional',url=source,kind='institutional'),territory='murcia')
  if row not in rows:rows.append(row)
 c.write(file,rows);changes.append(dict(person=id,correction='Grupo Mixto; Podemos se conserva como vinculación política documentada, diferenciada del grupo parlamentario.',source=source))

def full_name():
 old=root/'Marisol Sánchez Jódar';new=root/'María Soledad Sánchez Jódar'
 assert old.is_relative_to(root)and new.is_relative_to(root)
 if old.exists():
  assert not new.exists();meta=load(old/'ficha.json');assert meta['id']=='congreso-276-14';assert load(old/'datos-personales.json')['birthDate']=='1979-09-09';old.rename(new)
 meta=load(new/'ficha.json');meta.update(name=new.name,fullName=new.name,knownAs=list(dict.fromkeys(['Marisol Sánchez Jódar',*meta.get('knownAs',[])])),reviewedAt=c.CHECKED);c.write(new/'ficha.json',meta)
 for file in base.glob('*/*/composicion.json'):
  data=load(file)
  def visit(value):
   if isinstance(value,dict):
    if value.get('person')==meta['id']:value['name']=new.name
    for item in value.values():visit(item)
   elif isinstance(value,list):
    for item in value:visit(item)
  visit(data);c.write(file,data)
 changes.append(dict(person=meta['id'],previousName=old.name,fullName=new.name,correction='Nombre completo acreditado; se conserva el ID y toda la carpeta y sus recursos.',source='https://www.asambleamurcia.es/diputado/11038/maria-soledad-sanchez-jodar'))

def president_portrait():
 folder=root/'Fernando López Miras';meta=load(folder/'ficha.json');old=load(folder/'retrato.json');row=next(row for row in load(c.CACHE/'parlamentos/11.json')['members']if row['name']=='Fernando López Miras');source=row['source']
 if old['source']!=source:
  raw=c.fetch(row['image']);im=Image.open(io.BytesIO(raw));im.verify();suffix={'PNG':'png','JPEG':'jpg','WEBP':'webp'}[im.format]
  previous=folder/old['file'];historic=folder/('retrato-historico-'+meta['id']+previous.suffix)
  assert previous.is_relative_to(root)and historic.is_relative_to(root)
  if previous!=historic:
   if historic.exists():assert historic.read_bytes()==previous.read_bytes()
   else:previous.rename(historic)
  c.write(historic.with_suffix('.json'),{**old,'file':historic.name})
  file='retrato-murcia.'+suffix;(folder/file).write_bytes(raw);c.write(folder/'retrato.json',dict(file=file,credit='Asamblea Regional de Murcia · retrato institucional publicado en el directorio de la XI legislatura',source=source,original=row['image'],reviewedAt=c.CHECKED))
 changes.append(dict(person=meta['id'],correction='Retrato institucional de la Asamblea; imagen y créditos anteriores conservados como recurso histórico.',source=source))

if __name__=='__main__':
 parliamentary_group();full_name();president_portrait();c.write('Gobiernos/revisiones/2026-10-16-murcia/correcciones-finales.json',changes);print('CORRECCIONES',len(changes))
