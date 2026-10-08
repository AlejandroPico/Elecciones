"""Incorpora personas del Congreso y Senado desde 1977 con identidad y fuente individual.

Los planes de consulta se conservan en test-results/revision-partidos/parlamento.
No deduce militancia a partir de un grupo parlamentario ni toma las fechas de una
legislatura como fechas del mandato individual. Conserva las 300 fichas revisadas.
"""
import pathlib,json,re,sys,unicodedata,datetime,shutil,urllib.parse,collections,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[2];C=ROOT/'test-results/revision-partidos/parlamento';DATE='2026-10-08'
sys.stdout.reconfigure(encoding='utf-8')
def read(p,fallback=None):return json.loads(p.read_text(encoding='utf-8')) if p.exists() else fallback
def save(p,d):
    data=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
    if p.exists() and p.read_text(encoding='utf-8')==data:return
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data,encoding='utf-8')
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFD',s).encode('ascii','ignore').decode().lower())
def proper(s):
    return ' '.join(w.lower() if i and w.lower() in ['de','del','la','las','los','y','i','da','do'] else w.title() for i,w in enumerate(s.split()))
def dmy(s):
    m=re.search(r'(\d{2})/(\d{2})/(\d{4})',s or '')
    if not m:return None
    try:return datetime.date(int(m[3]),int(m[2]),int(m[1])).isoformat()
    except ValueError:return None
def congress_birth(paragraphs):
    months={v:i+1 for i,v in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}
    for p in paragraphs:
        if not re.match(r'Nacid[oa]\b',p):continue
        m=re.search(r'\b('+ '|'.join(months)+r') (\d{2}) \d{2}:\d{2}:\d{2} [A-Z]+ (\d{4})\b',p)
        if m:return datetime.date(int(m[3]),months[m[1]],int(m[2])).isoformat()
        if dmy(p):return dmy(p)
    return None
def ref(kind,url):return {'label':'Congreso de los Diputados · ficha individual' if kind=='congreso' else 'Senado de España · ficha individual','url':url,'kind':'institutional'}
def period(start,end):return f'{start} — {end}' if start and end else f'Alta: {start} · baja no indicada' if start else f'Hasta {end}' if end else 'Fechas individuales no publicadas'
def append_unique(old,new):
    result=list(old);known={json.dumps(x,sort_keys=True,ensure_ascii=False) for x in old}
    for item in new:
        key=json.dumps(item,sort_keys=True,ensure_ascii=False)
        if key not in known:result.append(item);known.add(key)
    return result

folders={};names=collections.defaultdict(set);dates={};identities={};conflicts=[];records=[]
for p in (ROOT/'Políticos').glob('*/ficha.json'):
    m=read(p);folders[m['id']]=p.parent
    for n in [m['fullName'],m['name'],*m.get('knownAs',[])]:names[norm(n)].add(m['id'])
    personal=read(p.parent/'datos-personales.json',{});dates[m['id']]=personal.get('birthDate')
    for i in read(p.parent/'institucional.json',[]):identities[(i['chamber'],i['key'])]=m['id']
originalIds=[r['id'] for r in read(ROOT/'Políticos/revisiones/2026-10-08/informe.json')['records']]
parties={read(p)['id']:read(p) for p in (ROOT/'Partidos').glob('*/ficha.json')};partyNames=collections.defaultdict(set)
for id,m in parties.items():
    for name in [m['name'],m['fullName'],*m.get('aliases',[])]:partyNames[norm(name)].add(id)
