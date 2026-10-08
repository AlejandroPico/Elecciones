"""Incorpora intervalos oficiales sin sustituir fichas previas ni deducir militancias.
Ejecutar tras consultar-catalunya.py. Reejecutable: no duplica fuentes ni mandatos.
"""
import collections, concurrent.futures, hashlib, io, json, pathlib, re, subprocess, sys, unicodedata, urllib.request
from urllib.parse import parse_qs, urlparse
sys.path.insert(0,'test-results/libraries')
from PIL import Image
BASE=pathlib.Path('.'); CACHE=BASE/'test-results/catalunya'; CHECKED='2026-10-08'
def read(p,default=None):return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def write(p,d):
    text=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
    if p.exists() and p.read_text(encoding='utf-8')==text:return
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def norm(value):
    value=unicodedata.normalize('NFD',value.lower())
    return ' '.join(w for w in re.sub(r'[^a-z0-9]+',' ',''.join(c for c in value if not unicodedata.combining(c))).split() if w!='i')
def slug(name):return norm(name).replace(' ','-')
def ref(url,label='Parlament de Catalunya · ficha oficial'):return {'label':label,'url':url,'kind':'institutional'}
def append(path,items):
    old=read(path,[]); keys={json.dumps(item,sort_keys=True,ensure_ascii=False) for item in old}
    for item in items:
        key=json.dumps(item,sort_keys=True,ensure_ascii=False)
        if key not in keys:old.append(item);keys.add(key)
    write(path,old)
people={}; index=collections.defaultdict(list)
for path in (BASE/'Políticos').glob('*/ficha.json'):
    meta=read(path); people[meta['id']]={'meta':meta,'folder':path.parent}
    for name in [meta.get('fullName'),meta.get('name'),*meta.get('knownAs',[])]:
        if name and meta['id'] not in index[norm(name)]:index[norm(name)].append(meta['id'])
previous_audit=read(BASE/'Gobiernos/revisiones/2026-10-08-catalunya/informe.json',{})
tracked=subprocess.check_output(['git','ls-files','-z','Políticos/*/ficha.json']).decode('utf-8').split('\0')
baseline={read(BASE/p)['id'] for p in tracked if p} - set(previous_audit.get('newPeople',[]))
organizations={}
for path in (BASE/'Partidos').glob('*/ficha.json'):
    m=read(path)
    for n in [m.get('name'),m.get('fullName'),*m.get('aliases',[])]:
        if n:organizations.setdefault(norm(n),m['id'])
profiles=read(CACHE/'profiles.json',[])
profile_by_key={parse_qs(urlparse(p['url']).query)['p_codi'][0]:p for p in profiles if 'error' not in p}
mapping={}; photo_jobs={}; ambiguous=[]; new=[id for id in people if id not in baseline]
correspondences={norm(item['name']):item['person'] for item in read(BASE/'Gobiernos/Autonomías/Cataluña/identidades.json',[])}
def identity(name,source,profile=None):
    matches=[correspondences[norm(name)]] if norm(name) in correspondences else index[norm(name)]
    if len(matches)>1:
        birth=next((v for k,v in (profile or {}).get('sections',{}).items() if k.startswith('Naixement')), '')
        year=re.search(r'\b(19\d{2}|20\d{2})\b',birth)
        if year:
            same=[]
            for candidate in matches:
                personal=read(people[candidate]['folder']/'datos-personales.json',{})
                known=personal.get('birthYear') or str(personal.get('birthDate') or people[candidate]['meta'].get('birthDate') or '')[:4]
                if str(known)==year[1]:same.append(candidate)
            if len(same)==1:matches=same
        if len(matches)>1:raise ValueError(f'Identidad ambigua: {name} {matches}')
    if matches:id=matches[0]
    else:
        id='catalunya-'+slug(name);folder=BASE/'Políticos'/name
        if folder.exists():raise ValueError(f'Carpeta sin correspondencia: {name}')
        meta={'id':id,'name':name,'fullName':name,'initials':''.join(w[0] for w in name.split() if len(w)>2)[:2].upper(),'organization':None,'relation':'Participación institucional documentada','role':'Representante de las instituciones de Cataluña','summary':'Trayectoria institucional documentada en las fuentes del Parlament y la Generalitat.','offices':[],'affiliationStatus':'pending','reviewedAt':CHECKED}
        people[id]={'meta':meta,'folder':folder};index[norm(name)].append(id);new.append(id);write(folder/'ficha.json',meta)
    entry=people[id];folder=entry['folder'];meta=entry['meta']
    append(folder/'fuentes.json',[ref(source)])
    if profile:
        fili=profile.get('sections',{}).get('Filiació','')
        party=re.search(r'Partit Polític:\s*(.*?)(?:Grup parlamentari:|$)',fili)
        if party and party[1].strip():
            pname=party[1].strip().rstrip('.');org=organizations.get(norm(pname))
            period='Última ficha institucional de esta persona consultada el '+CHECKED
            append(folder/'afiliaciones.json',[{'organization':org,'name':pname,'period':period,'kind':'membership','source':ref(source),'note':'La adscripción procede del campo Partit Polític de la ficha individual. No se deduce del grupo parlamentario.'}])
            if id not in baseline:
                meta.update(organization=org,affiliationStatus='documented',relation='Afiliación publicada por el Parlament');write(folder/'ficha.json',meta)
        # Conservar precisión: un año institucional nunca sustituye una fecha previa.
        birth=next((v for k,v in profile.get('sections',{}).items() if k.startswith('Naixement')), '')
        year=re.search(r'\b(?:el|l’any|l\'any)\s+(19\d{2}|20\d{2})\b',birth)
        personal=read(folder/'datos-personales.json',{})
        if year and not any(personal.get(k) or meta.get(k) for k in ['birthDate','birthYear']):
            personal.update(birthYear=int(year[1]),birthNote='La ficha del Parlament publica el año, sin fecha completa.',personalSources=[ref(source)]);write(folder/'datos-personales.json',personal)
        education=next((v for k,v in profile.get('sections',{}).items() if k.startswith('Formació')), '')
        if education and not read(folder/'formacion.json',[]):
            first=re.split(r'(?<=\.)\s+',education.strip())[0]
            if len(first.split())<=25:write(folder/'formacion.json',[first]);append(folder/'fuentes-formacion.json',[ref(source)])
        image=profile.get('image')
        if image and '/apl/gimg/' in image and not read(folder/'retrato.json'):photo_jobs[id]={'url':image,'source':source,'credit':'Parlament de Catalunya · fotografía institucional'}
    return id
