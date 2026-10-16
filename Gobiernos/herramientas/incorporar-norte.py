"""Integra las fuentes contrastadas del norte sin sustituir identidades ni inventar intervalos.

Ejecutar después de consultar-norte.py, documentar-gobiernos-norte.py,
preparar-datos-norte.py y transcribir-parlamento-navarra.py. Originales en test-results.
--plan valida todas las composiciones sin escribir fichas ni descargar retratos.
"""
import collections, datetime, importlib.util, pathlib, re, sys

s = importlib.util.spec_from_file_location('catalog', pathlib.Path(__file__).with_name('catalogo-regional.py'))
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
c = m.c; cat = m.Catalog(); CACHE = c.CACHE; CHECKED = c.CHECKED
ROMANS = m.n.ROMANS
outputs = []
BASQUE_LABELS={'GP NV':'Nacionalistas Vascos · EAJ-PNV','GP EA-NV':'Euzko Abertzaleak-Nacionalistas Vascos · EAJ-PNV','GP SV':'Socialistas Vascos','GP SV-ES':'Socialistas Vascos-Euskal Sozialistak',
              'GP PV':'Popular Vasco','GP PV-ETP':'Popular Vasco-Euskal Talde Popularra','GP PP':'Partido Popular','GP HB':'Herri Batasuna','GP EH':'Euskal Herritarrok','GP EE':'Euskadiko Ezkerra',
              'GP EA':'Eusko Alkartasuna','GP EP':'Elkarrekin Podemos','GP EP-IU':'Elkarrekin Podemos-Izquierda Unida','GP EH Bildu':'EH Bildu','GP IU':'Izquierda Unida'}

def read(name): return m.load(CACHE / (name + '.json'))
def source_dir(region): return pathlib.Path('Gobiernos/Autonomías') / m.REGIONS[region]
def canonical(id): return cat.people[id][1]['fullName']
def person(name, region, source, role): return cat.resolve(name, region, source, role)
def term(id, role, source, start=None, end=None, **extra):
    return dict(person=id, name=canonical(id), role=role, source=source, start=start, end=end, **extra)
def interval(start, end): return (start or 'Inicio no precisado') + (' – ' + end if end else '')
def stage(region, category, data):
    folder = f"{data['start'][:4]} {data['label']}"
    outputs.append((source_dir(region) / category / folder / 'composicion.json', data))
def grouping(rows, key='formationLabel'):
    groups = collections.defaultdict(list)
    for row in rows: groups[row.get(key) or 'Adscripción no publicada'].append(row)
    return [dict(name=name, source=members[0]['source'], members=members) for name,members in groups.items()]
def association(id, region, group, period, source):
    # Solo grupos explícitamente identificados: el resto conserva su nombre sin inferir militancia.
    org = {'GP NV':'pnv','GP EA-NV':'pnv','GP PV':'pp','GP PV-ETP':'pp','GP SV':'psoe','GP SV-ES':'psoe','GP EH Bildu':'eh-bildu','GP Mixto-Vox':'vox',
           'UPN':'upn','PSN-PSOE':'psoe','PSOE':'psoe','PP':'pp','PPN':'pp','EH Bildu':'eh-bildu',
           'G.P. Unión del Pueblo Navarro':'upn','G.P. Partido Socialista de Navarra':'psoe',
           'G.P. Partido Popular de Navarra':'pp','G.P. EH Bildu Nafarroa':'eh-bildu'}.get(group)
    cat.group(id,region,group,period,source,org)

