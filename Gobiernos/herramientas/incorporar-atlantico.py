"""Migra fuentes revisadas de Canarias, Ceuta y Melilla a las carpetas de dominio.

El directorio test-results/atlantico es solo la caché de consulta. Las fuentes
curadas, la procedencia y las composiciones quedan en Gobiernos/Autonomías.
No deduce militancia, retiros, fechas individuales ni asientos físicos.
"""
import base64, collections, concurrent.futures, hashlib, importlib.util, json, pathlib, re, sys, unicodedata
from urllib.parse import urljoin
spec=importlib.util.spec_from_file_location('consulta',pathlib.Path(__file__).with_name('consultar-canarias-ceuta-melilla.py'))
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
ROOT=pathlib.Path('.'); CACHE=c.CACHE; CHECKED=c.CHECKED
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI']
CURATED_NAMES={'Guillermo Guigou':'Guillermo Guigou Suárez','Rodolfo J. Núñez Ruano':'Rodolfo José Núñez Ruano','José Manuel Ruano':'José Miguel Ruano León','Narvay Quintero Castañeda':'Alejandro Narvay Quintero Castañeda','Poli Suárez Nuez':'Hipólito Alejandro Suárez Nuez'}
def load(path,default=None):
    p=pathlib.Path(path);return json.loads(p.read_text('utf8')) if p.exists() else default
def norm(name):
    return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()).strip()
def ref(url,label):return {'label':label,'url':url,'kind':'institutional'}
def union(a,b):
    seen={json.dumps(r,sort_keys=True,ensure_ascii=False) for r in a};out=list(a)
    for r in b:
        key=json.dumps(r,sort_keys=True,ensure_ascii=False)
        if key not in seen:out.append(r);seen.add(key)
    return out
def title(name):
    return ' '.join(w.lower() if w.lower() in ['de','del','la','las','los','y','el'] else w.title() for w in name.split())

