"""Incorpora Les Corts y el Consell en sus carpetas de dominio.

Identidades exactas y alias revisados; no deducir partido por grupo ni retirada
por fin de mandato. Fecha de baja oficial inclusiva convertida a fin exclusivo.
"""
import collections, concurrent.futures, datetime, hashlib, importlib.util, io, json, pathlib, re, sys, unicodedata
from urllib.parse import quote
spec=importlib.util.spec_from_file_location('cv',pathlib.Path(__file__).with_name('consultar-valencia.py'));cv=importlib.util.module_from_spec(spec);spec.loader.exec_module(cv)
from PIL import Image
BASE=pathlib.Path('.');CACHE=cv.CACHE;DEST=BASE/'Gobiernos/Autonomías/Comunitat Valenciana';CHECKED=cv.CHECKED
def read(p,default=None):return json.loads(p.read_text(encoding='utf8')) if p.exists() else default
def write(p,data):cv.write(p,data)
def norm(s):return re.sub(r'[^a-z0-9]+',' ',''.join(c for c in unicodedata.normalize('NFD',s.lower().replace('mª','maria')) if not unicodedata.combining(c))).strip()
def ref(url,label=None):return {'label':label or ('Les Corts · ficha institucional' if 'cortsvalencianes' in url else 'Consell · fuente del cargo'),'url':url,'kind':'encyclopedic' if 'wikipedia.org' in url else 'institutional'}
def append(p,rows):
    old=read(p,[]);known={json.dumps(r,sort_keys=True) for r in old}
    for r in rows:
        k=json.dumps(r,sort_keys=True)
        if k not in known:old.append(r);known.add(k)
    write(p,old)
def period(start,end):return f'{start or "Fecha no publicada"} – {((datetime.date.fromisoformat(end)-datetime.timedelta(days=1)).isoformat()) if end else "último registro"}'
def canonical(name):
    names={'Julio Millet España':'Juli Millet España','F. Javier Sanahuja Sanchis':'Francisco Javier Sanahuja Sanchis','Marian Cano García':'María Ángela Cano García','Vicente Barrera Simó':'Vicente José Barrera Simó','Gabriela Bravo Sanestanislao':'Gabriela Bravo San Estanislao','Josep María Coll Comín':'José María Coll Comín','Víctor Campos Guinot':'José Víctor Campos Guinot'}
    names.update({'Maria del Carmen Ortí Ferre':'María del Carmen Ortí Ferre','Marián Cano García':'María Ángela Cano García'})
    return names.get(name,name).replace('Mª','María').replace('OrtIz','Ortiz')
people={};index=collections.defaultdict(list)
for m in read(CACHE/'existing.json',[]):
    folder=pathlib.Path(m.pop('_folder'));m.pop('_personal',None);people[m['id']]={'meta':m,'folder':folder}
    for n in [m.get('name'),m.get('fullName'),*m.get('knownAs',[])]:
        if n and m['id'] not in index[norm(n)]:index[norm(n)].append(m['id'])
