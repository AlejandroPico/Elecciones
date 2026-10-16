"""Integra Asturias y Cantabria conservando fichas y distinguiendo archivo e instantánea.

Originales de trabajo: test-results/cantabrico. --plan prepara el informe sin escribir
contenido publicado. Las variantes nominales requieren revisión explícita en fuentes.
"""
import importlib.util,pathlib,json,re,collections,datetime,difflib,sys
s=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).with_name('catalogo-regional.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
CACHE=pathlib.Path('test-results/cantabrico');c=m.c;c.CACHE=CACHE;c.CHECKED='2026-10-16';CHECKED=c.CHECKED
cat=m.Catalog(revision='2026-10-16-cantabrico',alias_files=[f'Gobiernos/Autonomías/{r}/fuentes/identidades-revisadas.json'for r in ['Asturias','Cantabria']],portrait_stem='retrato-cantabrico')
outputs=[];ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
def read(file):return m.load(CACHE/file)
def path(region):return pathlib.Path('Gobiernos/Autonomías')/m.REGIONS[region]
def name(id):return cat.people[id][1]['fullName']
def resolve(label,region,source,role):return cat.resolve(label,region,source,role)
def term(id,role,source,**extra):return dict(person=id,name=name(id),start=None,end=None,role=role,source=source,**extra)
def stage(region,section,data):outputs.append((path(region)/section/(data['start'][:4]+' '+data['label'])/'composicion.json',data))
def groups(records):
 grouped=collections.defaultdict(list)
 for r in records:grouped[r.get('formationLabel')or'Adscripción no publicada'].append(r)
 return [dict(name=n,source=rows[0]['source'],members=rows)for n,rows in grouped.items()]
def ordered(label):
 if ','in label:
  surname,first=label.split(',',1);return c.clean(first+' '+surname)
 return c.clean(label)
def association(id,region,group,period,source):
 label=re.sub(r'^Grupo Parlamentario\s+(?:de\s+)?','',group,flags=re.I)
 code={'PSOE':'psoe','Partido Socialista Obrero Español':'psoe','PP':'pp','Partido Popular':'pp','Popular':'pp','Socialista':'psoe','VOX':'vox','Vox':'vox','IU':'iu','Izquierda Unida':'iu','PODEMOS':'podemos','Podemos Asturies':'podemos','C’S':'ciudadanos','C’s':'ciudadanos','Ciudadanos':'ciudadanos','FAC':'registro-4321','Foro Asturias':'registro-4321','Regionalista':'registro-362','Partido Regionalista de Cantabria':'registro-362'}.get(label)
 cat.group(id,region,group,period,source,code)

def profiles():
 ast={};cant={}
 for file in sorted((CACHE/'asturias-perfiles').glob('*.json')):
  r=m.load(file)
  if not r.get('groups')or not r.get('name')or r['name']=='Diputados y diputadas':continue
  id=resolve(r['name'],'asturias',r['source'],'Junta General del Principado de Asturias');ast[r['key']]=id
  cat.photo(id,r.get('photo'),r['source'],'Junta General del Principado de Asturias · ficha institucional')
  for line in (r.get('biography')or'').splitlines():
   if re.match(r'^(?:Licenciad[oa]|Diplomad[oa]|Graduad[oa]|Doctor[ae]?|Máster|Ingenier[oa]|Técnico Superior)',line)and len(line)<400:
    cat.add(id,'formacion.json',[line.strip()]);cat.add(id,'fuentes-formacion.json',[m.ref(r['source'],'Formación publicada por la Junta General')])
  for group in r['groups']:
   roman=re.match(r'^([IVX]+) Legislatura\s*(.*)',group)
   if roman and roman[2]:association(id,'asturias',roman[2],'Legislatura '+roman[1],r['source'])
 for file in sorted((CACHE/'cantabria-perfiles').glob('*.json')):
  r=m.load(file)
  if '/informacion-general/composicion/' not in r['source'] or 'Legislatura' in r['name']:continue
  id=resolve(ordered(r['name']),'cantabria',r['source'],'Parlamento de Cantabria');cant[r['source']]=id
  photo=r.get('image')
  if photo and '/styles/medium/public/'in photo:
   # El original de la fotografía está publicado con la propia ficha; se conserva sin el estilo de miniatura.
   photo=photo.split('?')[0].replace('/styles/medium/public/','/').removesuffix('.webp')
   # Algunos originales son WebP; en ese caso se emplea el recurso enlazado sin inferir la extensión.
   try:c.fetch(photo)
   except Exception:photo=r['image']
  cat.photo(id,photo,r['source'],'Parlamento de Cantabria · retrato institucional')
  for role in r['roles']:
   organ=role['organ'];period=(role['start']or'Fecha no precisada')+(' – '+role['end']if role['end']else'')
   if organ.startswith('Pleno')or organ.startswith('Mesa del Parlamento'):cat.event(id,'mandatos-autonomias.json','cantabria',role['role']+' · '+organ,period,r['source'])
   elif organ.startswith('Grupo Parlamentario')or organ=='Diputado no adscrito':association(id,'cantabria',organ,period,r['source'])
 return ast,cant

def asturias(ids):
 archives=read('asturias-relaciones-biblioteca.json');electoral=read('asturias-relaciones-electorales.json')
 # El cuadro de resultados de 2011 repite la fecha de 2007. El decreto de convocatoria confirma el 15-06-2011.
 electoral[7]['constitutionAt']='2011-06-15'
 for i,li in enumerate(archives):
  num=li['legislature'];el=electoral[i];records=[];initial=[];board=[]
  for r in li['members']:
   source=li['source']+'#page='+str(r['page']);id=resolve(r['name'],'asturias',source,'Junta General del Principado de Asturias')
   group=r['group'];snapshot_group=group.split('/GPM')[0];initial_row=r['initial']
   # La relación general imprime en redonda a Diana Camafeita en VII; el cuadro electoral de VII solo incluye los otros cuatro titulares de IU.
   if num==7 and r['name']=='Diana Camafeita Fernández':initial_row=False
   period=el['label']+(' · titular inicial'if initial_row else' · incorporación durante la legislatura')
   cat.event(id,'mandatos-autonomias.json','asturias','Junta General · '+el['label'],period,source);association(id,'asturias',group,el['label'],source)
   records.append(term(id,'Diputado/a de la Junta General',source,formationLabel=group,period=period))
   if initial_row:initial.append({**records[-1],'formationLabel':snapshot_group})
  assert len(initial)==len({r['person']for r in initial})==45,(num,'Titulares iniciales',len(initial))
  for r in li['board']:
   source=li['source']+'#page='+str(r['page']);id=resolve(r['name'],'asturias',source,'Mesa de la Junta General')
   board.append(term(id,r['role']+' · Mesa',source,period=el['label']));cat.event(id,'cargos-autonomias.json','asturias',r['role']+' · Mesa de la Junta General',el['label'],source)
  data=dict(id=f'asturias-parlamento-{num}',label=el['label'],start=el['constitutionAt'],end=electoral[i+1]['constitutionAt']if i<11 else None,checkedAt=CHECKED,source=li['source'],currentOnly=False,capacity=45,nominalOnly=True,records=records,board=[],groups=[],archiveBoard=board,archiveBoardNote='Miembros de la Mesa documentados durante la legislatura, incluidos sus relevos; no son una composición simultánea.',note='Relación de la Biblioteca de la Junta General; se conservan los titulares y los relevos sin atribuir intervalos individuales no publicados.',archivedComposition=dict(source=li['source'],checkedAt='2026-03-31',note='Titulares iniciales identificados por la tipografía que explica la Biblioteca; las siglas corresponden a la candidatura de origen. El archivo personal incluye los relevos.',groups=[dict(name=g['name'],source=g['source'],members=[r['person']for r in g['members']])for g in groups(initial)]))
  if num==12:
   current=read('asturias-actual.json')['members'];current_records=[]
   for r in current:
    key=re.search(r'diputadoId=(\d+)',r['source'])[1];id=ids[key];group=r.get('group','').removeprefix('Ir a ');source=r['source']
    cat.active(id,source);current_records.append(term(id,'Diputado/a de la Junta General',source,formationLabel=group,observedAt=CHECKED))
   assert len(current_records)==45
   data.update(currentOnly=True,nominalOnly=False,records=current_records,board=[{**r,'observedAt':CHECKED}for r in board],groups=groups(current_records),source='https://www.jgpa.es/diputados-y-diputadas',note='Composición vigente de la Junta General consultada. No se proyecta esta lista a la constitución de 2023.')
   data.pop('archivedComposition');data.pop('archiveBoard');data.pop('archiveBoardNote')
  stage('asturias','Parlamento',data)
 outputs.append((path('asturias')/'fuentes/relaciones-biblioteca.json',archives))

def cantabria(ids):
 archives=read('cantabria-relaciones-biblioteca.json');current_list=read('cantabria-legislatura-11.json');current_pleno=next(o for o in current_list['organs']if o['name'].startswith('Pleno'))
 for i,li in enumerate(archives):
  num=li['legislature'];records=[];board=[]
  for r in li['members']:
   source=li['source'].split('#')[0]+'#page='+str(r['page']);id=resolve(r['name'],'cantabria',source,'Parlamento de Cantabria')
   records.append(term(id,'Diputado/a del Parlamento de Cantabria',source,formationLabel=r['group'],constituency='Cantabria'))
   cat.event(id,'mandatos-autonomias.json','cantabria','Parlamento de Cantabria · '+li['label'],li['label']+' · relación nominal archivada',source);association(id,'cantabria',r['group'],li['label'],source)
  assert len(records)==len({r['person']for r in records})==(35 if num==1 or num>=9 else 39),(num,'Lista cántabra inconsistente')
  for r in li['board']:
   source=li['source'].split('#')[0]+'#page='+str(r['page']);id=resolve(r['name'],'cantabria',source,'Mesa del Parlamento de Cantabria')
   board.append(term(id,(r['role']or'Miembro de la Mesa')+' · Mesa',source,period=li['label']));cat.event(id,'cargos-autonomias.json','cantabria',(r['role']or'Mesa')+' · Parlamento de Cantabria',li['label'],source)
  # La constitución y la publicación son hechos distintos. Los cargos personales permanecen sin intervalos inventados.
  data=dict(id=f'cantabria-parlamento-{num}',label=li['label'],start=li['constitutionAt'],end=archives[i+1]['constitutionAt']if i<10 else None,checkedAt=CHECKED,source=li['source'],currentOnly=False,nominalOnly=True,capacity=35 if num==1 or num>=9 else 39,records=records,board=[],groups=[],archiveBoard=board,archiveBoardNote='Relación de la Biblioteca, incluidos los relevos de la Mesa. No atribuye una fecha común a todos sus integrantes.',note='Relación nominal archivada por la Biblioteca del Parlamento, actualizada durante la legislatura; no es la lista de la sesión constitutiva ni reconstruye todos los relevos.',archivedComposition=dict(source=li['source'],checkedAt='2026-04-28',note='Relación nominal de la Biblioteca; incluye las sustituciones incorporadas a su cuadro histórico.',groups=[dict(name=g['name'],source=g['source'],members=[r['person']for r in g['members']])for g in groups(records)]))
  if num==11:
   current=[];mesa=[]
   current_rows=[*current_pleno['members']]
   # El directorio del Pleno omite esta incorporación que sí documentan su ficha y el BOPCA.
   ana=next(r for r in current_list['members']if ordered(r['name'])=='Ana Obregón Abascal');current_rows.append(ana)
   for r in current_rows:
    id=ids[r['source']];profile=next(m.load(f)for f in(CACHE/'cantabria-perfiles').glob('*.json')if m.load(f)['source']==r['source'])
    ads=[e for e in profile['roles']if(e['organ'].startswith('Grupo Parlamentario')or e['organ']=='Diputado no adscrito')and not e['end']]
    group=ads[-1]['organ']if ads else('Grupo Parlamentario Regionalista'if name(id)=='Ana Obregón Abascal'else r.get('group')or'Adscripción no publicada')
    cat.active(id,r['source']);current.append(term(id,'Diputado/a del Parlamento de Cantabria',r['source'],formationLabel=group,constituency='Cantabria',observedAt=CHECKED))
   for organ in current_list['organs']:
    if not organ['name'].startswith('Mesa del Parlamento'):continue
    for r in organ['members']:
     id=ids[r['source']];mesa.append(term(id,(r.get('role')or'Miembro')+' · Mesa',r['source'],observedAt=CHECKED))
   assert len(current)==len({r['person']for r in current})==35 and len(mesa)==5
   data.update(currentOnly=True,nominalOnly=False,records=current,board=mesa,groups=groups(current),source=current_pleno['source'],note='Composición vigente consultada. El directorio del Pleno muestra 34 personas: se completa con Ana Obregón Abascal, cuya incorporación está documentada en su ficha y en el archivo de la Biblioteca.')
   data.pop('archivedComposition');data.pop('archiveBoard');data.pop('archiveBoardNote')
  stage('cantabria','Parlamento',data)
 outputs.append((path('cantabria')/'fuentes/relaciones-biblioteca.json',archives))

def governments(region):
 apps=read(region+'-presidencias-revisadas.json');archive=read(region+'-consejerias-historicas.json');current=read(region+'-gobierno-vigente.json')
 for r in current:
  id=resolve(r['name'],region,r['source'],r['role']);cat.active(id,r['source']);cat.photo(id,r.get('image'),r.get('portraitSource',r['source']),r.get('portraitCredit',m.REGIONS[region]+' · retrato del directorio de Gobierno'),**({'license':r['portraitLicense'],'licenseUrl':r['portraitLicenseUrl']}if r.get('portraitLicense')else{}))
 legs=[1,2,3,3,4,5,6,7,8,9,10,11,12]if region=='asturias'else[1,1,2,2,3,4,5,6,7,8,9,10,11]
 for i,a in enumerate(apps):
  start=a['date'];end=apps[i+1]['date']if i+1<len(apps)else None;id=resolve(a['name'],region,a['source'],'Presidencia de '+m.REGIONS[region]);label=ROMANS[legs[i]-1]+' · '+start[:4]+(' · segunda etapa'if i and legs[i]==legs[i-1]else'')
  data=dict(id=region+'-gobierno-'+str(i+1),label=label,start=start,end=end,checkedAt=CHECKED,name='Gobierno de '+m.REGIONS[region],source=a['source'],terms=[{**term(id,'Presidencia',a['source'],level='president'),'start':start,'end':end}],incidents=[],archiveTerms=[])
  cat.event(id,'cargos-autonomias.json',region,'Presidencia de '+m.REGIONS[region],start+(' – '+end if end else' – actualidad'),a['source'])
  combined={}
  for r in archive:
   years=[int(y)for y in re.findall(r'\b(?:19|20)\d{2}\b',r['period'])]
   if not years:continue
   if region=='asturias':applies=int(start[:4])>=min(years)and int(start[:4])<max(years+[2027]if len(years)==1 else years)
   else:
    ss=re.search(r'(\d{1,2}) de (\w+) de ((?:19|20)\d{2})',r['period']);rs=None
    if ss:
     months=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];rs=f'{ss[3]}-{months.index(ss[2])+1:02}-{int(ss[1]):02}'
    applies=rs is not None and start<=rs and(end is None or rs<end)
   if not applies:continue
   rid=resolve(r['name'],region,r['source'],r['role']);cat.event(rid,'cargos-autonomias.json',region,r['role']+' · Gobierno de '+m.REGIONS[region],r['period'],r['source'])
   if rid==id:continue
   key=(rid,r['period']);item=combined.setdefault(key,dict(person=rid,name=name(rid),start=None,end=None,role=r['role'],source=r['source'],period=r['period'],level='vice'if'vicepresiden'in r['role'].lower()else'minister'))
   if r['role']not in item['role']:item['role']+=' · '+r['role']
  data['archiveTerms']=list(combined.values())
  if i==len(apps)-1:
   data['currentOnly']=True;data['terms']=[]
   for r in current:
    rid=resolve(r['name'],region,r['source'],r['role']);data['terms'].append(term(rid,r['role'],r['source'],level='president'if rid==id else'vice'if'vicepresiden'in r['role'].lower()else'minister',observedAt=CHECKED));cat.event(rid,'cargos-autonomias.json',region,r['role'],CHECKED+' · composición vigente consultada',r['source'])
  if data['archiveTerms']:data['incidents'].append('El archivo de consejerías procede de una relación enciclopédica complementaria; sus intervalos y relevos están pendientes de contraste completo con los decretos originales.')
  stage(region,'Gobierno',data)
 outputs.append((path(region)/'fuentes/nombramientos-presidenciales.json',apps))
 outputs.append((path(region)/'fuentes/consejerias-historicas.json',archive))

if __name__=='__main__':
 # Los recursos exportados del navegador se identifican por su URL pública original.
 original_fetch=c.fetch;assets={}
 for file in CACHE.glob('retratos-*-manifiesto.json'):
  for a in m.load(file).get('assets',[]):
   p=pathlib.Path(a['path'])
   if p.exists():assets[a['url']]=p
 c.fetch=lambda url:assets[url].read_bytes()if url in assets else original_fetch(url)
 a,b=profiles();asturias(a);cantabria(b);governments('asturias');governments('cantabria')
 c.write(CACHE/'plan-identidades.json',dict(newPeople=cat.new,used=len(cat.used),compositions=len(outputs),records=[dict(path=str(p),id=d.get('id'))for p,d in outputs if isinstance(d,dict)]))
 if '--plan'in sys.argv:print('PLAN',len(cat.used),'personas;',len(cat.new),'nuevas;',len(outputs),'archivos',flush=True)
 else:
  cat.save()
  for p,data in outputs:c.write(p,data)