def profiles():
    basque = {}
    for row in read('pais-vasco-perfiles'):
        assert not row.get('error'),row
        id = person(row['name'],'pais-vasco',row['source'],'Parlamento Vasco')
        basque[row['key']] = id
        cat.photo(id,row.get('image'),row['source'],'Parlamento Vasco · retrato de la ficha institucional')
        for label,text in row.get('details',{}).items():
            if text:
                cat.add(id,'formacion.json',[label + ': ' + text])
                cat.add(id,'fuentes-formacion.json',[m.ref(row['source'],'Formación y profesión · Parlamento Vasco')])
    navarre = {}
    for row in read('navarra-perfiles-actuales'):
        id = person(row['name'],'navarra',row['source'],'Parlamento de Navarra');navarre[row['source']]=id
        cat.photo(id,row.get('image'),row['source'],'Parlamento de Navarra · retrato de la ficha institucional')
        cat.active(id,row['source'])
        for r in row['roles']:
            if r['organ']=='Pleno' or 'Mesa' in r['organ']:
                cat.event(id,'mandatos-autonomias.json','navarra',r['role']+' · '+r['organ'],interval(r['start'],r['end']),row['source'])
            elif r['organ'].startswith('G.P.') or r['organ']=='No adscrita':
                association(id,'navarra',r['organ'],interval(r['start'],r['end']),row['source'])
        for text in row['education']:
            cat.add(id,'formacion.json',[text])
            cat.add(id,'fuentes-formacion.json',[m.ref(row['source'],'Formación · Parlamento de Navarra')])
    return basque,navarre

def basque_parliaments(ids):
    lists=read('pais-vasco-listas');current=read('pais-vasco-actual')
    inconsistencies=[]
    for li in lists:
        number=li['legislature'];raw=li['records'];records=[];board=[]
        for r in raw:
            id=ids[r['key']];p=interval(r['start'],r['end'])
            if r['start']and r['end']and r['start']>r['end']:p='Intervalo inconsistente en el origen: '+p
            cat.event(id,'mandatos-autonomias.json','pais-vasco','Parlamento Vasco · Legislatura '+ROMANS[number-1],p,r['source'])
            if r['group']:association(id,'pais-vasco',r['group'],p,r['listSource'])
            if r['start'] and r['end'] and r['start']>r['end']:
                # Se conserva el error literal en la revisión; no se inventa el año correcto.
                outputs.append((source_dir('pais-vasco')/'fuentes/intervalo-inconsistente.json',dict(**r,basis='Fin anterior al inicio en el origen. Este mandato se conserva nominalmente, excluido de las instantáneas diarias.')))
                continue
            records.append(term(id,'Parlamentario/a',r['source'],r['start'],r['end'],formationLabel=BASQUE_LABELS.get(r['group'],r['group']) or 'Adscripción no publicada',**({'constituency':r['territory']}if r.get('territory')else{})))
        for r in li['board']:
            id=ids[r['key']];role=r['section']+' · Mesa del Parlamento Vasco'
            board.append(term(id,role,li['boardSource'],r['start'],r['end']))
            cat.event(id,'cargos-autonomias.json','pais-vasco',role,interval(r['start'],r['end']),li['boardSource'])
        start=min(r['start'] for r in raw if r['start'])
        end=max(r['end'] for r in raw if r['end']) if number<13 else None
        # El listado vigente confirma la continuidad hasta la fecha de consulta.
        if number==13:
            for row in current: cat.active(ids[row['key']],row['source'])
        data=dict(id=f'pais-vasco-parlamento-{number}',label=f'Legislatura {ROMANS[number-1]}',start=start,end=end,checkedAt=CHECKED,
                  source=li['source'],currentOnly=False,capacity=60 if number==1 else 75,records=records,board=board,
                  note='Altas, bajas y adscripciones publicadas por el Parlamento Vasco. Las fechas se conservan tal como figuran en la institución; el registro incluye sustituciones y periodos de Diputación Permanente.',groups=grouping(records))
        until=(datetime.date.fromisoformat(end)-datetime.timedelta(days=1)).isoformat()if end else CHECKED
        dates=sorted({start,until,*[r[k]for r in [*records,*board]for k in ['start','end']if r[k]and start<=r[k]<=until]})
        def count(date):return len({r['person']for r in records if r['start']and r['start']<=date and(not r['end']or date<r['end'])})
        data['snapshotDates']=[date for date in dates if count(date)<=data['capacity']]
        full=[date for date in dates if count(date)==data['capacity']]
        data['preferredDate']=full[-1]if full else max(data['snapshotDates'],key=count)
        for date in dates:
            if count(date)>data['capacity']:inconsistencies.append(dict(legislature=number,date=date,registered=count(date),capacity=data['capacity'],source=li['source']))
        if any(r['legislature']==number for r in inconsistencies):
            data['note']+=' Las fechas con solapamientos incompatibles con el aforo se conservan en la revisión de fuentes y se excluyen del selector cronológico.'
        if number==13:assert count(CHECKED)==75
        stage('pais-vasco','Parlamento',data)
    outputs.append((source_dir('pais-vasco')/'fuentes/solapamientos-cronologicos.json',dict(checkedAt=CHECKED,basis='Se conservan los intervalos originales sin decidir qué titular sustituye al otro. Las fechas que exceden el aforo no se ofrecen como instantáneas.',records=inconsistencies)))