for key,p in profile_by_key.items():mapping[key]=identity(p['name'],p['url'],p)

legs=read(CACHE/'parlament-raw.json')
personal_mandates=collections.defaultdict(list);personal_groups=collections.defaultdict(list);personal_offices=collections.defaultdict(list)
def mapped(r):
    p=profile_by_key.get(r['key'])
    id=mapping.get(r['key']) or identity(r['name'],r['url'])
    return {**r,'person':id,'name':people[id]['meta']['name'],'source':r['url']}
def period(start,end):return f'{start or "Fecha no publicada"} – {end or "último registro"}'
parliament=[]
for number,raw in enumerate(legs):
    is_current=number==0
    label=raw['label'];ident='catalunya-parlament-'+('15' if is_current else str(14-number))
    records=[mapped(r) for r in raw['records']]
    board=[r for r in records if r['role'] and r['role']!='Diputats']
    if is_current:
        groups=collections.defaultdict(list)
        for r in records:
            p=profile_by_key[r['key']];f=p['sections'].get('Filiació','')
            gm=re.search(r'Grup parlamentari:\s*(.*?)(?:\s*\.\s*|Membre\.|$)',f)
            group=gm[1].strip() if gm else r.get('group') or 'Grupo no publicado'
            cm=re.search(r'Circumscripció:\s*(.*?)(?:Partit Polític:|Grup parlamentari:|$)',f)
            r.update(start=None,end=None,constituency=cm[1].strip().replace('Circumscripció electoral de ','') if cm else '',group=group)
            groups[group].append(r)
        grouped=[{'name':g,'source':raw['source'],'members':m} for g,m in groups.items()]
    else:
        grouped=[{'name':g['name'],'source':g['source'],'members':[mapped(r) for r in g['members']]} for g in raw['groups']]
    legislature={'id':ident,'label':label,'start':raw['start'],'end':raw['end'],'checkedAt':CHECKED,'source':raw['source'],'records':records,'groups':grouped,'board':board,'currentOnly':is_current,
      'note':'El registro vigente se representa en la fecha de consulta; no se retroproyecta la composición actual.' if is_current else 'Altas y bajas publicadas por la Cámara. Los cambios de Mesa y de grupo se conservan por separado. Diagrama esquemático, sin asiento físico asignado.'}
    write(BASE/'Gobiernos/Autonomías/Cataluña/Parlamento'/f'{raw["start"][:4]} {label}'/'composicion.json',legislature)
    parliament.append(legislature)
    for r in records:
        if r['role']=='Diputats' or is_current:
            personal_mandates[r['person']].append({'title':f'Diputado/a del Parlament de Catalunya · {label}','period':f'Registro nominal de {CHECKED}' if is_current else period(r.get('start'),r.get('end')),'source':ref(r['source'])})
    for r in board:
        personal_offices[r['person']].append({'title':f'{r["role"]} · Mesa del Parlament de Catalunya','period':f'Registro nominal de {CHECKED}' if is_current else period(r.get('start'),r.get('end')),'source':ref(r['source'])})
    for g in grouped:
        for r in g['members']:
            personal_groups[r['person']].append({'title':g['name'],'period':f'Registro nominal de {CHECKED}' if is_current else period(r.get('start'),r.get('end')),'source':ref(g['source'],'Parlament · adscripción parlamentaria')})

