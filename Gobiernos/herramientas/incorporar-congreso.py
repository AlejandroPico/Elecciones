"""Incorpora mandatos, Mesa y adscripciones del Congreso en sus carpetas propias.

Lee la caché de consultar-congreso.py y del inventario parlamentario anterior.
No copia contactos ni deduce militancia, jubilación o asientos físicos.
"""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json, re, unicodedata

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'test-results/congreso-estructura'
ROMANS = ['Constituyente','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV']
CHECKED = '2026-10-08'

def read(path): return json.loads(path.read_text(encoding='utf8'))
def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
def norm(name):
    return re.sub('[^a-z0-9]', '', unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower())
def day(value):
    if not value: return None
    return datetime.strptime(value,'%d/%m/%Y').date().isoformat()
def source(code, leg):
    return 'https://www.congreso.es/busqueda-de-diputados?p_p_id=diputadomodule&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&mostrarFicha=true&codParlamentario='+str(code)+'&idLegislatura='+('0' if leg == 0 else ROMANS[leg])
def group_source(code, leg):
    return 'https://www.congreso.es/grupos/composicion-en-la-legislatura?p_p_id=grupos&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_grupos_idLegislatura='+('0' if leg == 0 else ROMANS[leg])+'&_grupos_mostrarFicha=true&_grupos_gruposView=true&_grupos_idGrupo='+str(code)
def period(start,end): return (start or 'Alta no publicada')+' – '+(end or 'Último registro')