def navarre_parliaments(ids):
    curated=m.load(source_dir('navarra')/'fuentes/relaciones-parlamentarias-revisadas.json')
    for index,li in enumerate(curated):
        number=li['legislature'];records=[];board=[]
        reference=li.get('referenceAt')or li['publishedAt']
        caption='Composición de la constitución documentada en la memoria 1979–1981'if number==0 else'Relación nominal publicada '+reference
        for name,group in li['members']:
            id=person(name,'navarra',li['source'],'Parlamento de Navarra')
            period=li['label']+' · '+caption
            cat.event(id,'mandatos-autonomias.json','navarra','Parlamento de Navarra · '+li['label'],period,li['source'])
            if group:association(id,'navarra',group,period,li['source'])
            records.append(term(id,'Parlamentario/a foral',li['source'],formationLabel=group or 'Adscripción no publicada',constituency='Navarra',period=period))
        assert len(records)==len({r['person']for r in records})==(70 if number==0 else 50),(number,'Duplicados o lista incompleta')
        for name,role in li.get('board',[]):
            id=person(name,'navarra',li['source'],'Mesa del Parlamento de Navarra')
            board.append(term(id,role+' · Mesa',li['source'],period=caption))
            cat.event(id,'cargos-autonomias.json','navarra',role+' · Mesa del Parlamento de Navarra',caption,li['source'])
        grouped=grouping(records)
        data=dict(id=f'navarra-parlamento-{number}',label=li['label'],start=li.get('constitutionAt')or reference,end=curated[index+1].get('constitutionAt',curated[index+1]['publishedAt'])if index+1<len(curated)else None,
                  checkedAt=CHECKED,source=li['source'],currentOnly=False,capacity=70 if number==0 else 50,records=records,board=[],groups=[],nominalOnly=True,
                  archiveBoard=board,archiveBoardNote='Composición publicada en el boletín o memoria de esta etapa. No atribuye intervalos individuales ni sustituye los relevos posteriores.',
                  note='Relación nominal de la publicación institucional; las fechas de publicación no son altas individuales. No reconstruye todos los relevos de la legislatura.',
                  archivedComposition=dict(source=li['source'],checkedAt=CHECKED,note=caption+'. Las siglas identifican el grupo o candidatura que declara la fuente, no militancia actual.',groups=[dict(name=g['name'],source=g['source'],members=[r['person']for r in g['members']])for g in grouped]))
        if number==11:
            current=[];current_board=[]
            for row in read('navarra-perfiles-actuales'):
                id=ids[row['source']]
                group=next((r['organ']for r in row['roles']if r['end']is None and(r['organ'].startswith('G.P.')or r['organ']=='No adscrita')),'No adscrita')
                current.append(term(id,'Parlamentario/a foral',row['source'],observedAt=CHECKED,constituency='Navarra',formationLabel=group))
                for r in row['roles']:
                    if r['end']is None and 'Mesa' in r['organ']:
                        current_board.append(term(id,r['role']+' · Mesa',row['source'],observedAt=CHECKED))
            assert len(current)==50 and len(current_board)==5,(len(current),len(current_board))
            data.update(currentOnly=True,records=current,board=current_board,groups=grouping(current),nominalOnly=False)
            data.pop('archivedComposition')
            data['source']='https://parlamentodenavarra.es/composicion-organos/parlamentarios-forales'
            data['note']='Composición vigente consultada; los mandatos anteriores de las fichas se conservan en el archivo personal, sin proyectar esta composición a 2023.'
        stage('navarra','Parlamento',data)

