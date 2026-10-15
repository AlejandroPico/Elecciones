"""Consolida únicamente correspondencias expresas contrastadas; no busca parecidos."""
import json,pathlib,shutil
ROOT=pathlib.Path('.').resolve();PEOPLE=ROOT/'Políticos';DATE='2026-10-15'
def read(p,default=None):return json.loads(p.read_text('utf8'))if p.exists()else default
def write(p,v):
    text=json.dumps(v,ensure_ascii=False,indent=2)+'\n';p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists()or p.read_text('utf8')!=text:p.write_text(text,'utf8')
def union(a,b):return a+[x for x in b if x not in a]

def consolidate(oldName,fullName,oldId,canonicalId,source):
    old=PEOPLE/oldName;new=PEOPLE/fullName
    if not old.exists():return
    assert old.resolve().parent==PEOPLE and new.resolve().parent==PEOPLE
    extra=read(old/'ficha.json');meta=read(new/'ficha.json')
    assert extra['id']==oldId and meta['id']==canonicalId
    for file in old.iterdir():
        if file.name=='ficha.json':continue
        target=new/file.name
        if file.suffix=='.json':
            a=read(target);b=read(file)
            if isinstance(a,list)and isinstance(b,list):write(target,union(a,b))
            elif a is None:shutil.copy2(file,target)
            elif isinstance(a,dict)and isinstance(b,dict):
                if file.name=='retrato.json':write(new/f'retrato-historico-{oldId}.json',b)
                else:write(target,{**b,**a})
            else:raise ValueError('Tipos incompatibles: '+str(file))
        elif not target.exists():shutil.copy2(file,target)
        elif file.read_bytes()!=target.read_bytes():raise ValueError('Recurso con colisión: '+str(file))
    meta['knownAs']=union(meta.get('knownAs',[]),[oldName]);meta['legacyIds']=union(meta.get('legacyIds',[]),[oldId,*extra.get('legacyIds',[])])
    write(new/'ficha.json',meta)
    write(new/'fuentes.json',union(read(new/'fuentes.json',[]),[{'label':'Identidad contrastada · trayectoria autonómica y Cortes Generales','url':source,'kind':'encyclopedic'}]))
    def replace(v):
        if isinstance(v,str):return canonicalId if v==oldId else v
        if isinstance(v,list):return [replace(x)for x in v]
        if isinstance(v,dict):
            result={k:replace(x)for k,x in v.items()}
            if result.get('person')==canonicalId and result.get('name')==oldName:result['name']=fullName
            return result
        return v
    for territory in ['Castilla-La Mancha','Castilla y León']:
        for p in (ROOT/'Gobiernos/Autonomías'/territory).rglob('*.json'):write(p,replace(read(p)))
    identities=ROOT/'Gobiernos/revisiones/2026-10-15-castillas/identidades.json';write(identities,replace(read(identities)))
    audit=PEOPLE/'revisiones/2026-10-15-castillas/informe.json';report=read(audit)
    report['newPeople']=[i for i in report['newPeople']if i!=oldId];report['totalPeople']-=1;report['peopleReviewed']-=1
    report['allMissingPortraits']=[i for i in report['allMissingPortraits']if i!=oldId];write(audit,report)
    mapping=ROOT/'Gobiernos/Autonomías/Castilla y León/fuentes/identidades-revisadas.json'
    write(mapping,{**read(mapping,{}),oldName:{'fullName':fullName,'source':source,'note':'Identidad contrastada con la biografía individual, la ficha parlamentaria y su trayectoria autonómica.'}})
    revisions=ROOT/'Gobiernos/revisiones/2026-10-15-castillas/correcciones-nominales.json'
    write(revisions,union(read(revisions,[]),[{'person':canonicalId,'legacyId':oldId,'nameInSource':oldName,'fullName':fullName,'source':source}]))
    backup=ROOT/'test-results/castillas/identidades-consolidadas'/oldName
    assert backup.resolve().is_relative_to(ROOT/'test-results/castillas')and not backup.exists()
    backup.parent.mkdir(parents=True,exist_ok=True);old.rename(backup)
    print('Consolidada',oldName,'→',fullName,flush=True)

if __name__=='__main__':
    consolidate('José Constantino Nalda','José Constantino Nalda García','cyl-jose-constantino-nalda','senado-10906','https://es.wikipedia.org/wiki/Jos%C3%A9_Constantino_Nalda')
    consolidate('Milagros Marcos','Milagros Marcos Ortega','cyl-milagros-marcos','congreso-320-15','https://es.wikipedia.org/wiki/Milagros_Marcos')
