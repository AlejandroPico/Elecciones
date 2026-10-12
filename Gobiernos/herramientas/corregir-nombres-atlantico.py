"""Correcciones nominales expresas; mantiene IDs, alias y los archivos originales."""
import importlib.util, json, pathlib, shutil
spec=importlib.util.spec_from_file_location('m','Gobiernos/herramientas/incorporar-atlantico.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ROOT=pathlib.Path('.').resolve();PEOPLE=ROOT/'Políticos';BACKUP=ROOT/'test-results/atlantico/fichas-corregidas'
corrections=[
 ('Guillermo Guigou','Guillermo Guigou Suárez','https://www.boe.es/boe/dias/2000/12/26/pdfs/A45813-45813.pdf'),
 ('Rodolfo J. Núñez Ruano','Rodolfo José Núñez Ruano','https://www.boe.es/diario_boe/txt.php?id=BOE-A-1990-17400'),
 ('José Manuel Ruano','José Miguel Ruano León','https://www.gobiernodecanarias.org/boc/2003/134/005.html'),
 ('Narvay Quintero Castañeda','Alejandro Narvay Quintero Castañeda','https://www.gobiernodecanarias.org/organigrama/ficha-altos-cargos/?ou=42084'),
 ('Poli Suárez Nuez','Hipólito Alejandro Suárez Nuez','https://www.parcan.es/files/media/texto/2023/texto11735.pdf'),
]
reports=[]
for old,new,url in corrections:
    a,b=PEOPLE/old,PEOPLE/new
    assert a.resolve().parent==PEOPLE.resolve() and b.resolve().parent==PEOPLE.resolve()
    if not (a/'ficha.json').exists():continue
    meta=m.load(a/'ficha.json');existing=m.load(b/'ficha.json')
    if existing:
        existing['legacyIds']=m.union(existing.get('legacyIds',[]),[meta['id'],*meta.get('legacyIds',[])])
        existing['knownAs']=m.union(existing.get('knownAs',[]),[old,*meta.get('knownAs',[])])
        for f in a.iterdir():
            if f.name=='ficha.json':continue
            target=b/f.name
            if not target.exists():shutil.copyfile(f,target)
            elif f.suffix=='.json':
                left,right=m.load(target),m.load(f)
                if isinstance(left,list) and isinstance(right,list):m.c.write(target,m.union(left,right))
        m.c.write(b/'ficha.json',existing)
        backup=BACKUP/old
        assert backup.resolve().is_relative_to((ROOT/'test-results').resolve()) and not backup.exists()
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(a),str(backup))
    else:
        meta['fullName']=new;meta['name']=new;meta['knownAs']=m.union(meta.get('knownAs',[]),[old]);m.c.write(a/'ficha.json',meta)
        a.rename(b)
    sources=m.load(b/'fuentes.json',[]);m.c.write(b/'fuentes.json',m.union(sources,[m.ref(url,'Contraste del nombre completo y del cargo')]))
    reports.append({'oldName':old,'fullName':new,'source':url,'id':m.load(b/'ficha.json')['id']})
path=ROOT/'Gobiernos/revisiones/2026-10-12-atlantico/correcciones-nominales.json'
m.c.write(path,m.union(m.load(path,[]),reports))
print('Nombres contrastados',len(reports))