baseline=set(people);new=[];mapping={};photos={};conflicts=[];aliases={norm(a['name']):a['person'] for a in read(DEST/'identidades.json',[])}
def identity(name,source,profile=None):
    name=canonical(name);matches=[aliases[norm(name)]] if norm(name) in aliases else index[norm(name)]
    if len(matches)>1:
        birth=(profile or {}).get('birthDate')
        same=[id for id in matches if birth and (read(people[id]['folder']/'datos-personales.json',{}).get('birthDate') or people[id]['meta'].get('birthDate'))==birth]
        if len(same)==1:matches=same
        else:raise ValueError('Identidad ambigua: '+name+': '+str(matches))
    if matches:id=matches[0]
    else:
        id='valencia-'+norm(name).replace(' ','-');folder=BASE/'Políticos'/name
        if folder.exists():
            meta=read(folder/'ficha.json');id=meta['id']
        else:
            meta={'id':id,'name':name,'fullName':name,'initials':''.join(w[0] for w in name.split() if len(w)>2)[:2].upper(),'organization':None,'relation':'Participación institucional documentada','role':'Representante de las instituciones valencianas','summary':'Trayectoria institucional documentada en Les Corts o en el Consell de la Generalitat Valenciana.','offices':[],'affiliationStatus':'pending','reviewedAt':CHECKED}
            write(folder/'ficha.json',meta)
        people[id]={'meta':meta,'folder':folder};index[norm(name)].append(id)
        if id not in baseline:new.append(id)
    folder=people[id]['folder'];append(folder/'fuentes.json',[ref(source)])
    if profile:
        write(folder/'registro-corts-valencianes.json',{'key':profile['key'],'nameInSource':profile['name'],'source':source,'checkedAt':CHECKED})
        personal=read(folder/'datos-personales.json',{});birth=profile.get('birthDate');known=personal.get('birthDate') or people[id]['meta'].get('birthDate')
        if birth and known and birth!=known:conflicts.append({'person':id,'field':'birthDate','existing':known,'corts':birth,'source':source})
        elif birth and not known:personal.update(birthDate=birth);personal.pop('birthYear',None);personal.pop('birthNote',None)
        if profile.get('birthPlace') and re.search(r'\w',profile['birthPlace']) and not personal.get('birthPlace'):personal['birthPlace']=profile['birthPlace'].replace('\\',' / ')
        if personal:
            personal['personalSources']=list({x['url']:x for x in [*personal.get('personalSources',[]),ref(source)]}.values());write(folder/'datos-personales.json',personal)
        if profile.get('education'):append(folder/'formacion.json',profile['education']);append(folder/'fuentes-formacion.json',[ref(source)])
        if profile.get('image') and not read(folder/'retrato.json'):photos[id]={'url':profile['image'],'source':source,'credit':'Les Corts Valencianes · retrato institucional'}
        # Una mención explícita de militancia o dirección partidaria, nunca la
        # mera adscripción al grupo, permite documentar la vinculación personal.
        text=profile.get('politicalText','')
        affiliations=[('pp',r'(?:militant|afiliad|membre|miembro|president|secretar|comit[ée]|executiv|ejecutiv)[^.;]{0,70}\b(?:PP|PPCV|Partido Popular|Partit Popular)\b'),('psoe',r'(?:militant|afiliad|membre|miembro|president|secretar|comit[ée]|executiv|ejecutiv)[^.;]{0,70}\b(?:PSOE|PSPV|PSPV-PSOE)\b')]
        meta=people[id]['meta']
        if not meta.get('organization'):
            found=[org for org,pattern in affiliations if re.search(pattern,text,re.I)]
            if len(found)==1:
                meta.update(organization=found[0],affiliationStatus='documented',relation='Vinculación partidaria expresamente publicada en la biografía institucional')
                write(folder/'ficha.json',meta)
    return id
profiles=read(CACHE/'profiles.json',[])
for p in profiles:mapping[p['key']]=identity(p['name'],p['source'],p)
def mapped(name,source):
    id=identity(name,source)
    return {'person':id,'name':people[id]['meta']['name'],'source':source,'constituency':'Comunitat Valenciana'}
