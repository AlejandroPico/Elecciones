"""Prioriza actividad acreditada sin equiparar falta de datos con jubilación.

Una disolución parlamentaria no implica que las personas o partidos abandonen
la política. Se conserva como actividad reciente la última composición previa
a ella; cada criterio incluye su fecha de consulta y la fuente individual.
"""
import json, pathlib, re, collections
ROOT=pathlib.Path(__file__).resolve().parents[2]
DATE='2026-10-08'
def read(path, default=None):
    return json.loads(path.read_text('utf8')) if path.exists() else default
def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
people={};aliases={}
def ongoing(period):
    return bool(re.search(r'^Desde\b|actualidad|presente',period,re.I)) and not bool(re.search(r'\bhasta\b\s+(?!la actualidad)|[–—]\s*(?:19|20)\d{2}',period,re.I))
for folder in (ROOT/'Políticos').iterdir():
    if not folder.is_dir() or not (folder/'ficha.json').exists():continue
    meta=read(folder/'ficha.json');personal=read(folder/'datos-personales.json',{})
    people[meta['id']]={'meta':meta,'personal':personal,'folder':folder,'timeline':read(folder/'trayectoria.json',[]),'affiliations':read(folder/'afiliaciones.json',[])}
    for alias in [meta['id']]+meta.get('legacyIds',[]):aliases[alias]=meta['id']
audit=read(ROOT/'Políticos/revisiones/2026-10-08-parlamento/informe.json')
ids={(r['chamber'],r['key']):aliases.get(r['id'],r['id']) for r in audit['records']}
evidence=collections.defaultdict(list)
for record in read(ROOT/'test-results/revision-partidos/parlamento/congreso-mandatos.json',[]):
    if record['idLegislatura']!=15:continue
    end=record.get('fchBaja') or ''
    if end and not re.search(r'0[56]/10/2026',end):continue
    key=str(record['codParlamentario'])+'-15';pid=ids.get(('congreso',key))
    if pid:evidence[pid].append({'label':'Congreso · mandato de la última legislatura','url':'https://www.congreso.es/es/busqueda-de-diputados?codParlamentario='+str(record['codParlamentario'])+'&idLegislatura=XV&mostrarFicha=true'})
for file in (ROOT/'test-results/senado-estructura/mandatos').glob('*-15.json'):
    d=read(file)
    if d.get('error'):continue
    credential=d.get('credential',[]);end=next((t for t in credential if t.startswith('Baja')),'')
    if end and not re.search(r'0[56]/10/2026',end):continue
    pid=ids.get(('senado',d['id']))
    if pid:evidence[pid].append({'label':'Senado · mandato de la última legislatura','url':d['source']})
gov=read(ROOT/'Gobiernos/XV Legislatura/composiciones.json')
for member in gov['cabinets'][-1]['members']:
    pid=aliases.get(member['person'])
    if pid:evidence[pid].append({'label':'La Moncloa · última composición documentada','url':gov['source']})
for pid,p in people.items():
    # Biografías ya contrastadas que precisan la continuidad de un cargo.
    if p['meta'].get('reviewedAt','') >= '2026-10-07':
        for t in p['timeline']:
            url=t['source']['url']
            if 'senado.es' in url and not re.search(r'legis=15(?:&|$)|SEN-1-\d+-15\.xml',url):continue
            if 'congreso.es' in url and not re.search(r'idLegislatura=(?:XV|15)(?:&|$)',url):continue
            if ongoing(t['period']) and not re.search(r'jubilad|retirad|emérit|honor',t['title'],re.I):
                evidence[pid].append(t['source'])
activeParties=collections.defaultdict(list);counts=collections.Counter()
for pid,p in people.items():
    target=p['folder']/'actividad.json';sources=evidence.get(pid,[])
    if p['personal'].get('deathDate') or p['personal'].get('deathYear'):
        state='historical';reason='Fallecimiento documentado.';sources=p['personal'].get('personalSources') or read(p['folder']/'fuentes.json',[])[:2]
    elif sources:
        state='active';reason='Actividad política documentada en la última legislatura, composición gubernamental o cargo con continuidad contrastada. La disolución de las Cámaras no acredita retirada política.'
    else:
        if not target.exists():continue
        state='unknown';reason='Actividad actual sin evidencia suficiente en las fuentes consultadas. No se afirma jubilación ni retirada.';sources=[]
    unique=list({s['url']:s for s in sources}.values())
    save(target,{'state':state,'reason':reason,'checkedAt':DATE,'sources':unique[:5]});counts[state]+=1
    if state=='active':
        for a in p['affiliations']:
            org=a.get('organization');period=a.get('period','')
            # Solo vinculaciones temporales del mandato reciente; no todas las
            # afiliaciones históricas de una persona todavía en actividad.
            if org and (re.search(r'2026-10-0[56]|actualidad',period,re.I) or (a.get('kind')=='membership' and re.search(r'^Desde\b|presente',period,re.I))):activeParties[org].append(a['source'])
        org=p['meta'].get('organization')
        currentRoles=[t for t in p['timeline'] if ongoing(t['period']) and re.search(r'presiden|secretar|portavoz|coordinador',t['title'],re.I)]
        if org and currentRoles:activeParties[org].extend(t['source'] for t in currentRoles)
partyCounts=collections.Counter()
for folder in (ROOT/'Partidos').iterdir():
    if not folder.is_dir() or not (folder/'ficha.json').exists():continue
    meta=read(folder/'ficha.json');dissolution=meta.get('dissolution');sources=activeParties.get(meta['id'],[])
    if dissolution and dissolution['date'] <= DATE:
        state='historical';reason='Disolución documentada; se conserva la ficha histórica.';sources=[dissolution['source']]
    elif sources:
        state='active';reason='Vinculación documentada con representantes o dirigentes en actividad reciente. No equivale a una candidatura proclamada para las próximas elecciones.'
    else:
        previous=read(folder/'actividad.json',{})
        if previous.get('state')!='active':continue
        state='unknown';reason='Actividad actual sin evidencia suficiente en las fuentes consultadas; la inscripción por sí sola no acredita actividad.';sources=[]
    save(folder/'actividad.json',{'state':state,'reason':reason,'checkedAt':DATE,'sources':list({s['url']:s for s in sources}.values())[:5]});partyCounts[state]+=1
print('Clasificación documentada personas',dict(counts),'partidos',dict(partyCounts),flush=True)