class Catalog:
    def __init__(self):
        self.people={};self.names=collections.defaultdict(set);self.files={};self.new=set();self.used=set();self.aliases=[];self.photos={};self.errors=[]
        self.preferredNames=load(ROOT/'Gobiernos/revisiones/2026-10-12-atlantico/nombres-preferentes.json',[])
        for row in load(CACHE/'personas-existentes.json'):
            folder=pathlib.Path(row.pop('_folder'))
            if not (folder/'ficha.json').exists() and row['fullName'] in CURATED_NAMES:folder=ROOT/'Políticos'/CURATED_NAMES[row['fullName']]
            if not (folder/'ficha.json').exists():
                corrections=load(ROOT/'Gobiernos/revisiones/2026-10-12-atlantico/nombres-preferentes.json',[])
                correction=next((r for r in corrections if r['oldName']==row['fullName'] and r['person']==row['id']),None)
                if correction:folder=ROOT/'Políticos'/correction['fullName']
            row=load(folder/'ficha.json');self.people[row['id']]=(folder,row)
            for n in [row['fullName'],row['name'],*row.get('knownAs',[])]:self.names[norm(n)].add(row['id'])
    def get(self,name,region,source,role):
        name=CURATED_NAMES.get(name.strip(),name.strip())
        key=norm(name);matches=self.names.get(key,set())
        if len(matches)>1:
            # Catálogo anterior con homónimos: no unir fichas sin evidencia extra.
            raise ValueError('Nombre ambiguo: '+name+' '+str(matches))
        if matches:person=next(iter(matches))
        else:
            person=region+'-'+key.replace(' ','-');folder=ROOT/'Políticos'/name
            meta=load(folder/'ficha.json')
            if not meta:
                preferred=next((r for r in self.preferredNames if r['person']==person and norm(r['fullName'])==key),None)
                if preferred:
                    folder=ROOT/'Políticos'/preferred['fullName'];meta=load(folder/'ficha.json')
            if meta:
                assert norm(meta['fullName'])==key,(name,meta['fullName'])
                person=meta['id']
            else:
                meta={'id':person,'name':name,'fullName':name,'initials':''.join(w[0] for w in name.split()[:2]),'organization':None,'affiliationStatus':'pending','relation':'Trayectoria institucional documentada','role':role,'summary':f'{role}.','offices':[],'reviewedAt':CHECKED}
            self.people[person]=(folder,meta);self.names[key].add(person);self.new.add(person)
        self.used.add(person);self.add(person,'afiliaciones.json',[]);self.add(person,'fuentes.json',[ref(source,role)])
        if (person,'actividad.json') not in self.files:
            previous=load(self.people[person][0]/'actividad.json',{})
            if previous.get('reason')=='Titular incluido en la composición institucional vigente consultada.':
                self.files[(person,'actividad.json')]={'state':'unknown','reason':'La actividad actual no se determina por el cierre de un cargo histórico.','checkedAt':CHECKED,'sources':previous.get('sources',[])}
        return person
    def alias(self,old,new,source):
        ids=self.names.get(norm(new),set())
        if len(ids)!=1:return
        person=next(iter(ids));self.names[norm(old)].add(person)
        folder,meta=self.people[person]
        if old!=meta['fullName']:meta['knownAs']=union(meta.get('knownAs',[]),[old])
        self.aliases.append({'nameInSource':old,'canonicalName':meta['fullName'],'person':person,'source':source})
    def prefer(self,person,name,source):
        name=CURATED_NAMES.get(name.strip(),name.strip());folder,meta=self.people[person];old=meta['fullName']
        if norm(old)!=norm(name) or old==name:return
        # El nombre publicado en una ficha identificada prevalece sobre una
        # transcripción electoral sin tildes. Nunca empareja apellidos parecidos.
        marks=lambda text:sum(bool(unicodedata.combining(ch)) for ch in unicodedata.normalize('NFD',text))
        if marks(name)<=marks(old):return
        target=ROOT/'Políticos'/name
        assert folder.resolve().parent==(ROOT/'Políticos').resolve() and target.resolve().parent==(ROOT/'Políticos').resolve()
        assert not target.exists(),(old,name)
        if folder.exists():folder.rename(target)
        meta['knownAs']=union(meta.get('knownAs',[]),[old]);meta['fullName']=name
        if norm(meta['name'])==norm(old):meta['name']=name
        self.people[person]=(target,meta)
        path=ROOT/'Gobiernos/revisiones/2026-10-12-atlantico/nombres-preferentes.json'
        c.write(path,union(load(path,[]),[{'person':person,'oldName':old,'fullName':name,'source':source}]))
    def add(self,person,file,rows):
        key=(person,file)
        if key not in self.files:
            previous=load(self.people[person][0]/file,[])
            if file in ['cargos-autonomias.json','mandatos-autonomias.json','grupos-autonomias.json']:previous=[]
            if file=='afiliaciones.json':previous=[r for r in previous if r.get('note')!='Relación electoral o parlamentaria documentada; no acredita por sí sola militancia.']
            self.files[key]=previous
        self.files[key]=union(self.files[key],rows)
    def active(self,person,url):
        folder,meta=self.people[person];personal=load(folder/'datos-personales.json',{})
        if personal.get('deathDate') or personal.get('deathYear'):raise ValueError('Titular vigente figura fallecido: '+person)
        self.files[(person,'actividad.json')]={'state':'active','reason':'Titular incluido en la composición institucional vigente consultada.','checkedAt':CHECKED,'sources':[ref(url,'Composición institucional vigente')]}
    def office(self,person,role,period,url):self.add(person,'cargos-autonomias.json',[{'title':role,'period':period,'source':ref(url,'Cargo institucional documentado')}])
    def mandate(self,person,role,period,url):self.add(person,'mandatos-autonomias.json',[{'title':role,'period':period,'source':ref(url,'Registro parlamentario o electoral')}])
    def group(self,person,group,period,url,organization=None):
        self.add(person,'grupos-autonomias.json',[{'title':group,'period':period,'source':ref(url,'Candidatura o grupo del registro consultado')}])
        if organization:
            self.add(person,'afiliaciones.json',[{'organization':organization,'name':group,'period':period,'kind':'association','source':ref(url,'Candidatura o formación indicada por la fuente institucional'),'note':'Relación electoral o parlamentaria documentada; no acredita por sí sola militancia.'}])
    def photo(self,person,image,source,credit):
        if image and 'nofoto' not in image and not (self.people[person][0]/'retrato.json').exists():self.photos[person]=(image,source,credit)
    def save(self):
        for person in self.used:
            folder,meta=self.people[person];c.write(folder/'ficha.json',meta)
        for (person,file),rows in self.files.items():c.write(self.people[person][0]/file,rows)
        def portrait(item):
            person,(url,source,credit)=item;folder=self.people[person][0]
            try:
                raw=base64.b64decode(url.split(',',1)[1]) if url.startswith('data:image') else c.fetch(url)
                from PIL import Image
                import io
                im=Image.open(io.BytesIO(raw));im.verify()
                suffix='png' if raw.startswith(b'\x89PNG') else 'jpg' if raw.startswith(b'\xff\xd8') else pathlib.Path(url.split('?')[0]).suffix.lstrip('.')
                file='retrato-atlantico.'+suffix; (folder/file).write_bytes(raw)
                c.write(folder/'retrato.json',{'file':file,'credit':credit,'source':source,'original':url if not url.startswith('data:') else source,'context':'Retrato de la ficha institucional consultada; no se atribuye una fecha de toma no publicada.'})
                return person
            except Exception as e:self.errors.append({'person':person,'source':source,'error':str(e)});return None
        with concurrent.futures.ThreadPoolExecutor(6) as pool:count=sum(bool(r) for r in pool.map(portrait,self.photos.items()))
        print('Personas',len(self.used),'nuevas',len(self.new),'retratos nuevos',count,'errores',len(self.errors),flush=True)
        portraitFiles=[person for person in self.used if str(load(self.people[person][0]/'retrato.json',{}).get('file','')).startswith('retrato-atlantico.')]
        c.write(ROOT/'Políticos/revisiones/2026-10-12-atlantico/informe.json',{'checkedAt':CHECKED,'people':len(self.used),'newPeople':len(self.new),'portraitsFromThisImport':len(portraitFiles),'aliases':self.aliases,'portraitErrors':self.errors})

cat=Catalog()
# Nombres desarrollados por la ficha de alto cargo; se conserva el ID previo.
cat.alias('Alejandro Narvay Quintero Castañeda','Narvay Quintero Castañeda','https://www.gobiernodecanarias.org/organigrama/ficha-altos-cargos/?ou=42084')
def term(name,region,role,source,start=None,end=None,**extra):
    person=cat.get(name,region,source,role)
    if extra.pop('preferredName',False) or extra.get('observedAt')==CHECKED:cat.prefer(person,name,source)
    return {'person':person,'name':cat.people[person][1]['fullName'],'role':role,'source':source,'start':start,'end':end,**extra}
