"""Consolidación expresa de variantes documentadas; nunca coincidencias aproximadas."""
import importlib.util,pathlib,shutil
s=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).with_name('catalogo-regional.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
root=pathlib.Path('Políticos').resolve()
cases=[
 ('Carlos García Adanero','Carlos Fernando García Adanero','Carlos Fernando García Adanero','congreso-266-15'),
 ('Román Felones Morras','Román José Felones Morras','Román José Felones Morrás','navarra-roman-jose-felones-morras'),
 ('Pedro Sánchez de Muniáin Lacasia','Pedro Sánchez de Muniáin Corera','Pedro Sánchez de Muniáin Corera','navarra-pedro-sanchez-de-muniain-corera'),
 ('Jesús Pejenaute Garde','Jesús Pejenaute Grávalos','Jesús Pejenaute Grávalos','navarra-jesus-pejenaute-garde'),
]
review=m.load('Gobiernos/revisiones/2026-10-16-norte/identidades-consolidadas.json',[])
for first,second,full,id in cases:
 folders=[root/first,root/second];destination=root/full
 existing=[p for p in folders if p.exists()]
 if not existing:continue
 for folder in [*existing,destination]:assert folder.resolve().parent==root
 metas=[m.load(p/'ficha.json')for p in existing]
 base=next((x for x in metas if x['id']==id),None)
 if not base:continue
 merged=dict(base);merged.update(name=full,fullName=full,knownAs=m.unique([first,second,*[name for x in metas for name in x.get('knownAs',[])]]),legacyIds=m.unique([*[x['id']for x in metas if x['id']!=id],*[v for x in metas for v in x.get('legacyIds',[])]]))
 # Un apellido completado erróneamente no se convierte en alias biográfico.
 wrong={'Pedro Sánchez de Muniáin Lacasia','Jesús Pejenaute Garde'}
 merged['knownAs']=[name for name in merged['knownAs']if name not in wrong and name!=full]
 files={}
 # La ficha con el identificador previo conserva la prioridad de sus metadatos.
 ordered=sorted(existing,key=lambda p:m.load(p/'ficha.json')['id']!=id)
 for folder in ordered:
  for file in folder.iterdir():
   assert file.is_file(),file
   if file.name=='ficha.json':continue
   if file.suffix=='.json':
    value=m.load(file)
    if file.name not in files:files[file.name]=value
    elif isinstance(value,list)and isinstance(files[file.name],list):files[file.name]=m.unique([*files[file.name],*value])
   else:
    destination.mkdir(parents=True,exist_ok=True);target=destination/file.name
    if file.resolve()!=target.resolve():
     if target.exists():assert target.read_bytes()==file.read_bytes(),file
     else:shutil.copyfile(file,target)
 destination.mkdir(parents=True,exist_ok=True)
 for name,value in files.items():m.c.write(destination/name,value)
 m.c.write(destination/'ficha.json',merged)
 for folder in existing:
  if folder.resolve()==destination.resolve():continue
  for file in folder.iterdir():
   # Solo retirar una copia después de comprobar su conservación en el destino.
   assert (destination/file.name).exists(),file
   file.unlink()
  folder.rmdir()
 review.append(dict(id=id,fullName=full,variants=[first,second],legacyIds=merged['legacyIds']))
if review:m.c.write('Gobiernos/revisiones/2026-10-16-norte/identidades-consolidadas.json',m.unique(review))
print('Consolidaciones verificadas',len(review))