def cabinet(region):
    raw=read(region+'-consejerias-historicas');appointments=read(region+'-presidencias')
    current=read(region+'-gobierno-vigente')
    # Resuelve nombres completos y retratos del directorio vigente antes de las formas históricas abreviadas.
    for row in current:
        id=person(row['name'],region,row['source'],row['role']);cat.photo(id,row.get('image'),row['source'],m.REGIONS[region]+' · retrato del directorio de gobierno');cat.active(id,row['source'])
    if region=='pais-vasco': legs=[1,2,2,3,4,5,6,7,8,9,10,11,12,13]
    else: legs=[1,2,3,4,4,5,6,7,8,9,10,11]
    for i,app in enumerate(appointments):
        start=app['date'];end=appointments[i+1]['date']if i+1<len(appointments)else None
        name=app['name'];id=person(name,region,app['source'],'Lehendakari'if region=='pais-vasco'else'Presidencia del Gobierno de Navarra')
        label=f"{ROMANS[legs[i]-1]} · {start[:4]}" + (' · segunda etapa'if i and legs[i]==legs[i-1]else'')
        title='Gobierno Vasco'if region=='pais-vasco'else'Gobierno de Navarra'
        data=dict(id=f'{region}-gobierno-{start}',label=label,name=title+' · '+canonical(id),start=start,end=end,checkedAt=CHECKED,source=app['source'],terms=[term(id,'Lehendakari'if region=='pais-vasco'else'Presidencia del Gobierno',app['source'],start,end,level='president',endBasis='Marco documental del siguiente nombramiento')],archiveTerms=[],incidents=[
            'El inicio corresponde a la fecha del decreto de nombramiento, no a la fecha de publicación ni necesariamente a la toma de posesión.',
            'Las consejerías archivadas incluyen cambios de esta etapa. No se atribuye simultaneidad ni una fecha individual que la fuente no permita contrastar.'
        ])
        cat.event(id,'cargos-autonomias.json',region,'Lehendakari'if region=='pais-vasco'else'Presidencia del Gobierno de Navarra',interval(start,end),app['source'])
        if end is None:
            data.update(currentOnly=True,terms=[],incidents=[data['incidents'][0]])
            for row in current:
                pid=person(row['name'],region,row['source'],row['role']);role=row['role']
                level='president'if pid==id else'vice'if re.search('vice',role,re.I)else'minister'
                data['terms'].append(term(pid,role,row['source'],level=level,observedAt=CHECKED,period='Composición consultada '+CHECKED))
                cat.event(pid,'cargos-autonomias.json',region,role,'Composición consultada '+CHECKED,row['source'])
        else:
            if region=='pais-vasco': subset=[r for r in raw if r['legislature']==legs[i]]
            else:
                bounds={1984:[1983],1987:[1987],1991:[1991],1995:[1995],1996:[1996],1999:[1999],2003:[2003],2007:[2007,2009],2011:[2011,2012],2015:[2015],2019:[2019]}
                subset=[r for r in raw if r['startYear']in bounds[int(start[:4])]]
            merged={}
            for row in subset:
                for entry in split_historical(row,region):
                    pid=person(entry['name'],region,entry['source'],entry['role'])
                    if pid==id:continue
                    cat.photo(pid,entry.get('image'),entry['source'],m.REGIONS[region]+' · archivo institucional de gobiernos')
                    cat.event(pid,'cargos-autonomias.json',region,entry['role'],entry['period'],entry['source'])
                    if pid not in merged:merged[pid]=term(pid,entry['role'],entry['source'],period='Relación histórica de la etapa; intervalo individual no precisado')
                    elif entry['role']not in merged[pid]['role']:merged[pid]['role']+=' · '+entry['role']
            data['archiveTerms']=list(merged.values())
        stage(region,'Gobierno',data)