def organization(group):
    key=norm(group)
    for pattern,id in [(r'\bpartido popular\b','pp'),(r'^gp popular$','pp'),(r'\bpartido socialista obrero espanol\b','psoe'),(r'^gp socialista canario$','psoe'),(r'^psoe$','psoe'),(r'^vox$','vox'),(r'^coalicion canaria$','cc')]:
        if re.search(pattern,key):return id
    return None
def sourcepath(region,file):return ROOT/'Gobiernos/Autonomías'/region/'fuentes'/file
def saveperiod(region,section,period):
    c.write(ROOT/'Gobiernos/Autonomías'/region/section/f"{period['start'][:4]} {period['label']}"/'composicion.json',period)
    if section=='Gobierno' and period.get('currentOnly'):
        c.write(sourcepath(region,'gobierno-vigente.json'),{'checkedAt':CHECKED,'members':period['terms']})

def canarias():
    region='Canarias';profiles=load(CACHE/'canarias-perfiles.json')
    for old,new in [('Antonio A. Castro Cordobez','Antonio Ángel Castro Córdobez'),('Antonio Castro Cordobez','Antonio Ángel Castro Córdobez'),('F. de Borja Benítez de Lugo Massieu','Francisco de Borja Benítez de Lugo Massieu'),('Ana M.ª Oramas González-Moro','Ana María Oramas González-Moro'),('Manuel Hermoso Rojas','Manuel Antonio Hermoso Rojas'),('Lorenzo Olarte Cullen','Lorenzo Olarte Cullén'),('Blas Trujillo Oramas','Blas Gabriel Trujillo Oramas')]:
        cat.alias(old,new,'https://www.parcan.es/composicion/diputados/')
    apis={i:load(CACHE/f'pleno-{i}.json') for i in range(4,12)}
    api={str(r['miembro']).zfill(5):r for rows in apis.values() for r in rows}
    # La misma ficha numérica permite recuperar un nombre desarrollado en la API.
    expanded={}
    for p in profiles:
        a=api.get(p['key']);name=' '.join(a[k] for k in ['nombre','apellido1','apellido2'] if a.get(k)) if a else p['name']
        name=name.replace('M.ª','María')
        expanded[p['key']]=name
        cat.get(name,'canarias',p['source'],'Miembro del Parlamento de Canarias')
        if p['name']!=name:cat.alias(p['name'],name,p['source'])
    # Variantes acreditadas por nombramientos y fichas individuales, no coincidencias parciales.
    aliases={'Manuel Hermoso Rojas':'Manuel Antonio Hermoso Rojas','Fernando Fernández Martín':'Fernando Manuel Fernández Martín','Lorenzo Olarte Cullen':'Lorenzo Olarte Cullén','Antonio Castro Cordobez':'Antonio Ángel Castro Córdobez','Antonio A. Castro Cordobez':'Antonio Ángel Castro Córdobez','Blas Trujillo Oramas':'Blas Gabriel Trujillo Oramas','Narvay Quintero Castañeda':'Alejandro Narvay Quintero Castañeda','María Dolores Palliser García':'María Dolores Palliser Díez','Padro Cabrera Hernández':'Pedro Cabrera Hernández','Julio Pérez Hernández':'Julio Manuel Pérez Hernández'}
    for old,new in aliases.items():
        cat.get(new,'canarias','https://www.gobiernodecanarias.org/igualdad/documentos/estadisticas/Esta_Gobcan_1983-2019.pdf','Trayectoria institucional de Canarias')
        cat.alias(old,new,'https://www.gobiernodecanarias.org/igualdad/documentos/estadisticas/Esta_Gobcan_1983-2019.pdf')
    correction={'Padro Cabrera Hernández':'https://www.gobiernodecanarias.org/boc/1991/055/003.html','María Dolores Palliser García':'https://www.gobiernodecanarias.org/igualdad/documentos/estadisticas/Esta_Gobcan_1983-2019.pdf'}
    starts=['1983-05-08','1987-06-10','1991-05-26','1995-05-28','1999-06-13','2003-05-25','2007-05-27','2011-05-22','2015-05-24','2019-05-26','2023-05-28']
    for i,start in enumerate(starts,1):
        label=f'Legislatura {ROMANS[i-1]}';url=f'https://www.parcan.es/composicion/diputados/busqueda_alfabetico/{i}/'
        period={'id':f'canarias-parlamento-{i}','label':label,'start':start,'end':starts[i] if i<11 else None,'checkedAt':CHECKED,'source':url,'capacity':60 if i<10 else 70,'currentOnly':i==11,'nominalOnly':i!=11,'note':'Composición vigente consultada; las adscripciones corresponden a esta consulta.' if i==11 else 'Marco por fechas electorales, no por altas individuales. El archivo nominal incluye los relevos publicados; no reconstruye una ocupación diaria ni el asiento físico.','records':[],'board':[],'groups':[]}
        groups=collections.defaultdict(list)
        if i<=3:
            rows=load(CACHE/f'parl{i}-grupos.json');pdf=f'https://www.gobiernodecanarias.org/igualdad/documentos/estadisticas/Esta_Parcan_Legislatura{i}_{start[:4]}-{starts[i][:4]}.pdf';period['source']=pdf
            for g in rows:
                group=re.sub(r'\s+\d+\s+escaños?.*','',g['group'])
                if i==1 and group in ['Unión del Pueblo Canario-','Asamblea Canaria-Izquierda Canaria']:group='Unión del Pueblo Canario–Asamblea Canaria–Izquierda Canaria'
                for r in g['members']:
                    raw=r['name'];name=re.sub(r'\s*\([^)]*\)','',raw).strip();name=aliases.get(name,name)
                    t=term(name,'canarias','Miembro del Parlamento de Canarias',pdf,period=label, endBasis='Intervalo individual no publicado en el cuadro nominal.')
                    period['records'].append(t)
                    if 'hasta' not in raw:groups[group].append(t['person'])
                    cat.mandate(t['person'],'Parlamento de Canarias',f'{label} · {start[:4]}–{starts[i][:4]}',pdf)
                    cat.group(t['person'],f'Canarias · clasificación del informe ICI: {group}',label,pdf,organization(group))
                    if raw in correction:cat.add(t['person'],'fuentes.json',[ref(correction[raw],'Contraste de errata nominal del informe')])
            period['archivedComposition']={'source':pdf,'checkedAt':CHECKED,'note':'Cuadro nominal del Instituto Canario de Igualdad. Se excluyen del esquema los diputados con baja expresamente anotada; se conservan en el archivo. La clasificación partidista del informe no se equipara a una adscripción diaria a un grupo parlamentario.','groups':[{'name':g,'source':pdf,'members':ids}for g,ids in groups.items()]}
        else:
            ps=[p for p in profiles if p['legislature']==i];bykey={p['key']:p for p in ps}
            for p in ps:
                t=term(expanded[p['key']],'canarias','Miembro del Parlamento de Canarias',p['source'],p['start'],p['endInSource'],preferredName=True,constituency=p['constituency'],**({'formation':api[p['key']]['grupo'],'formationLabel':'Formación indicada por la Cámara'}if p['key'] in api else {}))
                period['records'].append(t)
                date=p['start'] or 'Alta no indicada';end=p['endInSource'] or 'baja no indicada';span=f'{label} · {date} — {end}'
                cat.mandate(t['person'],f"Parlamento de Canarias · {p['constituency'] or 'circunscripción no indicada'}",span,p['source'])
                if p['group']:cat.group(t['person'],f"Canarias · {p['group']}",f'{label} · adscripción del registro consultado',p['source'],organization(api.get(p['key'],{}).get('grupo',p['group'])))
                cat.photo(t['person'],p['image'],p['source'],'Parlamento de Canarias')
                if p.get('education'):
                    cat.add(t['person'],'formacion.json',p['education']);cat.add(t['person'],'fuentes-formacion.json',[ref(p['biographySource'],'Parlamento de Canarias · formación')])
            roster=[]
            for a in apis[i]:
                p=bykey[str(a['miembro']).zfill(5)];t=next(t for t in period['records'] if t['source']==p['source'])
                group=p['group'] or 'Sin adscripción';groups[group].append(t['person']);roster.append(t)
            if i==11:
                period['records']=roster
                period['groups']=[{'name':g,'source':url,'members':[t for t in roster if t['person']in ids]}for g,ids in groups.items()]
                for t in roster:cat.active(t['person'],t['source'])
            else:period['archivedComposition']={'source':url,'checkedAt':CHECKED,'note':'Última relación nominal conservada por la API del Parlamento, agrupada según las fichas publicadas. Incluye únicamente los nombres que el Pleno archivado identifica; las posiciones no identificadas quedan sin atribuir. No es una reconstrucción diaria de la legislatura.','groups':[{'name':g,'source':url,'members':ids} for g,ids in groups.items()]}
            mesaSource=f'https://www.parcan.es/api/composicion/mesa/{i}/?format=json'
            mesa=json.loads(c.fetch(mesaSource))
            board=[]
            for a in mesa:
                name=' '.join(a[k] for k in ['nombre','apellido1','apellido2'] if a.get(k)).replace('M.ª','María')
                p=next((r for r in ps if norm(expanded[r['key']])==norm(name)),None)
                if not p:continue
                role=p['role'] if p['role'] not in ['Diputado','Diputada'] else 'Miembro de la Mesa del Parlamento'
                t=term(expanded[p['key']],'canarias',role,p['source'],period=f'Mesa de la legislatura {ROMANS[i-1]} · registro consultado',**({'observedAt':CHECKED}if i==11 else {}));board.append(t)
                cat.office(t['person'],'Canarias · '+role,t['period'],p['source'])
            if i==11:period['board']=board
            else:
                period['archiveBoard']=board
                period['archiveBoardNote']='Miembros de la Mesa identificados por la API institucional. Se conserva la denominación de la ficha cuando publica el cargo; no se asignan fechas individuales ni puestos no especificados.'
            c.write(sourcepath(region,f'mesa-{i}.json'),mesa)
            def board_order(t):
                role=t['role'].lower()
                if 'president' in role and 'vice' not in role:return 0
                if 'vicepresident' in role:return 1 if 'primer' in role else 2
                if 'secretari' in role:return 3 if 'primer' in role else 4
                return 5
            board.sort(key=board_order)
        saveperiod(region,'Parlamento',period)
    c.write(sourcepath(region,'fichas-parlamento.json'),profiles)
    c.write(sourcepath(region,'plenos-archivados.json'),apis)
    for i in range(1,4):
        c.write(sourcepath(region,f'cuadro-parlamento-{i}.json'),load(CACHE/f'parl{i}-grupos.json'))
    governments(region,'canarias',load(CACHE/'canarias-presidencias.json'))

