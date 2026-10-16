"""Correcciones explícitas de esta incorporación, con conservación de recursos e IDs."""
import importlib.util,pathlib,shutil
s=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).with_name('catalogo-regional.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
root=pathlib.Path('Políticos').resolve()
cases=[('Sergio Marqués','Sergio Marqués Fernández'),('Lydia Espina','Lydia Espina López'),('Nieves Roqueñí','María Nieves Roqueñí Gutiérrez')]
review=[]
for short,full in cases:
 source=root/short;target=root/full
 if not source.exists():continue
 assert source.parent==target.parent==root
 base=m.load(target/'ficha.json')or m.load(source/'ficha.json');other=m.load(source/'ficha.json')
 target.mkdir(exist_ok=True)
 for file in source.iterdir():
  assert file.is_file()
  if file.name=='ficha.json':continue
  dest=target/file.name
  if dest.exists():
   if file.suffix=='.json':
    old=m.load(dest);new=m.load(file)
    if isinstance(old,list)and isinstance(new,list):m.c.write(dest,m.unique(old+new))
   else:assert dest.read_bytes()==file.read_bytes()
  else:shutil.copyfile(file,dest)
 base.update(name=full,fullName=full,knownAs=m.unique([short,*base.get('knownAs',[]),*other.get('knownAs',[])]))
 if base['id']!=other['id']:base['legacyIds']=m.unique([*base.get('legacyIds',[]),other['id'],*other.get('legacyIds',[])])
 m.c.write(target/'ficha.json',base)
 for file in source.iterdir():
  assert (target/file.name).exists();file.unlink()
 source.rmdir();review.append(dict(person=base['id'],variant=short,fullName=full))
# La página de paginación no es una identidad. Este registro erróneo aún no se ha publicado.
bad=root/'XI Legislatura'
baseline=m.load('Gobiernos/revisiones/2026-10-16-cantabrico/conservacion.json')['baselineIds']
if bad.exists():
 assert bad.parent==root and m.load(bad/'ficha.json')['id']not in baseline
 for file in bad.iterdir():assert file.is_file();file.unlink()
 bad.rmdir()
aliases=pathlib.Path('Gobiernos/Autonomías/Asturias/fuentes/identidades-revisadas.json')
data=m.load(aliases);data.update(dict(cases));m.c.write(aliases,data)
if review:m.c.write('Gobiernos/revisiones/2026-10-16-cantabrico/identidades-consolidadas.json',review)
