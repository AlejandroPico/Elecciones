"""Migra Madrid a sus carpetas de dominio. Ejecutar tras consultar-madrid.py.

No deduce militancia del grupo, jubilación por edad, ni el órgano de los cargos
del CSV de ocupaciones. La identidad se contrasta con las fichas existentes.
"""
import collections, concurrent.futures, csv, datetime, hashlib, io, json, pathlib, re, subprocess, sys, unicodedata
sys.path.insert(0,'test-results/libraries')
from PIL import Image
BASE=pathlib.Path('.'); CACHE=BASE/'test-results/madrid'; DEST=BASE/'Gobiernos/Autonomías/Madrid'; CHECKED='2026-10-09'
CSV_URL='https://ctyp.asambleamadrid.es/static/doc/opendata/SGP_ADMIN.OPENDATA_OCUPACIONES_ASAMBLEA.csv'
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII']

def read(p,default=None):return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def write(p,data):
    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if p.exists() and p.read_text(encoding='utf-8')==text:return
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
def norm(s):return re.sub(r'[^a-z0-9]+',' ',''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))).strip()
def ref(url,label='Asamblea de Madrid · archivo oficial',kind='institutional'):return {'label':label,'url':url,'kind':kind}
def append(p,items):
    old=read(p,[]);keys={json.dumps(x,sort_keys=True) for x in old}
    for item in items:
        k=json.dumps(item,sort_keys=True)
        if k not in keys:old.append(item);keys.add(k)
    write(p,old)
people={};index=collections.defaultdict(list)
for p in (BASE/'Políticos').glob('*/ficha.json'):
    m=read(p);people[m['id']]={'meta':m,'folder':p.parent}
    for n in [m.get('name'),m.get('fullName'),*m.get('knownAs',[])]:
        if n and m['id'] not in index[norm(n)]:index[norm(n)].append(m['id'])
audit_path=BASE/'Gobiernos/revisiones/2026-10-09-madrid/informe.json'
old_audit=read(audit_path,{})
tracked=subprocess.check_output(['git','ls-files','-z','Políticos/*/ficha.json']).decode('utf-8').split('\0')
baseline={read(BASE/p)['id'] for p in tracked if p}-set(old_audit.get('newPeople',[]))
aliases={norm(x['name']):x['person'] for x in read(DEST/'identidades.json',[])}
new=[p for p in people if p not in baseline];photos={};mapping={};conflicts=[]

def identity(name,url,profile=None):
    matches=[aliases[norm(name)]] if norm(name) in aliases else index[norm(name)]
    if len(matches)>1:
        birth=(profile or {}).get('birthDate')
        same=[id for id in matches if read(people[id]['folder']/'datos-personales.json',{}).get('birthDate')==birth]
        if birth and len(same)==1:matches=same
        else:raise ValueError(f'Identidad ambigua: {name}: {matches}')
    if matches:id=matches[0]
    else:
        id='madrid-'+norm(name).replace(' ','-');folder=BASE/'Políticos'/name
        if folder.exists():raise ValueError('Carpeta existente sin correspondencia: '+name)
        meta={'id':id,'name':name,'fullName':name,'initials':''.join(w[0] for w in name.split() if len(w)>2)[:2].upper(),'organization':None,'relation':'Participación institucional documentada','role':'Representante de las instituciones de Madrid','summary':'Trayectoria institucional documentada en la Asamblea y el Gobierno de la Comunidad de Madrid.','offices':[],'affiliationStatus':'pending','reviewedAt':CHECKED}
        people[id]={'meta':meta,'folder':folder};index[norm(name)].append(id);new.append(id);write(folder/'ficha.json',meta)
    folder=people[id]['folder'];append(folder/'fuentes.json',[ref(url)])
    if profile:
        write(folder/'registro-asamblea-madrid.json',{'key':profile['key'],'nameInSource':name,'source':url,'checkedAt':CHECKED})
        personal=read(folder/'datos-personales.json',{});birth=profile.get('birthDate');known=personal.get('birthDate') or people[id]['meta'].get('birthDate')
        if birth and known and birth!=known:conflicts.append({'person':id,'field':'birthDate','existing':known,'assembly':birth,'source':url})
        elif birth and not known:
            personal.update(birthDate=birth);personal.pop('birthYear',None);personal.pop('birthNote',None)
            personal['personalSources']=[*personal.get('personalSources',[]),ref(url)];write(folder/'datos-personales.json',personal)
        edu=[x['degree']+(f" · {x['center']}" if x['center'] else '') for x in profile.get('education',[])]
        if edu:
            append(folder/'formacion.json',edu);append(folder/'fuentes-formacion.json',[ref(url)])
        if profile.get('image') and not profile['image'].endswith('/default.jpg') and not read(folder/'retrato.json'):
            photos[id]={'url':profile['image'],'source':url,'credit':'Asamblea de Madrid · retrato institucional'}
    return id

