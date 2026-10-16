"""Integra La Rioja desde el Parlamento y los cuadros históricos de Transparencia.

--plan resuelve identidades sin escribir fichas ni composiciones. Los listados
archivados no acreditan una fecha común de vigencia de todas las adscripciones.
"""
import importlib.util,pathlib,json,re,collections,sys
s=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).with_name('catalogo-regional.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);c=m.c
c.CACHE=pathlib.Path('test-results/rioja');c.CHECKED='2026-10-16';CHECKED=c.CHECKED;CACHE=c.CACHE
m.CHECKED=CHECKED
BASE=pathlib.Path('Gobiernos/Autonomías/La Rioja');REGION='la-rioja';outputs=[]
cat=m.Catalog(revision='2026-10-16-rioja',alias_files=[BASE/'fuentes/identidades-revisadas.json'],portrait_stem='retrato-rioja')
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI']
MONTHS=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']

def read(file):return m.load(CACHE/file)
def resolve(name,source,role):
 if ','in name:name=c.clean(name.split(',',1)[1]+' '+name.split(',',1)[0])
 return cat.resolve(name,REGION,source,role)
def term(id,role,source,**kw):return {**dict(person=id,name=cat.people[id][1]['fullName'],start=None,end=None,role=role,source=source),**kw}
def stage(section,data):outputs.append((BASE/section/(data['start'][:4]+' '+data['label'])/'composicion.json',data))
def group(label):return re.sub(r'^Grupo Parlamentario\s*(?:del |de |de la )?','',label).replace('VOX','Vox').strip()
def associate(id,label,period,source):
 label=group(label);org='pp'if 'Popular'in label else'psoe'if'Socialista'in label else'vox'if'Vox'in label else'ciudadanos'if'Ciudadanos'in label else None
 cat.group(id,REGION,label,period,source,org)
def unique(rows):return list({r['person']:r for r in reversed(rows)}.values())[::-1]
def groups(rows):
 by=collections.defaultdict(list)
 for r in rows:by[r['formationLabel']].append(r)
 return [dict(name=n,source=rs[0]['source'],members=rs)for n,rs in by.items()]

def profiles():
 # Las primeras fotografías disponibles son las de la etapa en que ejercían.
 files=sorted((CACHE/'perfiles').glob('*.json'),key=lambda p:(int(p.name.split('-')[0]),p.name))
 for file in files:
  r=m.load(file);id=resolve(r['name'],r['source'],'Parlamento de La Rioja');text=r['text'];lines=text.splitlines()
  cat.photo(id,r.get('image'),r['source'],'Parlamento de La Rioja · retrato institucional de la legislatura '+file.name.split('-')[0])
  for line in lines:
   if re.match(r'^(?:Licenciad[oa]|Diplomad[oa]|Graduad[oa]|Doctor[ae]?\b|Máster|Ingenier[oa]|Técnico Superior)',line)and len(line)<350:
    cat.add(id,'formacion.json',[line]);cat.add(id,'fuentes-formacion.json',[m.ref(r['source'],'Formación publicada por el Parlamento de La Rioja')])
  # Solo el encabezado biográfico, nunca fechas de comisiones o contactos.
  head=' '.join(lines[:4]);birth=re.search(r'(\d{1,2}) de (\w+) de (\d{4})',head,re.I)
  date=c.iso(head.replace('.','/'))
  if birth and birth[2].lower()in MONTHS:date=f'{birth[3]}-{MONTHS.index(birth[2].lower())+1:02}-{int(birth[1]):02}'
  if date:
   personal=cat.files.get((id,'datos-personales.json'),m.load(cat.people[id][0]/'datos-personales.json',{}))
   if not personal.get('birthDate'):
    personal.update(birthDate=date,birthNote='Fecha publicada en la biografía del Parlamento de La Rioja.',personalSources=[*personal.get('personalSources',[]),m.ref(r['source'],'Nacimiento publicado por el Parlamento de La Rioja')]);cat.files[id,'datos-personales.json']=personal
   if personal.get('birthDate')==date and not personal.get('birth'):
    birthline=next((line for line in lines[1:4]if c.iso(line.replace('.','/'))==date or re.search(r'\d{1,2} de (?:'+ '|'.join(MONTHS)+r') de \d{4}',line,re.I)),None)
    if birthline:
     personal['birth']=c.clean(birthline)
     if ','in birthline:personal['birthPlace']=birthline.split(',',1)[0].strip()
     cat.files[id,'datos-personales.json']=personal
  biography=re.search(r'Trayectoria política e institucional:\s*([\s\S]+?)(?:Contacto:|Documentos relativos|$)',text)
  if biography:
   for line in biography[1].splitlines():
    line=c.clean(line)
    if not line or len(line)>450:continue
    period=re.search(r'\((?:de |del )?(\d{4}(?: a \d{4})?)\)|desde (\d{4})',line)
    if period:cat.event(id,'cargos-autonomias.json',REGION,line,(period[1]or period[2])+' · biografía de la legislatura '+file.name.split('-')[0],r['source'])
 # Dos fichas individuales fallan en ambos dominios. Retratos contrastados en
 # Commons (autor y licencia de la fotografía, no de la página) y el ayuntamiento.
 alda=read('foto-alda.json');id=resolve('Ángel Alda Pérez','https://www.parlamento-larioja.org/composicion-y-organos/diputados','Diputado del Parlamento de La Rioja')
 cat.photo(id,alda['original'],alda['source'],alda['credit'],license=alda['license'],licenseUrl=alda['licenseUrl'])
 id=resolve('Víctor Manuel Rada Resano','https://quel.org/en/ayuntamiento/','Diputado del Parlamento de La Rioja y alcalde de Quel')
 cat.photo(id,'https://quel.org/wp-content/uploads/2026/01/victor-manuel-rada-fernandodiaz0625-e1724847558600-2-150x150.webp','https://quel.org/en/ayuntamiento/','Ayuntamiento de Quel · retrato de su alcalde; fotografía identificada como Fernando Díaz')

def parliaments():
 originals=[read(f'parlamentos/{n}.json')for n in range(1,12)]
 starts=[min(c.iso(r['text'])for r in d['board'])for d in originals]
 # En II la presidencia fue relevada; el resto de la Mesa acredita 06/07/1987.
 for i,d in enumerate(originals):
  n=i+1;label='Legislatura '+ROMANS[i];records=[];by_name={};source=d['source'];board=[]
  for r in d['members']:
   id=resolve(r['name'],r['source'],'Diputado/a del Parlamento de La Rioja');by_name[m.norm(r['name'])]=id
   formation=group(r['group'])if'cesante'not in r['group'].lower()else'Adscripción pendiente de contraste'
   row=term(id,'Diputado/a del Parlamento de La Rioja',r['source'],formationLabel=formation,constituency='La Rioja',period=label+' · directorio institucional archivado')
   records.append(row);cat.event(id,'mandatos-autonomias.json',REGION,'Parlamento de La Rioja · '+label,row['period'],r['source'])
   if 'cesante'not in r['group'].lower():associate(id,r['group'],label,r['source'])
   if n==11:cat.active(id,source)
  for r in d['board']:
   id=resolve(r['name'],r['source'],r['role']);date=c.iso(r['text']);note='Alta documentada el '+date
   board.append(term(id,r['role'],r['source'],period=note,**(dict(observedAt=CHECKED)if n==11 else{})))
   cat.event(id,'cargos-autonomias.json',REGION,r['role'],label+' · '+note,r['source'])
   previous=re.search(r'Sustituye a:\s*(.+)$',r['text'])
   if previous:
    pid=resolve(previous[1],r['source'],r['role']);board.append(term(pid,r['role'],r['source'],period=label+' · titular anterior al relevo del '+date))
  if n==3:
   proof='https://www.parlamento-larioja.org/recursos-de-informacion/publicaciones-oficiales/boletin-oficial/bopr-3-17c/at_download/file';id=resolve('Leopoldo Virosta Garoz',proof,'Vicepresidente primero de la Diputación General')
   board.append(term(id,'Vicepresidente primero de la Diputación General',proof,period='Cargo acreditado en el boletín de 7 de noviembre de 1991; intervalo individual no precisado'))
   cat.event(id,'cargos-autonomias.json',REGION,'Vicepresidente primero de la Diputación General',label+' · acreditado en noviembre de 1991',proof)
  records=unique(records)
  if n==11:
   chosen=records
  else:
   plenary=read(f'plenos/{n}.json')or dict(source=d['source'],members=[r for r in d['members']if'cesante'not in r['group'].lower()],note='El endpoint del Pleno no responde; se utiliza la relación agrupada del directorio histórico.')
   names={m.norm(r['name'])for r in plenary['members']}|{m.norm(r['name'])for r in d['board']}
   if n==3:names.add(m.norm('Leopoldo Virosta Garoz'))
   chosen=[r for r in records if r['person']in {by_name[k]for k in names if k in by_name}]
  capacity=35 if n==1 else 33
  assert len(chosen)==capacity,(n,len(chosen),capacity)
  data=dict(id=f'la-rioja-parlamento-{n}',label=label,start=starts[i],end=starts[i+1]if n<11 else None,checkedAt=CHECKED,source=source,capacity=capacity,currentOnly=n==11,records=records,board=board if n==11 else[],groups=groups(chosen)if n==11 else[],note='Directorio vigente consultado el 16 de octubre de 2026; no se proyecta a la constitución de 2023.'if n==11 else'Relación nominal institucional archivada y relevos documentados. Las fechas del selector delimitan etapas entre constituciones; no son fechas de baja de cada diputado ni certifican adscripción simultánea.')
  if n<11:data.update(nominalOnly=True,archiveBoard=board,archiveBoardNote='Titulares y relevos acreditados, sin presentarlos como una Mesa simultánea.',archivedComposition=dict(source=plenary['source'],checkedAt=CHECKED,note=('Relación agrupada del directorio histórico; el endpoint del Pleno no responde.'if plenary.get('note')else'Relación archivada del Pleno, completada con la Mesa y sus fuentes.')+' Agrupación documental, sin una fecha común certificada para todas las adscripciones.',groups=[dict(name=g['name'],source=g['source'],members=[r['person']for r in g['members']])for g in groups(chosen)]))
  stage('Parlamento',data)
 outputs.append((BASE/'fuentes/directorios-parlamentarios.json',originals))
 outputs.append((BASE/'fuentes/plenos-archivados.json',[read(f'plenos/{n}.json')for n in range(1,12)if read(f'plenos/{n}.json')]))

def governments():
 archives=read('gabinetes-preparados.json');current=read('gobierno-actual.json');names=['Luis Javier Rodríguez Moroy','Antonio Rodríguez Basulto','José María de Miguel Gil','Joaquín Espert Pérez-Caballero','José Ignacio Pérez Sáenz','José Ignacio Pérez Sáenz',*(['Pedro María Sanz Alonso']*5),'José Ignacio Ceniceros González','Concepción Andreu Rodríguez','Gonzalo Capellán de Miguel']
 legs=[None,None,1,2,2,3,4,5,6,7,8,9,10,11]
 for i,name in enumerate(names):
  a=archives[i]if i<13 else dict(start='2023-06-28',source='https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-15140',members=[])
  start=a['start'];end=archives[i+1]['start']if i<12 else'2023-06-28'if i==12 else None
  id=resolve(name,a['source'],'Presidente/a de La Rioja');label='Etapa provisional · '+('Rodríguez Moroy'if i==0 else'Rodríguez Basulto')if i<2 else'Legislatura '+ROMANS[legs[i]-1]+(' · Espert'if i==3 else' · Pérez Sáenz'if i==4 else'')
  data=dict(id=f'la-rioja-gobierno-{i+1}',label=label,name='Gobierno de La Rioja · '+cat.people[id][1]['fullName'],start=start,end=end,checkedAt=CHECKED,source=a['source'],terms=[term(id,'Presidente/a de La Rioja',a['source'],start=start,end=end,level='president')],incidents=['Fechas de nombramiento y cese transcritas de los cuadros del Portal de Transparencia. No equivalen necesariamente a la fecha de toma de posesión. Las consejerías que continúan en funciones conservan sus propias fechas documentadas.'])
  cat.event(id,'cargos-autonomias.json',REGION,'Presidente/a de La Rioja',start+' – '+(end or'actualidad'),a['source'])
  for member in a['members']:
   rid=resolve(member['name'],a['source'],member['role']);role=member['role'];begin=member['start'];source=a['source']
   if member['name']=='Eva Hita Lorite':
    begin='2019-08-29';source='https://www.boe.es/diario_boe/txt.php?id=BOE-A-2020-1767'
   if role=='Consejo de Presidencia':role='Consejero de Presidencia'
   data['terms'].append(term(rid,role,source,start=begin,end=member['end'],level='vice'if role.lower().startswith('vice')else'minister'))
   cat.event(rid,'cargos-autonomias.json',REGION,role,begin+' – '+member['end'],source)
  if i==13:
   p=c.soup(current['source']);roles=[]
   for h in p.select('h5'):
    heading=c.clean(h.get_text());following=h.find_next_sibling()
    if following and heading in [r['name']for r in current['images']]:roles.append((heading,c.clean(following.get_text(' ',strip=True))))
   assert len(roles)==7,roles
   for name,role in roles:
    rid=resolve(name,current['source'],'Consejero/a de '+role);row=term(rid,'Consejería de '+role,current['source'],observedAt=CHECKED,level='minister');data['terms'].append(row);cat.active(rid,current['source']);cat.event(rid,'cargos-autonomias.json',REGION,row['role'],'Composición consultada el '+CHECKED,current['source'])
   cat.active(id,current['source']);data['preferredDate']=CHECKED
   for image in current['images']:
    if not image['name']:continue
    rid=id if image['name']=='Presidente'else resolve(image['name'],current['source'],'Gobierno de La Rioja')
    cat.photo(rid,image['url'],current['source'],'Gobierno de La Rioja · retrato institucional')
  else:
   snapshots=sorted({r['start']for r in data['terms']if r['start']and r['start']>=start and(not end or r['start']<end)})
   if snapshots:data['preferredDate']=snapshots[1]if len(snapshots)>1 else snapshots[0]
  stage('Gobierno',data)
 outputs.append((BASE/'fuentes/cuadros-gobiernos-anteriores.json',archives))

if __name__=='__main__':
 profiles();parliaments();governments()
 c.write(CACHE/'plan-identidades.json',dict(newPeople=cat.new,used=len(cat.used),outputs=len(outputs)))
 if '--plan'in sys.argv:print('PLAN',len(cat.used),'personas',len(cat.new),'nuevas',len(outputs),'archivos',flush=True)
 else:
  cat.save()
  for file,data in outputs:c.write(file,data)
