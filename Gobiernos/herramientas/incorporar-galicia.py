"""Integra Galicia desde los originales revisados. --plan no escribe el catálogo.

Los alias son decisiones nominales explícitas, nunca coincidencias aproximadas.
Los cuadros archivados y las instantáneas con fecha no se convierten en mandatos
diarios. Ejecutar desde la raíz con la caché de consulta en test-results/galicia.
"""
import importlib.util,pathlib,json,re,collections,sys
s=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).with_name('catalogo-regional.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
CACHE=pathlib.Path('test-results/galicia');c=m.c;c.CACHE=CACHE;c.CHECKED='2026-10-16';CHECKED=c.CHECKED
BASE=pathlib.Path('Gobiernos/Autonomías/Galicia');outputs=[]
cat=m.Catalog(revision='2026-10-16-galicia',alias_files=[BASE/'fuentes/identidades-revisadas.json'],portrait_stem='retrato-galicia')
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
def read(f):return m.load(CACHE/f)
def resolve(label,source,role):return cat.resolve(label,'galicia',source,role)
def full(id):return cat.people[id][1]['fullName']
def term(id,role,source,**kw):return {**dict(person=id,name=full(id),start=None,end=None,role=role,source=source),**kw}
def stage(section,data):outputs.append((BASE/section/(data['start'][:4]+' '+data['label'])/'composicion.json',data))
def group(label):
 label=re.sub(r'^(?:G\.P\.|Grupo Parlamentario)\s*(?:do |dos )?','',label).strip()
 if label.startswith('de En Marea'):return 'En Marea'
 return label
def display_role(label):
 return ' '.join(w if w.lower()in ['de','del','la','y','e','do','da']else w[:1].upper()+w[1:]for w in label.split())
def organization(label):
 value=group(label)
 return 'pp'if 'Popular'in value else'psoe'if 'Socialista'in value else'bng'if 'Bloque Nacionalista'in value else None
def associate(id,label,period,source):cat.group(id,'galicia',group(label),period,source,organization(label))
def groups(rows):
 by=collections.defaultdict(list)
 for r in rows:by[r['formationLabel']].append(r)
 return [dict(name=n,source=rs[0]['source'],members=rs)for n,rs in by.items()]
def unique(rows):return list({r['person']:r for r in reversed(rows)}.values())[::-1]

def profiles():
 rows=[]
 for file in sorted((CACHE/'perfiles').glob('*.json')):
  r=m.load(file);text=r['text'];lines=[s.strip()for s in text.splitlines()if s.strip()];name=lines[0]
  id=resolve(name,r['source'],'Parlamento de Galicia');formation=next(s for s in lines if s.startswith('Grupo Parlamentario'))
  constituency=lines[lines.index('Circunscrición electoral:')+1]
  image=next(x['url']for x in r['images']if '/Deputados/'in x['url'])
  cat.photo(id,image,r['source'],'Parlamento de Galicia · retrato institucional')
  cat.active(id,r['source']);associate(id,formation,'XII · composición consultada el '+CHECKED,r['source'])
  biography=text.split('Biografía:',1)[-1].split('Asistencias aos órganos',1)[0].strip()
  # Datos profesionales breves, sin importar teléfonos, correos ni declaraciones.
  for paragraph in biography.split('\n'):
   if re.match(r'^(?:Licenciad[oa]|Diplomad[oa]|Graduad[oa]|Doutor[ae]?|Máster|Enxeñeir[oa])',paragraph)and len(paragraph)<700:
    cat.add(id,'formacion.json',[paragraph]);cat.add(id,'fuentes-formacion.json',[m.ref(r['source'],'Formación publicada por el Parlamento de Galicia')])
  birth=re.search(r'Nacemento:\s*([^\n]+?)\s+-\s+(\d{4})',text)
  if birth:
   personal=cat.files.get((id,'datos-personales.json'),m.load(cat.people[id][0]/'datos-personales.json',{}))
   if not personal.get('birthDate')and not personal.get('birthYear'):
    personal.update(birthYear=int(birth[2]),birthPlace=birth[1],birthNote='Año y lugar publicados por el Parlamento de Galicia; no se precisa el día de nacimiento.',personalSources=[m.ref(r['source'],'Nacimiento publicado por el Parlamento de Galicia')]);cat.files[id,'datos-personales.json']=personal
   if not personal.get('birth')and not personal.get('birthDate')and personal.get('birthYear')==int(birth[2]):
    personal['birth']=birth[1]+' · '+birth[2];cat.files[id,'datos-personales.json']=personal
  extra={}
  if name=='Armando Ojea Bouzo':
   extra['formation']='Democracia Ourensana'
   cat.add(id,'afiliaciones.json',[dict(organization='registro-2351',name='Democracia Ourensana',period='Candidatura electoral de 2024',kind='association',territory='galicia',source=m.ref(r['source'],'Candidatura publicada en la biografía parlamentaria'),note='La biografía institucional documenta la candidatura y su condición de fundador; no se deduce de pertenecer al Grupo Mixto.')])
  rows.append(term(id,'Diputado/a del Parlamento de Galicia',r['source'],formationLabel=group(formation),constituency=constituency,observedAt=CHECKED,**extra))
 assert len(rows)==len({r['person']for r in rows})==75
 return rows

def parliaments(current):
 archives=read('parlamentos-preparados.json')
 for li in archives:
  n=li['legislature'];label='Legislatura '+ROMANS[n-1];records=[];initial=[];board=[]
  for r in li['members']:
   source=r.get('correctionSource')or li['source']+'#page='+str(r['page']);id=resolve(r['name'],source,'Parlamento de Galicia')
   period=label+' · '+('titular inicial documentado'if r['initial']else'incorporación durante la legislatura')
   record=term(id,'Diputado/a del Parlamento de Galicia',source,formationLabel=group(r['group']),period=period)
   records.append(record)
   if r['initial']:initial.append(record)
   cat.event(id,'mandatos-autonomias.json','galicia','Parlamento de Galicia · '+label,period,source);associate(id,r['group'],label,source)
  # IX utiliza la proclamación oficial completa como referencia electoral,
  # separada de una supuesta lista de toma de posesión en la constitución.
  source=li['source'];note='Titulares iniciales identificados en la relación de la Biblioteca. Los relevos constan en el archivo personal; los intervalos individuales no se deducen de fechas erróneas o incompletas.'
  if n==9:
   initial=[];source=li['electedSource'];note='Diputados proclamados electos en el DOG de 7 de noviembre de 2012. Es una referencia electoral, no una certificación de posesión simultánea de los escaños durante toda la legislatura.'
   for r in li['elected']:
    id=resolve(r['name'],source,'Diputado/a proclamado/a electo/a');record=term(id,'Diputado/a proclamado/a electo/a',source,formationLabel=r['group'],constituency=r['constituency'],period='Proclamación electoral de 2012')
    initial.append(record)
    if id not in {x['person']for x in records}:records.append(record)
    associate(id,r['group'],label+' · proclamación electoral',source)
  initial=unique(initial)
  assert len(initial)==(71 if n<=2 else 75),(n,len(initial),[(r['name'],r['formationLabel'])for r in initial])
  for r in li['board']:
   id=resolve(r['name'],li['source'],'Mesa del Parlamento de Galicia')
   board.append(term(id,r['role']+' · Mesa',li['source'],period=label+' · '+r['note']))
   cat.event(id,'cargos-autonomias.json','galicia',r['role']+' · Mesa del Parlamento de Galicia',label+' · '+r['note'],li['source'])
  stage('Parlamento',dict(id=f'galicia-parlamento-{n}',label=label,start=li['constitutionAt'],end=li['dissolutionAt'],checkedAt=CHECKED,source=li['source'],capacity=71 if n<=2 else 75,currentOnly=False,nominalOnly=True,records=unique(records),board=[],groups=[],archiveBoard=board,archiveBoardNote='Personas documentadas en la Mesa, incluidos sus relevos. La relación no representa una Mesa simultánea.',note='Archivo de participantes y relevos de la Biblioteca del Parlamento. Las fechas individuales se conservan en la transcripción de fuentes sin convertir erratas en precisión inventada.',archivedComposition=dict(source=source,checkedAt=CHECKED,note=note,groups=[dict(name=g['name'],source=g['source'],members=[r['person']for r in g['members']])for g in groups(initial)])))
 board=[];mesa=read('mesa-vigente.json')
 for link in mesa['links']:
  if '/Composicion/Deputados/'not in link.get('url',link.get('href','')):continue
  text=link['text'];url=link.get('url',link.get('href'));label,role=text.split('Cargo:',1);surname,first=label.strip().split(',',1)
  name=c.clean(first+' '+surname);role=c.clean(role);id=resolve(name,url,'Mesa del Parlamento de Galicia')
  board.append(term(id,role+' · Mesa',mesa['source'],observedAt=CHECKED));cat.event(id,'cargos-autonomias.json','galicia',role+' · Mesa del Parlamento de Galicia',CHECKED+' · composición vigente consultada',mesa['source'])
 assert len(board)==5,mesa['links']
 stage('Parlamento',dict(id='galicia-parlamento-12',label='Legislatura XII',start='2024-03-18',end=None,checkedAt=CHECKED,source='https://www.parlamentodegalicia.es/Composicion/Organos/1200003',capacity=75,currentOnly=True,records=current,board=board,groups=groups(current),note='Directorio vigente del Pleno y de la Mesa, consultado el 16 de octubre de 2026. No se proyecta a la constitución de 2024.'))
 outputs.append((BASE/'fuentes/relaciones-biblioteca.json',archives))

def governments():
 apps=read('presidencias.json');cab=read('gabinetes-preparados.json');current=read('gobierno-vigente.json');gallery=read('retratos-presidentes.json');leg=[1,2,2,3,4,5,6,7,8,9,10,11,11,12]
 complementary=read('gabinetes-complementarios.json')
 for i,r in enumerate(apps):
  id=resolve(r['name'],r['source'],'Presidente de la Xunta de Galicia');end=apps[i+1]['date']if i+1<len(apps)else None
  label='Legislatura '+ROMANS[leg[i]-1]+(' · González Laxe'if i==2 else' · Rueda'if i==12 else' · Feijóo'if i==11 else' · Fernández Albor'if i==1 else'')
  data=dict(id=f'galicia-gobierno-{i+1}',label=label,name='Xunta de Galicia · '+full(id),start=r['date'],end=end,checkedAt=CHECKED,source=r['source'],terms=[term(id,'Presidente de la Xunta de Galicia',r['source'],start=r['date'],end=end,level='president')],incidents=['La fecha de inicio corresponde al Real Decreto de nombramiento presidencial. Las consejerías solo aparecen en las fechas de las composiciones documentadas; no se prolongan automáticamente durante toda la etapa.'],archiveTerms=[])
  cat.event(id,'cargos-autonomias.json','galicia','Presidente de la Xunta de Galicia',r['date']+' – '+(end or'actualidad'),r['source'])
  for photograph in gallery['rows']:
   if m.norm(full(id))in m.norm(photograph['context'])or(id and 'Gerardo Fernández Albor'in full(id)and'albor.jpg'in photograph['image'])or('González Laxe'in full(id)and'laxe.jpg'in photograph['image']):cat.photo(id,photograph['image'],gallery['source'],'Xunta de Galicia · galería institucional de presidencias')
  for decree in cab:
   if not(r['date']<=decree['date']and(not end or decree['date']<end)):continue
   for member in decree['members']:
    rid=resolve(member['name'],decree['source'],member['role']);row=term(rid,member['role'][0].upper()+member['role'][1:],decree['source'],level='vice'if 'vicepresident'in member['role']else'minister',observedAt=decree['date'])
    data['terms'].append(row);cat.event(rid,'cargos-autonomias.json','galicia',row['role'],'Nombramiento publicado el '+decree['date'],decree['source'])
    if member['name']=='María José Rubio Vidal':cat.add(rid,'fuentes.json',[m.ref('https://www.xunta.gal/dog/Publicados/2005/20050805/Anuncio1C19A_gl.html','Corrección oficial del apellido: Vidal, no Vilar')])
  if i==len(apps)-1:
   for member in current:
    rid=resolve(member['name'],member['source'],member['role']);role=display_role(member['role']);data['terms'].append(term(rid,role,member['source'],level='president'if rid==id else'minister',observedAt=CHECKED));cat.active(rid,member['source'])
    cat.photo(rid,member.get('image'),member['source'],'Xunta de Galicia · retrato institucional')
    cat.event(rid,'cargos-autonomias.json','galicia',role,CHECKED+' · composición vigente consultada',member['source'])
    biography=member.get('biography','').split('\n')[0]
    if biography and len(biography)<900:cat.add(rid,'biografia-institucional.json',[dict(text=biography,source=m.ref(member['source'],'Biografía profesional publicada por la Xunta de Galicia'))])
    for appointment in member['appointments']:cat.add(rid,'fuentes.json',[m.ref(appointment['url'],appointment['title'])])
   # La presidencia fechada no se duplica en la instantánea vigente.
   data['terms']=[t for t in data['terms']if not(t['person']==id and t.get('observedAt'))]
  if i<5:
   suffix=['Fernández Albor I','Fernández Albor II','González Laxe','Fraga I','Fraga II'][i]
   archive=next(a for a in complementary if a['name']=='Gouvernement '+suffix)
   for member in archive['members']:
    rid=resolve(member['name'],archive['source'],member['role'])
    data['archiveTerms'].append(term(rid,member['role'],archive['source'],period=f"{r['date'][:4]} – {end[:4]} · relación histórica complementaria"))
    cat.event(rid,'cargos-autonomias.json','galicia',member['role'],f"{r['date'][:4]} – {end[:4]} · cargo documentado en esta etapa; intervalo individual pendiente",archive['source'])
   data['incidents'].append('Las consejerías anteriores a 1997 se conservan como archivo enciclopédico complementario, incluidos los relevos. Sus fechas individuales necesitan contraste completo con los decretos originales y no se representan como una composición simultánea.')
  snapshots=sorted({t['observedAt']for t in data['terms']if t.get('observedAt')})
  if snapshots:data['preferredDate']=snapshots[-1]
  stage('Gobierno',data)
 outputs.append((BASE/'fuentes/nombramientos-presidenciales.json',apps));outputs.append((BASE/'fuentes/nombramientos-consellerias.json',cab))
 outputs.append((BASE/'fuentes/consejerias-complementarias.json',complementary))

if __name__=='__main__':
 original=c.fetch;assets={}
 for file in CACHE.glob('retratos-*-manifiesto.json'):
  for asset in m.load(file).get('assets',[]):
   p=pathlib.Path(asset['path'])
   if p.exists():assets[asset['url']]=p
 c.fetch=lambda url:assets[url].read_bytes()if url in assets else original(url)
 current=profiles();parliaments(current);governments()
 c.write(CACHE/'plan-identidades.json',dict(newPeople=cat.new,used=len(cat.used),compositions=len(outputs)))
 if '--plan'in sys.argv:print('PLAN',len(cat.used),'personas;',len(cat.new),'nuevas;',len(outputs),'archivos',flush=True)
 else:
  cat.save()
  for p,data in outputs:c.write(p,data)
