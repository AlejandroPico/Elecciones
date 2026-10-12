"""Incorpora fuentes revisadas de Andalucía conservando las identidades existentes.

Los históricos parlamentarios no publican intervalos de mandato: archivo nominal,
nunca un Pleno ficticio. La Mesa sí publica altas y bajas. Los retratos se guardan
en su formato original, sin recortes ni generación de rostros.
"""
import collections, concurrent.futures, datetime, hashlib, importlib.util, io, json, pathlib, re, sys, unicodedata
spec=importlib.util.spec_from_file_location('ad',pathlib.Path(__file__).with_name('consultar-andalucia.py'))
ad=importlib.util.module_from_spec(spec);spec.loader.exec_module(ad)
snapshot_spec=importlib.util.spec_from_file_location('snapshot',pathlib.Path(__file__).with_name('documentar-hemiciclos-andalucia.py'))
snapshot=importlib.util.module_from_spec(snapshot_spec);snapshot_spec.loader.exec_module(snapshot)
from PIL import Image
DEST=pathlib.Path('Gobiernos/Autonomías/Andalucía');CACHE=ad.CACHE;CHECKED=ad.CHECKED
AUDIT=pathlib.Path('Gobiernos/revisiones/2026-10-12-andalucia')
ROMANS=['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII']
def read(p,default=None):return json.loads(p.read_text('utf8')) if p.exists() else default
def norm(s):return re.sub('[^a-z0-9]+',' ',''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))).strip()
def ref(u,label='Andalucía · fuente institucional'):return {'label':label,'url':u,'kind':'institutional'}
def title(s):return ' '.join(w.lower() if w.lower() in ['de','del','la','las','los','y'] else w.capitalize() for w in s.split())
ALIASES={
 'Angel López y López':'Ángel Manuel López y López','Antonio Ávila Cano':'Antonio Jesús Ávila Cano',
 'Arturo Bernal Bergua':'Carlos Arturo Bernal Bergua','Carmen Castillo Mena':'María del Carmen Castillo Mena',
 'Carmen Crespo Díaz':'María Carmen Crespo Díaz','María del Carmen Crespo Díaz':'María Carmen Crespo Díaz',
 'Concepción Gutiérrez del Castillo':'María Concepción Gutiérrez del Castillo','Gaspar Zarrías Arévalo':'Gaspar Carlos Zarrías Arévalo',
 'Inmaculada Romacho Romero':'María Inmaculada Romacho Romero','Jorge Paradela Gutiérrez':'Jorge Ángel Paradela Gutiérrez',
 'José Antonio Griñón Martínez':'José Antonio Griñán Martínez','José Hurtado Sánchez':'José Antonio Hurtado Sánchez',
 'José Luis García de Arboleya y Tornero':'José Luis García de Arboleya Tornero','José Luis García-Arboleya Tornero':'José Luis García de Arboleya Tornero',
 'José Ma Romero Calero':'José María Romero Calero','Manuel Pezzi Ceretto':'Manuel Pezzi Cereto',
 'Manuel Chaves González':'Manuel María Chaves González','Rafael Rodríguez Bermúdez':'Rafael Francisco Rodríguez Bermúdez',
 'Ramón Fernández Pacheco':'Ramón Fernández-Pacheco Monterreal','Rocío Blanco Eguren':'Rocío Pilar Blanco Eguren',
 'Rocío Díaz Jiménez':'María Rocío Díaz Jiménez','Sonia Gaya Sánchez':'María Sonia Gaya Sánchez',
 'Teresa Jiménez Vilchez':'María Teresa Jiménez Vílchez','Enrique Moratalla Molina':'José Enrique Moratalla Molina',
 'Emilio de Llera Suárez-Barcenas':'Emilio de Llera Suárez-Bárcena',
 'Angel Martín-Lagos Contreras':'Ángel Martín-Lagos Contreras','Angel Ojeda Avilés':'Ángel Ojeda Avilés',
 'Cesar Estrada Martínez':'César Estrada Martínez','Francisco Javier Del Rio Lopez':'Francisco Javier del Río López','Julio Rodriguez Lopez':'Julio Rodríguez López',
 # Erratas del nombramiento contrastadas con la ficha parlamentaria y actos posteriores.
 'Luis Pizarro Fernández':'Luis Pizarro Medina','Jesús Ramón García Muñoz':'Jesús Ramón Aguirre Muñoz',
}
ALIASES={norm(a):b for a,b in ALIASES.items()}
people={};index=collections.defaultdict(set);files={};new=set();conflicts=[];photo_candidates=collections.defaultdict(list)
baseline_rows=read(CACHE/'existing.json',[])
if not baseline_rows:
 excluded=set(read(AUDIT/'informe.json',{}).get('newPeople',[]))
 folders=[p for p in pathlib.Path('Políticos').iterdir() if p.is_dir() and p.name not in ['interfaz','herramientas','revisiones']]
 def inventory(folder):
  meta=read(folder/'ficha.json',{})
  return {**meta,'_folder':str(folder),'_personal':read(folder/'datos-personales.json',{})} if meta.get('id') and meta['id'] not in excluded else None
 with concurrent.futures.ThreadPoolExecutor(24) as pool:baseline_rows=[r for r in pool.map(inventory,folders) if r]