def governments(region,id,rows):
    for i,r in enumerate(rows):
        start=r['date'];end=rows[i+1]['date'] if i+1<len(rows) else None
        name=r['name'];name={'Mustafa Hamed Moh-Mohamed':'Mustafa Hamed Moh Mohamed'}.get(name,name)
        t=term(name,id,f'Presidencia de {region}',r['source'],start,end,level='president',endBasis='Siguiente nombramiento documentado en el BOE; no fecha de retirada personal.')
        label=f"Gobierno {start[:4]}"+(f' · {start[5:]}' if sum(x['date'][:4]==start[:4] for x in rows)>1 else '')
        p={'id':f'{id}-gobierno-{start}','label':label,'name':f"{region} · {name}",'start':start,'end':end,'checkedAt':CHECKED,'source':r['source'],'terms':[t],'incidents':['El eje utiliza las fechas de los reales decretos de nombramiento. Elección, publicación y toma de posesión pueden ser posteriores o anteriores; no se equiparan automáticamente.'],'archiveTerms':[]}
        cat.office(t['person'],f'Presidencia de {region}',f'{start} — {end or "actualidad"} · fechas de nombramiento',r['source'])
        if id=='canarias':
            add_canary_cabinet(p)
        elif i+1==len(rows):
            current_city_cabinet(p,region,id)
        if id in ['ceuta','melilla']:
            for r in load(CACHE/'consejerias-ciudades.json',[]):
                if r['region']!=region or r['date']<start or (end and r['date']>=end):continue
                name=title(r['name']);name={'Dunia Almansouri Umpierrez':'Dunia Al-Mansouri Umpierrez'}.get(name,name)
                role=r['role'].strip().rstrip(',').replace('nuev as','nuevas').replace('porta voz','portavoz').replace('fomento ,','fomento,')
                t=term(name,id,role,r['source'],period=r.get('documentedPeriod','Nombramiento · '+r['date']+' · cese individual no reconstruido'),level='minister')
                p['archiveTerms'].append(t);cat.office(t['person'],region+' · '+role,t['period'],r['source'])
            if p['archiveTerms']:p['incidents'].append('Se conservan los nombramientos iniciales localizados en los boletines oficiales. No se proyectan como una composición simultánea durante toda la etapa; los ceses y relevos no fechados requieren contraste individual.')
        if end is None:cat.active(t['person'],r['source'])
        if not p['archiveTerms'] and len(p['terms'])==1:p['incidents'].append('Las consejerías de esta etapa todavía requieren contraste de sus nombramientos y relevos; el organigrama identifica únicamente la presidencia documentada.')
        saveperiod(region,'Gobierno',p)
    c.write(sourcepath(region,'nombramientos-presidencias.json'),[{k:v for k,v in r.items() if k!='text'} for r in rows])

