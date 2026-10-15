"""Incorporación reproducible sin duplicar biografías ni inventar intervalos históricos."""
import base64,collections,concurrent.futures,hashlib,importlib.util,io,json,pathlib,re,sys,unicodedata
from urllib.parse import urljoin
spec=importlib.util.spec_from_file_location('c','Gobiernos/herramientas/consultar-castillas.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
from PIL import Image
ROOT=pathlib.Path('.');PERSONS=ROOT/'Políticos';AUDIT=ROOT/'Gobiernos/revisiones/2026-10-15-castillas';DATE=c.CHECKED
REGIONS={'clm':'Castilla-La Mancha','cyl':'Castilla y León'}
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
def load(path,default=None):
    p=pathlib.Path(path);return json.loads(p.read_text('utf8'))if p.exists()else default
def cached(file):return load(c.CACHE/file)
def norm(s):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip()
def unique(rows):
    out=[];seen=set()
    for row in rows:
        k=json.dumps(row,ensure_ascii=False,sort_keys=True)
        if k not in seen:out.append(row);seen.add(k)
    return out
def canonical(url):return url.replace('http://www.ccyl.es/','https://www.ccyl.es/').replace('https://gestorcontenidos.jcyl.es/','https://gobierno.jcyl.es/').replace('http://gestorcontenidos.jcyl.es/','https://gobierno.jcyl.es/')
def ref(url,label):return {'label':label,'url':canonical(url),'kind':'encyclopedic'if 'wikipedia.org'in url else'institutional'}
def regional(region):return ROOT/'Gobiernos/Autonomías'/REGIONS[region]
def ordinal(text):return ROMANS.index(text)+1
def source_person(path):
    meta=load(path/'ficha.json');return (path,meta)if meta else None
class Catalog:
    def __init__(self):
        folders=[p for p in PERSONS.iterdir()if p.is_dir()and p.name not in ['interfaz','herramientas','revisiones']]
        with concurrent.futures.ThreadPoolExecutor(24)as pool:rows=[r for r in pool.map(source_person,folders)if r]
        self.people={m['id']:(p,m)for p,m in rows};assert len(self.people)==len(rows)
        self.names=collections.defaultdict(set)
        for folder,meta in rows:
            for n in [meta['fullName'],meta['name'],*meta.get('knownAs',[])]:self.names[norm(n)].add(meta['id'])
        existing=load(AUDIT/'conservacion.json')
        self.baseline=set(existing['baselineIds'])if existing else set(self.people)
        if not existing:c.write(AUDIT/'conservacion.json',{'checkedAt':DATE,'baselineIds':sorted(self.baseline)})
        self.used=set();self.files={};self.photos={};self.errors=[];self.mappings=[];self.unresolved=[]
    def resolve(self,name,region,source,role,allow_new=True):
        name=re.sub(r'^(?:(?:Excmo\.|Excma\.|Ilmo\.|Ilma\.)\s*)?(?:Sr\.|Sra\.|Dña\.|D\.|Don |Doña )\s*','',c.clean(name)).strip(' .')
        corrections=load(regional(region)/'fuentes/identidades-revisadas.json',{})
        corrected=corrections.get(name,name)
        name=corrected['fullName']if isinstance(corrected,dict)else corrected
        matches=self.names.get(norm(name),set())
        if len(matches)>1:raise ValueError('Identidad ambigua: '+name+' '+str(matches))
        if matches:id=next(iter(matches))
        elif not allow_new:
            self.unresolved.append({'name':name,'source':source,'role':role});return None
        else:
            id=region+'-'+norm(name).replace(' ','-');folder=PERSONS/name
            assert not folder.exists(),name
            meta={'id':id,'name':name,'fullName':name,'initials':''.join(w[0]for w in name.split()[:2]),'organization':None,'affiliationStatus':'pending','relation':'Trayectoria institucional documentada','role':role,'summary':role+'.','offices':[],'reviewedAt':DATE}
            self.people[id]=(folder,meta);self.names[norm(name)].add(id)
        self.used.add(id);folder,meta=self.people[id]
        if name!=meta['fullName']:meta['knownAs']=unique([*meta.get('knownAs',[]),name])
        self.add(id,'fuentes.json',[ref(source,role)])
        return id
    def add(self,id,file,rows):
        key=(id,file)
        if key not in self.files:
            previous=load(self.people[id][0]/file,[])
            self.files[key]=[r for r in previous if not isinstance(r,dict)or r.get('territory')not in REGIONS]
            for r in self.files[key]:
                if isinstance(r,dict)and isinstance(r.get('url'),str):r['url']=canonical(r['url'])
                if isinstance(r,dict)and isinstance(r.get('source'),dict):r['source']['url']=canonical(r['source']['url'])
        self.files[key]=unique([*self.files[key],*rows])
    def event(self,id,file,region,title,period,url):self.add(id,file,[{'title':title,'period':period,'source':ref(url,'Registro institucional'if 'wikipedia.org'not in url else'Wikipedia · cuadro histórico'),'territory':region}])
    def group(self,id,region,name,period,url):
        self.event(id,'grupos-autonomias.json',region,f'{REGIONS[region]} · {name}',period,url)
        lower=norm(name);org='psoe'if lower in ['gps','socialista']else'pp'if lower in ['gpp','popular']else'vox'if lower in ['gpv','vox castilla y leon']else'cs'if lower in ['gpc','ciudadanos']else None
        self.add(id,'afiliaciones.json',[{'organization':org,'name':f'{REGIONS[region]} · {name}','period':period,'kind':'association','source':ref(url,'Grupo parlamentario publicado por la Cámara'),'note':'Adscripción parlamentaria del periodo indicado; no acredita por sí sola militancia.','territory':region}])
    def photo(self,id,image,url,credit,metadata=None):
        if image and not (self.people[id][0]/'retrato.json').exists()and not any(k in image.lower()for k in ['nofoto','sinfoto','no-foto']):self.photos[id]=(image,url,credit,metadata or {})
    def active(self,id,url):
        personal=load(self.people[id][0]/'datos-personales.json',{})
        assert not(personal.get('deathDate')or personal.get('deathYear')),id
        self.files[id,'actividad.json']={'state':'active','reason':'Titular incluido en la composición institucional consultada.','checkedAt':DATE,'sources':[ref(url,'Composición institucional vigente')]}
    def save(self):
        writes=[(self.people[id][0]/'ficha.json',self.people[id][1])for id in self.used]
        writes += [(self.people[id][0]/file,value)for (id,file),value in self.files.items()if value]
        with concurrent.futures.ThreadPoolExecutor(16)as pool:list(pool.map(lambda row:c.write(*row),writes))
        def portrait(item):
            id,(url,source,credit,metadata)=item
            try:
                import html
                url=html.unescape(canonical(url))if 'gestorcontenidos.jcyl.es'in url else url
                raw=base64.b64decode(url.split(',',1)[1])if url.startswith('data:')else c.fetch(url)
                im=Image.open(io.BytesIO(raw));fmt=im.format;im.verify()
                suffix={'JPEG':'jpg','PNG':'png','WEBP':'webp','GIF':'gif'}[fmt]
                folder=self.people[id][0];file='retrato-castillas.'+suffix;(folder/file).write_bytes(raw)
                c.write(folder/'retrato.json',{'file':file,'source':canonical(source),'credit':credit,'original':source if url.startswith('data:')else url,'context':'Retrato identificado en la fuente enlazada; no se atribuye una fecha de toma desconocida.',**metadata})
                return id
            except Exception as error:self.errors.append({'person':id,'source':source,'error':str(error)});return None
        with concurrent.futures.ThreadPoolExecutor(6)as pool:completed=[r for r in pool.map(portrait,self.photos.items())if r]
        photos={id:load(folder/'retrato.json',{})for id,(folder,_)in self.people.items()}
        missing=sorted(id for id,(folder,_)in self.people.items()if not photos[id].get('file')or not(folder/photos[id]['file']).is_file())
        audit={'checkedAt':DATE,'baselinePeople':len(self.baseline),'totalPeople':len(self.people),'peopleReviewed':len(self.used),'newPeople':sorted(set(self.people)-self.baseline),'portraitErrors':self.errors,'portraitsAdded':sum(p.get('file','').startswith('retrato-castillas.')for p in photos.values()),'allMissingPortraits':missing,'unresolvedHistoricalNames':unique(self.unresolved)}
        c.write(PERSONS/'revisiones/2026-10-15-castillas/informe.json',audit)
        c.write(AUDIT/'identidades.json',self.mappings)
        assert self.baseline<=set(self.people)
        print('CATALOGO',len(self.people),'nuevas',len(audit['newPeople']),'retratos',len(completed),'errores',len(self.errors),'historicos pendientes',len(audit['unresolvedHistoricalNames']),flush=True)
cat=Catalog()
profiles={r:{p['source']:p for p in cached(r+'-perfiles.json')}for r in REGIONS}
personKeys={r:{}for r in REGIONS}
def term(name,region,role,url,**extra):
    id=cat.resolve(name,region,url,role);return {'person':id,'name':cat.people[id][1]['fullName'],'role':role,'source':canonical(url),'start':None,'end':None,**extra}
def saveperiod(region,section,p):c.write(regional(region)/section/f"{p['start'][:4]} {p['label']}"/'composicion.json',p)
CLM_DATES=['1983-05-31','1987-07-02','1991-06-21','1995-06-21','1999-07-07','2003-06-17','2007-06-19','2011-06-16','2015-06-18','2019-06-19','2023-06-22']
CYL_DATES=['1983-05-21','1987-07-02','1991-06-21','1995-06-21','1999-07-05','2003-06-17','2007-06-19','2011-06-14','2015-06-16','2019-06-21','2022-03-10','2026-04-14']
def parliaments(region):
    lists=cached(region+'-listas.json');dates=CLM_DATES if region=='clm'else CYL_DATES
    boards=cached('clm-mesas.json')if region=='clm'else cached('cyl-composiciones.json')
    currentKeys={m['key']for m in cached('cyl-pleno-vigente.json')['members']}if region=='cyl'else set(lists[-1]['listed'])
    chamber='Cortes de '+REGIONS[region];result=[]
    for li,listing in enumerate(lists):
        leg=li+1;current=leg==len(lists);label='Legislatura '+ROMANS[li];allrows=listing['records'];records=[];bykey={};groupRows=collections.defaultdict(list)
        for row in allrows:
            profile=profiles[region][row['source']];name=profile['name'];key=row['key']
            if key in personKeys[region]:
                known=personKeys[region][key];cat.names[norm(name)].add(known)
            item=term(name,region,'Miembro de las '+chamber,row['source'],constituency=row.get('constituency'),formation=row.get('group'),formationLabel='Grupo parlamentario',period=f'{label} · registro nominal consultado')
            personKeys[region][key]=item['person'];bykey[key]=item
            cat.mappings.append({'territory':region,'key':key,'legislature':leg,'person':item['person'],'nameInSource':name,'source':canonical(row['source'])})
            if item['person']not in {r['person']for r in records}:records.append(item)
            period=f'{label} · composición consultada {DATE}'if current and key in currentKeys else f'{label} · archivo nominal'
            cat.event(item['person'],'mandatos-autonomias.json',region,chamber+' · '+(row.get('constituency')or'circunscripción no indicada'),period,row['source'])
            if row.get('group'):
                cat.group(item['person'],region,row['group'],label+' · adscripción publicada',row['source'])
            cat.add(item['person'],'formacion.json',profile.get('education',[]))
            if profile.get('education'):cat.add(item['person'],'fuentes-formacion.json',[ref(row['source'],'Cortes · titulación o formación declarada')])
            for bio in profile.get('biography',[]):
                years=[int(y)for y in re.findall(r'\d{4}',bio['period'])]
                if len(years)>1 and years[-1]<years[0]:continue
                cat.event(item['person'],'cargos-autonomias.json',region,bio['title'],bio['period'],row['source'])
            if region=='clm':
                for role in profile.get('roles',[]):
                    if 'Grupo Parlamentario'in role['organ']:continue
                    cat.event(item['person'],'cargos-autonomias.json',region,role['role']+' · '+role['organ'],f"{role['start']} — {role['endInSource']or'fin no publicado'}",row['source'])
            cat.photo(item['person'],profile.get('image'),row['source'],'Cortes de '+REGIONS[region])
        finalRows=[r for r in allrows if r['key']in (set(listing['listed'])if region=='clm'else currentKeys)]if current else [r for r in allrows if r['key']in set(listing['listed'])]if region=='clm'else[r for r in allrows if 'Hasta 'not in r['note']]
        final=[];seen=set()
        for row in finalRows:
            item={**bykey[row['key']],'formation':row['group'],'constituency':row['constituency']}
            if item['person']in seen:raise ValueError('Dos adscripciones finales '+str(row))
            seen.add(item['person']);final.append(item);groupRows[row['group']or'Sin adscripción publicada'].append(item)
            if current:cat.active(item['person'],row['source']);item['observedAt']=DATE
        capacity=([44,47,47,47,47,47,47,49,33,33,33][li]if region=='clm'else boards[li]['capacity'])
        p={'id':region+'-cortes-'+str(leg),'label':label,'start':dates[li],'end':dates[li+1]if li+1<len(dates)else None,'checkedAt':DATE,'source':canonical(listing['source']),'currentOnly':current,'nominalOnly':not current,'capacity':capacity,'note':'Composición consultada; no se atribuyen asientos físicos ni se reconstruyen adscripciones diarias sin fecha.','records':final if current else records,'board':[],'archiveBoard':[],'groups':[{'name':g,'source':canonical(listing['source']),'members':members}for g,members in groupRows.items()]}
        if not current:p['archivedComposition']={'source':canonical(listing['source']),'checkedAt':DATE,'note':'Composición archivada de la Cámara: relación principal de diputados.'if region=='clm'else'Últimas adscripciones conservadas por la Cámara: se excluyen las filas con baja expresa («Hasta»). No acredita una composición para cada día de la legislatura.','groups':[{'name':g,'source':canonical(listing['source']),'members':[m['person']for m in members]}for g,members in groupRows.items()]}
        b=[r for r in boards if r['legislature']==ROMANS[li]]if region=='clm'else boards[li]['board']
        for row in b:
            key=row.get('key');id=personKeys[region].get(key)
            if not id:id=cat.resolve(row['name'],region,row['source'],row['role']+' de las Cortes')
            item=term(cat.people[id][1]['fullName'],region,row['role']+' de las Cortes',row['source'],period=('Mesa vigente · '+DATE)if current else'Mesa histórica publicada · '+label,**({'observedAt':DATE}if current else{}))
            p['board'if current else'archiveBoard'].append(item);cat.event(id,'cargos-autonomias.json',region,REGIONS[region]+' · '+item['role'],item['period'],row['source'])
        if not current:p['archiveBoardNote']='Titulares publicados sin atribuir intervalos diarios no contrastados.'
        saveperiod(region,'Parlamento',p);result.append(p)
    c.write(regional(region)/'fuentes/registro-parlamentario.json',[{k:v for k,v in r.items()if k!='image'}for r in profiles[region].values()])
    return result
def governments(region):
    appointments=cached(region+'-presidencias.json');result=[]
    for i,a in enumerate(appointments):
        current=i==len(appointments)-1;end=appointments[i+1]['date']if not current else None
        p={'id':region+'-gobierno-'+a['date'],'label':'Gobierno '+a['date'][:4]+(' · '+a['date'][5:]if sum(r['date'][:4]==a['date'][:4]for r in appointments)>1 else''),'start':a['date'],'end':end,'checkedAt':DATE,'name':REGIONS[region]+' · '+a['name'],'source':a['source'],'terms':[term(a['name'],region,'Presidencia de '+REGIONS[region],a['source'],start=a['date'],end=end,level='president',endBasis='Siguiente nombramiento presidencial documentado; marco de consulta, no fecha individual de toma de posesión.',**({'observedAt':DATE}if current else{}))],'archiveTerms':[],'incidents':['Las fechas del marco corresponden al real decreto de nombramiento. No equivalen por sí solas a toma de posesión ni a ceses individuales.'],'currentOnly':current}
        id=p['terms'][0]['person'];cat.event(id,'cargos-autonomias.json',region,REGIONS[region]+' · Presidencia','Nombramiento · '+a['date'],a['source'])
        result.append(p)
    current=result[-1];rows=cached(region+'-gobierno-vigente.json')
    if region=='clm':
        prepared=[]
        for row in rows:
            if row['source'].endswith('/presidente'):continue
            name=row['text'].removeprefix(row['heading']).removesuffix('Consejería Organigrama').strip();role=row['heading']
            prepared.append({'name':name,'role':role,'source':row['source'],'image':row['image']})
    else:
        prepared=[{'name':r['nombre'],'role':r['titulo'],'source':r['enlace_al_contenido'],'image':r.get('fotografia'),'education':r.get('formacionacademica')}for r in rows if not r['titulo'].startswith('Presidente de la Junta')]
        president=next(r for r in rows if r['titulo'].startswith('Presidente de la Junta'));cat.photo(current['terms'][0]['person'],president.get('fotografia'),president['enlace_al_contenido'],'Junta de Castilla y León')
    combined={}
    for row in prepared:
        id=cat.resolve(row['name'],region,row['source'],row['role']);cat.photo(id,row.get('image'),row['source'],'Gobierno de '+REGIONS[region]);cat.active(id,row['source'])
        education=row.get('education')
        if education:
            items=[c.clean(n.get_text(' ',strip=True))for n in c.BeautifulSoup(education,'html.parser').select('li')]
            cat.add(id,'formacion.json',items);cat.add(id,'fuentes-formacion.json',[ref(row['source'],'Formación publicada en el directorio de altos cargos')])
        cat.event(id,'cargos-autonomias.json',region,REGIONS[region]+' · '+row['role'],'Composición consultada · '+DATE,row['source'])
        if id in combined:
            combined[id]['role']+=' · '+row['role'];continue
        item=term(cat.people[id][1]['fullName'],region,row['role'],row['source'],observedAt=DATE,period='Composición vigente · '+DATE,level='vice'if row['role'].lower().startswith('vicepres')else'minister');combined[id]=item
    current['terms'] += sorted(combined.values(),key=lambda t:0 if 'primera'in t['role'].lower()or'primero'in t['role'].lower()else 1 if 'segunda'in t['role'].lower()else 2)
    cat.active(current['terms'][0]['person'],current['source'])
    for p in result:saveperiod(region,'Gobierno',p)
    c.write(regional(region)/'fuentes/nombramientos-presidenciales.json',appointments)
    c.write(regional(region)/'fuentes/gobierno-vigente.json',{'checkedAt':DATE,'members':current['terms']})
    return result
def historical_cabinets(governmentsByRegion):
    admitted=collections.defaultdict(list)
    for row in cached('consejerias-historicas.json')or[]:
        region=row['territory'];p=next((g for g in governmentsByRegion[region]if int(g['start'][:4])==row['stageYear']),None)
        if not p:continue
        id=cat.resolve(row['name'],region,row['source'],row['role'],allow_new=bool(row.get('primaryMatched')and not row.get('existingIdentityOnly')))
        if not id:continue
        item={'person':id,'name':cat.people[id][1]['fullName'],'role':row['role'],'source':canonical(row['source']),'start':None,'end':None,'period':row['period']}
        p['archiveTerms']=unique([*p['archiveTerms'],item]);cat.event(id,'cargos-autonomias.json',region,REGIONS[region]+' · '+row['role'],row['period'],row['source'])
        admitted[region].append({**row,'person':id,'fullName':item['name']})
    for region,governments in governmentsByRegion.items():
        for p in governments:
            if not p.get('currentOnly'):p['incidents'].append('El archivo de consejerías reúne titulares y cambios documentados; no es una composición simultánea ni un inventario completo de remodelaciones. Las referencias enciclopédicas complementarias están identificadas en cada enlace.')
            saveperiod(region,'Gobierno',p)
        c.write(regional(region)/'fuentes/consejerias-historicas.json',unique(admitted[region]))

def reviewed_biographies():
    # Correspondencias revisadas individualmente. No extraer identidades por
    # similitud ni completar apellidos a partir de un cargo compartido.
    for region in REGIONS:
        for row in load(regional(region)/'fuentes/biografias-revisadas.json',[]):
            id=cat.resolve(row['fullName'],region,row['source'],'Trayectoria autonómica documentada')
            for alias in [row['nameInSource'],*row.get('aliases',[])]:
                matches=cat.names.get(norm(alias),set())
                assert not matches or matches=={id},(alias,matches,id)
                cat.names[norm(alias)].add(id)
                meta=cat.people[id][1]
                if alias!=meta['fullName']:meta['knownAs']=unique([*meta.get('knownAs',[]),alias])
            photo=row.get('photo')
            if photo:cat.photo(id,photo['image'],photo['source'],photo['credit'],{k:photo[k]for k in ['license','licenseUrl']if photo.get(k)})
            personal=load(cat.people[id][0]/'datos-personales.json',{})
            for field in ['birthDate','deathDate']:
                date=row.get(field)
                if date and re.fullmatch(r'\d{4}-\d{2}-\d{2}',date)and not personal.get(field):personal[field]=date
            if personal:
                personal['sources']=unique([*personal.get('sources',[]),ref(row['source'],'Identificación biográfica complementaria')])
                cat.files[id,'datos-personales.json']=personal

if __name__=='__main__':
    reviewed_biographies()
    report={};governmentsByRegion={}
    for region in REGIONS:
        parls=parliaments(region);govs=governments(region)
        governmentsByRegion[region]=govs
        report[region]={'parliaments':len(parls),'governments':len(govs),'currentMembers':len(parls[-1]['records']),'currentCabinet':len(govs[-1]['terms']),'archiveCounts':[sum(len(g['members'])for g in p.get('archivedComposition',{}).get('groups',[]))for p in parls]}
    historical_cabinets(governmentsByRegion)
    for region,govs in governmentsByRegion.items():report[region]['historicalCabinetCounts']=[len(g['archiveTerms'])for g in govs]
    cat.save();c.write(AUDIT/'cobertura.json',report)
