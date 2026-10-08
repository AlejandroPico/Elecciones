"""Genera la biblioteca del Senado y los mandatos personales desde sus fuentes.

No convierte el comienzo de la legislatura en la fecha de nombramiento de una
persona. Las bajas individuales se consideran inclusivas para la vista temporal.
Los cambios internos de grupo sin fecha no se reconstruyen por inferencia.
"""
import pathlib,json,re,collections
ROOT=pathlib.Path(__file__).resolve().parents[2]
C=ROOT/'test-results/senado-estructura';DATE='2026-10-08'
def read(path,default=None):return json.loads(path.read_text('utf8')) if path.exists() else default
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if not path.exists() or path.read_text('utf8')!=text:path.write_text(text,encoding='utf8',newline='\n')
def dmy(text):
    m=re.search(r'(\d{2})/(\d{2})/(\d{4})',text)
    return '-'.join([m[3],m[2],m[1]]) if m else None
people={};aliases={}
for folder in (ROOT/'Políticos').iterdir():
    if not folder.is_dir() or not (folder/'ficha.json').exists():continue
    p=read(folder/'ficha.json');people[p['id']]={'folder':folder,**p}
    for alias in [p['id']]+p.get('legacyIds',[]):aliases[alias]=p['id']
audit=read(ROOT/'Políticos/revisiones/2026-10-08-parlamento/informe.json')
ids={r['key']:aliases.get(r['id'],r['id']) for r in audit['records'] if r['chamber']=='senado'}
personRoles=collections.defaultdict(list);personMandates=collections.defaultdict(list);report=[]
for leg in read(C/'legislaturas.json'):
    terms=[];senators=[];incidents=[];rawRecords=[]
    for member in leg['members']:
        sid=member['senateId'];pid=ids[sid];p=people[pid]
        data=read(C/'mandatos'/f"{sid}-{leg['number']}.json",{})
        if data.get('error') or not data.get('institutionalName'):
            incidents.append(f"{sid}: {data.get('error','consulta pendiente')}");continue
        source={'label':'Senado · ficha individual de la '+leg['label']+' legislatura','url':data['source']}
        credential=data.get('credential',[])
        start=dmy(next((s for s in credential if s.startswith('Fecha:')),''))
        end=dmy(next((s for s in credential if s.startswith('Baja')),''))
        group=next((s.strip() for s in credential if s.startswith('GRUPO PARLAMENTARIO')),'')
        senators.append({'person':pid,'name':p['name'],'start':start,'end':end,'group':group,'source':data['source']})
        if start:
            period=start+' — '+(end or 'último registro de esta legislatura')
            proced=next((s for s in credential if s.startswith(('Electo','Electa','Designado','Designada'))),'')
            personMandates[pid].append({'title':'Mandato en el Senado · '+leg['label']+' · '+proced,'period':period,'source':source})
        for office in data.get('offices',[]):
            mesa=bool(re.search(r'MESA DEL SENADO',office['organ'],re.I))
            spokesperson=bool(re.match(r'PORTAVOZ(?:\s|$)',office['role'],re.I) and re.match(r'GRUPO PARLAMENTARIO',office['organ'],re.I))
            commission=bool(re.match(r'PRESIDENT[EA](?:\s|$)',office['role'],re.I) and re.match(r'COMISI[ÓO]N',office['organ'],re.I))
            if not (mesa or spokesperson or commission):continue
            if office['start'] and office['end'] and office['start']>office['end']:
                incidents.append(f"{sid}: intervalo de cargo invertido en la fuente");continue
            term={'person':pid,'name':p['name'],'role':office['role'],'organ':office['organ'],'start':office['start'],'end':office['end'],'source':data['source']}
            if term not in terms:terms.append(term)
            title=office['role'].capitalize()+' · '+office['organ'].capitalize()
            period=(office['start'] or 'Alta no publicada')+' — '+(office['end'] or 'último registro de esta legislatura')
            personal={'title':title,'period':period,'source':source}
            if personal not in personRoles[pid]:personRoles[pid].append(personal)
        rawRecords.append({'senateId':sid,'person':pid,'source':data['source'],'sha256':data['sha256']})
    board=[]
    for m in leg['board']:
        pid=ids[m['senateId']];p=people[pid]
        board.append({'person':pid,'name':p['name'],'role':m['role'],'organ':'MESA DEL SENADO','start':None,'end':None,'source':leg['mesaSource']})
    document={'id':'senado-'+str(leg['number']),'number':leg['number'],'label':leg['label'],'start':leg['start'],'end':leg['end'],'source':leg['source'],'mesaSource':leg['mesaSource'],'checkedAt':DATE,'terms':terms,'senators':senators,'finalBoard':board,'incidents':incidents}
    folder=ROOT/'Gobiernos/Senado'/('Legislatura Constituyente' if leg['number']==0 else leg['label']+' Legislatura')
    save(folder/'composicion.json',document)
    save(folder/'fuentes.json',rawRecords)
    report.append({'legislature':leg['number'],'senators':len(senators),'datedMandates':sum(bool(s['start']) for s in senators),'boardTerms':sum('MESA DEL SENADO' in t['organ'] for t in terms),'spokespersonTerms':sum('PORTAVOZ' in t['role'] for t in terms),'incidents':incidents})
    print('Incorporada',leg['label'],len(senators),'mandatos',len(terms),'cargos',flush=True)
for pid,mandates in personMandates.items():save(people[pid]['folder']/'mandatos-senado.json',mandates)
for pid,roles in personRoles.items():save(people[pid]['folder']/'cargos-senado.json',roles)
save(ROOT/'Gobiernos/revisiones/2026-10-08-senado/informe.json',{'checkedAt':DATE,'legislatures':report,'uniqueSenators':len(ids),'mandates':sum(x['senators'] for x in report),'limitations':['El grupo de cada mandato es la última adscripción conservada en la ficha, no un historial fechado de cambios internos.','No se inventan fechas para cargos o mandatos sin alta individual publicada.','El Pleno y Mesa de la XV Legislatura se representan antes de la disolución del 6 de octubre de 2026.','Los cargos de la Mesa y portavocías se reconstruyen a partir de intervalos individuales de todas las legislaturas desde 1977.']})
print('Incorporación terminada.',flush=True)
