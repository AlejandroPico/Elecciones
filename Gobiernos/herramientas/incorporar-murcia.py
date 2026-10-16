"""Incorpora Murcia sin proyectar los directorios archivados a fechas no acreditadas.

--plan contrasta identidades sin escribir el catálogo ni las composiciones.
Las fuentes originales de consulta permanecen en test-results/murcia.
"""
import importlib.util,pathlib,json,re,collections,sys
s=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).with_name('catalogo-regional.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.c
c.CACHE=pathlib.Path('test-results/murcia');c.CHECKED='2026-10-16';m.CHECKED=c.CHECKED;CHECKED=c.CHECKED;CACHE=c.CACHE
BASE=pathlib.Path('Gobiernos/Autonomías/Región de Murcia');REGION='murcia';outputs=[]
cat=m.Catalog(revision='2026-10-16-murcia',alias_files=[BASE/'fuentes/identidades-revisadas.json'],portrait_stem='retrato-murcia')
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI']
STARTS=['1983-05-28','1987-07-01','1991-06-14','1995-06-23','1999-06-30','2003-06-19','2007-06-18','2011-06-14','2015-06-15','2019-06-11','2023-06-14']
STAGE_SOURCES={2:'https://www.boe.es/boe/dias/1987/04/14/pdfs/A11165-11165.pdf',3:'https://www.boe.es/diario_boe/txt.php?id=BOE-A-1991-7964',4:'https://www.boe.es/diario_boe/txt.php?id=BOE-A-1995-8136',9:'https://www.borm.es/services/anuncio/731938/pdf',10:'https://www.asambleamurcia.es/tualidad'}

def read(file):return m.load(CACHE/file)
def name(value):
 value=re.sub(r'\s+(?:X\s+)?Causó Baja\b','',value,flags=re.I).replace('Mª','María').replace('M.ª','María')
 value=value.replace('Ramón Luís Valcárcel','Ramón Luis Valcárcel')
 return re.sub(r'\b(De|Del|La|Los|Las|Y)\b',lambda t:t[0].lower(),value)
def resolve(value,source,role):return cat.resolve(name(value),REGION,source,role)
def term(id,role,source,**kw):return {**dict(person=id,name=cat.people[id][1]['fullName'],start=None,end=None,role=role,source=source),**kw}
def unique(rows):return list({r['person']:r for r in reversed(rows)}.values())[::-1]
def stage(section,data):outputs.append((BASE/section/(data['start'][:4]+' '+data['label'])/'composicion.json',data))
def group(label):return re.sub(r'^de\s+','',label or'Adscripción pendiente de contraste').strip().replace('Mixto) 2003-2007','Mixto')
def groups(rows):
 by=collections.defaultdict(list)
 for row in rows:by[row['formationLabel']].append(row)
 return [dict(name=n,source=rs[0]['source'],members=rs)for n,rs in by.items()]
def associate(id,label,period,source):
 label=group(label);org='pp'if label=='Popular'else'psoe'if label=='Socialista'else'vox'if label=='Vox'else'ciudadanos'if label=='Ciudadanos'else'podemos'if label=='Podemos'else None
 if label!='Adscripción pendiente de contraste':cat.group(id,REGION,label,period,source,org)

profile_rows={}
def profiles():
 files=sorted((CACHE/'perfiles').glob('*.json'),key=lambda p:(0 if p.stem.startswith('legacy-')else 1,int(p.stem.split('-')[1])if p.stem.startswith('legacy-')else 12,p.name))
 for file in files:
  r=m.load(file)
  if '/legacy/'in r['source']and not file.name.startswith('legacy-'):continue
  profile_rows[r['source']]=r;id=resolve(r['name'],r['source'],'Asamblea Regional de Murcia');text=r['text'];lines=text.splitlines()
  cat.photo(id,r.get('image'),r['source'],'Asamblea Regional de Murcia · retrato institucional de la etapa documentada')
  for line in lines[:12]:
   education=re.search(r'\b(?:Licenciad[oa]|Diplomad[oa]|Graduad[oa]|Doctor\b|Doctora\b|Máster|Ingenier[oa]|MBA\b|Técnico Superior)[^.\n]*',line)
   if education and 12<len(education[0])<350:
    cat.add(id,'formacion.json',[education[0].strip()]);cat.add(id,'fuentes-formacion.json',[m.ref(r['source'],'Formación publicada por la Asamblea Regional de Murcia')])
   # Un nacimiento debe tener contexto biográfico; nunca usar la fecha de
   # nombramiento, de una comisión, de una agenda o de una intervención.
   if ','not in line or re.search(r'Diputad|[Pp]residen|[Ss]ecretari|[Cc]onsejer|[Dd]esde|[Hh]asta|[Gg]rupo',line):continue
   born=re.search(r'(?<!\d)(\d{1,2})/(\d{1,2})/(\d{4})(?!\d)',line)
   if not born or int(born[3])>2005:continue
   import datetime
   date=datetime.date(int(born[3]),int(born[2]),int(born[1])).isoformat()
   personal=cat.files.get((id,'datos-personales.json'),m.load(cat.people[id][0]/'datos-personales.json',{}))
   if not personal.get('birthDate'):
    place=line.split(',',1)[0].strip();personal.update(birthDate=date,birthPlace=place,birth=place+', '+born[0],personalSources=[*personal.get('personalSources',[]),m.ref(r['source'],'Nacimiento publicado por la Asamblea Regional de Murcia')]);cat.files[id,'datos-personales.json']=personal
  for line in lines[:16]:
   if re.match(r'^(?:Ha sido|Fue |Diputad[oa] (?:regional |a Cortes)|Consejer[oa] |Alcald[ea] |Concejal)',line)and len(line)<550:
    cat.event(id,'cargos-autonomias.json',REGION,line,'Biografía institucional de '+('la legislatura '+ROMANS[r['legislature']-1]if r.get('legislature')else'la ficha consultada'),r['source'])

def row_group(r):
 text=profile_rows.get(r['source'],{}).get('text','')
 if 'Trayectoria parlamentaria:'in text:text=text.split('Trayectoria parlamentaria:',1)[1]
 # Las fichas individuales de Antelo, Martínez García y Marín precisan los
 # cambios de grupo de 2026; el distintivo de la tarjeta puede estar obsoleto.
 match=re.search(r'Diputad[oa](?: regional)? del Grupo Parlamentario\s+(.+?)(?:\s+por la |\s+desde |\s+hasta |[,\.\n]|$)',text,re.I)
 if not match:match=re.search(r'Portavoz(?: adjunt[oa])? del Grupo Parlamentario\s+([^,\.\n]+)',text,re.I)
 return group(match[1]if match else r.get('group'))

def board_from_profiles(n,records):
 out=[]
 for row in records:
  text=profile_rows.get(row['source'],{}).get('text','');head=' '.join(text.splitlines()[:2])
  match=re.search(r'\b(President[ea]|Vicepresident[ea](?: (?:primer[oa]|segund[oa]))?|Secretari[oa] (?:primer[oa]|segund[oa])) de (?:la Mesa de )?la Asamblea Regional',head,re.I)
  if not match:continue
  role=match[1][0].upper()+match[1][1:].lower()+' de la Asamblea Regional de Murcia'
  out.append(term(row['person'],role,row['source'],period='Legislatura '+ROMANS[n-1]+' · cargo descrito en la ficha institucional, sin intervalo diario completo'))
 # En I, la ficha de Collado abre con su posterior presidencia regional;
 # conserva expresamente la presidencia de la Asamblea hasta marzo de 1984.
 if n==1:
  for surname,role in [('Carlos Collado Mena','Presidente'),('Manuel Tera Bueno','Vicepresidente primero')]:
   row=next(r for r in records if r['name']==surname)
   out.append(term(row['person'],role+' de la Asamblea Regional de Murcia',row['source'],period='Legislatura I · anterior al relevo de abril de 1984'))
 if n==8:
  for full,role in [('Alberto Garre López','Vicepresidente primero'),('Pedro Antonio Sánchez López','Vicepresidente segundo')]:
   row=next(r for r in records if r['name']==full);out.append(term(row['person'],role+' de la Asamblea Regional de Murcia',row['source'],period='Legislatura VIII · cargo anterior al nombramiento como miembro del Gobierno regional, descrito en su ficha oficial'))
 return out

def parliaments():
 descriptions=read('etapas-asamblea.json')
 for n in range(1,12):
  d=read(f'parlamentos/{n}.json');label='Legislatura '+ROMANS[n-1];records=[];chosen=[]
  legacy=read('parlamentos/9-legacy.json')if n==9 else None
  for r in [*d['members'],*(legacy['members']if legacy else[])]:
   id=resolve(r['name'],r['source'],'Diputado/a de la Asamblea Regional de Murcia');formation=row_group(r)
   text=profile_rows.get(r['source'],{}).get('text','');district=re.search(r'circunscripción(?: electoral)?\s*(?:número|nº|n\.|n)?\s*(\d)',text,re.I)
   constituency='Región de Murcia'if n>=10 else'Circunscripción '+district[1]+' · Región de Murcia'if district else'Región de Murcia · circunscripción no precisada'
   row=term(id,'Diputado/a de la Asamblea Regional de Murcia',r['source'],formationLabel=formation,constituency=constituency,period=label+' · '+r.get('period','directorio institucional'))
   records.append(row);cat.event(id,'mandatos-autonomias.json',REGION,row['role'],row['period'],r['source']);associate(id,formation,label,r['source'])
   if n==11 and r.get('group')=='Podemos'and formation=='Mixto':
    cat.add(id,'afiliaciones.json',[dict(organization='podemos',name='Podemos',period='Dirección regional documentada en la biografía de la XI legislatura',kind='association',source=m.ref(r['source'],'Trayectoria política publicada por la Asamblea Regional'),territory=REGION)])
   include=not r['ceased']
   # La biografía de Pardo acredita que sustituyó a Ojeda en marzo de 1996;
   # el rótulo de baja 1995-1996 del índice está atribuido al sustituto.
   if n==4 and name(r['name'])=='Ángel Pardo Navarro':include=True
   # El índice coloca el único diputado del Mixto después del epígrafe de
   # bajas, pero su ficha documenta íntegra la VI legislatura (2003-2007).
   if n==6 and name(r['name'])=='Cayetano Jaime Moltó':include=True
   if include and(not legacy or r['source'].startswith('https://www.asambleamurcia.es/legacy/')):chosen.append(row)
   if n==11 and include:cat.active(id,d['source'])
  records=unique(records);chosen=unique(chosen);board=board_from_profiles(n,records)
  source=(legacy or d)['source'];capacity=43 if n==1 else 45
  data=dict(id=f'murcia-parlamento-{n}',label=label,start=STARTS[n-1],end=STARTS[n]if n<11 else None,checkedAt=CHECKED,source=source,currentOnly=n==11,capacity=capacity,records=chosen if n==11 else records,board=[],groups=groups(chosen),note='Archivo nominal de la Asamblea Regional. Las bajas y los relevos se conservan en las fichas personales; el hemiciclo vigente contiene solo titulares actuales. Los grupos publicados no acreditan por sí solos militancia partidista.')
  if n<11:
   data.update(nominalOnly=True,archiveBoard=board,archiveBoardNote='Cargos documentados en las fichas oficiales de esta legislatura. Incluye relevos; no atribuye simultaneidad ni intervalos diarios desconocidos.',archivedComposition=dict(source=source,checkedAt=CHECKED,note=f'Relación agrupada del directorio archivado: {len(chosen)} de {capacity} escaños identificados. No es una reconstrucción diaria ni una asignación física de asientos.',groups=[dict(name=g['name'],source=g['source'],members=[r['person']for r in g['members']])for g in groups(chosen)]))
  else:
   source='https://www.asambleamurcia.es/arm/organos-x'
   board_names=[('Visitación Martínez Martínez','Presidenta'),('Miguel Ángel Miralles González-Conde','Vicepresidente primero'),('Alfonso Martínez Baños','Vicepresidente segundo'),('María del Carmen Ruiz Jódar','Secretaria primera'),('Virginia Lopo Morales','Secretaria segunda')]
   for full,role in board_names:
    id=resolve(full,source,role+' de la Asamblea Regional de Murcia');data['board'].append(term(id,role+' de la Asamblea Regional de Murcia',source,observedAt=CHECKED));cat.event(id,'cargos-autonomias.json',REGION,role+' de la Asamblea Regional de Murcia',label+' · consulta de '+CHECKED,source)
  if n in[9,10]:
   source='https://www.asambleamurcia.es/legacy/es/organos-de-la-asamblea/rectores/mesa.html'if n==9 else'https://www.asambleamurcia.es/arm/organos-x/rectores/mesa'
   p=c.soup(source);body=p.select_one('main')or p.select_one('#contenido')or p
   if n==9:
    text=body.get_text(' ',strip=True);bs=re.findall(r'(Presidenta|Vicepresidenta Primera|Vicepresidente Segundo|Secretario Primero|Secretario Segundo):\s*([^()]+?)\s*\(GP',text,re.I)
   else:
    text=body.get_text(' ',strip=True);bs=re.findall(r'(Presidente|Vicepresidente 1º|Vicepresidenta 2ª|Secretaria 1ª|Secretario 2º):\s*(.+?)(?=\s+(?:Vicepresiden|Secretari)|$)',text)
   for fullrole,full in bs:
    id=resolve(full,source,fullrole+' de la Asamblea Regional de Murcia');board.append(term(id,fullrole+' de la Asamblea Regional de Murcia',source,period=label+' · Mesa archivada por la institución'))
   data['archiveBoard']=list({(r['person'],r['role']):r for r in board}.values())
   if n==10:
    source='https://www.asambleamurcia.es/ACTAS10L/ORGANOS%20DE%20LA%20CAMARA/PLENO/2019/112010-017.pdf'
    for full,role in [('Francisco José Carrera de la Fuente','Secretario primero'),('Emilio Ivars Ferrer','Secretario segundo')]:
     id=resolve(full,source,role+' de la Asamblea Regional de Murcia');row=term(id,role+' de la Asamblea Regional de Murcia',source,period='Mesa acreditada por el acta de 20 de noviembre de 2019');data['archiveBoard'].append(row);cat.event(id,'cargos-autonomias.json',REGION,row['role'],row['period'],source)
  for row in board:cat.event(row['person'],'cargos-autonomias.json',REGION,row['role'],row['period'],row['source'])
  stage('Parlamento',data)
  print('ASAMBLEA',n,len(records),len(chosen),'MESA',len(data.get('archiveBoard',data['board'])),flush=True)

def governments():
 presidencies=read('presidencias.json');presidencies.insert(0,dict(name='Andrés Hernández Ros',date='1982-07-22',source='https://www.asambleamurcia.es/content/periodo-provisional'))
 tables=read('gabinetes-enciclopedicos.json');by_year={1982:[5],1983:[6],1984:[7],1987:[8],1991:[9],1993:[10],1995:[11],1999:[12],2003:[13],2007:[14],2011:[15],2014:[16],2015:[17,18],2017:[19,20],2019:[21],2023:[22]}
 for i,p in enumerate(presidencies):
  start=p['date'];end=presidencies[i+1]['date']if i+1<len(presidencies)else None;id=resolve(p['name'],p['source'],'Presidencia de la Región de Murcia');label='Etapa provisional'if i==0 else'Legislatura '+ROMANS[max(j for j,d in enumerate(STARTS)if d<=start)]+' · '+cat.people[id][1]['name'];president=term(id,'Presidente de la Región de Murcia'if not p['name'].startswith('M')else'Presidenta de la Región de Murcia',p['source'],start=start,end=end,level='president',period=('Investidura del 22 de julio de 1982'if i==0 else'Nombramiento por Real Decreto del '+start))
  archive=[]
  for table in tables:
   if table['index']not in by_year[int(start[:4])]:continue
   for row in table['rows']:
    if len(row)<2 or not re.match(r'Vicepresiden|Consejer|Secretario General',row[0]):continue
    role=row[0];full=row[2]if not row[1]and len(row)>2 else row[1]
    if table['index']==22:continue # La tabla complementaria mantiene cargos y erratas obsoletos en 2026.
    if len(full.split())<2 or full in['Titular','Nombre']:continue
    member=resolve(full,table['source'],role);period=('Etapa provisional'if i==0 else label)+' · relación histórica complementaria; intervalo individual no contrastado'
    archive.append(term(member,role,table['source'],level='vice'if role.startswith('Vicepresiden')else'minister',period=period));cat.event(member,'cargos-autonomias.json',REGION,role,period,table['source'])
  archive=list({(r['person'],r['role']):r for r in archive}.values())
  data=dict(id='murcia-gobierno-'+start,label=label,start=start,end=end,checkedAt=CHECKED,name=cat.people[id][1]['fullName'],source=p['source'],terms=[president],archiveTerms=archive,incidents=['La fecha presidencial corresponde al Real Decreto de nombramiento; no es la fecha de toma de posesión.'if i else'La etapa provisional se inicia aquí con la investidura acreditada por el archivo institucional.','Las relaciones históricas complementarias conservan cargos conocidos; no certifican la composición simultánea de todos los días.'])
  cat.event(id,'cargos-autonomias.json',REGION,president['role'],start+' — '+(end or'actualidad'),p['source'])
  if end is None:
   for row in read('gobierno-vigente.json'):
    member=resolve(row['name'],row['source'],row['role']);data['terms'].append(term(member,row['role'],row['source'],level='minister',observedAt=CHECKED,period='Composición vigente contrastada el '+CHECKED));cat.active(member,row['source']);cat.event(member,'cargos-autonomias.json',REGION,row['role'],'Vigente en la consulta de '+CHECKED,row['source']);cat.photo(member,row.get('image'),row.get('portraitSource',row['source']),row.get('credit','CARM · retrato institucional'))
    if row.get('education'):cat.add(member,'formacion.json',row['education']);cat.add(member,'fuentes-formacion.json',[m.ref(row.get('educationSource',row.get('portraitSource',row['source'])),'Formación institucional')])
   data['preferredDate']=CHECKED;cat.active(id,p['source'])
  stage('Gobierno',data)
  print('GOBIERNO',start,len(archive),len(data['terms']),flush=True)
 outputs.append((BASE/'fuentes/nombramientos-presidenciales.json',presidencies))
 outputs.append((BASE/'fuentes/composicion-vigente.json',read('gobierno-vigente.json')))
 outputs.append((BASE/'fuentes/directorios-asamblea.json',[read(f'parlamentos/{n}.json')for n in range(1,12)]+[read('parlamentos/9-legacy.json')]))

if __name__=='__main__':
 profiles();parliaments();governments()
 c.write(CACHE/'plan-identidades.json',dict(newPeople=cat.new,used=len(cat.used),outputs=len(outputs)))
 if '--plan'in sys.argv:print('PLAN',len(cat.used),'personas',len(cat.new),'nuevas',len(outputs),'archivos',flush=True)
 else:
  cat.save()
  for file,data in outputs:c.write(file,data)