def current_baseline(row):
 folder=pathlib.Path(row['_folder']);meta=read(folder/'ficha.json')
 if not meta or meta['id']!=row['id']:raise ValueError('Ficha anterior ausente o identidad modificada: '+str(folder))
 return {**meta,'_folder':str(folder),'_personal':read(folder/'datos-personales.json',{})}
# La caché delimita la migración, pero no sustituye las fichas que el usuario haya
# actualizado desde la consulta. Leerlas en paralelo antes de conservar sus datos.
with concurrent.futures.ThreadPoolExecutor(24) as pool:baseline_rows=list(pool.map(current_baseline,baseline_rows))
for row in baseline_rows:
 folder=pathlib.Path(row['_folder']);meta={k:v for k,v in row.items() if not k.startswith('_')};people[meta['id']]={'meta':meta,'folder':folder,'personal':row.get('_personal',{})}
 for name in [meta.get('name'),meta.get('fullName'),*meta.get('knownAs',[])]:
  if name:index[norm(name)].add(meta['id'])
baseline=set(people)
def buffer(folder,file):
 p=folder/file
 if p not in files:files[p]=read(p,[])
 return files[p]
def add(folder,file,rows):
 current=buffer(folder,file);known={json.dumps(r,sort_keys=True) for r in current}
 for r in rows:
  k=json.dumps(r,sort_keys=True)
  if k not in known:current.append(r);known.add(k)
def identity(name,source):
 name=ALIASES.get(norm(name),name);matches=index[norm(name)]
 if len(matches)>1:raise ValueError('Identidad ambigua: '+name+str(matches))
 if matches:id=next(iter(matches))
 else:
  id='andalucia-'+norm(name).replace(' ','-');folder=pathlib.Path('Políticos')/name
  meta={'id':id,'name':name,'fullName':name,'initials':''.join(w[0] for w in name.split() if len(w)>2)[:2].upper(),'organization':None,'affiliationStatus':'pending','relation':'Participación institucional documentada','role':'Representante de las instituciones de Andalucía','summary':'Trayectoria documentada en el Parlamento de Andalucía o en el Consejo de Gobierno de la Junta.','offices':[],'reviewedAt':CHECKED}
  existing=read(folder/'ficha.json')
  if existing:
   if existing['id']!=id:raise ValueError('Colisión de carpeta: '+str(folder))
   meta={**existing,'name':name,'fullName':name}
  people[id]={'meta':meta,'folder':folder,'personal':{}};index[norm(name)].add(id);new.add(id)
 add(people[id]['folder'],'fuentes.json',[ref(source)])
 return id
