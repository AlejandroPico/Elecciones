"""Transcripción verificable de gabinetes; no completa fechas por suposición.

Los cuadros anteriores a 2011 se mantienen como archivo de cargos de la etapa
cuando no hay un intervalo diario contrastado. Desde 2011 se conservan los
nombramientos del BOCM y la cronología, indicando la base de cada límite.
"""
import concurrent.futures, datetime, importlib.util, json, pathlib, re, unicodedata
spec=importlib.util.spec_from_file_location('consulta',pathlib.Path(__file__).with_name('consultar-madrid.py'))
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
from bs4 import BeautifulSoup
DEST=pathlib.Path('Gobiernos/Autonomías/Madrid');CACHE=q.CACHE
ANNEX='https://es.wikipedia.org/wiki/Anexo:Composici%C3%B3n_de_los_Gobiernos_de_la_Comunidad_de_Madrid'
def norm(s):return re.sub(r'[^a-z0-9]+',' ',''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))).strip()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);q.write(p,d)
def expanded(table):
    spanning={};out=[]
    for tr in table.select('tr'):
        cells=tr.find_all(['td','th'],recursive=False);row=[];col=0
        for cell in cells:
            while col in spanning:
                remaining,item=spanning[col];row.append(item)
                if remaining==1:del spanning[col]
                else:spanning[col]=(remaining-1,item)
                col+=1
            for _ in range(int(cell.get('colspan',1))):
                row.append(cell)
                if int(cell.get('rowspan',1))>1:spanning[col]=(int(cell['rowspan'])-1,cell)
                col+=1
        while col in spanning:
            remaining,item=spanning[col];row.append(item)
            if remaining==1:del spanning[col]
            else:spanning[col]=(remaining-1,item)
            col+=1
        out.append(row)
    return out
def text(cell):return re.sub(r'\[.*?\]','',cell.get_text(' ',strip=True)).strip()
profiles=read(CACHE/'profiles.json')
profile_names={norm(p['name']):p['name'] for p in profiles}
people=[];name_index={}
for file in pathlib.Path('Políticos').glob('*/ficha.json'):
    m=read(file);people.append(m)
    for name in [m.get('name'),m.get('fullName'),*m.get('knownAs',[])]:
        if name:name_index.setdefault(norm(name),[]).append(m)
people_by_id={m['id']:m for m in people}
aliases={norm(x['name']):x['person'] for x in read(DEST/'identidades.json')}