def add_canary_cabinet(p):
    start=p['start']; year=int(start[:4]);source='https://www.gobiernodecanarias.org/igualdad/documentos/estadisticas/Esta_Gobcan_1983-2019.pdf'
    if year<2019:
        leg=1 if year<=1985 else 2 if year<=1988 else 3 if year<=1993 else 4 if year==1995 else 5 if year==1999 else 6 if year==2003 else 7 if year==2007 else 8 if year==2011 else 9
        current=0
        for row in load(CACHE/'gobierno.json'):
            left,role,names=row['cells']
            m=re.match(r'([IVX]+) LEGISLATURA',role)
            if m:current=ROMANS.index(m[1])+1
            if current!=leg or not re.match(r'^(?:\d+\.?\s*)?Consejería',role):continue
            role=re.sub(r'^\d+\.?\s*','',role);names=re.sub(r'^\d+\.?\s*','',names)
            for name in names.split('/'):
                name=re.sub(r'\s*\(supr\)','',name).strip()
                if not name:continue
                # La transcripción conserva abreviaturas de la fuente cuando no hay contraste nominal.
                t=term(name,'canarias',role,source,period=f'Legislatura {ROMANS[leg-1]} · intervalo individual no precisado',level='minister')
                p['archiveTerms'].append(t);cat.office(t['person'],f'Canarias · {role}',t['period'],source)
        p['incidents'].append('Las consejerías proceden del cuadro histórico del Instituto Canario de Igualdad. Las barras separan titulares sucesivos sin fechar individualmente sus relevos; se conservan como archivo, no como un gabinete simultáneo. El cuadro incluye cargos suprimidos y etapas provisionales.')
    elif year==2019:
        source='https://www.gobiernodecanarias.org/boc/2019/137/002.html';page=c.soup(source)
        for node in page.select('p'):
            line=node.get_text(' ',strip=True)
            m=re.match(r'D(?:ña)?\.\s+(.+?),\s+(Consejer[oa] .+)\.',line)
            if not m:continue
            t=term(m[1],'canarias',m[2],source,period='Nombramiento inicial · 17 de julio de 2019',level='minister');p['archiveTerms'].append(t);cat.office(t['person'],'Canarias · '+t['role'],t['period'],source)
        assert len(p['archiveTerms'])==10,len(p['archiveTerms'])
        p['incidents'].append('Se documentan los diez nombramientos iniciales del 17 de julio de 2019. La lista no se proyecta sobre todo el mandato; los relevos posteriores requieren sus disposiciones individuales.')
    else:
        p['currentOnly']=True;p['terms'][0]['observedAt']=CHECKED
        for row in load(CACHE/'canarias-gobierno-actual.json'):
            heading=next((x for x in row['text'] if x.startswith(('Excmo.','Excma.'))),None)
            if not heading:continue
            name=re.sub(r'^.*?D(?:ña)?\.\s*','',heading)
            if name==p['terms'][0]['name']:continue
            role=row['text'][row['text'].index(heading)-1]
            role=('Vicepresidencia y '+role) if name=='Manuel Domínguez González' else role
            t=term(name,'canarias',role,row['source'],observedAt=CHECKED,period='Composición vigente · '+CHECKED,level='vice' if name=='Manuel Domínguez González' else 'minister')
            p['terms'].append(t);cat.office(t['person'],'Canarias · '+role,t['period'],t['source']);cat.active(t['person'],t['source'])
            if row['images']:cat.photo(t['person'],row['images'][0]['src'],t['source'],'Gobierno de Canarias')
        president=next(r for r in load(CACHE/'canarias-gobierno-actual.json') if r['source'].endswith('42091'))
        cat.photo(p['terms'][0]['person'],president['images'][0]['src'],president['source'],'Gobierno de Canarias')
        assert len(p['terms'])==13,len(p['terms'])
        p['incidents'].append('Instantánea de las fichas de altos cargos, consultada el 12 de octubre de 2026; se conserva por separado de los nombramientos iniciales de 2023.')

