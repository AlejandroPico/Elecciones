"""Comprueba referencias, capacidad, retratos reales y cobertura del catálogo final."""
import concurrent.futures,json,pathlib
ROOT=pathlib.Path('.');PEOPLE=ROOT/'Políticos'
def read(path,default=None):return json.loads(path.read_text('utf8')) if path.exists() else default
def personal(folder):
    meta=read(folder/'ficha.json')
    if not meta:return None
    photo=read(folder/'retrato.json',{})
    return meta, bool(photo.get('file') and (folder/photo['file']).is_file())
with concurrent.futures.ThreadPoolExecutor(24) as pool:rows=[r for r in pool.map(personal,[p for p in PEOPLE.iterdir() if p.is_dir() and p.name not in ['interfaz','herramientas','revisiones']])if r]
people={m['id']:(m,photo)for m,photo in rows}
assert len(people)==len(rows),'IDs personales repetidos'
regions={}
for region in ['Canarias','Ceuta','Melilla']:
    groups={}
    for section in ['Gobierno','Parlamento']:
        periods=[read(p)for p in (ROOT/'Gobiernos/Autonomías'/region/section).glob('*/composicion.json')]
        for p in periods:
            terms=[*p.get('terms',[]),*p.get('archiveTerms',[]),*p.get('records',[]),*p.get('board',[]),*p.get('archiveBoard',[])]
            for t in terms:assert t['person']in people,(region,t['name'])
            if p.get('currentOnly'):
                current=p.get('terms',p.get('records',[]))
                assert len({t['person']for t in current})==len(current)
                groups[section]={'periods':len(periods),'currentPeople':len(current),'currentMissingPortraits':[t['person']for t in current if not people[t['person']][1]]}
        assert groups.get(section),(region,section)
    regions[region]=groups
p=PEOPLE/'revisiones/2026-10-12-atlantico/informe.json';audit=read(p)
audit['totalPeople']=len(rows);audit['allMissingPortraits']=sorted(m['id']for m,photo in rows if not photo);audit['coverage']=regions
p.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n','utf8')
target=ROOT/'Gobiernos/revisiones/2026-10-12-atlantico/informe.json';target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps({'checkedAt':audit['checkedAt'],'coverage':regions,'peopleReviewed':audit['people'],'newPeople':audit['newPeople'],'portraitsFromThisImport':audit['portraitsFromThisImport']},ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'totalPeople':len(rows),'missingPortraits':len(audit['allMissingPortraits']),'coverage':regions},ensure_ascii=False),flush=True)
