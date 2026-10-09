"""Transcripción de datos factuales: fuente por cargo y cambios fechados.

Las tablas históricas secundarias se conservan como archivo si no se ha
contrastado la continuidad diaria. El Consell vigente procede del DOGV.
"""
import importlib.util, json, pathlib, re
spec=importlib.util.spec_from_file_location('cv',pathlib.Path(__file__).with_name('consultar-valencia.py'));cv=importlib.util.module_from_spec(spec);spec.loader.exec_module(cv)
DEST=pathlib.Path('Gobiernos/Autonomías/Comunitat Valenciana')
ALIASES={
'Joan Lerma':'Joan Lerma Blasco','Joan Lerma i Blasco':'Joan Lerma Blasco',
'Eduardo Zaplana':'Eduardo Zaplana Hernández-Soro','José Luis Olivas':'José Luis Olivas Martínez',
'Paco Camps':'Francisco Enrique Camps Ortiz','Francisco Camps Ortiz':'Francisco Enrique Camps Ortiz','Francesc Camps Ortiz':'Francisco Enrique Camps Ortiz',
'Ximo Puig i Ferrer':'Ximo Puig Ferrer','Joaquim Francesc Puig i Ferrer':'Ximo Puig Ferrer',
'Felipe Guardiola':'Felipe Guardiola Sellés','Rafael Blasco':'Rafael Blasco Castany','Antonio Birlanga':'Antonio Birlanga Casanova',
'Vicente Llombart':'Vicente Llombart Rosa','Ciprià Ciscar':'Ciprià Ciscar i Casaban','Miguel Ángel Millana':'Miguel Antonio Millana Sansaturio',
'Segundo Bru':'Segundo Bru Parra','Luis Font de Mora':'Luis Font de Mora Montesinos','Vicent Soler':'Vicent Enric Soler Marco',
'Vicent Soler i Marco':'Vicent Enric Soler Marco','Joaquín Colomer':'Joaquín Colomer Sala','Miguel Doménech':'Miguel Doménech Pastor',
'José Joaquín Ripoll':'José Joaquín Ripoll Serrano','Vicent Rambla':'Vicente Rambla Momplet','Manuel Tarancón':'Manuel Tarancón Fandos',
'José Emilio Cervera':'José Emilio Cervera Llavador','Fernando Castelló':'Fernando Castelló Boronat','Àngels Ramón-Llin':'María Angels Ramón-Llin Martínez',
'Maria Àngels Ramón-Llin i Martínez':'María Angels Ramón-Llin Martínez','Fernando Modrego':'Fernando Modrego Caballero','Serafín Castellano':'Serafín Castellano Gómez',
'Carlos González Cepeda':'Carlos Javier González Cepeda','Alejandro Font de Mora':'Alejandro Font de Mora Turón','Gerardo Camps':'Gerardo Camps Devesa',
'Víctor Campos':'Víctor Campos Guinot','Miguel Peralta Viñes':'Miguel Ignacio Peralta Viñes','Milagrosa Martínez':'María Milagrosa Martínez Navarro',
'Juan Gabriel Cotino':'Juan Gabriel Cotino Ferrer','Justo Nieto':'Justo Nieto Nieto','Trinidad Miró':'Trinidad María Miró Mira',
'Manuel Cervera':'Manuel Cervera Taulet','Belén Juste':'María Belén Juste Picón','Bélen Juste':'María Belén Juste Picón',
'Angélica Such':'Angelica Gemma Such Ronda','Paula Sánchez de León':'Paula Sánchez De León Guardiola',
'Isabel Bonig Trigueros':'Isabel Plácida Bonig Trigueros','Isabel Plácida Bonig i Trigueros':'Isabel Plácida Bonig Trigueros',
'Manuel Llombart Fuertes':'Manuel María Llombart Fuertes','Pilar Pedraza':'Pilar Pedraza Martínez','Luis Berenguer Fuster':'Luis Francisco Berenguer Fuster',
'Emèrit Bono i Martínez':'Emérito Bono Martínez','Antoni Escarré Esteve':'Antonio Escarré Esteve','Josep Maria Coll i Comín':'José María Coll Comín',
'Carlos Mazón Guixot':'Carlos Arturo Mazón Guixot',
'Aitana Joana Mas i Mas':'Aitana Joana Mas Mas','Carmen Más Rubio':'María del Carmen Mas Rubio','Fernando de Rosa':'Fernando De Rosa Torner','Francisco Javier Sanahuja Sanchis':'F. Javier Sanahuja Sanchis','Gabriela Bravo Sanestanislao':'Gabriela Bravo San Estanislao','José María Coll Comín':'Josep María Coll Comín','María José Català Verdet':'María José Catalá Verdet','Manuel Alcaraz Ramos':'Manuel Francisco Alcaraz Ramos','Mario Flores Lanuza':'Mario Francisco José Flores Lanuza','María Ángela Cano García':'Marian Cano García','Máximo Buch Torralva':'Máximo Hartwig Buch Torralva','Rosa Pérez Garijo':'Rosa María Pérez Garijo','Víctor Campos Guinot':'José Víctor Campos Guinot','Aurelio Martínez Estévez':'Aurelio Martínez Esteve',
}
translations={
'Président de la Généralité':'President de la Generalitat','Président':'President de la Generalitat',
'Premier vice-président':'Vicepresidente primero','Première vice-présidente':'Vicepresidenta primera','Seconde vice-présidente':'Vicepresidenta segunda','Second vice-président':'Vicepresidente segundo','Deuxième vice-présidente':'Vicepresidenta segunda','Deuxième vice-président':'Vicepresidente segundo','Troisième vice-président':'Vicepresidente tercero','Vice-présidente':'Vicepresidenta','Vice-président':'Vicepresidente',
'Conseillère':'Consellera','Conseiller':'Conseller','Porte-parole du conseil':'Portavoz del Consell','porte-parole':'portavoz','secrétaire du Conseil':'secretario del Consell','Secrétaire':'Secretaria','du conseil':'del Consell','du Conseil':'del Consell',
'à la ':'de ','aux ':'de ','au ':'de ',"à l'":'de ',"à l’":'de ',
'Économie durable':'Economía Sostenible','Économie':'Economía','Finances':'Hacienda','Administration publique':'Administración Pública','Administrations publiques':'Administraciones Públicas',
'Travaux publics':'Obras Públicas','Urbanisme':'Urbanismo','Transports':'Transportes','Infrastructure':'Infraestructura','Infrastructures':'Infraestructuras',
'Culture':'Cultura','Éducation':'Educación','Science':'Ciencia','Santé universelle':'Sanidad Universal','Santé publique':'Salud Pública','Santé':'Sanidad',
'Travail':'Trabajo','Sécurité sociale':'Seguridad Social','Consommation':'Consumo','Industrie':'Industria','Commerce':'Comercio','Tourisme':'Turismo','Agriculture':'Agricultura','Pêche':'Pesca','Alimentation':'Alimentación','Environnement':'Medio Ambiente','Présidence':'Presidencia','Intérieur':'Interior','Justice':'Justicia','Emploi':'Empleo','Bien-être social':'Bienestar Social','Innovation':'Innovación','Compétitivité':'Competitividad','Sports':'Deportes','Sport':'Deporte','Entreprises':'Empresa','Enseignement supérieur':'Universidades','Relations institutionnelles':'Relaciones Institucionales','Communication':'Comunicación','Coopération':'Cooperación','Participation':'Participación','Territoire':'Territorio','Logement':'Vivienda','Eaux':'Agua','Eau':'Agua','Immigration':'Inmigración','Citoyenneté':'Ciudadanía','Formation':'Formación','Égalité':'Igualdad','Politiques inclusives':'Políticas Inclusivas','Modèle économique':'Modelo Económico','Réformes démocratiques':'Reformas Democráticas','Libertés publiques':'Libertades Públicas','Recherche':'Investigación','Secteurs productifs':'Sectores Productivos','Changement climatique':'Cambio Climático','Développement rural':'Desarrollo Rural','Structuration du territoire':'Vertebración del Territorio','Transparence':'Transparencia','Responsabilité sociale':'Responsabilidad Social','Architecture bioclimatique':'Arquitectura Bioclimática','Urgence climatique':'Emergencia Climática','Transition écologique':'Transición Ecológica','Politique territoriale':'Política Territorial','Mobilité':'Movilidad','Société numérique':'Sociedad Digital','Qualité démocratique':'Calidad Democrática','Services sociaux':'Servicios Sociales','Élevage':'Ganadería','Reconstruction économique et sociale':'Recuperación Económica y Social','Communauté valencienne':'Comunitat Valenciana','Urgences':'Emergencias','Famille':'Familia','Enfance':'Infancia','Jeunesse':'Juventud','Reconstruction':'Recuperación',' et ':' y '," et à l'":' y de ',' et aux ':' y de ',' et au ':' y de ',' et à la ':' y de ', 'a.i.':'(en funciones)', 'par intérim':'en funciones'
}
def translate(role):
    for a,b in sorted(translations.items(),key=lambda x:-len(x[0])):role=role.replace(a,b)
    return role