def current_city_cabinet(p,region,id):
    p['currentOnly']=True;p['terms'][0]['observedAt']=CHECKED
    rows=load(CACHE/f'{id}-gobierno.json')
    if id=='ceuta':
        roles=['Vicepresidencia primera · Medio Ambiente, Servicios Urbanos y Vivienda','Vicepresidencia segunda · Hacienda, Transición Económica y Transformación Digital','Educación, Cultura y Juventud','Presidencia y Gobernación','Sanidad y Servicios Sociales','Comercio, Turismo, Empleo y Deporte','Urbanismo y Transportes']
        for r,role in zip(rows,roles):r['role']=role
        cat.photo(p['terms'][0]['person'],'https://www.ceuta.es/gobiernodeceuta/images/stories/demo/Presidente.jpg','https://www.ceuta.es/gobiernodeceuta/index.php/el-presidente','Ciudad Autónoma de Ceuta')
    else:
        original=rows
        rows=[r.copy() for r in rows if not any(n in r['name'] for n in ['Conesa','Quevedo']) and 'Presidente'!=r['role']]
        for r in rows:
            if 'Miguel Marín' in r['name']:
                r['role']='Vicepresidencia primera y Consejería de Economía, Comercio, Innovación Tecnológica, Turismo y Fomento';r['source']='https://bomemelilla.es/bome/descargar/BOME-BX-2023-45.pdf'
            if 'Daniel Ventura' in r['name']:
                r['role']='Vicepresidencia tercera y Consejería de Medio Ambiente y Naturaleza';r['source']='https://bomemelilla.es/bome/BOME-BX-2024-22/articulo/75'
            if 'Fadela Mohatar' in r['name']:
                r['role']='Vicepresidencia segunda, Portavocía y Consejería de Cultura, Patrimonio Cultural y del Mayor';r['source']='https://www.melilla.es/melillaportal/RecursosWeb/DOCUMENTOS/1/2_28868_1.pdf'
            if 'Randa Mohamed' in r['name']:r['role']='Consejería de Políticas Sociales y Salud Pública'
            if 'Miguel Ángel Fernández' in r['name']:r['role']='Consejería de Educación, Juventud y Deportes'
        rows.append({'name':'José Bienvenido Ronda Inglés','role':'Consejería de Seguridad Ciudadana','source':'https://bomemelilla.es/bome/BOME-BX-2024-22/articulo/76'})
        rows.append({'name':'Jesús Manuel Romero Imbroda','role':'Fomento Universitario e Investigación','source':'https://bomemelilla.es/bome/BOME-BX-2026-34/articulo/86','image':'https://www.melilla.es/melillaportal/RecursosWeb/IMAGENES/1/1_38371_1.jpg'})
        for r in original:
            if r['role']=='Presidente':continue
            name=re.sub(r'^Dª\.\s*','',r['name']);name={'Miguel Ángel Fernández Bonnemaisón':'Miguel Ángel Fernández Bonnemaison'}.get(name,name)
            source='https://bomemelilla.es/bome/descargar/BOME-BX-2023-45.pdf'
            t=term(name,id,r['role'],source,period='Nombramiento inicial · 10 de julio de 2023',level='minister');p['archiveTerms'].append(t);cat.office(t['person'],region+' · '+r['role'],t['period'],source)
        p['incidents'].append('El directorio general conserva fichas de 2023. El decreto 1056 de 25 de octubre de 2023 cesó a Manuel Ángel Quevedo y nombró vicepresidenta segunda a Fadela Mohatar. Los decretos 74 y 75 de abril de 2024 intercambiaron las competencias de Daniel Ventura y José Ronda. Los cargos vigentes se contrastan en los decretos, sin reutilizar el organigrama inicial.')
        p['incidents'].append('El decreto 302 de 24 de julio de 2026 cesó a Daniel Conesa en Hacienda. El nuevo nombramiento de Jesús Manuel Romero se contrasta en el decreto 305. No se atribuye un sustituto de Hacienda sin nombramiento documentado.')
    for r in rows:
        name=re.sub(r'^Dª\.\s*','',r['name']);name={'Miguel Ángel Fernández Bonnemaisón':'Miguel Ángel Fernández Bonnemaison'}.get(name,name)
        role=r['role'];role=role if 'Consejer' in role or 'Vicepresidencia' in role else 'Consejería de '+role
        t=term(name,id,role,r['source'],observedAt=CHECKED,period='Composición vigente · '+CHECKED,level='vice' if role.startswith('Vicepresid') else 'minister')
        p['terms'].append(t);cat.office(t['person'],region+' · '+role,t['period'],r['source']);cat.active(t['person'],r['source'])
        cat.photo(t['person'],r.get('image'),r['source'],'Ciudad Autónoma de '+region)
        if id=='ceuta':
            first=r['text'][0];education=[]
            if name=='Alejandro Ramírez Hurtado':education=['Administración y Dirección de Empresas; Ciencias Empresariales; estudios de posgrado y máster en Dirección y Gestión de Empresas.']
            elif name=='Kissy Chandiramani Ramesh':education=['Derecho, Facultad San Pablo CEU de Madrid (1997–2001).','Derecho de la Unión Europea, Universidad Panthéon-Sorbonne de París (2001–2002).','Formación de posgrado en dirección, mediación civil y mercantil y marketing turístico.']
            elif name=='Pilar Orozco Valverde':education=['Diplomatura en Turismo, Universidad de Sevilla (2008–2012).','Grado Superior de Gestión Comercial y Marketing, IES Puertas del Campo.']
            elif name=='Alberto Ramón Gaitán Rodríguez':education=['Derecho y Ciencias Económicas y Empresariales, Universidad Pontificia de Comillas.']
            elif name=='Nabila Benzina Pavón':education=['Grado en Educación Social, Universidad de Granada (2018–2022).','Técnico Superior en Administración, IES Puertas del Campo.']
            elif name=='Rafael Martínez Peñalver Mateos':education=['Ingeniería de Caminos, Canales y Puertos, Universidad de Granada.']
            if education:cat.add(t['person'],'formacion.json',education);cat.add(t['person'],'fuentes-formacion.json',[ref(r['source'],'Ciudad de Ceuta · formación')])
            year=re.search(r'Nacid[oa] en (\d{4})',first)
            if year:
                folder=cat.people[t['person']][0];personal=load(folder/'datos-personales.json',{})
                if not personal.get('birthDate'):personal['birthYear']=int(year[1]);personal['personalSources']=union(personal.get('personalSources',[]),[ref(r['source'],'Ciudad de Ceuta · datos biográficos')]);c.write(folder/'datos-personales.json',personal)
    assert len(p['terms'])==(8 if id=='ceuta' else 9),(id,len(p['terms']))
    if id=='melilla':
        order={'primera':1,'segunda':2,'tercera':3}
        p['terms'].sort(key=lambda t:0 if t['level']=='president' else next((n for word,n in order.items()if word in t['role']),4)if t['level']=='vice' else 4)