transcription=read(BASE/'Gobiernos/Autonomías/Cataluña/Gobierno/transcripcion.json');dossiers=read(CACHE/'dossiers.json')
governments=[]
for p in transcription['periods']:
    source=dossiers[p['dossier']]['url'];terms=[]
    for row in [['Presidencia de la Generalitat',p['president'],p['start'],p.get('presidentEnd') or p['end']],*p['terms']]:
        role,name,*dates=row;start=(dates[0] if dates else None) or p['start'];end=(dates[1] if len(dates)>1 else None) or p['end']
        term_source=p.get('sourceOverrides',{}).get(role) or p.get('sourceOverrides',{}).get(name) or source
        id=identity(name,term_source)
        level='president' if role in ['Presidencia de la Generalitat','Vicepresidencia en sustitución de la presidencia'] else 'vice' if any(t in role.lower() for t in ['vicepresid','conseller en cap','adjunt a la presid']) else 'minister'
        title=role if level=='president' else 'Conseller/a · '+role
        terms.append({'person':id,'name':people[id]['meta']['name'],'role':title,'level':level,'start':start,'end':end,'source':term_source,'endBasis':'cese publicado' if len(dates)>1 and dates[1] else 'siguiente composición documentada'})
        personal_offices[id].append({'title':title+' · Generalitat de Catalunya','period':period(start,end)+' (intervalo del cuadro institucional)','source':ref(term_source,'Parlament · composición histórica del Govern')})
    g={'id':'catalunya-govern-'+p['start'],'label':p['label'],'start':p['start'],'end':p['end'],'checkedAt':CHECKED,'name':p['president'],'source':source,'terms':terms,'incidents':p.get('incidents',[])}
    write(BASE/'Gobiernos/Autonomías/Cataluña/Gobierno'/f'{p["start"][:4]} {p["label"]}'/'composicion.json',g);governments.append(g)
for id in set(personal_mandates)|set(personal_groups)|set(personal_offices):
    folder=people[id]['folder']
    # Estos tres documentos se generan de los registros regionales; no acumular
    # transcripciones corregidas ni intervalos de versiones anteriores.
    for file,items in [('mandatos-catalunya.json',personal_mandates[id]),('grupos-catalunya.json',personal_groups[id]),('cargos-catalunya.json',personal_offices[id])]:
        unique=list({json.dumps(item,sort_keys=True,ensure_ascii=False):item for item in items}.values())
        if unique:write(folder/file,unique)
current_ids={r['person'] for r in parliament[0]['records']}|{r['person'] for r in governments[-1]['terms'] if not r['end']}
for id in current_ids:
    write(people[id]['folder']/'actividad.json',{'state':'active','reason':'Participación vigente documentada en el Parlament o el Govern de Catalunya.','checkedAt':CHECKED,'sources':[ref(parliament[0]['source'] if id in {r['person'] for r in parliament[0]['records']} else governments[-1]['source'])]})
def photograph(item):
    id,job=item;folder=people[id]['folder'];photo_cache=CACHE/'images';photo_cache.mkdir(exist_ok=True)
    path=photo_cache/(hashlib.sha256(job['url'].encode()).hexdigest()+'.bin')
    try:
        if not path.exists():path.write_bytes(urllib.request.urlopen(job['url'],timeout=45).read())
        with Image.open(io.BytesIO(path.read_bytes())) as image:
            image=image.convert('RGB');image.thumbnail((500,650));folder.mkdir(parents=True,exist_ok=True);image.save(folder/'retrato.webp',quality=87)
        write(folder/'retrato.json',{'file':'retrato.webp','credit':job['credit'],'source':job['source'],'original':job['url']})
        return {'id':id,'ok':True}
    except Exception as e:return {'id':id,'ok':False,'error':str(e)}
if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    print('Personas nuevas',len(new),'existentes conservadas',len(baseline),'retratos pendientes',len(photo_jobs),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        photos=[]
        for i,p in enumerate(pool.map(photograph,photo_jobs.items())):
            photos.append(p)
            if i%100==0:print('Retratos',i+1,'/',len(photo_jobs),flush=True)
    missing=[{'id':id,'name':p['meta']['name']} for id,p in people.items() if id not in baseline and not read(p['folder']/'retrato.json')]
    audit={'checkedAt':CHECKED,'baselinePeople':len(baseline),'newPeople':new,'people':len(people),'profileRecords':len(profiles),'officialProfileErrors':[p for p in profiles if 'error' in p],'parliamentLegislatures':len(parliament),'parliamentRecords':sum(len(p['records']) for p in parliament),'governmentPeriods':len(governments),'governmentTerms':sum(len(g['terms']) for g in governments),'photosAdded':sum(bool(read(people[id]['folder']/'retrato.json')) for id in new),'photoErrors':[p for p in photos if not p['ok']],'missingNewPortraits':missing,'missingPortraits':[{'id':id,'name':p['meta']['name']} for id,p in people.items() if not read(p['folder']/'retrato.json')],'identities':[{'key':key,'person':id,'source':profile_by_key[key]['url']} for key,id in mapping.items()]}
    write(BASE/'Gobiernos/revisiones/2026-10-08-catalunya/informe.json',audit);print('Finalizado',json.dumps({k:v for k,v in audit.items() if k not in ['newPeople','identities','missingNewPortraits']},ensure_ascii=False),flush=True)