FULL_NAMES={
 'Joaquín Leguina':'Joaquín Leguina Herrán','Alberto Ruiz-Gallardón':'Alberto Ruiz-Gallardón Jiménez','Esperanza Aguirre':'Esperanza Aguirre Gil de Biedma',
 'Ignacio González':'Jaime Ignacio González González','Ignacio González González':'Jaime Ignacio González González',
 'Isabel Díaz Ayuso':'Isabel Natividad Díaz Ayuso','Cristina Cifuentes':'Cristina Cifuentes Cuencas','Ángel Garrido':'Ángel Garrido García','Pedro Rollán':'Pedro Rollán Ojeda',
 'César Cimadevilla':'César Cimadevilla Costa','Francisco Gil':'Francisco Gil García','Luis Alejandro Cendrero':'Luis Alejandro Cendrero Agulló',
 'Virgilio Cano':'Virgilio Cano de Lope','Eduardo Mangada':'Eduardo Mangada Samain','Javier Ledesma':'Francisco Javier Ledesma Bartret','Agapito Ramos':'Agapito Ramos Cuenca','María Gómez Mendoza':'María Gómez de Mendoza',
 'Ramón Espinar':'Ramón Espinar Gallego','Elena Vázquez':'Elena Vázquez Menéndez','Pedro Sabando':'Pedro Sabando Suárez','Julián Revenga':'Julián Revenga Frauca',
 'Luis Blázquez':'Luis Blázquez Torres','Gustavo Villapalos':'Gustavo Villapalos Salas','Antonio Beteta':'Antonio Germán Beteta Barreda','Jesús Pedroche':'Jesús Pedroche Nieto','Rosa Posada':'Rosa Posada Chapado',
 'Manuel Cobo':'Manuel Cobo Vega','Ignacio Echániz':'José Ignacio Echániz Salgado','Pilar Martínez López':'María del Pilar Martínez López','Alicia Moreno':'Alicia Moreno Espert',
 'Alfredo Prada':'Alfredo Prada Presa','Santiago Fisas':'Santiago Fisas Ayxelà','Fernando Merry del Val':'Fernando Merry del Val Díez','Luis Peral':'Luis Peral Guerra','Juan José Güemes':'Juan José Güemes Barrios',
 'Beatriz Elorriaga':'Beatriz Elorriaga Pisarik','Engracia Hidalgo':'Engracia Hidalgo Tena','Mariano Zabía':'Mariano Zabía Lasala','Francisco Granados':'Francisco Granados Lerena','Manuel Lamela':'Manuel Lamela Fernández',
 'María Dolores de Cospedal':'María Dolores de Cospedal García','Elvira Rodríguez':'María Elvira Rodríguez Herrer','Alberto López Viejo':'Alberto López Viejo','Lucía Figar':'Lucía Figar de Lacalle',
 'Paloma Adrados':'María Paloma Adrados Gautier','Gádor Ongil':'María Gádor Ongil Cores','Javier Fernández-Lasquetty':'Javier Fernández-Lasquetty y Blanc','Ana Isabel Mariño':'Ana Isabel Mariño Ortega','José Ignacio Echeverría':'José Ignacio Echeverría Echániz',
 'Regina Plañiol':'Regina María Plañiol de Lacalle','Percival Manglano':'Percival Peter Manglano Albacar','Salvador Victoria':'Salvador Victoria Bolívar','Pablo Cavero':'Pablo Cavero Martínez de Campos',
 'Enrique Ossorio':'Enrique Matías Ossorio Crespo','Borja Sarasola':'Borja Sarasola Jáudenes','Jesús Fermosel':'Jesús Fermosel Díaz','Javier Rodríguez':'Francisco Javier Rodríguez Rodríguez','Javier Maldonado':'Javier Maldonado González',
 'Jaime González Taboada':'Jaime González Taboada','Jesús Sánchez Martos':'Jesús Sánchez Martos','Rafael van Grieken':'Rafael van Grieken Salvador','Rosalía Gonzalo':'Rosalía Gonzalo López','Jaime Miguel de los Santos':'Jaime Miguel de los Santos González',
 'María Dolores Moreno':'María Dolores Moreno Molino','Yolanda Ibarrola':'Yolanda Ibarrola de la Fuente','Ignacio Aguado':'Ignacio Jesús Aguado Crespo','Eugenia Carballedo':'Eugenia Carballedo Berlanga',
 'Enrique López':'Enrique López López','Paloma Martín':'Paloma Martín Martín','Alberto Reyero':'Alberto Reyero Zubiri','Eduardo Sicilia':'Eduardo Sicilia Cavanillas','Javier Luengo':'Francisco Javier Luengo Vicente','Concepción Dancausa':'Concepción Dancausa Treviño',
 'Miguel Ángel García':'Miguel Ángel García Martín','Rocío Albert':'Rocío Albert López','Emilio Viciana':'Emilio Viciana Duro','Jorge Rodrigo':'Jorge Rodrigo Domínguez','Fátima Matute':'Fátima Matute Teresa','Carlos Novillo':'Carlos Novillo Piris','Ana Dávila':'Ana Dávila-Ponce de León Municio','Mariano de Paco':'Mariano de Paco Serrano',
}
def full_name(name):
    clean=re.sub(r'\s*\(.*','',name).strip().rstrip('.')
    if norm(clean) in aliases:
        meta=people_by_id[aliases[norm(clean)]]
        return meta.get('fullName') or meta['name']
    value=FULL_NAMES.get(clean,clean)
    if norm(value) in aliases:
        meta=people_by_id[aliases[norm(value)]]
        return meta.get('fullName') or meta['name']
    matches=name_index.get(norm(value)) or name_index.get(norm(clean))
    if matches:return matches[0].get('fullName') or matches[0]['name']
    return profile_names.get(norm(value),value)