profiles=read(CACHE/'profiles.json',[]);bio=read(DEST/'fuentes/biografias-parlamento.json',[])
biographies={norm(r['nameInBook']):r for r in bio};mapping={};registries=collections.defaultdict(list)
for p in profiles:
 b=biographies.get(norm(p['name']));name=title(b['nameInBook']) if b else p['name']
 id=identity(name,p['source']);mapping[p['key']]=id;registries[id].append({k:p[k] for k in ['key','legislature','name','source','checkedAt']})
 if p.get('image'):photo_candidates[id].append({'url':p['image'],'source':p['source'],'credit':'Parlamento de Andalucía · retrato institucional','legislature':p['legislature']})
 if b:
  personal=people[id]['personal'];known=personal.get('birthDate') or people[id]['meta'].get('birthDate')
  if known and known!=b['birthDate']:conflicts.append({'person':id,'field':'birthDate','existing':known,'parliament':b['birthDate'],'source':b['source']})
  elif not known:personal['birthDate']=b['birthDate'];personal.pop('birthYear',None);personal.pop('birthNote',None)
  # El primer renglón de cada biografía contiene lugar y fecha; no se copia el relato.
  place=re.split(r',?\s*\d{1,2} de ',b['birthPlace'])[0].strip(' ,(')
  if not personal.get('birthPlace') and place and len(place)<100:personal['birthPlace']=place
  if b.get('deathDate') and not personal.get('deathDate'):personal['deathDate']=b['deathDate']
  personal['personalSources']=list({r['url']:r for r in [*personal.get('personalSources',[]),ref(b['source'],'Parlamento · memoria histórica, página '+str(b['page']))]}.values())
  add(people[id]['folder'],'formacion.json',b['education']);add(people[id]['folder'],'fuentes-formacion.json',[ref(b['source'])])
def mapped(name,source):
 id=identity(name,source);return {'person':id,'name':people[id]['meta']['name'],'source':source,'constituency':'Andalucía'}
def dates(start,end):return f'{start or "Fecha individual no publicada"} – {end or "sin baja publicada"}'
mandates=collections.defaultdict(list);groups=collections.defaultdict(list);offices=collections.defaultdict(list);committees=collections.defaultdict(list)
starts=['1982-06-21','1986-07-17','1990-07-16','1994-07-05','1996-03-29','2000-04-06','2004-03-31','2008-04-03','2012-04-19','2015-04-16','2018-12-27','2022-07-14','2026-06-11']
chronology='https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=CRONOL_LEGISL_ANDALUCIA'
parliaments=[];active=set()
for leg in range(1,14):
 ps=[p for p in profiles if p['legislature']==leg];label='Legislatura '+ROMANS[leg-1];records=[];board=[];grouped=collections.defaultdict(list)
 for p in ps:
  id=mapping[p['key']];item={'person':id,'name':people[id]['meta']['name'],'source':p['source'],'constituency':p['constituency'] or 'No publicada','role':'Diputado/a del Parlamento de Andalucía','start':None,'end':None,'period':label+' · participación documentada; fechas individuales no publicadas'}
  if leg<13 or p['groupsInList']:records.append(item)
  if leg==13 and p['groupsInList']:active.add(id)
  for group in p['groupsInList']:
   grouped[group].append(item);groups[id].append({'title':group+' · '+label,'period':'Adscripción publicada en la ficha de esta legislatura; sin intervalo individual','source':ref(p['source'])})
  mandates[id].append({'title':item['role']+' · '+label+' · '+item['constituency'],'period':item['period'],'source':ref(p['source'])})
  for o in p['organs']:
   row={**item,'role':o['role']+' · '+o['organ'],'start':o['start'],'end':o['endInSource'],'period':dates(o['start'],o['endInSource'])}
   # El portal usa la misma fecha para la baja y el alta de los relevos de la Mesa.
   if o['organ']=='Mesa del Parlamento de Andalucía':board.append(row)
   record={'title':row['role'],'period':row['period'],'source':ref(p['source'])}
   if 'Comisión' in o['organ'] or 'comisión' in o['organ']:committees[id].append(record)
   else:offices[id].append(record)
 source=ps[0]['listSource'];data={'id':'andalucia-parlamento-'+str(leg),'label':label,'start':starts[leg-1],'end':starts[leg] if leg<13 else None,'checkedAt':CHECKED,'source':source,'chronologySource':chronology,'capacity':109,'currentOnly':leg==13,'nominalOnly':leg<13,'note':'La lista histórica reúne todas las personas que participaron, incluidas las sustituciones. No publica intervalos individuales de escaño: se conserva el registro nominal, sin reconstruir un Pleno simultáneo. Las fechas del selector delimitan la biblioteca por sesiones constitutivas, no por disoluciones.' if leg<13 else 'Composición vigente publicada por el Parlamento, consultada el 12 de octubre de 2026. La pertenencia a un grupo no acredita por sí sola militancia en un partido.','records':records,'board':board,'archiveBoard':board if leg==13 else [],'archiveBoardNote':'Historial fechado de la Mesa de esta legislatura. Los representantes de grupos tienen voz y no voto; se distinguen de los siete cargos electos.','groups':[{'name':name,'source':source,'members':rs} for name,rs in grouped.items()]}
 if leg<13:data['archivedComposition']=snapshot.composition(data,ps,mapping)
 ad.write(DEST/'Parlamento'/f'{starts[leg-1][:4]} {label}'/'composicion.json',data);parliaments.append(data)