def cities():
    dates=['1995-05-28','1999-06-13','2003-05-25','2007-05-27','2011-05-22','2015-05-24','2019-05-26','2023-05-28']
    ceutaSource='https://www.ceuta.es/gobiernodeceuta/index.php/el-gobierno/la-asamblea'
    melillaSource='https://sede.melilla.es/sta/CarpetaPublic/doEvent?APP_CODE=STA&PAGE_CODE=PTS2_MIEMBROS'
    ceutaGroups={
      'Partido Popular':['Juan Jesús Vivas Lara','Alejandro Ramírez Hurtado','Kissy Chandiramani Ramesh','Alberto Ramón Gaitán Rodríguez','Pilar Orozco Valverde','Rafael Martínez Peñalver Mateos','Nabila Benzina Pavón','Nicola Cecchi Bissoni','Mina Mohamed Laarbi'],
      'Partido Socialista Obrero Español':['Hanan Ahmed Ouahid','Sebastián Guerrero Martín','Melchor León Encomienda'],
      'Vox':['Juan Sergio Redondo Pacheco','Carlos Francisco Verdejo Ferrer','Francisco José Ruiz Enríquez','Ana Belén Cifuentes Cánovas'],
      'Movimiento por la Dignidad y la Ciudadanía':['Fátima Hamed Hossain','Nadia Mohamed Abdel Lah','Mohamed Mohamed Ali Duas'],
      'Ceuta Ya!':['Mohamed Mustafa Ahmed','Julia Alejandra Ferreras Guerra'],
      'No adscritos':['Mohamed Navil Rahal Abdelkrim','Fidda Mustafa Hossain','María Teresa López Álvarez','Hikma Mohamed Mohamed']}
    for region,id,url in [('Ceuta','ceuta',ceutaSource),('Melilla','melilla',melillaSource)]:
        for index,start in enumerate(dates):
            year=int(start[:4]);label=f'Legislatura {ROMANS[index]}'
            p={'id':f'{id}-asamblea-{year}','label':label,'start':start,'end':dates[index+1] if index<7 else None,'checkedAt':CHECKED,'source':url,'currentOnly':year==2023,'capacity':25,'nominalOnly':year!=2023,'note':'Miembros vigentes según el registro institucional consultado; no se proyectan sobre el inicio de la legislatura.','records':[],'board':[],'groups':[]}
            gs=collections.defaultdict(list)
            if year<2023:
                elects=load(CACHE/f'{id}-interior-{year}.json');p['source']=elects[0]['source'];p['note']='Relación de electos de los comicios, no lista de todos los relevos durante el mandato. El marco se delimita por fechas electorales; no atribuye altas ni bajas individuales.'
                c.write(sourcepath(region,f'electos-{year}.json'),elects)
                for r in elects:
                    name=title(r['name']);t=term(name,id,f'Miembro electo de la Asamblea de {region}',r['source'],period=f'Electo · {start}',constituency=region,formation=r['formation']['name'])
                    p['records'].append(t);gs[r['formation']['name']].append(t)
                    cat.mandate(t['person'],f'Electo a la Asamblea de {region}',start,r['source']);cat.group(t['person'],f"{region} · candidatura {r['formation']['name']}",f'Elecciones · {start}',r['source'],organization(r['formation']['name']))
                    cat.add(t['person'],'fuentes.json',[{'label':'Copia verificable de los microdatos de Interior · archivo público','url':r['mirror'],'kind':'encyclopedic'}])
                p['archivedComposition']={'source':p['source'],'checkedAt':CHECKED,'note':'Los 25 electos proclamados en los datos del Ministerio del Interior. La copia consultada y su huella Git se conservan en las fuentes. Los cambios posteriores de adscripción o titular no se deducen de los resultados electorales.','groups':[{'name':g,'source':p['source'],'members':[t['person']for t in ts]}for g,ts in gs.items()]}
            else:
                if id=='ceuta':entries=[(name,g) for g,names in ceutaGroups.items()for name in names]
                else:
                    entries=[]
                    from bs4 import BeautifulSoup
                    for r in load(CACHE/'melilla-miembros.json'):
                        text=BeautifulSoup(r['nameInSource'],'html.parser').get_text(' ',strip=True)
                        if ',' not in text:continue
                        surname,first=text.split(',',1);first=re.split(r'\s+-\s+|\s+\(',first)[0].strip();name=first+' '+surname.strip()
                        group=BeautifulSoup(r['groupText'],'html.parser').get_text(' ',strip=True)
                        group=group[group.find('Grupo Político'):] if 'Grupo Político' in group else group
                        entries.append((name,group))
                assert len(entries)==25,(id,len(entries))
                for name,g in entries:
                    t=term(name,id,f'Miembro de la Asamblea de {region}',url,observedAt=CHECKED,constituency=region,formation=g,formationLabel='Grupo político',period='Composición vigente · '+CHECKED);p['records'].append(t);gs[g].append(t)
                    cat.mandate(t['person'],f'Asamblea de {region}',f'{label} · composición consultada {CHECKED}',url);cat.group(t['person'],f'{region} · {g}',f'Consulta · {CHECKED}',url,organization(g));cat.active(t['person'],url)
                p['groups']=[{'name':g,'source':url,'members':ts}for g,ts in gs.items()]
                board=[('Juan Jesús Vivas Lara','Presidencia'),('Melchor León Encomienda','Vicepresidencia primera'),('Fátima Hamed Hossain','Vicepresidencia segunda')] if id=='ceuta' else [('Juan José Imbroda Ortiz','Presidencia'),('María José Aguilar Silvetti','Vicepresidencia primera'),('Rachid Bussian Mohamed','Vicepresidencia segunda')]
                for name,role in board:
                    t=term(name,id,role+' de la Asamblea',url,observedAt=CHECKED,period='Mesa vigente · '+CHECKED);p['board'].append(t);cat.office(t['person'],region+' · '+t['role'],t['period'],url)
            saveperiod(region,'Parlamento',p)
        governments(region,id,load(CACHE/f'{id}-presidencias.json'))
        c.write(sourcepath(region,'miembros-vigentes.json'),p)