def translate_heading(heading):
    months={'janvier':'enero','février':'febrero','mars':'marzo','avril':'abril','mai':'mayo','juin':'junio','juillet':'julio','août':'agosto','septembre':'septiembre','octobre':'octubre','novembre':'noviembre','décembre':'diciembre'}
    heading=heading.replace('Initiale','Composición inicial').replace('Remaniement du','Reorganización del').replace('Ajustement du','Ajuste del').replace('Composition','Composición')
    for french,spanish in months.items():
        heading=re.sub(r'(\d+) '+french+r' (\d{4})',r'\1 de '+spanish+r' de \2',heading)
    return heading
def role_level(role):return 'vice' if 'Vicepresiden' in role else 'president' if role.startswith('President de') else 'minister'
def member(name,role,start=None,end=None,source=None,period=None):
    name=ALIASES.get(name,name)
    return {'name':name,'role':role,'level':role_level(role),'start':start,'end':end,'source':source,**({'period':period} if period else {})}

stages=[('Lerma_I','Lerma I','1983-06-28'),('Lerma_II','Lerma II','1987-07-27'),('Lerma_III','Lerma III','1991-07-15'),('Zaplana_I','Zaplana I','1995-07-04'),('Zaplana_II','Zaplana II','1999-07-21'),('Olivas','Olivas','2002-07-24'),('Camps_I','Camps I','2003-06-20'),('Camps_II','Camps II','2007-06-27'),('Camps_III','Camps III','2011-06-21'),('Fabra','Fabra','2011-07-28'),('Puig_I','Puig I','2015-06-28'),('Puig_II','Puig II','2019-06-16'),('Mazón','Mazón','2023-07-17'),('Pérez_Llorca','Pérez Llorca','2025-12-02')]
presidents=['Joan Lerma Blasco']*3+['Eduardo Zaplana Hernández-Soro']*2+['José Luis Olivas Martínez']+['Francisco Enrique Camps Ortiz']*3+['Alberto Fabra Part']+['Ximo Puig Ferrer']*2+['Carlos Arturo Mazón Guixot','Juan Francisco Pérez Llorca']
cabinet_map={c['name']:c for c in json.loads((cv.CACHE/'cabinets.json').read_text('utf8'))}
governments=[]
for i,(key,label,start) in enumerate(stages):
    end=stages[i+1][2] if i+1<len(stages) else None
    source=cabinet_map.get(key,{}).get('source') or json.loads((cv.CACHE/('cabinet-'+{'Lerma_II':'II','Lerma_III':'III','Zaplana_I':'IV'}[key]+'.json')).read_text('utf8'))['source']
    g={'id':'valencia-consell-'+str(i+1),'label':label,'name':'Consell de la Generalitat Valenciana','start':start,'end':end,'source':source,'terms':[member(presidents[i],'President de la Generalitat',start,end,source)],'archiveTerms':[],'incidents':[]}
    if key=='Pérez_Llorca':
        g['source']='https://www.gva.es/es/web/generalitat/el-consell';g['terms'][0]['source']='https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-24162'
        roles=[('Susana Camarero Benítez','Vicepresidenta primera y consellera de Vivienda, Empleo, Juventud e Igualdad'),('José Luis Díez Climent','Vicepresidente segundo, conseller de Presidencia y secretario del Consell'),('Vicente Martínez Mus','Vicepresidente tercero y conseller de Medio Ambiente, Infraestructuras, Territorio y de la Recuperación'),('José Antonio Rovira Jover','Conseller de Economía, Hacienda y Administración Pública'),('Marciano Gómez Gómez','Conseller de Sanidad'),('Elena Albalat Aguilella','Consellera de Servicios Sociales, Familia e Infancia'),('Maria del Carmen Ortí Ferre','Consellera de Educación, Cultura y Universidades'),('Miguel Barrachina Ros','Conseller de Agricultura, Agua, Ganadería y Pesca y portavoz del Consell'),('Nuria Martínez Sanchis','Consellera de Justicia, Transparencia y Participación'),('Juan Carlos Valderrama Zurián','Conseller de Emergencias e Interior'),('Marian Cano García','Consellera de Industria, Turismo, Innovación y Comercio')]
        g['terms'] += [member(n,r,'2025-12-04',None,'https://dogv.gva.es/datos/2025/12/03/pdf/2025_49244_es.pdf') for n,r in roles]
        g['incidents']=['Nombramiento del president: BOE de 29 de noviembre de 2025; toma de posesión: 2 de diciembre. Los nombramientos de las consellerias producen efectos el 4 de diciembre de 2025, según la disposición final del Decreto 17/2025. La composición vigente se contrasta con el portal de la Generalitat.']
    elif key in ['Lerma_II','Lerma_III','Zaplana_I']:
        data=json.loads((cv.CACHE/('cabinet-'+{'Lerma_II':'II','Lerma_III':'III','Zaplana_I':'IV'}[key]+'.json')).read_text('utf8'))
        # Solo tabla de cargos, excluyendo infotaulas y plantillas de navegación.
        for row in data['tables'][0][2:]:
            if not row:continue
            role=row[0]
            for value in row[1:]:
                n=re.sub(r'\s*\([^)]*\)','',value).strip()
                if not n or n in ['Dissolta','No existeix']:continue
                ca={'Economia i Hisenda':'Economía y Hacienda','Administració Pública':'Administración Pública','Obres Públiques, Urbanisme i Transports':'Obras Públicas, Urbanismo y Transportes','Cultura, Educació i Ciència':'Cultura, Educación y Ciencia','Cultura':'Cultura','Educació i Ciència':'Educación y Ciencia','Sanitat i Consum':'Sanidad y Consumo','Treball i Seguretat Social':'Trabajo y Seguridad Social','Treball i Afers Socials':'Trabajo y Asuntos Sociales','Indústria, Comerç i Turisme':'Industria, Comercio y Turismo','Indústria i Comerç':'Industria y Comercio','Agricultura, Pesca i Alimentació':'Agricultura, Pesca y Alimentación','Medi Ambient':'Medio Ambiente','Presidència':'Presidencia','Ocupació, Indústria i Comerç':'Empleo, Industria y Comercio','Benestar Social':'Bienestar Social','Agricultura i Medi Ambient':'Agricultura y Medio Ambiente'}
                title='Conseller/a de '+ca.get(role,role)
                g['archiveTerms'].append(member(n,title,None,None,source,'Etapa '+label+' · fechas individuales pendientes de contraste'))
        g['incidents']=['Las consejerías históricas de esta etapa están documentadas en una fuente secundaria. Se conserva el listado con su referencia, sin atribuirle un intervalo diario ni una composición simultánea.']
    else:
        # Composiciones sucesivas fechadas en las fuentes; conservar como registro
        # de observaciones, no convertir observaciones en ceses personales.
        c=cabinet_map[key]
        for table in c['tables']:
            for row in table['rows'][1:]:
                if len(row)<3:continue
                role=row[0];n=row[-2]
                if not role or not n or role.startswith('Président'):continue
                # Las celdas con sucesiones de nombres se desglosan expresamente.
                parts=re.split(r'\s*\(jusqu[^)]*\)\s*',n)
                for part in parts:
                    person=re.sub(r'\s*\([^)]*\)|\s+a\.i\.$','',part).strip()
                    if not person:continue
                    r=translate(role);r=re.sub(r'\s*\([^)]*\)','',r).strip()
                    item=member(person,r,None,None,source,translate_heading(table['heading'])+' · composición histórica documentada')
                    if not any(x['name']==item['name'] and x['role']==item['role'] for x in g['archiveTerms']):g['archiveTerms'].append(item)
        g['incidents']=['Las consejerías y sus reorganizaciones se conservan en el archivo de la etapa. La fuente secundaria documenta composiciones y cambios; el intervalo diario de cada nombramiento sigue pendiente de contraste con el DOGV.']
    governments.append(g)