def main():
    folders = {}; names = defaultdict(set)
    for file in (ROOT/'Políticos').glob('*/ficha.json'):
        person = read(file); folders[person['id']] = (file.parent,person)
        for name in [person.get('fullName'),person.get('name'),*(person.get('knownAs') or [])]:
            if name: names[norm(name)].add(person['id'])
    audit = read(ROOT/'Políticos/revisiones/2026-10-08-parlamento/informe.json')
    for record in audit['records']:
        if record['chamber'] == 'congreso':
            names[norm(record['name'])].add(record['id'])
            cached = read(ROOT/'test-results/revision-partidos/parlamento/congreso'/(record['key']+'.json'))['record']
            names[norm(cached['nombre']+' '+cached['apellidos'])].add(record['id'])
    mandates = read(ROOT/'test-results/revision-partidos/parlamento/congreso-mandatos.json')
    for record in read(ROOT/'Gobiernos/revisiones/2026-10-08-congreso/identidades.json')['records']:
        names[norm(record['name'])].add(record['person'])
    identity = {}; unmatched = []
    for row in mandates:
        ids = names[norm(row['nombre']+' '+row['apellidos'])]
        if len(ids) != 1:
            unmatched.append({'name':row['apellidosNombre'],'legislature':row['idLegislatura'],'candidates':sorted(ids)})
        else: identity[(int(row['idLegislatura']),int(row['codParlamentario']))] = next(iter(ids))
    if unmatched:
        write(CACHE/'identidades-pendientes.json',unmatched)
        raise RuntimeError('Identidades sin correspondencia única: '+str(len(unmatched))+'; revisar identidades-pendientes.json')
    own_board = defaultdict(list); own_groups = defaultdict(list); own_mandates = defaultdict(list); report = []
    for leg in range(16):
        mesa = read(CACHE/f'mesa-{leg}.json'); groups = read(CACHE/f'grupos-{leg}.json')['data']
        start = day(mesa['fechaConstitucion']['fechaConstitucion'])
        end = day(mesa['fechaDisolucion']['fechaDisolucion'])
        mesa_url = 'https://www.congreso.es/mesa?p_p_id=organos&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_organos_selectedLegislatura='+('0' if leg == 0 else ROMANS[leg])+'&_organos_compoHistorica=true'
        members = []; board = []; memberships = []; definitions = []; incidents = []
        for row in mandates:
            if int(row['idLegislatura']) != leg: continue
            pid = identity[(leg,int(row['codParlamentario']))]; person=folders[pid][1]
            members.append({'person':pid,'name':person.get('fullName') or person['name'],'code':int(row['codParlamentario']),
                'start':day(row['fchAlta']),'end':day(row['fchBaja']),'constituency':row.get('nombreCircunscripcion') or '',
                'formation':row.get('formacion') or '', 'source':source(row['codParlamentario'],leg)})
            own_mandates[pid].append({'title':'Diputado en el Congreso · '+ROMANS[leg]+' Legislatura · '+(row.get('nombreCircunscripcion') or 'Circunscripción no publicada'),
                'period':period(day(row['fchAlta']),day(row['fchBaja'])),
                'source':{'label':'Congreso · mandato individual','url':source(row['codParlamentario'],leg),'kind':'institutional'}})
        for row in mesa['data']:
            if not row.get('urlFichaDiputado'):
                incidents.append('Cargo sin mandato ni fechas individuales: '+row['descCargo']+' · '+row['apellidosNombre'])
                continue
            code = int(re.search(r'codParlamentario=(\d+)', row['urlFichaDiputado'])[1]); pid=identity[(leg,code)]
            term = {'person':pid,'name':folders[pid][1].get('fullName') or folders[pid][1]['name'], 'role':row['descCargo'],
                'start':day(row.get('fechaAltaFormat')),'end':day(row.get('fechaBajaFormat')),'source':mesa_url}
            board.append(term)
            own_board[pid].append({'title':term['role']+' de la Mesa del Congreso · '+ROMANS[leg]+' Legislatura',
                'period':period(term['start'],term['end']),'source':{'label':'Congreso · composición histórica de la Mesa','url':mesa_url,'kind':'institutional'}})
        for group in groups:
            code = int(group['codOrg']); url = group_source(code,leg)
            definitions.append({'code':code,'name':group['grpDesc'],'shortName':group['nombreGrupo'],'start':day(group.get('fechaConstitucion')),'source':url})
            for row in read(CACHE/f'grupo-{leg}-{code}.json')['data']:
                key=(leg,int(row['codParlamentario']))
                if key not in identity:
                    incidents.append('Adscripción sin mandato en el inventario: '+row['apellidosNombre']); continue
                pid=identity[key]; term={'person':pid,'code':code,'start':day(row.get('fchAlta')),'end':day(row.get('fchBaja')),'source':url}
                if term in memberships: continue
                memberships.append(term)
                own_groups[pid].append({'title':group['grpDesc']+' · '+ROMANS[leg]+' Legislatura','period':period(term['start'],term['end']),
                    'source':{'label':'Congreso · adscripción parlamentaria fechada','url':url,'kind':'institutional'}})
        data={'id':f'congreso-{leg}','number':leg,'label':'Legislatura Constituyente' if leg==0 else ROMANS[leg]+' Legislatura',
            'start':start,'end':end,'checkedAt':CHECKED,'source':'https://www.congreso.es/opendata/diputados','mesaSource':mesa_url,
            'members':members,'groups':definitions,'memberships':memberships,'board':board,'incidents':incidents,
            'physicalSeating':{'status':'unavailable','checkedAt':CHECKED,'source':'https://www.congreso.es/hemiciclo',
                'reason':'El plano público está sustituido por el aviso de disolución. El inventario de mandatos y grupos no publica ubicaciones físicas fechadas.'}}
        directory=ROOT/'Gobiernos/Congreso'/data['label']
        write(directory/'composicion.json',data)
        write(directory/'fuentes.json',[{'label':'Congreso · diputados por legislatura','url':data['source'],'kind':'institutional'},
            {'label':'Congreso · Mesa histórica','url':mesa_url,'kind':'institutional'},
            {'label':'Congreso · grupos parlamentarios','url':'https://www.congreso.es/grupos/composicion-en-la-legislatura','kind':'institutional'}])
        dates=sorted({start,(datetime.fromisoformat(end)-timedelta(days=1)).date().isoformat(),*[m['start'] for m in members if m['start'] and start<=m['start']<end],*[m['end'] for m in members if m['end'] and start<=m['end']<end]})
        counts={d:len({m['person'] for m in members if m['start'] and m['start']<=d and (not m['end'] or d<m['end'])}) for d in dates}
        report.append({'number':leg,'mandates':len(members),'groups':len(groups),'memberships':len(memberships),'boardTerms':len(board),
            'latestCount':counts[dates[-1]],'minCount':min(counts.values()),'maxCount':max(counts.values()),'incidents':incidents})
    for pid,terms in own_board.items(): write(folders[pid][0]/'cargos-congreso.json',terms)
    for pid,terms in own_groups.items(): write(folders[pid][0]/'grupos-congreso.json',terms)
    for pid,terms in own_mandates.items(): write(folders[pid][0]/'mandatos-congreso.json',terms)
    result={'checkedAt':CHECKED,'legislatures':report,'matchedMandates':len(mandates),'unmatched':unmatched,'peopleWithBoardTerms':len(own_board),
        'peopleWithGroups':len(own_groups),'physicalSeatsVerified':False,'intervalCriterion':'Alta inclusiva; baja exclusiva. En la disolución termina el Pleno, aunque permanezcan miembros de la Diputación Permanente.',
        'startCriterion':'Inicio del recorrido: fecha de constitución de la Mesa publicada por el Congreso; no se confunde con la primera sesión de la Cámara.'}
    write(ROOT/'Gobiernos/revisiones/2026-10-08-congreso/informe.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
