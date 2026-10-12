"""Prepara hechos de las fuentes andaluzas para revisión e incorporación.

Extrae datos breves, no reproduce biografías ni declaraciones personales. Los
intervalos parlamentarios ausentes permanecen ausentes. El BOJA conserva la
precisión del acto y sus efectos; no se deduce una ceremonia de posesión.
"""
import datetime, importlib.util, json, pathlib, re, unicodedata
spec = importlib.util.spec_from_file_location('ad', pathlib.Path(__file__).with_name('consultar-andalucia.py'))
ad = importlib.util.module_from_spec(spec); spec.loader.exec_module(ad)
DEST = pathlib.Path('Gobiernos/Autonomías/Andalucía')
MONTHS = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
ROMANS = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII']
BOOK = 'https://www.parlamentodeandalucia.es/documents/20121/397974/memoria_XXVaniversario.pdf/b2ef6f02-03ef-30c3-e70a-bc3cece5d8b0?t=1675331357713'

def normal(text):
    return re.sub(r'[^a-z0-9]+',' ',''.join(c for c in unicodedata.normalize('NFD',text.lower()) if not unicodedata.combining(c))).strip()

def birthday(text):
    match = re.search(r'(\d{1,2}) de (\w+) de (\d{4})',text,re.I)
    if not match or match[2].lower() not in MONTHS: return None
    return f'{match[3]}-{MONTHS.index(match[2].lower())+1:02d}-{int(match[1]):02d}'

def biographies():
    pages = json.loads((ad.CACHE/'memoria-2-text.json').read_text('utf8'))
    text = '\n'.join(pages[196:446]); pattern = r'(?m)^[A-ZÁÉÍÓÚÜÑ’\- .]{8,}$'
    headers = [(m.start(),m.end(),m[0].strip()) for m in re.finditer(pattern,text) if 3<=len(m[0].split())<=11 and not any(w in m[0] for w in ['MEMORIA','HISTÓRICA','LEGISLATURA','PARLAMENTO'])]
    rows = []
    for i,(start,end,name) in enumerate(headers):
        body = text[end:headers[i+1][0] if i+1<len(headers) else len(text)]
        intro = re.split(r'\b[IVX]+ Legislatura',body,maxsplit=1)[0]
        lines = [l.strip() for l in intro.splitlines() if l.strip()]
        date = birthday(intro)
        if not date: continue
        page = next(n+197 for n in range(250) if sum(len(p)+1 for p in pages[196:196+n+1])>start)
        education = [l for l in lines if re.search(r'^(?:Licenciad[oa]|Diplomad[oa]|Doctor|Ingenier[oa]|Estudios|Maestr[oa]|Bachiller|Graduad[oa])',l,re.I) and len(l)<180]
        death = re.search(r'\d{1,2} de \w+ de \d{4}\s*-\s*(\d{1,2} de \w+ de \d{4}|\d{4})',intro)
        row = {'nameInBook':name,'birthDate':date,'birthPlace':lines[0], 'education':education,'source':BOOK+f'#page={page}','page':page}
        if death:
            if birthday(death[1]): row['deathDate']=birthday(death[1])
            elif len(death[1])==4: row['deathYear']=int(death[1])
        rows.append(row)
    ad.write(DEST/'fuentes/biografias-parlamento.json',rows)
    print('Datos biográficos de la memoria:',len(rows),flush=True)

def appointment_date(row):
    text = row['text']; match = re.search(r'de (\d{1,2}) de (\w+)',row['label'],re.I)
    year = re.search(r'/((?:19|20)\d{2})',row['label'])
    day = birthday(match[0]+' de '+(year[1] if year else row['published'][:4])) if match else row['published']
    if re.search(r'efectos el día de su aprobación',text,re.I):
        return day, 'Aprobación, según la cláusula de efectos.'
    if re.search(r'día siguiente al de su publicación',text,re.I):
        return (datetime.date.fromisoformat(row['published'])+datetime.timedelta(days=1)).isoformat(), 'Día siguiente a la publicación, según el articulado.'
    if re.search(r'(?:efectos|vigor)[^.]{0,90}(?:día de su publicación|día de la publicación|mismo día de su publicación)',text,re.I):
        return row['published'], 'Publicación, según la cláusula de efectos.'
    return day or row['published'], 'Fecha del acto de nombramiento o cese; no equivale por sí sola a la toma de posesión.'