# Etapas presidenciales: publicación del nombramiento cuando no hay una toma de
# posesión contrastada; desde 2009 se citan los actos institucionales disponibles.
stage_rows=read(DEST/'fuentes/etapas-presidenciales.json',[])
events=[*read(DEST/'fuentes/nombramientos.json')['events'],*read(DEST/'fuentes/nombramientos-complementarios.json',[])];events.sort(key=lambda e:(e['date'],0 if e['ceaseAll'] or e['cease'] else 1 if e['full'] else 2));all_terms=[];open_terms=[]
def close(t,date,source):
 if t['start']<date:t.update(end=date,endBasis=source)
 else:t['end']=date
 if t in open_terms:open_terms.remove(t)
for e in events:
 if e['ceaseAll'] or e['full']:
  for t in list(open_terms):close(t,e['date'],e['source'])
 for name in e['cease']:
  id=identity(name,e['source'])
  for t in list(open_terms):
   if t['person']==id and (not re.search(r'como Vicepresidente',e['label'],re.I) or 'y Consejero' in e['label'] or t.get('viceOnly')):close(t,e['date'],e['source'])
 for row in [*e['members'],*e['vice']]:
  m=mapped(row['nameInSource'],e['source']);role=row['role'];viceOnly=row in e['vice']
  # Una persona puede reunir la vicepresidencia y una consejería; la presentación
  # acumula ambos cargos, pero no los atribuye a los restantes titulares del cargo.
  for t in list(open_terms):
   if t['person']==m['person'] and bool(t.get('viceOnly'))==viceOnly:close(t,e['date'],e['source'])
  t={**m,'role':role,'level':'vice' if 'Vicepresident' in role else 'minister','start':e['date'],'end':None,'startBasis':e['basis']}
  if viceOnly:t['viceOnly']=True
  all_terms.append(t);open_terms.append(t)
governments=[]
for i,s in enumerate(stage_rows):
 end=stage_rows[i+1]['start'] if i+1<len(stage_rows) else None;pres=mapped(s['name'],s['source']);terms=[{**pres,'role':'Presidencia de la Junta de Andalucía','level':'president','start':s['start'],'end':s.get('presidentEnd',end),'startBasis':s['basis']}]
 for t in all_terms:
  if (not t['end'] or t['end']>s['start']) and (not end or t['start']<end):
   r={**t,'start':max(t['start'],s['start']),'end':min(d for d in [t['end'],end] if d) if t['end'] or end else None}
   if not r['end'] or r['start']<r['end']:terms.append(r)
 data={'id':'andalucia-junta-'+str(i+1),'label':s['label'],'name':'Consejo de Gobierno de la Junta de Andalucía','start':s['start'],'end':end,'checkedAt':CHECKED,'source':s['source'],'terms':terms,'archiveTerms':[],'incidents':[s['basis'],'Las consejerías siguen los efectos de los decretos consultados. El límite de una nueva composición no equivale a retirada personal. No se atribuye una ceremonia a una fecha de nombramiento.']}
 if s.get('presidentEnd'):data['incidents'].append('El cese presidencial precede al relevo. No se prolonga el mandato ni se atribuye una presidencia interina sin una fuente específica.')
 ad.write(DEST/'Gobierno'/f'{s["start"][:4]} {s["label"]}'/'composicion.json',data);governments.append(data)
 for t in terms:
  offices[t['person']].append({'title':t['role']+' · Junta de Andalucía','period':dates(t['start'],t['end']),'source':ref(t['source'])})
  if t.get('endBasis'):add(people[t['person']]['folder'],'fuentes.json',[ref(t['endBasis'],'BOJA · cese o composición posterior')])