ROLES={
 'President':'Presidencia de la Comunidad de Madrid',
 'Vice President and Spokesperson of the Government Minister of Culture and Sports':'Vicepresidencia, Cultura y Deporte y Portavocía del Gobierno',
 'Minister of the Presidency and Justice':'Consejería de Presidencia y Justicia','Minister of Economy and Finance':'Consejería de Economía y Hacienda','Minister of Transport and Infrastructures':'Consejería de Transportes e Infraestructuras','Minister of Education and Employment':'Consejería de Educación y Empleo','Minister of Environment and Territory Planning':'Consejería de Medio Ambiente y Ordenación del Territorio','Minister of Health':'Consejería de Sanidad','Minister of Social Affairs':'Consejería de Asuntos Sociales',
 'Minister of the Presidency, Justice and Spokesperson of the Government':'Consejería de Presidencia, Justicia y Portavocía del Gobierno','Minister of Transport, Infrastructures and Housing':'Consejería de Transportes, Infraestructuras y Vivienda','Minister of Education, Youth and Sports':'Consejería de Educación, Juventud y Deporte','Minister of the Environment and Territory Planning':'Consejería de Medio Ambiente y Ordenación del Territorio','Minister of Employment, Tourism and Culture':'Consejería de Empleo, Turismo y Cultura',
 'Minister of Economy, Employment and Finance':'Consejería de Economía, Empleo y Hacienda','Minister of the Environment, Local Administration and Territory Planning':'Consejería de Medio Ambiente, Administración Local y Ordenación del Territorio','Minister of Social Policies and Family':'Consejería de Políticas Sociales y Familia','Minister of Transport, Housing and Infrastructures':'Consejería de Transportes, Vivienda e Infraestructuras','Minister of Education and Research':'Consejería de Educación e Investigación','Minister of Culture, Tourism and Sports':'Consejería de Cultura, Turismo y Deporte',
 'Vice President, Minister of the Presidency and Spokesperson of the Government':'Vicepresidencia, Presidencia y Portavocía del Gobierno','Minister of Justice':'Consejería de Justicia',
 'Vice President, Minister of Sports and Transparency and Spokesperson of the Government':'Vicepresidencia, Deportes, Transparencia y Portavocía del Gobierno','Minister of the Presidency':'Consejería de Presidencia','Minister of Justice, Interior and Victims':'Consejería de Justicia, Interior y Víctimas','Minister of Finance and Civil Service':'Consejería de Hacienda y Función Pública','Minister of Economy, Employment and Competitiveness':'Consejería de Economía, Empleo y Competitividad','Minister of Housing and Local Administration':'Consejería de Vivienda y Administración Local','Minister of the Environment, Territory Planning and Sustainability':'Consejería de Medio Ambiente, Ordenación del Territorio y Sostenibilidad','Minister of Social Policies, Families, Equality and Natality':'Consejería de Políticas Sociales, Familias, Igualdad y Natalidad','Minister of Transport, Mobility and Infrastructures':'Consejería de Transportes, Movilidad e Infraestructuras','Minister of Education and Youth':'Consejería de Educación y Juventud','Minister of Science, Universities and Innovation':'Consejería de Ciencia, Universidades e Innovación','Minister of Culture and Tourism':'Consejería de Cultura y Turismo','Minister of Sports and Transparency':'Consejería de Deportes y Transparencia','Spokesperson of the Government':'Portavocía del Gobierno','Vice President':'Vicepresidencia',
 'Minister of the Presidency, Justice and Interior':'Consejería de Presidencia, Justicia e Interior','Minister of Education, Universities, Science and Spokesperson':'Consejería de Educación, Universidades, Ciencia y Portavocía','Minister of the Environment, Housing and Agriculture':'Consejería de Medio Ambiente, Vivienda y Agricultura','Minister of Economy, Finance and Employment':'Consejería de Economía, Hacienda y Empleo','Minister of Family, Youth and Social Policy':'Consejería de Familia, Juventud y Política Social','Minister of Local Administration and Digitalization':'Consejería de Administración Local y Digitalización','Vice President, Minister of Education and Universities':'Vicepresidencia y Consejería de Educación y Universidades',
 'Minister of the Presidency, Justice and Local Administration and Spokesperson':'Consejería de Presidencia, Justicia y Administración Local y Portavocía','Minister of Digitalization':'Consejería de Digitalización','Minister of Education, Universities, Science':'Consejería de Educación, Ciencia y Universidades','Minister of the Housing, Transport and Infrastructures':'Consejería de Vivienda, Transportes e Infraestructuras','Minister of Environment, Agriculture and Interior':'Consejería de Medio Ambiente, Agricultura e Interior',
}
def english_date(value):
    if value in ['Incumbent','Present','present']:return None
    return datetime.datetime.strptime(value,'%d %B %Y').date().isoformat()
def level(role):return 'president' if role.startswith('Presidencia de') or role=='Presidencia' else 'vice' if role.startswith('Vicepresidencia') else 'minister'