profiles=read(CACHE/'profiles.json',[])
by_name={norm(p['name']):p for p in profiles}
for p in profiles:mapping[p['key']]=identity(p['name'],p['source'],p)

def mapped(name,source):
    p=by_name.get(norm(name));id=mapping[p['key']] if p else identity(name,source)
    append(people[id]['folder']/'fuentes.json',[ref(source,'Cargo en Madrid · fuente del registro','encyclopedic' if 'wikipedia.org' in source else 'institutional')])
    return {'person':id,'name':people[id]['meta']['name'],'source':source,'constituency':'Madrid'}
def from_csv(text):
    return datetime.datetime.strptime(text.split(' ')[0],'%d/%m/%Y').date().isoformat() if text and text!='-' else None
def period(start,end):return f'{start or "Fecha no publicada"} – {end or "último registro"}'
mandates=collections.defaultdict(list);groups_by_person=collections.defaultdict(list);offices=collections.defaultdict(list);committees=collections.defaultdict(list)
records=collections.defaultdict(list);groups=collections.defaultdict(list);boards=collections.defaultdict(list)
for p in profiles:
    for l in p['legs']:
        leg=ROMANS.index(l['label'].split(' ')[-1])+1
        for r in l['roles']:
            item={**mapped(p['name'],p['source']),**r,'source':p['source']}
            if r['body']=='Asamblea de Madrid' and r['role'] in ['Diputado','Diputada']:records[leg].append(item)
            elif r['body'] in ['Asamblea de Madrid','Mesa de la Asamblea'] and re.match(r'^(President[ae]|Vicepresident[ae]|Secretari[oa])\b',r['role']):boards[leg].append(item)
            if r['body'].startswith('Comisión'):
                committees[item['person']].append({'title':r['role']+' · '+r['body'],'period':period(r['start'],r['end']),'source':ref(p['source'])})
            elif r['role'] not in ['Diputado','Diputada'] and r['body'] not in ['Gobierno']:
                offices[item['person']].append({'title':r['role']+' · '+r['body'],'period':period(r['start'],r['end']),'source':ref(p['source'])})
        for g in l['groups']:groups[leg].append({**mapped(p['name'],p['source']),**g})

# El CSV desplaza II a I, VI a V y el inicio de VII a VI. Se reasigna
# exclusivamente cuando el intervalo pertenece inequívocamente a otra etapa.
corrections=[]
for row in csv.DictReader(open(CACHE/'cache/ocupaciones.csv',encoding='utf-8-sig',newline='')):
    if row['CARGO'] not in ['Diputado','Diputada']:continue
    start,end=from_csv(row['FECHA_INICIO']),from_csv(row['FECHA_FIN']);leg=int(row['LEGISLATURA']);original=leg
    if leg==1 and start>='1987-01-01':leg=2
    elif leg==5 and start>='2003-01-01':leg=6
    elif leg==6 and start>='2003-10-01':leg=7
    if original!=leg:corrections.append({'name':row['NOMBRE'],'originalLegislature':original,'legislature':leg,'start':start,'end':end,'source':CSV_URL})
    item={**mapped(row['NOMBRE'],CSV_URL),'role':row['CARGO'],'start':start,'end':end,'body':'Asamblea de Madrid'}
    if not any(r['person']==item['person'] and r['start']==start for r in records[leg]):records[leg].append(item)
    # Adscripción agregada del registro de mandato: usarla solo si no hay una
    # adscripción individual fechada para esa persona en esta legislatura.
    if not any(g['person']==item['person'] for g in groups[leg]):groups[leg].append({**item,'name':row['GRUPO_PARLAMENTARIO'].replace('  (leg. X y ant.)','').replace(' (leg. X y ant.)','').strip().rstrip('.')})