manual={'PP':'pp','PSOE':'psoe','PSC-PSOE':'psc','PSC(PSC-PSOE)':'psc','VOX':'vox','Vox':'vox','ERC':'erc','PNV':'pnv','EAJ-PNV':'pnv','EH Bildu':'eh-bildu','BNG':'bng','CC':'cc','CCa':'cc','PODEMOS':'podemos','IU':'iu','Cs':'cs','UPN':'upn','SUMAR':'sumar-coalicion-2023','UCD':'registro-282','PCE':'registro-49','EA':'registro-807','CiU':'registro-2425','CIU':'registro-2425','PRC':'registro-362','UPyD':'registro-3779'}
def party_id(name,code=''):
    if code in manual and manual[code] in parties:return manual[code]
    cleaned=re.sub(r'\s*\([^()]*\)\s*$','',name).strip();options=partyNames.get(norm(cleaned),set()) or partyNames.get(norm(name),set())
    return next(iter(options)) if len(options)==1 else None
mandates=collections.defaultdict(list)
for r in read(C/'congreso-mandatos.json',[]):mandates[norm(r['nombre']+' '+r['apellidos'])].append(r)
roman=['C','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV']
def source_congress(r):return 'https://www.congreso.es/es/busqueda-de-diputados?p_p_id=diputadomodule&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_diputadomodule_mostrarFicha=true&codParlamentario='+str(r['codParlamentario'])+'&idLegislatura='+roman[r['idLegislatura']]

def locate(name,birth,chamber,key):
    if (chamber,key) in identities:return identities[(chamber,key)]
    options=names.get(norm(name),set())
    if len(options)==1:
        id=next(iter(options))
        if birth and dates.get(id) and birth!=dates[id]:conflicts.append({'name':name,'id':id,'existingDate':dates[id],'institutionalDate':birth,'action':'Conservar dato anterior y registrar discrepancia para revisión individual'})
        return id
    if birth:
        tokens=set(re.findall(r'\w+',unicodedata.normalize('NFD',name).encode('ascii','ignore').decode().lower()))
        possible=[]
        for id,existing in dates.items():
            if birth!=existing:continue
            m=read(folders[id]/'ficha.json');other=set(re.findall(r'\w+',unicodedata.normalize('NFD',m['fullName']).encode('ascii','ignore').decode().lower()))
            useful=tokens-{'de','del','la','las','los','y','i'};otherUseful=other-{'de','del','la','las','los','y','i'}
            if len(tokens&other)/max(len(tokens),len(other))>=.8 or (min(len(useful),len(otherUseful))>=3 and (useful.issubset(otherUseful) or otherUseful.issubset(useful))):possible.append(id)
        if len(possible)==1:return possible[0]
    return None