# Reconstrucción diaria del Consell reciente desde los efectos de los decretos,
# que no siempre coinciden con su firma, publicación ni toma de posesión.
g=governments[-2];g['archiveTerms']=[];g['source']='https://dogv.gva.es/datos/2023/07/19/pdf/2023_8241.pdf'
nom23=g['source'];jul24='https://dogv.gva.es/datos/consolidacion/2024/2024_7011_20240717_es.pdf';nov24='https://dogv.gva.es/datos/2024/11/22/pdf/2024_12367_es.pdf';nov25='https://dogv.gva.es/datos/2025/11/04/pdf/2025_45304_es.pdf';dec25='https://dogv.gva.es/datos/2025/12/03/pdf/2025_49244_es.pdf'
def term(n,r,s,e,url,end_source=None):
    t=member(n,r,s,e,url)
    if end_source:t['endBasis']=end_source
    g['terms'].append(t)
term('Vicente José Barrera Simó','Vicepresidente primero y conseller de Cultura y Deporte','2023-07-20','2024-07-11',nom23,'https://dogv.gva.es/datos/2024/07/11/pdf/2024_6992_es.pdf')
term('Susana Camarero Benítez','Vicepresidenta segunda, consellera de Servicios Sociales, Igualdad y Vivienda y secretaria del Consell','2023-07-20','2024-07-12',nom23,jul24)
term('Ruth María Merino Peña','Consellera de Hacienda, Economía y Administración Pública y portavoz del Consell','2023-07-20','2024-11-22',nom23,nov24)
term('Elisa María Núñez Sánchez','Consellera de Justicia e Interior','2023-07-20','2024-07-11',nom23,'https://dogv.gva.es/datos/2024/07/11/pdf/2024_6992_es.pdf')
term('Marciano Gómez Gómez','Conseller de Sanidad','2023-07-20','2025-12-03',nom23,dec25)
term('José Antonio Rovira Jover','Conseller de Educación, Universidades y Empleo','2023-07-20','2024-07-12',nom23,jul24)
term('José Luis Aguirre Larrauri','Conseller de Agricultura, Ganadería y Pesca','2023-07-20','2024-07-11',nom23,'https://dogv.gva.es/datos/2024/07/11/pdf/2024_6992_es.pdf')
term('Salomé Pradas Ten','Consellera de Medio Ambiente, Agua, Infraestructuras y Territorio','2023-07-20','2024-07-12',nom23,jul24)
term('Nuria Montes de Diego','Consellera de Innovación, Industria, Comercio y Turismo','2023-07-20','2024-11-22',nom23,nov24)
term('Susana Camarero Benítez','Vicepresidenta y consellera de Servicios Sociales, Igualdad y Vivienda y secretaria del Consell','2024-07-12','2024-11-22',jul24,nov24)
term('Salomé Pradas Ten','Consellera de Justicia e Interior','2024-07-12','2024-11-22',jul24,nov24)
term('José Antonio Rovira Jover','Conseller de Educación, Cultura, Universidades y Empleo','2024-07-12','2025-12-03',jul24,dec25)
term('Miguel Barrachina Ros','Conseller de Agricultura, Agua, Ganadería y Pesca','2024-07-12','2025-12-03',jul24,dec25)
term('Vicente Martínez Mus','Conseller de Medio Ambiente, Infraestructuras y Territorio','2024-07-12','2025-11-04',jul24,nov25)
term('Susana Camarero Benítez','Vicepresidenta primera y consellera de Servicios Sociales, Igualdad y Vivienda, secretaria y portavoz del Consell','2024-11-23','2025-12-03',nov24,dec25)
term('Francisco José Gan Pampols','Vicepresidente segundo y conseller para la Recuperación Económica y Social','2024-11-23','2025-11-04',nov24,nov25)
term('Ruth María Merino Peña','Consellera de Hacienda y Economía','2024-11-23','2025-12-03',nov24,dec25)
term('Nuria Martínez Sanchis','Consellera de Justicia y Administración Pública','2024-11-23','2025-12-03',nov24,dec25)
term('Juan Carlos Valderrama Zurián','Conseller de Emergencias e Interior','2024-11-23','2025-12-03',nov24,dec25)
term('Marian Cano García','Consellera de Innovación, Industria, Comercio y Turismo','2024-11-23','2025-12-03',nov24,dec25)
term('Vicente Martínez Mus','Vicepresidente segundo y conseller para la Recuperación Económica y Social y de Medio Ambiente, Infraestructuras y Territorio','2025-11-05','2025-12-03',nov25,dec25)
g['incidents']=['Los nombramientos de 2023 surten efecto el 20 de julio; los ceses de los tres miembros de Vox, el 11 de julio de 2024. La reorganización del 12 de julio entra en vigor ese mismo día. Los nombramientos publicados el 22 de noviembre de 2024 y el 4 de noviembre de 2025 producen efecto al día siguiente. Se preservan las vacantes de un día previstas por estos decretos.','El cese de la presidencia no se toma como cese de cada conseller: los cargos que siguen en funciones se documentan hasta el 3 de diciembre de 2025, según el Decreto 17/2025.']
current=governments[-1]
current['terms'].extend(dict(t) for t in g['terms'] if t['level']!='president' and t.get('end')=='2025-12-03')
# La fecha del gabinete no sustituye la toma de posesión del president.
from urllib.parse import quote
academic='https://idus.us.es/bitstreams/52ea4a32-95ce-4880-a17c-142ace05b9a9/download'
def diary(leg,n):return 'https://www.cortsvalencianes.es/publicaciones-CV/obtenerHtmlDS?f_clave_dscv='+quote(leg.ljust(4)+str(n).zfill(5)+'0')+'&idioma=es_ES'
presidential_sources=[
 'https://roderic.uv.es/bitstream/10550/73197/1/1983%20Joan%20Lerma%20primer%20presidente%20GV.pdf',academic,academic,academic,
 diary('V',3),diary('V',140),diary('VI',3),diary('VII',3),diary('VIII',3),diary('VIII',8),
 'https://www.cortsvalencianes.es/sites/default/files/media/file_author/429_461_cronica_marco.pdf',
 'https://www.ces.gva.es/sites/default/files/2019-07/noticia.pdf',
 'https://www.ces.gva.es/sites/default/files/2023-10/ACTIVIDADES%20DEL%20COMIT%C3%89%20REV.112.pdf',
 'https://www.ces.gva.es/sites/default/files/2026-01/IV.%20ACTIVIDADES%20DEL%20COMIT%C3%89%20REV.121.pdf'
]
for g,url in zip(governments,presidential_sources):
 g['terms'][0]['source']=url
 g['incidents'].append('El inicio de la etapa corresponde a la toma de posesión del president, documentada en la fuente de su cargo; no a la formación del gabinete.')
g=governments[4]
g['terms'][0].update(end='2002-07-10',endBasis='https://www.boe.es/diario_boe/txt.php?id=BOE-A-2002-13573')
g['incidents'].append('El cese de Eduardo Zaplana se publicó el 10 de julio de 2002. José Luis Olivas tomó posesión el 24 de julio. No se prolonga el mandato de Zaplana hasta esa fecha ni se atribuye una investidura anterior a Olivas.')
cv.write(DEST/'fuentes/posesiones-presidencia.json',[{'stage':g['label'],'date':g['start'],'source':u,'kind':'academic' if u==academic else 'institutional'} for g,u in zip(governments,presidential_sources)])
cv.write(DEST/'Gobierno/transcripcion.json',governments)
cv.write(DEST/'fuentes/alias-consell.json',[{'name':a,'canonicalName':b,'source':'Contraste nominal con las fichas de Les Corts y la composición de la etapa'} for a,b in ALIASES.items()])
print('Etapas',len(governments),'cargos',sum(len(g['terms'])+len(g['archiveTerms']) for g in governments))