def appointments(text):
    clean = re.sub(r'\s+',' ',text)
    members = []
    # Primer Consejo autonómico: lista de nombres y carteras sin puntos.
    if '- Dª AMPARO RUBIALES' in text:
        for m in re.finditer(r'- D(?:ª|\.)\s+(.+?)\s+(Consejer[oa].+?)(?=\n- D|\nSevilla)',text,re.S):
            members.append({'nameInSource':re.sub(r'\s+',' ',m[1]).title(),'role':re.sub(r'\s+',' ',m[2]).strip()})
        return members
    for line in text.splitlines():
        m = re.fullmatch(r'((?:Vicepresident[ea].*? y )?Consejer[oa]\s+(?:de|para).+?)\s+a\s+do(?:n|ña)\s+(.+?)\.?',line.strip(),re.I)
        if m: members.append({'nameInSource':m[2].strip(), 'role':m[1].strip()})
    if members: return members
    # Disposiciones antiguas: nombre seguido de la cartera.
    for m in re.finditer(r'\b(?:Don|Doña|Dña\.?|Dª|D\.)\s+([^.;]{5,110}?),?\s+como\s+(Consejer[oa]\s+(?:de|para)[^.]+)\.',clean,re.I):
        members.append({'nameInSource':m[1].strip(' ,'), 'role':m[2].strip()})
    # Disposiciones actuales: cartera seguida del nombre.
    for m in re.finditer(r'((?:Vicepresident[ea][^.]*? y )?Consejer[oa]\s+(?:de|para)[^.]+?)\s+a\s+do(?:n|ña)\s+([^.;]+)\.',clean,re.I):
        members.append({'nameInSource':m[2].strip(), 'role':m[1].strip()})
    # Nombramiento individual en el título y en el articulado, sin "como".
    if not members:
        for m in re.finditer(r'\b(?:don|doña|D\.)\s+([^.;,]{5,110}),?\s+(?:como\s+)?(Consejer[oa]\s+de\s+[^.]+)\.',clean,re.I):
            members.append({'nameInSource':m[1].strip(), 'role':m[2].strip()})
    return list({(normal(m['nameInSource']),normal(m['role'])):m for m in members}.values())

def government():
    norms = json.loads((ad.CACHE/'normas-gobierno.json').read_text('utf8'))
    events, rejected = [], []
    for row in norms:
        label = row['label']
        if not re.search(r'(?:del Presidente|de la Presidenta|miembros del Consejo de Gobierno)',label,re.I): continue
        if re.search(r'Consejo Consultivo|Consejo Audiovisual|Cámara de Cuentas|Gabinete de la Vicepresidencia',label,re.I): continue
        if re.search(r'reestructur|reasignación|modifica',label,re.I): continue
        date, basis = appointment_date(row)
        full = bool(re.search(r'designan (?:los )?(?:miembros del Consejo|Consejeros|Vicepresidencias)',label,re.I))
        cease_all = bool(re.search(r'cese (?:del Vicepresidente (?:de la Junta de Andalucía )?y de los |de los )Consejeros',label,re.I))
        members = appointments(row['text']) if not re.search(r'cese',label,re.I) else []
        if full and len(members)<8:
            rejected.append({'source':row['source'],'label':label,'reason':'Lista completa requiere transcripción individual.'}); continue
        cease = []
        if re.search('cese',label,re.I) and not cease_all:
            m = re.search(r'cese(?:, a petición propia,)? de do(?:n|ña)\s+(.+?)\s+(?:como|en)',label,re.I)
            if m: cease=[m[1].strip(' ,')]
        vice = []
        if not members and 'Vicepresidente' in label and re.search(r'designa',label,re.I):
            m = re.search(r'do(?:n|ña)\s+([^.,]+)',label,re.I)
            if m:
                role = re.search(r'(Vicepresidente(?:\s+(?:Primero|Segundo|Tercero))?)',label,re.I)
                vice=[{'nameInSource':m[1].strip(),'role':role[1] if role else 'Vicepresidente'}]
        if members or cease or cease_all or vice:
            events.append({'date':date,'basis':basis,'source':row['source'],'label':label,'full':full,'ceaseAll':cease_all,'cease':cease,'members':members,'vice':vice})
        elif not re.search('cese.*Vicepresidente',label,re.I): rejected.append({'source':row['source'],'label':label,'reason':'Disposición que requiere contraste de suplencia o competencia.'})
    events.sort(key=lambda e:(e['date'],0 if e['ceaseAll'] or e['cease'] else 1 if e['full'] else 2))
    ad.write(DEST/'fuentes/nombramientos.json',{'checkedAt':ad.CHECKED,'events':events,'norms':[r for r in norms if r['source'] in {e['source'] for e in events}],'pending':rejected})
    print('Eventos BOJA:',len(events),'pendientes de transcripción:',len(rejected),flush=True)

if __name__ == '__main__': biographies(); government()
