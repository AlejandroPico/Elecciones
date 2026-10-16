"""Reúne cuatro marcadores de baja importados, sin perder IDs ni retratos."""
import importlib.util,pathlib,json,shutil,re
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-murcia.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
root=pathlib.Path('Políticos').resolve();base=pathlib.Path('Gobiernos/Autonomías/Región de Murcia');replacements={};names={};report=[]
def load(path):return json.loads(pathlib.Path(path).read_text('utf8'))
def unique(rows):return list({json.dumps(row,sort_keys=True,ensure_ascii=False):row for row in rows}.values())
for previous,current in [
 ('Encarnación Causó Baja Guillén Navarro','Encarnación Guillén Navarro'),
 ('Francisco Martín Causó Baja Bernabé Pérez','Francisco Martín Bernabé Pérez'),
 ('Manuel Causó Baja Molina Boix','Manuel Molina Boix'),
 ('Violante Causó Baja Tomás Olivares','Violante Tomás Olivares')]:
 old=root/previous;target=root/current
 assert old.is_relative_to(root)and target.is_relative_to(root)and old.parent==target.parent==root
 assert re.sub(r'\s+Causó Baja','',previous)==current
 if not old.exists():continue
 original=load(old/'ficha.json');meta=load(target/'ficha.json');oldid=original['id'];id=meta['id'];assert oldid.startswith('murcia-')and oldid!=id
 personal=old/'datos-personales.json';existing=target/'datos-personales.json'
 if personal.exists()and existing.exists():assert load(personal).get('birthDate')==load(existing).get('birthDate')
 photo=load(old/'retrato.json')if(old/'retrato.json').exists()else None
 for file in old.iterdir():
  assert file.is_file()
  if file.name=='ficha.json'or photo and file.name in['retrato.json',photo['file']]:continue
  dest=target/file.name
  if not dest.exists():shutil.copyfile(file,dest)
  elif file.suffix=='.json':
   a=load(file);b=load(dest)
   if isinstance(a,list)and isinstance(b,list):c.write(dest,unique(b+a))
   elif isinstance(a,dict)and isinstance(b,dict):
    merged={**a,**b}
    for key in a.keys()&b.keys():
     if isinstance(a[key],list)and isinstance(b[key],list):merged[key]=unique(b[key]+a[key])
    c.write(dest,merged)
  else:assert dest.read_bytes()==file.read_bytes()
 if photo:
  raw=(old/photo['file']).read_bytes()
  if not(target/'retrato.json').exists():
   shutil.copyfile(old/photo['file'],target/photo['file']);c.write(target/'retrato.json',photo)
  else:
   file='retrato-historico-'+oldid+pathlib.Path(photo['file']).suffix;dest=target/file
   if dest.exists():assert dest.read_bytes()==raw
   else:dest.write_bytes(raw)
   c.write(dest.with_suffix('.json'),{**photo,'file':file})
 meta['legacyIds']=unique([*meta.get('legacyIds',[]),oldid,*original.get('legacyIds',[])])
 meta['knownAs']=unique([n for n in [*meta.get('knownAs',[]),*original.get('knownAs',[])]if 'Causó Baja'not in n]);c.write(target/'ficha.json',meta)
 replacements[oldid]=id;names[id]=current
 report.append(dict(person=id,fullName=current,previousId=oldid,previousName=previous,reason='El índice de IX inserta la anotación causó baja en el nombre. La ficha individual y la trayectoria identifican a la misma persona; las fechas de nacimiento coinciden cuando están publicadas.',portraitPreserved=bool(photo)))
 # Solo carpetas personales explícitas y verificadas dentro de Políticos.
 for file in old.iterdir():
  assert file.resolve().is_relative_to(root)and file.parent==old;file.unlink()
 old.rmdir()

for file in base.glob('*/*/composicion.json'):
 data=load(file)
 def visit(value):
  if isinstance(value,dict):
   if value.get('person')in replacements:value['person']=replacements[value['person']];value['name']=names[value['person']]
   for item in value.values():visit(item)
  elif isinstance(value,list):
   for i,item in enumerate(value):
    if isinstance(item,str)and item in replacements:value[i]=replacements[item]
    else:visit(item)
 visit(data)
 if 'records'in data:data['records']=list({row['person']:row for row in data['records']}.values())
 c.write(file,data)

if replacements:
 file=root/'revisiones/2026-10-16-murcia/informe.json';audit=load(file);audit['newPeople']=[p for p in audit['newPeople']if p['id']not in replacements];audit['totalPeople']-=len(replacements);audit['peopleReviewed']-=len(replacements)
 available={id for id,name in names.items()if(root/name/'retrato.json').exists()}
 for key in['missingPortraits','allMissingPortraits']:audit[key]=sorted(id for id in audit[key]if id not in replacements and id not in available)
 audit['consolidatedIdentities']=report;c.write(file,audit);c.write('Gobiernos/revisiones/2026-10-16-murcia/identidades-consolidadas.json',report)
print('IDENTIDADES REUNIDAS',len(report),flush=True)