if __name__=='__main__':
    annex=BeautifulSoup((CACHE/'cache/gobiernos-wiki.html').read_text(encoding='utf-8'),'html.parser')
    early=[('Leguina I','1983-06-14','Joaquín Leguina Herrán','BOE-A-1983-16666',0),('Leguina II','1987-07-20','Joaquín Leguina Herrán','BOE-A-1987-17054',1),('Leguina III','1991-07-12','Joaquín Leguina Herrán','BOE-A-1991-18122',2),('Ruiz-Gallardón I','1995-06-29','Alberto Ruiz-Gallardón Jiménez','BOE-A-1995-15897',3),('Ruiz-Gallardón II','1999-07-07','Alberto Ruiz-Gallardón Jiménez','BOE-A-1999-15036',4),('Aguirre I','2003-11-20','Esperanza Aguirre Gil de Biedma','BOE-A-2003-21196',6),('Aguirre II','2007-06-19','Esperanza Aguirre Gil de Biedma',None,7)]
    result=[]
    for label,start,president,boe,tableid in early:
        source=f'https://www.boe.es/diario_boe/txt.php?id={boe}' if boe else 'https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=aut_investidura_16'
        roles=[]
        for cells in expanded(annex.select('table.wikitable')[tableid])[1:]:
            if len(cells)<2:continue
            role=text(cells[0]).rstrip("'");value=text(cells[1])
            if role=='Presidencia' or not value:continue
            # Un cuadro puede publicar dos nombres dentro de una sola celda.
            parts=re.split(r'(?<=\))\s+(?=[A-ZÁÉÍÓÚ])',value)
            for part in parts:
                name=full_name(part)
                if re.search(r'\b(?:hasta|desde|además|ademas)\b',name):continue
                roles.append({'name':name,'role':role,'level':level(role),'start':None,'end':None,'period':f'Etapa {label} · '+(re.search(r'\((.*?)\)',part)[1] if '(' in part else 'intervalo diario pendiente de contraste'),'source':ANNEX})
        result.append({'id':'madrid-gobierno-'+norm(label).replace(' ','-'),'label':label,'name':full_name(president),'start':start,'end':None,'source':source,'terms':[{'name':full_name(president),'role':'Presidencia de la Comunidad de Madrid','level':'president','start':start,'end':None,'source':source}],'archiveTerms':roles,'incidents':['Las consejerías de esta etapa proceden del cuadro histórico de composición. Se conservan los cargos publicados, pero no se inventan fechas diarias de alta o cese ni se dibujan como un gabinete simultáneo.']})
    modern=read(CACHE/'cabinets-en.json');pdfs=read(CACHE/'decrees-read.json');pdf_by_url={p['url']:p for p in pdfs};verification=[]
    labels=['Aguirre III','González','Cifuentes / Garrido en funciones','Garrido / Rollán en funciones','Díaz Ayuso I','Díaz Ayuso II','Díaz Ayuso III']
    for (article,url,tables),label in zip(modern,labels):
        page=q.soup(url);terms=[]
        rows=expanded(BeautifulSoup(tables[0],'html.parser'))
        for cells in rows:
            if len(cells)!=7:continue
            portfolio,name=text(cells[0]),text(cells[1]);starttext,endtext=text(cells[4]),text(cells[5])
            if not re.match(r'^\d+ [A-Z][a-z]+ \d{4}$',starttext):continue
            if portfolio not in ROLES:raise ValueError('Competencia sin traducción: '+portfolio)
            source=url;cit=cells[-1].select_one('a[href^="#cite_note"]')
            if cit:
                note=page.select_one(cit['href']);a=note.select_one('a.external[href*="bocm.es"]') if note else None
                if a:
                    p=pdf_by_url.get(a['href']);full=full_name(name)
                    normalized=re.sub(r'[^a-z0-9]','',norm((p or {}).get('text','')))
                    named=re.sub(r'[^a-z0-9]','',norm(full))
                    verified=bool(p and (named in normalized or re.sub(r'[^a-z0-9]','',norm(name)) in normalized))
                    verification.append({'name':full,'role':ROLES[portfolio],'url':a['href'],'personMentionVerified':verified})
                    if verified:source=a['href']
            role=ROLES[portfolio]
            terms.append({'name':full_name(name),'role':role,'level':level(role),'start':english_date(starttext),'end':english_date(endtext),'source':source,'chronologySource':url,'endBasis':'Límite del cuadro histórico de composición; conserva suplencias hasta el siguiente gabinete.'})
        if not terms:raise ValueError('Gabinete sin cargos: '+article)
        start=min(t['start'] for t in terms);end=max(t['end'] for t in terms if t['end']) if any(t['end'] for t in terms) else None
        result.append({'id':'madrid-gobierno-'+norm(label).replace(' ','-'),'label':label,'name':next(t['name'] for t in terms if t['level']=='president'),'start':start,'end':end,'source':url,'terms':terms,'archiveTerms':[],'incidents':['Nombramientos enlazados al BOCM cuando el documento confirma a la persona. La cronología complementaria procede del cuadro histórico; se distingue de la fecha de firma del decreto y de la toma de posesión.']})
    # Suplencias documentadas, conservando a la misma persona una sola vez en el árbol.
    additions=[(7,'Jaime Ignacio González González','Presidencia en funciones','2012-09-17','2012-09-27'),(7,'Regina María Plañiol de Lacalle','Transportes e Infraestructuras · despacho ordinario','2011-12-24','2012-01-25'),(8,'Javier Hernández Martínez','Presidencia, Justicia y Portavocía · funciones','2015-06-08','2015-06-26'),(8,'Manuel Pérez Gómez','Educación, Juventud y Deporte · funciones','2015-06-08','2015-06-26'),(9,'Ángel Garrido García','Presidencia en funciones','2018-04-25','2018-05-19'),(10,'Pedro Rollán Ojeda','Presidencia en funciones','2019-04-11','2019-08-17')]
    for i,name,role,start,end in additions:result[i]['terms'].append({'name':full_name(name),'role':role,'level':'president' if role.startswith('Presidencia en') else 'minister','start':start,'end':end,'source':result[i]['source'],'endBasis':'Suplencia expresamente documentada en el cuadro de composición.'})
    for cells in expanded(BeautifulSoup(modern[4][2][0],'html.parser')):
        if len(cells)<2:continue
        value=text(cells[1]);portfolio=text(cells[0])
        m=re.match(r'(.*?) served as surrogate from (.*?) to (.*?)\.',value)
        if m:
            start='2021-03-11' if m[2]=='11 March' else '2021-06-08';end='2021-06-21'
            result[11]['terms'].append({'name':full_name(m[1]),'role':ROLES[portfolio]+' · suplencia','level':'minister','start':start,'end':end,'source':modern[4][1],'endBasis':'Suplencia expresamente documentada.'})
    # El cuadro enciclopédico vigente no recoge el relevo de 2026: prevalece el BOCM.
    current=result[-1];edurole='Consejería de Educación, Ciencia y Universidades'
    for term in current['terms']:
        if term['role']==edurole:term['end']='2026-02-16';term['endSource']='https://www.bocm.es/boletin/CM_Orden_BOCM/2026/02/17/BOCM-20260217-1.PDF';term['endBasis']='Cese por Decreto 5/2026 de 16 de febrero.'
    current['terms'].append({'name':'María Mercedes Zarzalejo Carbajo','role':edurole,'level':'minister','start':'2026-02-16','end':None,'source':'https://www.bocm.es/boletin/CM_Orden_BOCM/2026/02/17/BOCM-20260217-2.PDF','dateBasis':'Decreto de nombramiento 7/2026 de 16 de febrero, publicado el 17.'})
    current['source']='https://www.comunidad.madrid/gobierno/equipo-gobierno'
    current['incidents'].append('El nombramiento de Mercedes Zarzalejo está fechado el 16 de febrero de 2026 y publicado el 17; no se utiliza la fecha de noticias posteriores.')
    for i,g in enumerate(result[:-1]):
        g['end']=result[i+1]['start']
        if i<len(early):
            g['end']=result[i+1]['start'];g['terms'][0]['end']=g['end'];g['terms'][0]['endBasis']='Siguiente nombramiento presidencial documentado.'
    result[-1]['end']=None
    result[4]['incidents'].append('La VI legislatura de 2003 no produjo una investidura: el Ejecutivo anterior continuó en funciones hasta noviembre. Las delegaciones de despacho no se convierten en nombramientos de un gabinete nuevo.')
    # Recursos oficiales del gabinete vigente para fichas nuevas sin retrato previo.
    equipo=BeautifulSoup((CACHE/'cache/equipo.html').read_text(encoding='utf-8'),'html.parser');photos=[]
    for h in equipo.select('#main-content h2'):
        heading=h.get_text(' ',strip=True);name=heading.split('. ')[0];im=h.find_next('img')
        official_role=heading.split('. ',1)[1]
        for term in current['terms']:
            if term['name']==full_name(name) and not term['end']:
                term['role']='Presidencia de la Comunidad de Madrid' if term['level']=='president' else re.sub(r'^Consejer[oa] de ', 'Consejería de ',official_role)
        if im:photos.append({'name':full_name(name),'url':im['src'],'source':current['source'],'credit':'Comunidad de Madrid · equipo institucional de Gobierno'})
    write(DEST/'Gobierno/transcripcion.json',result);write(DEST/'fuentes/contraste-nombramientos.json',verification);write(CACHE/'government-photos.json',photos)
    print('Etapas',len(result),'cargos con intervalo',sum(len(g['terms']) for g in result),'cargos de archivo',sum(len(g['archiveTerms']) for g in result),'documentos contrastados',sum(r['personMentionVerified'] for r in verification))