def incorporate(kind,key,name,birth,meta,terms,affiliations,biography,education,personalExtra=None):
    id=locate(name,birth,kind,key);existing=bool(id)
    if not id:
        id=('congreso-' if kind=='congreso' else 'senado-')+key;folder=ROOT/'Políticos'/name
        if folder.exists():raise ValueError('Nombre duplicado sin resolución de identidad: '+name)
        folders[id]=folder;names[norm(name)].add(id);dates[id]=birth
        latest=affiliations[-1] if affiliations else None
        m={'id':id,'name':name,'fullName':name,'initials':''.join(w[0] for w in name.split()[:2]),'organization':latest.get('organization') if latest else None,'affiliationStatus':'documented' if affiliations else 'pending','relation':'Trayectoria parlamentaria documentada','role':'Miembro del Congreso' if kind=='congreso' else 'Miembro del Senado','summary':'Trayectoria documentada en el archivo histórico del Congreso de los Diputados.' if kind=='congreso' else 'Trayectoria documentada en el archivo histórico del Senado de España.','offices':[],'reviewedAt':DATE};save(folder/'ficha.json',m)
    folder=folders[id];reference=ref(kind,meta['source']);identities[(kind,key)]=id
    save(folder/'institucional.json',append_unique(read(folder/'institucional.json',[]),[{'chamber':kind,'key':key,'source':meta['source'],'checkedAt':DATE,'sourceSha256':meta.get('sha256'),'error':meta.get('error')}]))
    save(folder/'fuentes.json',append_unique(read(folder/'fuentes.json',[]),[reference]))
    if birth and not read(folder/'datos-personales.json',{}).get('birthDate'):
        personal=read(folder/'datos-personales.json',{});personal.update({'birthDate':birth,'birthYear':int(birth[:4]),'birth':datetime.date.fromisoformat(birth).strftime('%d/%m/%Y'),'personalSources':append_unique(personal.get('personalSources',[]),[reference])});personal.update(personalExtra or {});save(folder/'datos-personales.json',personal)
    if affiliations:save(folder/'afiliaciones.json',append_unique(read(folder/'afiliaciones.json',[]),affiliations))
    if personalExtra:
        personal=read(folder/'datos-personales.json',{});personal.update(personalExtra);personal['personalSources']=append_unique(personal.get('personalSources',[]),[reference]);save(folder/'datos-personales.json',personal)
    if terms:save(folder/'trayectoria.json',append_unique(read(folder/'trayectoria.json',[]),terms))
    if education and not read(folder/'formacion.json',[]):save(folder/'formacion.json',education);save(folder/'fuentes-formacion.json',[reference])
    if biography:
        items=[{'text':text,'source':reference} for text in biography]
        save(folder/'biografia-institucional.json',append_unique(read(folder/'biografia-institucional.json',[]),items))
    photo=read(C/'retratos'/(kind+'-'+key+'.json'),{})
    if photo.get('file') and not (folder/'retrato.json').exists():
        file='retrato'+photo['extension'];shutil.copyfile(ROOT/photo['file'],folder/file);save(folder/'retrato.json',{'file':file,'credit':photo['credit'],'source':photo['source'],'original':photo['original'],'context':'Retrato conservado por la cámara en la ficha del mandato consultado; no se atribuye una fecha de toma no publicada.'})
    records.append({'id':id,'chamber':kind,'key':key,'name':name,'source':meta['source'],'merged':existing,'portrait':(folder/'retrato.json').exists(),'sourceError':meta.get('error'),'portraitError':photo.get('error'),'portraitLocated':bool(meta.get('portrait'))})

for file in sorted((C/'congreso').glob('*.json')):
    d=read(file);r=d['record'];name=(r['nombre']+' '+r['apellidos']).strip();source=ref('congreso',d['source']);birth=congress_birth(d.get('biography',[]));terms=[];affiliations=[]
    rows=sorted(mandates[norm(name)],key=lambda r:(r['idLegislatura'],dmy(r.get('fchAlta')) or ''))
    for row in rows:
        start=dmy(row.get('fchAlta'));end=dmy(row.get('fchBaja'));individual=ref('congreso',source_congress(row));title=('Diputado' if row['genero']==1 else 'Diputada')+' en el Congreso por '+row['nombreCircunscripcion']+' · '+('Legislatura Constituyente' if row['idLegislatura']==0 else roman[row['idLegislatura']]+' Legislatura');terms.append({'period':period(start,end),'title':title,'source':individual})
        formation=row.get('formacion')
        if formation:affiliations.append({'organization':party_id(formation,formation),'name':formation,'period':period(start,end),'kind':'association','source':individual,'note':'Formación electoral indicada por el Congreso para esta candidatura. No acredita por sí sola militancia ni vinculación actual.'})
    bi=[p for p in d.get('biography',[]) if not re.match(r'(Nacid[oa]|Diputad[oa]|Casad[oa]|Solter[oa]|Divorciad[oa]|Viud[oa]|\d+\s+hij|\d{4}\.?$|https?://)',p,re.I)]
    education=[p for p in bi if re.search(r'licenciad|licenciatura|doctorad|graduad|diplomad|ingenier[oa]|máster|master|estudios|bachiller|técnic[oa] superior',p,re.I) and len(p)<400][:8]
    bi=[p for p in bi if p not in education and len(p)>30 and len(p)<600 and not re.search(r'\bhij[oa]s?\b|casad[oa]|divorciad[oa]|viud[oa]',p,re.I)][:6]
    incorporate('congreso',file.stem,name,birth,d,terms,affiliations,bi,education)
    if len(records)%500==0:print('Fichas incorporadas',len(records),flush=True)