def exclusive(date):return (datetime.date.fromisoformat(date)+datetime.timedelta(days=1)).isoformat() if date else None
mandates=collections.defaultdict(list);groups_person=collections.defaultdict(list);offices=collections.defaultdict(list);committees=collections.defaultdict(list);parliaments=[];date_issues=[]
starts=['1983-06-07','1987-07-02','1991-06-18','1995-06-20','1999-07-09','2003-06-12','2007-06-14','2011-06-09','2015-06-11','2019-05-16','2023-06-26']
boundaries=read(DEST/'fuentes/limites-legislaturas.json',[])
historical=read(DEST/'fuentes/mesa-historica.json',{});current=read(CACHE/'current-members.json',[])
for leg,rows in enumerate(read(CACHE/'lists.json',[]),1):
    source=rows[0]['listSource'];start=starts[leg-1];boundary=next((b for b in boundaries if b['legislature']==leg),None);end=boundary['end'] if boundary else (starts[leg] if leg<11 else None);label='Legislatura '+cv.ROMANS[leg-1];rs=[];grouped=collections.defaultdict(list)
    for r in rows:
        id=mapping[r['key']];item={'person':id,'name':people[id]['meta']['name'],'source':r['source'],'constituency':r['constituency'],'role':'Diputado/a de Les Corts','start':r['start'],'end':exclusive(r['endInclusive'])}
        append(people[id]['folder']/'fuentes.json',[ref(r['source'])])
        if item['start'] and (item['start']<start or (end and item['start']>=end)) or item['end'] and item['start'] and item['end']<=item['start']:date_issues.append({'legislature':leg,'person':id,'start':item['start'],'end':item['end'],'source':source})
        rs.append(item);grouped[r['group']].append(item)
        mandates[id].append({'title':'Diputado/a de Les Corts Valencianes · '+label+' · '+r['constituency'],'period':period(item['start'],item['end']),'source':ref(r['source'])})
        groups_person[id].append({'title':r['group']+' · '+label,'period':period(item['start'],item['end']),'source':ref(source,'Les Corts · grupo parlamentario y fechas de alta y baja')})
    archive=[]
    for name,role in historical['legislatures'][leg-1]['members']:
        item={**mapped(name,historical['source']),'role':role+' de Les Corts','start':None,'end':None,'period':label+' · cargo documentado en la publicación institucional de 2024'};archive.append(item)
        offices[item['person']].append({'title':item['role'],'period':item['period'],'source':ref(item['source'],'Les Corts · Mesa histórica')})
    board=[]
    if leg==11:
        # La página de la Mesa ignora la selección histórica: estos cinco cargos
        # solo se atribuyen a la fecha de consulta, no al comienzo de XI.
        for row in read(CACHE/'mesas.json',[])[-1]:
            id=mapping[row['key']];item={'person':id,'name':people[id]['meta']['name'],'source':row['listSource'],'constituency':next(r['constituency'] for r in current if r['key']==row['key']),'role':row['role'].capitalize()+' de Les Corts','start':CHECKED,'end':None,'observedAt':CHECKED,'period':'Composición publicada · '+CHECKED};board.append(item)
            offices[id].append({'title':item['role'],'period':item['period'],'source':ref(item['source'],'Les Corts · Mesa vigente')})
    capacity=89 if leg<=6 else 99
    data={'id':'valencia-corts-'+str(leg),'label':label,'start':start,'end':end,'checkedAt':CHECKED,'source':source,'capacity':capacity,'currentOnly':False,'note':'Altas, bajas y grupos publicados por Les Corts. Las bajas se publican como último día de pertenencia. Las vacantes y las fechas discrepantes del registro se conservan; no se asignan asientos físicos.','records':rs,'board':board,'archiveBoard':archive,'groups':[{'name':n,'source':source,'members':m} for n,m in grouped.items()]}
    if boundary:
        data['endSource']=boundary['source'];data['note']+=' El Pleno se representa hasta el límite de la legislatura; los mandatos posteriores de la Diputación Permanente se conservan en el archivo personal.'
    if leg in [5,6,8,11]:data['note']+=' El registro individual incluye altas anteriores o posteriores a la sesión constitutiva; se conservan sus fechas originales, sin atribuirles una sesión parlamentaria.'
    dates={start,*(r['start'] for r in rs if r['start']),*(r['end'] for r in rs if r['end'])}
    over=[d for d in dates if d>=start and (not end or d<end) and len({r['person'] for r in rs if r['start'] and r['start']<=d and (not r['end'] or d<r['end'])})>capacity]
    data['nominalOnly']=bool(over)
    if over:data['note']='Los intervalos del registro oficial se solapan por encima del número de escaños de esta legislatura. Se ofrece su archivo nominal con las fechas originales; no se eligen personas arbitrariamente para reconstruir un Pleno diario.'
    write(DEST/'Parlamento'/f'{start[:4]} {label}'/'composicion.json',data);parliaments.append(data)
government_data=read(DEST/'Gobierno/transcripcion.json',[]);governments=[]
for g in government_data:
    data={**g,'checkedAt':CHECKED}
    for field in ['terms','archiveTerms']:
        data[field]=[{**r,**mapped(r['name'],r['source'])} for r in g.get(field,[])]
        for r in data[field]:
            offices[r['person']].append({'title':r['role']+' · Generalitat Valenciana','period':r.get('period') or period(r['start'],r['end']),'source':ref(r['source'])})
            if r.get('endBasis'):append(people[r['person']]['folder']/'fuentes.json',[ref(r['endBasis'],'DOGV · efectos del cese')])
    write(DEST/'Gobierno'/f'{g["start"][:4]} {g["label"]}'/'composicion.json',data);governments.append(data)
for p in profiles:
    id=mapping[p['key']]
    committees[id]=[{'title':'Participación en '+t,'period':'Ficha institucional · '+cv.ROMANS[cv.ROMANS.index(p['legislature'])]+' · consulta '+CHECKED,'source':ref(p['source'])} for t in p.get('committees',[])]
