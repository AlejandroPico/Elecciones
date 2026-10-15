"""Correspondencias nominales explícitas; conserva IDs, recursos y variantes publicadas."""
import json,pathlib,shutil
ROOT=pathlib.Path('.').resolve();PEOPLE=ROOT/'Políticos';DATE='2026-10-15'
def read(p,default=None):return json.loads(p.read_text('utf8'))if p.exists()else default
def write(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8')
def union(a,b):
    seen={json.dumps(x,sort_keys=True,ensure_ascii=False)for x in a};return a+[x for x in b if json.dumps(x,sort_keys=True,ensure_ascii=False)not in seen]
report=[]
old=PEOPLE/'Mª Mercedes Gómez Rodríguez';new=PEOPLE/'María Mercedes Gómez Rodríguez'
source='https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=aut_composiciongob_11'
if old.exists():
    assert old.resolve().parent==PEOPLE and new.resolve().parent==PEOPLE and not new.exists()
    meta=read(old/'ficha.json');meta['knownAs']=union(meta.get('knownAs',[]),[meta['fullName'],'Mercedes Gómez Rodríguez']);meta['name']=meta['fullName']=new.name
    old.rename(new);write(new/'ficha.json',meta)
    write(new/'fuentes.json',union(read(new/'fuentes.json',[]),[{'label':'Senado · nombre completo y nombramiento','url':source,'kind':'institutional'}]))
    report.append({'person':meta['id'],'nameInSource':old.name,'fullName':new.name,'source':source})
old=PEOPLE/'Blanca Fernández Morena';new=PEOPLE/'Blanca Pilar Fernández Morena'
source='https://www.cortesclm.es/web2/tv/vconsulta.php?id=6203'
if old.exists()and new.exists():
    original=read(old/'ficha.json');extra=read(new/'ficha.json');assert original['id']=='congreso-107-13'
    for file in old.iterdir():
        if file.name=='ficha.json':continue
        target=new/file.name
        if file.suffix=='.json'and file.name!='retrato.json':
            a=read(file);b=read(target)
            if isinstance(a,list)and isinstance(b,list):write(target,union(a,b))
            elif isinstance(a,dict)and isinstance(b,dict):write(target,{**b,**a})
            elif not target.exists():shutil.copy2(file,target)
        elif file.name=='retrato.json':
            photo=read(target)
            if photo:write(new/f"retrato-historico-{extra['id']}.json",photo)
            shutil.copy2(file,target)
        elif not target.exists():shutil.copy2(file,target)
        elif file.read_bytes()!=target.read_bytes():raise ValueError('Recurso con colisión: '+str(file))
    original['legacyIds']=union(original.get('legacyIds',[]),[extra['id'],*extra.get('legacyIds',[])])
    original['knownAs']=union(original.get('knownAs',[]),[original['name'],original['fullName']]);original['name']=original['fullName']=new.name;original['reviewedAt']=DATE
    write(new/'ficha.json',original);write(new/'fuentes.json',union(read(new/'fuentes.json',[]),[{'label':'Cortes · nombre completo y trayectoria regional','url':source,'kind':'institutional'}]))
    backup=ROOT/'test-results/castillas/identidades-originales'/old.name
    assert old.resolve().parent==PEOPLE and backup.resolve().is_relative_to(ROOT/'test-results/castillas')and not backup.exists()
    backup.parent.mkdir(parents=True,exist_ok=True);old.rename(backup)
    report.append({'person':original['id'],'legacyId':extra['id'],'nameInSource':old.name,'fullName':new.name,'source':source})
path=ROOT/'Gobiernos/revisiones/2026-10-15-castillas/correcciones-nominales.json';write(path,union(read(path,[]),report))
mapping={'Mª Mercedes Gómez Rodríguez':{'fullName':'María Mercedes Gómez Rodríguez','source':'https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=aut_composiciongob_11'},'Blanca Fernández Morena':{'fullName':'Blanca Pilar Fernández Morena','source':source}}
mappingPath=ROOT/'Gobiernos/Autonomías/Castilla-La Mancha/fuentes/identidades-revisadas.json'
write(mappingPath,{**read(mappingPath,{}),**mapping})
print('Identidades corregidas',len(report),flush=True)