# Biografías y retratos de la Junta: guardar datos y títulos breves, no el texto completo.
for row in read(CACHE/'biografias-gobierno.json',[]):
 id=identity(row['name'],row['source'])
 for img in row['images']:photo_candidates[id].insert(0,{'url':img['url'],'source':row['source'],'credit':'Junta de Andalucía · retrato institucional','legislature':13})
for row in read(DEST/'fuentes/biografias-gobierno.json',[]):
 id=identity(row['name'],row['source']);personal=people[id]['personal']
 for field in ['birthDate','birthYear','birthPlace']:
  if row.get(field) and not personal.get(field) and not (field=='birthYear' and personal.get('birthDate')):personal[field]=row[field]
 personal['personalSources']=list({r['url']:r for r in [*personal.get('personalSources',[]),ref(row['source'])]}.values())
 add(people[id]['folder'],'formacion.json',row.get('education',[]));add(people[id]['folder'],'fuentes-formacion.json',[ref(row['source'])])
current_government=[t for t in governments[-1]['terms'] if t['start']<=CHECKED and (not t['end'] or CHECKED<t['end'])]
active.update(t['person'] for t in current_government)
external_active={}
for row in read(DEST/'fuentes/datos-personales-complementarios.json',[]):
 id=identity(row['name'],row['source']);p=people[id];p['personal'].update(row.get('personal',{}));p['personal']['personalSources']=list({r['url']:r for r in [*p['personal'].get('personalSources',[]),ref(row['source'])]}.values())
 if row.get('organization'):p['meta'].update(organization=row['organization'],affiliationStatus='documented',relation='Vinculación publicada expresamente por la fuente de la ficha')
 if row.get('active'):active.add(id);external_active[id]=row['source']
 add(p['folder'],'formacion.json',row.get('education',[]))
 if row.get('education'):add(p['folder'],'fuentes-formacion.json',[ref(row['source'])])
involved=set(mapping.values())|set(offices)
for id in involved:
 p=people[id];folder=p['folder']
 for file,rs in [('mandatos-andalucia.json',mandates[id]),('grupos-andalucia.json',groups[id]),('cargos-andalucia.json',offices[id]),('comisiones-andalucia.json',committees[id])]:
  if rs:files[folder/file]=list({json.dumps(r,sort_keys=True):r for r in rs}.values());add(folder,'fuentes.json',[r['source'] for r in rs])
 if registries[id]:files[folder/'registro-parlamento-andalucia.json']=registries[id]
 if id in active:
  roles=[t['role'] for t in current_government if t['person']==id];p['meta']['role']=' · '.join(roles) or ('Eurodiputada' if id in external_active else 'Diputado/a del Parlamento de Andalucía');p['meta']['reviewedAt']=CHECKED
  files[folder/'actividad.json']={'state':'active','reason':'Participación institucional vigente documentada por la fuente.','checkedAt':CHECKED,'sources':[ref(external_active.get(id) or (parliaments[-1]['source'] if id in {r['person'] for r in parliaments[-1]['records']} else governments[-1]['source']))]}
 elif id in new:files[folder/'actividad.json']={'state':'historical' if p['personal'].get('deathDate') else 'unknown','reason':'Fallecimiento publicado en la memoria institucional.' if p['personal'].get('deathDate') else 'Trayectoria histórica documentada; actividad actual no confirmada.','checkedAt':CHECKED,'sources':buffer(folder,'fuentes.json')[:1]}
 if id in new or id in active:files[folder/'ficha.json']=p['meta']
 if p['personal']:files[folder/'datos-personales.json']=p['personal']
