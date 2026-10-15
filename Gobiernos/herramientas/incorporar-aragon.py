"""Incorporación reproducible sin duplicar biografías ni inventar intervalos históricos."""
import base64,collections,concurrent.futures,hashlib,importlib.util,io,json,pathlib,re,sys,unicodedata
from urllib.parse import urljoin
spec=importlib.util.spec_from_file_location('c','Gobiernos/herramientas/consultar-aragon.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);c=a.c
from PIL import Image
ROOT=pathlib.Path('.');PERSONS=ROOT/'Políticos';AUDIT=ROOT/'Gobiernos/revisiones/2026-10-16-aragon';DATE=c.CHECKED
REGIONS={'aragon':'Aragón'}
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
        lower=norm(name);org='psoe'if lower in ['socialista','g p socialista']else'pp'if lower in ['popular','g p popular de las cortes de aragon']else'vox'if lower=='g p vox en aragon'else'cs'if lower=='g p ciudadanos partido de la ciudadania cs'else None
        self.add(id,'afiliaciones.json',[{'organization':org,'name':f'{REGIONS[region]} · {name}','period':period,'kind':'association','source':ref(url,'Grupo parlamentario publicado por la Cámara'),'note':'Adscripción parlamentaria del periodo indicado; no acredita por sí sola militancia.','territory':region}])
    def photo(self,id,image,url,credit,metadata=None):
        if image and image!=url and not '.html?'in image and not (self.people[id][0]/'retrato.json').exists()and not any(k in image.lower()for k in ['nofoto','sinfoto','no-foto']):self.photos[id]=(image,url,credit,metadata or {})
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
                folder=self.people[id][0];file='retrato-aragon.'+suffix;(folder/file).write_bytes(raw)
                c.write(folder/'retrato.json',{'file':file,'source':canonical(source),'credit':credit,'original':source if url.startswith('data:')else url,'context':'Retrato identificado en la fuente enlazada; no se atribuye una fecha de toma desconocida.',**metadata})
                return id
            except Exception as error:self.errors.append({'person':id,'source':source,'error':str(error)});return None
        with concurrent.futures.ThreadPoolExecutor(6)as pool:completed=[r for r in pool.map(portrait,self.photos.items())if r]
        photos={id:load(folder/'retrato.json',{})for id,(folder,_)in self.people.items()}
        missing=sorted(id for id,(folder,_)in self.people.items()if not photos[id].get('file')or not(folder/photos[id]['file']).is_file())
        audit={'checkedAt':DATE,'baselinePeople':len(self.baseline),'totalPeople':len(self.people),'peopleReviewed':len(self.used),'newPeople':sorted(set(self.people)-self.baseline),'portraitErrors':self.errors,'portraitsAdded':sum(p.get('file','').startswith('retrato-aragon.')for p in photos.values()),'allMissingPortraits':missing,'unresolvedHistoricalNames':unique(self.unresolved)}
        c.write(PERSONS/'revisiones/2026-10-16-aragon/informe.json',audit)
        c.write(AUDIT/'identidades.json',self.mappings)
        assert self.baseline<=set(self.people)
        print('CATALOGO',len(self.people),'nuevas',len(audit['newPeople']),'retratos',len(completed),'errores',len(self.errors),'historicos pendientes',len(audit['unresolvedHistoricalNames']),flush=True)

def proper(s):
    return ' '.join(w.lower()if w.lower()in ['de','del','la','las','los','y','el']else w.capitalize()for w in s.split())if s.isupper()else s

def periodfile(section,p):c.write(regional('aragon')/section/f"{p['start'][:4]} {p['label']}"/'composicion.json',p)

def run():
    cat=Catalog();profiles={p['key']:p for p in cached('perfiles.json')};lists=cached('listas.json');details={d['source']:d for d in cached('desgloses.json')}
    # Correspondencias expresas contrastadas entre nombres completos de la
    # Cámara, del organigrama y del archivo parlamentario anterior. No hay
    # emparejamiento por distancia de texto ni por grupo.
    corrections={'Alfredo Arola Blanquet':'Alfredo Francisco Javier Arola Blanquet','Antonio Joaquín Piazuelo Plou':'Antonio Piazuelo Plou','Antonio Romero Santolaria':'Antonio Ignacio Romero Santolaria','Begoña Sancho Antonio':'María Begoña Sancho Antonio','Blanca Puyuelo del Val':'María Blanca Puyuelo del Val','Eloy Vicente Suárez Lamata':'Eloy Suárez Lamata','Elías Cebrián Torralba':'Elías Ramón Cebrián Torralba','Herminio Sancho Iñiguez':'Herminio Rufino Sancho Íñiguez','Ines Pociña Perez':'María Inés Pociña Pérez','Joaquín Tejera Miro':'Joaquín Ignacio Tejera Miró','Luis Navarro Elola':'Luis Gonzaga Navarro Elola','Manuel Blasco Nogués':'Manuel Lorenzo Blasco Nogués','Octavio Lopez Rodriguez':'Octavio Adolfo López Rodríguez','Ricardo Canals Lizano':'Ricardo Luis Gabriel Canals Lizano','Rocío Divar Conde':'María del Rocío Dívar Conde','Carmen M.ª Susín Gabarre':'Carmen María Susín Gabarre','Roberto Bermúdez de Castro':'Roberto Bermúdez de Castro Mur','Pilar Ventura Contreras':'María Pilar Ventura Contreras','Tomasa Hernández Martínez':'Tomasa Hernández Martín','Marã�a Navarro Viscasillas':'María Navarro Viscasillas','Javier Valentã�n Alonso Coronel':'Javier Valentín Alonso Coronel','Beatriz Sanchez Garcã‰s':'Beatriz Sánchez Garcés','Marã�a Lorena Garcia Lopez':'María Lorena García López'}
    corrections.update({'Jorge Azcón Navarro':'Jorge Antonio Azcón Navarro','María Pilar Alegría Continente':'María del Pilar Alegría Continente'})
    corrections.update({'Alfredo Boné Pueyo':'Alfredo Valeriano Boné Pueyo','Arturo Aliaga López':'José Arturo Aliaga López','Eva Almunia Badía':'María Eva Almunia Badía','Miguel Ferrer Górriz':'Juan Miguel Ferrer Górriz','Ricardo Oliván Bellosta':'Ricardo Francisco Oliván Bellosta'})
    corrections={name:value for name,value in corrections.items()if not any(x in name for x in ['�','Ã','ã'])}
    c.write(regional('aragon')/'fuentes/identidades-revisadas.json',corrections)
    keys={};parliaments=[];coverage=[]
    def identify(row):
        key=row['key'];profile=profiles.get(key,row);name=proper(profile.get('nameInProfile')or row['name'])
        if key in keys:return keys[key]
        id=cat.resolve(name,'aragon',row['source'],'Miembro de las Cortes de Aragón');keys[key]=id
        cat.photo(id,profile.get('image')or row.get('image'),row['source'],'Cortes de Aragón · retrato de la ficha individual')
        cat.add(id,'formacion.json',profile.get('education',[]))
        if profile.get('education'):cat.add(id,'fuentes-formacion.json',[ref(row['source'],'Formación declarada en las Cortes')])
        cat.mappings.append({'territory':'aragon','key':key,'nameInSource':name,'person':id,'source':row['source']})
        for r in profile.get('roles',[]):
            if not r['title'].startswith('Diputad'):cat.event(id,'cargos-autonomias.json','aragon',r['title'],f"Legislatura {ROMANS[r['legislature']-1]} · registro de la ficha",row['source'])
        return id
    for li,listing in enumerate(lists):
        leg=li+1;current=leg==12;label='Legislatura '+ROMANS[li];records={};groups=[];province={};board=[]
        for link in listing['links']:
            if 'uidcir'in link['source']:
                for row in details[link['source']]['records']:province[row['key']]=re.sub(r'\s+\d+$','',link['label'])
        for row in listing['records']:
            id=identify(row);profile=profiles.get(row['key'],{});start,end=row.get('start'),row.get('endInSource')
            period=f'{label} · registro nominal consultado {DATE}'if current else f'{label} · {start or "alta no publicada"} — {end or "baja no publicada"}'
            item={'person':id,'name':cat.people[id][1]['fullName'],'role':'Miembro de las Cortes de Aragón','source':row['source'],'start':None,'end':None,'constituency':province.get(row['key'])or profile.get('constituency'),'period':period}
            records[id]=item;cat.event(id,'mandatos-autonomias.json','aragon','Cortes de Aragón · '+(item['constituency']or'circunscripción no indicada'),period,row['source'])
            if row.get('group'):cat.group(id,'aragon',row['group'],label+' · adscripción archivada sin intervalo propio',row['source'])
        for link in listing['links']:
            if 'uidgru'not in link['source']:continue
            rows=details[link['source']]['records'];name=re.sub(r'\s+\d+$','',link['label']);expected=int(re.search(r'(\d+)$',link['label'])[1]);assert len(rows)==expected,(label,name,len(rows),expected)
            members=[]
            for row in rows:
                id=identify(row)
                if id not in records:records[id]={'person':id,'name':cat.people[id][1]['fullName'],'role':'Miembro de las Cortes de Aragón','source':row['source'],'start':None,'end':None}
                item={**records[id],'formation':name,'formationLabel':'Grupo parlamentario','constituency':province.get(row['key'])or records[id].get('constituency')}
                members.append(item)
                if current:item['observedAt']=DATE;cat.active(id,listing['source'])
            groups.append({'name':name,'source':link['source'],'members':members})
        for link in listing['links']:
            if 'uidcom'not in link['source']:continue
            for row in details[link['source']]['records']:
                id=identify(row);role=row['group']+' de las Cortes de Aragón';item={'person':id,'name':cat.people[id][1]['fullName'],'role':role,'source':link['source'],'start':None,'end':None,'period':label+' · Mesa publicada'}
                if current:item['observedAt']=DATE
                board.append(item);cat.event(id,'cargos-autonomias.json','aragon',role,item['period'],link['source'])
        final=[m for group in groups for m in group['members']];assert len(set(m['person']for m in final))==len(final),label
        capacity=sum(int(re.search(r'(\d+)$',x['label'])[1])for x in listing['links']if 'uidcir'in x['source']);assert len(final)==capacity,(label,len(final),capacity)
        # Marco nominal publicado; no se presenta como toma de posesión de todos.
        start=min(r['start']for r in listing['records']if r.get('start'));end=None if current else max((r['endInSource']for r in listing['records']if r.get('endInSource')),default=None)
        if current:start='2026-03-03'
        p={'id':'aragon-cortes-'+str(leg),'label':label,'start':start,'end':end,'checkedAt':DATE,'source':listing['source'],'currentOnly':current,'nominalOnly':not current,'capacity':capacity,'note':'Diagrama nominal de las adscripciones archivadas por las Cortes. No reproduce asientos físicos ni cambios diarios de grupo. El registro histórico conserva sustituciones aparte.','records':final if current else list(records.values()),'board':board if current else[],'archiveBoard':[]if current else board,'groups':groups}
        if not current:p['archivedComposition']={'source':listing['source'],'checkedAt':DATE,'note':'Relaciones por grupo publicadas en el archivo de la legislatura; no equivalen a una composición diaria.','groups':[{'name':g['name'],'source':g['source'],'members':[m['person']for m in g['members']]}for g in groups]};p['archiveBoardNote']='Titulares conservados por la Cámara; no se supone completa la Mesa histórica ni se inventan fechas individuales.'
        periodfile('Parlamento',p);parliaments.append(p);coverage.append({'legislature':leg,'nominalPeople':len(records),'composition':len(final),'capacity':capacity,'board':len(board),'source':listing['source']})
    appointments=cached('presidencias.json');history=cached('consejerias-historicas.json');governments=[];periodkeys=[11,10,9,8,7,6,5,4,3,21,24,25,26,27]
    # El PDF de 1995 contiene "ju/io" en su capa de texto. Su decreto original
    # identifica expresamente el 8 de julio; no usar la publicación del día 11.
    for ap in appointments:
        if ap['name']=='Santiago Lanzuela Marina':ap['date']='1995-07-08'
    for i,ap in enumerate(appointments):
        id=cat.resolve(ap['name'],'aragon',ap['source'],'Presidencia de Aragón');current=i==len(appointments)-1;end=appointments[i+1]['date']if not current else None
        title='Presidencia interina de Aragón'if ap.get('interim')else'Presidencia de Aragón';president={'person':id,'name':cat.people[id][1]['fullName'],'role':title,'level':'president','start':ap['date'],'end':end,'source':ap['source'],'endBasis':'Siguiente marco presidencial publicado; no acredita por sí solo la fecha de cese.'}
        if current:president['observedAt']=DATE
        p={'id':'aragon-gobierno-'+ap['date'],'label':'Gobierno '+ap['date'][:4]+(' · interino'if ap.get('interim')else' · '+ap['date'][5:]if ap['date'][:4]=='1995'else''),'start':ap['date'],'end':end,'checkedAt':DATE,'name':'Aragón · '+president['name'],'source':ap['source'],'terms':[president],'archiveTerms':[],'incidents':['El marco presidencial utiliza la fecha del decreto de nombramiento; no equivale a la toma de posesión. Las consejerías del archivo no se atribuyen simultaneidad ni fechas individuales desconocidas.'],'currentOnly':current}
        for row in history:
            if row['legislatureKey']!=periodkeys[i]or current:continue
            if row['role'].lower().startswith('president'):continue
            role=row['role']+' de '+row['entity'];rid=cat.resolve(row['name'],'aragon',row['source'],role);period=row['period']+(f" · {row['start']} — {row['endInSource']or'fin no publicado'}"if row['start']else' · intervalo individual no publicado')
            p['archiveTerms'].append({'person':rid,'name':cat.people[rid][1]['fullName'],'role':role,'source':row['source'],'start':None,'end':None,'period':period});cat.event(rid,'cargos-autonomias.json','aragon',role,period,row['source'])
        p['archiveTerms']=unique(p['archiveTerms']);governments.append(p);cat.event(id,'cargos-autonomias.json','aragon',title,'Nombramiento · '+ap['date'],ap['source'])
    latest=governments[-1]
    for row in cached('gobierno-vigente.json'):
        id=cat.resolve(row['name'],'aragon',row['source'],row['role']);cat.photo(id,row['image'],row['source'],'Gobierno de Aragón · ficha de transparencia');cat.active(id,row['directory'])
        if id==latest['terms'][0]['person']:continue
        latest['terms'].append({'person':id,'name':cat.people[id][1]['fullName'],'role':row['role'],'source':row['source'],'start':None,'end':None,'observedAt':DATE,'level':'vice'if row['role'].startswith('Vicepres')else'minister','period':'Composición consultada · '+DATE});cat.event(id,'cargos-autonomias.json','aragon',row['role'],'Composición consultada · '+DATE,row['source'])
    assert len(latest['terms'])==10
    for p in governments:periodfile('Gobierno',p)
    c.write(regional('aragon')/'fuentes/nombramientos-presidenciales.json',appointments)
    c.write(regional('aragon')/'fuentes/registro-parlamentario.json',[{k:v for k,v in p.items()if k!='image'}for p in profiles.values()])
    c.write(regional('aragon')/'fuentes/consejerias-historicas.json',history)
    c.write(regional('aragon')/'fuentes/gobierno-vigente.json',{'checkedAt':DATE,'source':'https://www.aragon.es/transparencia/gobierno','members':latest['terms']})
    c.write(AUDIT/'informe.json',{'checkedAt':DATE,'legislatures':coverage,'governments':len(governments),'historicalCabinetRecords':len(history),'currentGovernmentPeople':len(latest['terms']),'profileErrors':[{'key':p['key'],'name':p['name'],'source':p['source'],'error':p['sourceError']}for p in profiles.values()if p.get('sourceError')]})
    cat.save()

if __name__=='__main__':run()