starts=['1983-06-08','1987-07-02','1991-06-20','1995-06-22','1999-06-30','2003-06-10','2003-11-12','2007-06-12','2011-06-07','2015-06-09','2019-06-11','2021-06-08','2023-06-13']
capacities=[94,96,101,103,102,111,111,120,129,129,132,136,135]
dissolutions={r["legislature"]:r for r in read(DEST/"fuentes/disoluciones-anticipadas.json",[])}
parliaments=[]
for leg in range(1,14):
    label='Legislatura '+ROMANS[leg-1];end=dissolutions.get(leg,{}).get('end') or (starts[leg] if leg<13 else None)
    source=f'https://www.asambleamadrid.es/la-asamblea/historia/legislatura-{ROMANS[leg-1].lower()}' if leg<13 else 'https://www.asambleamadrid.es/composicion/diputados'
    # No inventar alta anterior a la publicada ni atribuirla a una Mesa de Edad.
    def unique(rows):return list({(r['person'],r.get('role'),r.get('name') if not r.get('role') else '',r['start'],r['end']):r for r in rows}.values())
    rs=unique(records[leg]);bs=unique(boards[leg]);gs=unique(groups[leg]);grouped=collections.defaultdict(list)
    for g in gs:grouped[g['name']].append({**g,'name':people[g['person']]['meta']['name']})
    note='Altas, bajas y adscripciones documentadas por la Asamblea. Los registros antiguos tienen lagunas y fechas discrepantes, detalladas en el informe de fuentes. Después de una disolución, el registro de mandatos no equivale a un Pleno en funcionamiento.'
    data={'id':f'madrid-asamblea-{leg}','label':label,'start':starts[leg-1],'end':end,'checkedAt':CHECKED,'source':source,'capacity':capacities[leg-1],'currentOnly':False,'note':note,'records':rs,'board':bs,'groups':[{'name':name,'source':source,'members':rows} for name,rows in grouped.items()]}
    if leg in dissolutions:data['endSource']=dissolutions[leg]['source']
    dates={data['start'],*(r['start'] for r in rs if r['start']),*(r['end'] for r in rs if r['end'])}
    too_many=[d for d in dates if d>=data['start'] and (not end or d<end) and len({r['person'] for r in rs if r['start'] and r['start']<=d and (not r['end'] or d<r['end'])})>data['capacity']]
    data['nominalOnly']=bool(too_many)
    if too_many:data['note']='El registro oficial contiene intervalos superpuestos que superan el número de escaños de esta legislatura. Se ofrece el archivo nominal con sus fuentes; no se reconstruye un hemiciclo diario ni se seleccionan personas arbitrariamente para hacerlo cuadrar.'
    write(DEST/'Parlamento'/f'{starts[leg-1][:4]} {label}'/'composicion.json',data);parliaments.append(data)
    for r in rs:mandates[r['person']].append({'title':('Registro histórico de la Asamblea de Madrid · ' if too_many and r['source']==CSV_URL else 'Diputado/a de la Asamblea de Madrid · ')+label,'period':period(r['start'],r['end']),'source':ref(r['source'])})
    for g in gs:groups_by_person[g['person']].append({'title':g['name']+' · '+label,'period':period(g['start'],g['end']),'source':ref(g['source'])})

# Las composiciones del Ejecutivo se generan a partir de una transcripción
# contrastada; los cargos históricos sin intervalo diario se presentan aparte.
governments=read(DEST/'Gobierno/transcripcion.json',[])
for gov in governments:
    data={**gov,'checkedAt':CHECKED}
    for field in ['terms','archiveTerms']:
        data[field]=[{**r,**mapped(r['name'],r.get('source') or gov['source'])} for r in gov.get(field,[])]
        for r in data[field]:offices[r['person']].append({'title':r['role']+' · Comunidad de Madrid','period':r.get('period') or period(r.get('start'),r.get('end')),'source':ref(r['source'],'Gobierno de Madrid · cargo documentado','encyclopedic' if 'wikipedia.org' in r['source'] else 'institutional')})
    folder_label=gov['label'].replace(' / ', ' y ')
    write(DEST/'Gobierno'/f'{gov["start"][:4]} {folder_label}'/'composicion.json',data)

for p in read(CACHE/'government-photos.json',[]):
    id=identity(p['name'],p['source'])
    if not read(people[id]['folder']/'retrato.json'):photos[id]=p

for cv in read(DEST/'fuentes/curriculos.json',[]):
    id=identity(cv['name'],cv['source']);folder=people[id]['folder'];source=ref(cv['source'],'Comunidad de Madrid · currículo institucional')
    append(folder/'formacion.json',cv['education']);append(folder/'fuentes-formacion.json',[source])
    append(folder/'trayectoria.json',[{**t,'source':source} for t in cv['timeline']])
    meta=people[id]['meta'];meta['summary']=cv['summary'];write(folder/'ficha.json',meta)
    personal=read(folder/'datos-personales.json',{})
    if cv.get('birthYear') and not personal.get('birthDate') and not personal.get('birthYear'):
        personal.update(birthYear=cv['birthYear'],birthNote='El currículo institucional publica el año; no se atribuye una fecha de nacimiento completa.',personalSources=[source]);write(folder/'datos-personales.json',personal)