with concurrent.futures.ThreadPoolExecutor(24) as pool:list(pool.map(lambda kv:ad.write(*kv),files.items()))
print('Personas',len(involved),'nuevas',len(new),'gobiernos',len(governments),'legislaturas',len(parliaments),flush=True)
def portrait(job):
 id,candidates=job;p=people[id]
 if read(p['folder']/'retrato.json'):return {'person':id,'existing':True}
 errors=[]
 # En los históricos se prefiere el retrato más antiguo disponible; en activo el vigente.
 candidates=sorted(candidates,key=lambda c:c['legislature'],reverse=id in active)
 seen=set()
 for c in candidates:
  if c['url'] in seen:continue
  seen.add(c['url'])
  try:
   raw=ad.fetch(c['url'],'.img');im=Image.open(io.BytesIO(raw));im.load()
   if min(im.size)<60 or len(im.convert('RGB').getcolors(1000000) or [])<12:raise ValueError('Recurso sin retrato reconocible')
   ext={'JPEG':'jpg','PNG':'png','WEBP':'webp','GIF':'gif'}.get(im.format)
   if not ext:raise ValueError('Formato no admitido '+str(im.format))
   return {'person':id,'raw':raw,'hash':hashlib.sha256(raw).hexdigest(),'filename':'retrato-andalucia.'+ext,'meta':{**c,'license':'Fotografía institucional; consultar las condiciones de reutilización de la fuente.','licenseUrl':c['source'],'date':'Retrato asociado a la legislatura '+ROMANS[c['legislature']-1]+'; fecha fotográfica no publicada.'}}
  except Exception as e:errors.append({'url':c['url'],'error':str(e)})
 return {'person':id,'errors':errors}
results=[]
with concurrent.futures.ThreadPoolExecutor(4) as pool:
 for i,r in enumerate(pool.map(portrait,photo_candidates.items()),1):
  results.append(r)
  if i%100==0:print('Retratos',i,'/',len(photo_candidates),flush=True)
hashes=collections.defaultdict(set)
for r in results:
 if r.get('hash'):hashes[r['hash']].add(r['person'])
errors=[];added=[]
for r in results:
 if r.get('existing'):continue
 if not r.get('hash'):errors.append(r);continue
 if len(hashes[r['hash']])>1:errors.append({'person':r['person'],'error':'Imagen idéntica para varias identidades; excluida hasta contraste individual.','hash':r['hash']});continue
 folder=people[r['person']]['folder'];(folder/r['filename']).write_bytes(r['raw']);m=r['meta'];ad.write(folder/'retrato.json',{'file':r['filename'],'credit':m['credit'],'source':m['source'],'original':m['url'],'license':m['license'],'licenseUrl':m['licenseUrl'],'date':m['date']});added.append(r['person'])
with concurrent.futures.ThreadPoolExecutor(24) as pool:all_missing={id for id,has in pool.map(lambda kv:(kv[0],(kv[1]['folder']/'retrato.json').exists()),people.items()) if not has}
missing=sorted(involved&all_missing)
audit={'checkedAt':CHECKED,'baselinePeople':len(baseline),'newPeople':sorted(new),'parliamentProfiles':len(profiles),'parliamentIdentities':len(mapping),'identityMapping':mapping,'profileErrors':read(CACHE/'errors.json',[]),'governments':len(governments),'legislatures':len(parliaments),'currentMembers':len(parliaments[-1]['records']),'birthConflicts':list({json.dumps(r,sort_keys=True):r for r in conflicts}.values()),'portraitsAdded':sorted(set(read(AUDIT/'informe.json',{}).get('portraitsAdded',[]))|set(added)),'portraitErrors':errors,'missingPortraits':[{'id':id,'name':people[id]['meta']['name']} for id in missing],'currentMissingPortraits':sorted(set(missing)&active),'allMissingPortraits':sorted(all_missing)}
ad.write(AUDIT/'informe.json',audit)
ad.write(DEST/'identidades.json',[{'name':a,'person':next(iter(index[norm(b)]))} for a,b in ALIASES.items() if len(index[norm(b)])==1])
print('Retratos añadidos',len(added),'ausencias',len(missing),'ausencias vigentes',audit['currentMissingPortraits'],flush=True)