involved=set(mapping.values())|set(offices);current_ids={mapping[r['key']] for r in current}|{r['person'] for r in governments[-1]['terms'] if r['start']<=CHECKED and (not r['end'] or CHECKED<r['end'])}
for id in involved:
    folder=people[id]['folder']
    for file,rows in [('mandatos-valencia.json',mandates[id]),('grupos-valencia.json',groups_person[id]),('cargos-valencia.json',offices[id]),('comisiones-valencia.json',committees[id])]:
        if rows:
            write(folder/file,list({json.dumps(r,sort_keys=True):r for r in rows}.values()))
            append(folder/'fuentes.json',[r['source'] for r in rows])
    if id in current_ids:
        write(folder/'actividad.json',{'state':'active','reason':'Participación vigente documentada en Les Corts o en el Consell de la Generalitat Valenciana.','checkedAt':CHECKED,'sources':[ref('https://www.cortsvalencianes.es/es/composicion/diputados?legislature=XI') if id in {mapping[r['key']] for r in current} else ref(governments[-1]['source'])]})
        roles=[r['role'] for r in governments[-1]['terms'] if r['person']==id and r['start']<=CHECKED and (not r['end'] or CHECKED<r['end'])]
        if not roles:roles=[r['role'] for r in parliaments[-1]['board'] if r['person']==id]
        meta=read(folder/'ficha.json');meta.update(role=' · '.join(roles) or 'Diputado/a en Les Corts Valencianes',reviewedAt=CHECKED)
        write(folder/'ficha.json',meta)
    elif id in new and not read(folder/'actividad.json'):write(folder/'actividad.json',{'state':'unknown','reason':'Trayectoria histórica documentada; no se ha confirmado si continúa en actividad política.','checkedAt':CHECKED,'sources':read(folder/'fuentes.json',[])[:1]})
# El portal del Consell proporciona el retrato oficial de cada titular vigente.
for p in read(CACHE/'government-photos.json',[]):
    id=identity(p['name'],p['source'])
    if not read(people[id]['folder']/'retrato.json'):photos[id]=p
def photo_job(job):
    id,p=job;folder=people[id]['folder']
    try:
        raw=cv.fetch(quote(p['url'],safe=':/%?=&'),'.img');im=Image.open(io.BytesIO(raw));im.load()
        if min(im.size)<65 or len(im.convert('RGB').getcolors(1000000) or [])<12:raise ValueError('Imagen genérica o insuficiente')
        im.thumbnail((500,650));buffer=io.BytesIO();im.convert('RGB').save(buffer,format='JPEG',quality=88)
        return {'person':id,'ok':True,'hash':hashlib.sha256(raw).hexdigest(),'bytes':buffer.getvalue(),'meta':{'file':'retrato-valencia.jpg','credit':p['credit'],'source':p['source'],'original':p['url'],'license':'Fotografía institucional; consultar las condiciones de reutilización de la fuente.','licenseUrl':p['source'],'date':'Etapa institucional publicada por la fuente; fecha fotográfica no indicada'}}
    except Exception as e:return {'person':id,'url':p['url'],'error':str(e)}
photo_results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for i,r in enumerate(pool.map(photo_job,photos.items()),1):
        photo_results.append(r)
        if i%50==0:print('Retratos consultados',i,'/',len(photos),flush=True)
duplicates=collections.Counter(r['hash'] for r in photo_results if r.get('ok'));errors=[]
for r in photo_results:
    if not r.get('ok'):errors.append(r);continue
    if duplicates[r['hash']]>1:errors.append({'person':r['person'],'error':'Recurso idéntico para varias identidades: se excluye hasta contraste visual.','hash':r['hash']});continue
    folder=people[r['person']]['folder'];(folder/'retrato-valencia.jpg').write_bytes(r['bytes']);write(folder/'retrato.json',r['meta'])
audit={'checkedAt':CHECKED,'baselinePeople':len(baseline),'newPeople':sorted(set(new)),'cortsProfiles':len(profiles),'profileErrors':read(CACHE/'errors.json',[]),'identityMapping':mapping,'birthConflicts':conflicts,'governments':len(governments),'legislatures':[{'id':p['id'],'mandates':len(p['records']),'nominalOnly':p['nominalOnly'],'capacity':p['capacity']} for p in parliaments],'dateIssues':date_issues,'portraitsAdded':sum((p['folder']/'retrato-valencia.jpg').exists() for p in people.values()),'portraitErrors':errors,'missingPortraits':[{'id':id,'name':people[id]['meta']['name']} for id in sorted(involved) if not read(people[id]['folder']/'retrato.json')],'allMissingPortraits':sorted(id for id,p in people.items() if not read(p['folder']/'retrato.json'))}
write(BASE/'Gobiernos/revisiones/2026-10-09-valencia/informe.json',audit)
print('Valencia',len(governments),'etapas',len(profiles),'fichas oficiales',len(set(new)),'personas nuevas',audit['portraitsAdded'],'retratos añadidos',len(errors),'incidencias de retrato',flush=True)
