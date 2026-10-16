"""Una única ficha para Concepción Bravo, conservando el ID previo del Congreso."""
import importlib.util,pathlib,shutil
s=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).with_name('catalogo-regional.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
root=pathlib.Path('Políticos').resolve();source=root/'Mª Concepción Bravo Ibáñez';target=root/'María Concepción Bravo Ibáñez'
if source.exists():
 assert source.parent==target.parent==root
 base=m.load(source/'ficha.json');other=m.load(target/'ficha.json',{})
 assert base['id']=='congreso-45-11'
 assert m.load(source/'datos-personales.json')['birthDate']==m.load(target/'datos-personales.json')['birthDate']=='1954-05-29'
 target.mkdir(exist_ok=True)
 for file in source.iterdir():
  assert file.is_file()
  if file.name=='ficha.json':continue
  dest=target/file.name
  if not dest.exists():shutil.copyfile(file,dest)
  elif file.suffix=='.json':
   old=m.load(file);new=m.load(dest)
   if isinstance(old,list)and isinstance(new,list):m.c.write(dest,m.unique(old+new))
   elif isinstance(old,dict)and isinstance(new,dict):
    merged={**new,**old}
    for key in old.keys()&new.keys():
     if isinstance(old[key],list)and isinstance(new[key],list):merged[key]=m.unique(old[key]+new[key])
    m.c.write(dest,merged)
  else:assert dest.read_bytes()==file.read_bytes()
 base.update(name=target.name,fullName=target.name,knownAs=m.unique([source.name,*base.get('knownAs',[]),*other.get('knownAs',[])]),legacyIds=m.unique([*base.get('legacyIds',[]),other['id'],*other.get('legacyIds',[])]))
 m.c.write(target/'ficha.json',base)
 for file in source.iterdir():
  assert(target/file.name).exists();file.unlink()
 source.rmdir()
 m.c.write('Gobiernos/revisiones/2026-10-16-rioja/identidades-consolidadas.json',[dict(person=base['id'],fullName=base['fullName'],previousName=source.name,legacyIds=base['legacyIds'],reason='Coinciden nombre, fecha de nacimiento 29/05/1954 y trayectoria riojana en las fichas institucionales del Congreso y del Parlamento.')])