if __name__=='__main__':
    canarias();cities()
    for r in load(CACHE/'melilla-retratos-oficiales.json',[]):
        name=r['caption'].removeprefix('Foto ')
        # La página de Presidencia desarrolla el nombre de Marta; la foto usa su forma abreviada.
        name={'Marta Fernández De Castro Ruiz':'Marta Victoria Fernández de Castro Ruiz'}.get(name,name)
        matches=cat.names.get(norm(name),set())
        if len(matches)==1:
            person=next(iter(matches));cat.photo(person,r['image'],r['source'],'Ciudad Autónoma de Melilla');cat.add(person,'fuentes.json',[ref(r['source'],'Ciudad de Melilla · retrato del titular')])
    for r in load(sourcepath('Ceuta','retratos-complementarios.json'),[]):
        matches=cat.names.get(norm(r['name']),set())
        if len(matches)==1:
            person=next(iter(matches));cat.photo(person,r['image'],r['source'],r['credit']);cat.add(person,'fuentes.json',[ref(r['source'],'Retrato identificado por la organización política')])
    cat.save()
    for region in ['Ceuta','Melilla']:
        c.write(sourcepath(region,'consejerias-historicas.json'),[r for r in load(CACHE/'consejerias-ciudades.json',[]) if r['region']==region])