def unique_terms(rows):return list({json.dumps(r,sort_keys=True):r for r in rows}.values())
involved=set(mapping.values())|set(mandates)|set(offices)
for id in involved:
    folder=people[id]['folder']
    for file,rows in [('mandatos-madrid.json',mandates[id]),('grupos-madrid.json',groups_by_person[id]),('cargos-madrid.json',offices[id]),('comisiones-madrid.json',committees[id])]:
        if rows:write(folder/file,unique_terms(rows))
    current=[r for r in parliaments[-1]['records'] if r['person']==id and r['start']<=CHECKED and (not r['end'] or CHECKED<r['end'])]
    current.extend(r for g in governments for r in g.get('terms',[]) if norm(r['name']) in index and id in index[norm(r['name'])] and r.get('start') and r['start']<=CHECKED and (not r.get('end') or CHECKED<r['end']))
    if current:write(folder/'actividad.json',{'state':'active','reason':'Participación vigente documentada en las instituciones de la Comunidad de Madrid.','checkedAt':CHECKED,'sources':[ref(current[0]['source'])]})
    elif id in new and not read(folder/'actividad.json'):write(folder/'actividad.json',{'state':'unknown','reason':'Trayectoria histórica documentada; no se ha confirmado si continúa en actividad política.','checkedAt':CHECKED,'sources':read(folder/'fuentes.json',[])[:1]})

# Retratos oficiales, nunca la silueta genérica. Se conservan los retratos previos.
def photo_job(job):
    id,p=job;folder=people[id]['folder']
    try:
        result=subprocess.run(['curl.exe','--fail','--silent','--show-error','--location','--max-time','40',p['url']],capture_output=True,check=True)
        im=Image.open(io.BytesIO(result.stdout));im.load()
        if min(im.size)<80 or len(im.convert('RGB').getcolors(1000000) or [])<12:raise ValueError('Imagen genérica o insuficiente')
        im.thumbnail((500,650));im.convert('RGB').save(folder/'retrato-madrid.jpg',quality=88)
        if hashlib.sha256((folder/'retrato-madrid.jpg').read_bytes()).hexdigest() in read(DEST/'fuentes/siluetas.json',[]):
            (folder/'retrato-madrid.jpg').unlink()
            raise ValueError('Silueta institucional genérica: no corresponde a un retrato personal')
        write(folder/'retrato.json',{'file':'retrato-madrid.jpg','credit':p['credit'],'source':p['source'],'original':p['url'],'license':'Fotografía institucional; consultar las condiciones de reutilización de la fuente.','licenseUrl':p['source'],'date':'Etapa institucional publicada por la fuente; fecha fotográfica no indicada'})
        return {'person':id,'ok':True}
    except Exception as e:return {'person':id,'url':p['url'],'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:photo_results=list(pool.map(photo_job,photos.items()))
write(DEST/'fuentes/correcciones-legislaturas.json',corrections)
all_missing=sorted(id for id,p in people.items() if not read(p['folder']/'retrato.json'))
audit={'checkedAt':CHECKED,'baselinePeople':len(baseline),'newPeople':sorted(new),'assemblyProfiles':len(profiles),'profileErrors':read(CACHE/'errors.json',[]),'identityMapping':mapping,'birthConflicts':conflicts,'portraitsAdded':sum(r.get('ok',False) for r in photo_results),'portraitErrors':[r for r in photo_results if 'error' in r],'missingPortraits':[{'id':id,'name':people[id]['meta']['name']} for id in sorted(involved) if not read(people[id]['folder']/'retrato.json')], 'legislatures':[{'id':p['id'],'mandates':len(p['records']),'boardTerms':len(p['board'])} for p in parliaments],'csvLegislatureCorrections':len(corrections),'governments':len(governments)}
audit['allMissingPortraits']=all_missing
audit['portraitsAdded']=sum((p['folder']/'retrato-madrid.jpg').exists() for p in people.values())
write(audit_path,audit);print({k:v for k,v in audit.items() if k in ['assemblyProfiles','portraitsAdded','csvLegislatureCorrections','governments']},'personas nuevas',len(new),'conflictos de nacimiento',len(conflicts),'retratos ausentes',len(audit['missingPortraits']),flush=True)