def split_historical(row,region):
    row=dict(row);name=row['name']
    name=re.sub(r'\s*\(\d{2}/\d{2}/\d{4}.*','',name)
    if '. Sustituido por 'in name:
        first,rest=name.split('. Sustituido por ',1);second=rest.rsplit(' el ',1)[0]
        return [{**row,'name':first},{**row,'name':second}]
    row['name']=name
    return [row]

def early_navarre():
    source='https://www.navarra.es/es/gobierno-de-navarra/presidencias-anteriores'
    stages=[('1979-04-19','1980-04-28','Jaime Ignacio del Burgo Tajadura'),('1980-09-29','1984-01-14','Juan Manuel Arza Muñuzuri'),('1984-01-14','1984-05-04','Jaime Ignacio del Burgo Tajadura')]
    raw=read('navarra-consejerias-historicas')
    for start,end,name in stages:
        id=person(name,'navarra',source,'Presidencia de la Diputación Foral')
        data=dict(id='navarra-gobierno-'+start,label='Diputación · '+start[:4],name='Diputación Foral · '+canonical(id),start=start,end=end,checkedAt=CHECKED,source=source,
                  terms=[term(id,'Presidencia de la Diputación Foral',source,start,end,level='president')],archiveTerms=[],incidents=[
                      'Marco de presidencia publicado por el Gobierno de Navarra. La fuente no fecha aquí la presidencia interina entre abril y septiembre de 1980.',
                      'En 1984 se distingue el fin publicado de la presidencia de la Diputación (4 de mayo) del decreto de nombramiento de Urralburu (18 de abril); son hitos distintos.'
                  ])
        for row in raw:
            if row['startYear']==1979:
                pid=person(row['name'],'navarra',row['source'],row['role'])
                if pid!=id:
                    data['archiveTerms'].append(term(pid,row['role'],row['source'],period='Diputación 1979–1984 · relación nominal; no acredita coincidencia diaria'))
                    cat.event(pid,'cargos-autonomias.json','navarra',row['role'],'Diputación 1979–1984',row['source'])
        cat.event(id,'cargos-autonomias.json','navarra','Presidencia de la Diputación Foral',interval(start,end),source)
        stage('navarra','Gobierno',data)

def reviewed_names():
    review=m.load(source_dir('navarra')/'fuentes/revision-apellidos.json')
    for row in review['cases']:
        person(row['fullName'],'navarra',row['source'],'Identidad contrastada con documentación institucional')

if __name__=='__main__':
    basque,navarre=profiles();basque_parliaments(basque);navarre_parliaments(navarre)
    cabinet('pais-vasco');cabinet('navarra');early_navarre();reviewed_names()
    # Validación previa a cualquier publicación.
    for path,data in outputs:
        if 'start'not in data or 'label'not in data:continue
        rows=[*data.get('records',[]),*data.get('terms',[]),*data.get('archiveTerms',[]),*data.get('board',[]),*data.get('archiveBoard',[])]
        assert all(r['person']in cat.people for r in rows),path
        assert all(not r['start']or not r['end']or r['start']<=r['end'] for r in rows),path
    print('COMPOSICIONES',len(outputs),'PERSONAS',len(cat.used),'NUEVAS',len(cat.new),flush=True)
    c.write(CACHE/'plan-integracion.json',dict(compositions=len(outputs),reviewedPeople=len(cat.used),newPeople=cat.new))
    if '--plan'not in sys.argv:
        for path,data in outputs:c.write(path,data)
        cat.save()