for file in sorted((C/'senado').glob('*.json')):
    d=read(file);personal=d.get('personal',{});name=proper((personal.get('nombre','')+' '+personal.get('apellidos','')).strip()) if personal.get('nombre') else proper(d.get('institutionalName',''))
    if not name:
        parts=d['name'].split(',',1);name=proper(parts[1].strip()+' '+parts[0].strip())
    birth=dmy(personal.get('fechaNacimiento'));source=ref('senado',d.get('xmlSource') or d['source']);terms=[];affiliations=[];knownLegs=set()
    for leg in d.get('terms',[]):
        knownLegs.add(leg['legislature'])
        for cred in leg['credentials']:
            start=dmy(cred.get('procedFecha'));end=dmy(cred.get('bajaLiteral'));terms.append({'period':period(start,end),'title':'Senador · '+leg['name']+' · '+cred.get('procedLiteral','').strip(' .'),'source':source});party=cred.get('partidoNombre');code=cred.get('partidoSiglas')
            if party:affiliations.append({'organization':party_id(party,code),'name':proper(party),'period':period(start,end),'kind':'membership','source':source,'note':'Partido político indicado por el Senado para esta credencial; corresponde al periodo documentado.'})
        for office in leg.get('offices',[]):
            if not office.get('cargoNombre'):continue
            terms.append({'period':period(dmy(office.get('cargoAltaFec')),dmy(office.get('cargoBajaFec'))),'title':proper(office['cargoNombre'])+' · '+proper(office.get('cargoOrganoNombre','')),'source':source})
    for leg in d.get('previousLegislatures',[]):
        if leg['legantsenLegislatura'] in knownLegs:continue
        terms.append({'period':'Legislatura '+leg['legantsenLegislatura']+' · fechas del mandato individual no publicadas en esta ficha','title':'Participación en el Senado · '+leg['legantsenLegRomano'],'source':source})
    if not terms:terms=[{'period':'Legislatura '+str(d['leg'])+' · fechas individuales pendientes de contraste','title':'Senador incluido en el archivo oficial desde 1977','source':ref('senado',d['source'])}]
    for office in d.get('otherOffices',[]):
        if office.get('corporacionLocalCargo'):terms.append({'period':office.get('corporacionLocalPeriodo') or 'Fechas no publicadas','title':proper(office['corporacionLocalCargo'])+' · '+office.get('corporacionLocalNombre',''),'source':source})
    bio=personal.get('biografia') or d.get('biography') or '';bi=[]
    # La biografía institucional es una fuente, no un currículum inferido por la profesión.
    if bio and len(bio)<2500 and not re.search(r'estado civil|casad[oa]|hij[oa]',bio,re.I):bi=[bio]
    extra={};death=dmy(personal.get('fallecidoFecha'))
    if death:extra.update({'deathDate':death,'deathYear':int(death[:4])})
    incorporate('senado',file.stem,name,birth,d,terms,affiliations,bi,[],extra)
    if len(records)%500==0:print('Fichas incorporadas',len(records),flush=True)

save(ROOT/'Políticos/revisiones/2026-10-08-parlamento/informe.json',{'date':DATE,'sourceCounts':{'congreso':3023,'senado':2521},'consulted':len(records),'uniquePeople':len(folders),'originalIds':originalIds,'records':records,'identityConflicts':conflicts,'coverage':'Desde la Legislatura Constituyente de 1977. Las fechas de participación anterior en Senado no sustituyen las fechas del mandato individual. Se conservan fuentes por persona y por cargo. Los datos no publicados no se completan por conjetura.'})
print('Registros institucionales',len(records),'personas únicas',len(folders),'retratos',sum(r['portrait'] for r in records),'discrepancias documentadas',len(conflicts),flush=True)
