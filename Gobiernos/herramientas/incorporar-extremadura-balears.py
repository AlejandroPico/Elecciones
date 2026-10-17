"""Integración conservadora de Extremadura e Illes Balears.

--plan revisa identidades y prepara composiciones sin escribir las fichas.
Las equivalencias se basan en nombres completos acreditados; las coincidencias
aproximadas se guardan para revisión y no se fusionan automáticamente.
"""
import importlib.util,pathlib,re,json,collections,sys,unicodedata
s=importlib.util.spec_from_file_location('m',pathlib.Path(__file__).with_name('catalogo-regional.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-extremadura-balears.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c;m.CHECKED=c.CHECKED;m.c=c
CACHE=c.CACHE;CHECKED=c.CHECKED;REVISION='2026-10-16-extremadura-balears';ROOTS={'extremadura':pathlib.Path('Gobiernos/Autonomías/Extremadura'),'baleares':pathlib.Path('Gobiernos/Autonomías/Illes Balears')};outputs=[]
def read(file):return m.load(CACHE/file)
baselineFile=CACHE/'catalogo-base.json'
if baselineFile.exists()and not(pathlib.Path('Políticos/revisiones')/REVISION/'informe.json').exists():
 baseline=m.load(baselineFile);cat=m.Catalog.__new__(m.Catalog);cat.revision=REVISION;cat.portrait_stem='retrato-autonomico';cat.people={row['id']:(pathlib.Path(row['folder']),row['meta'])for row in baseline};cat.baseline=set(cat.people);cat.names=collections.defaultdict(set)
 for id,(folder,meta)in cat.people.items():
  for name in[meta['name'],meta['fullName'],*meta.get('knownAs',[])]:cat.names[m.norm(name)].add(id)
 cat.aliases={};cat.used=set();cat.files={};cat.photos={};cat.correspondences=[];cat.errors=[];cat.new=[];cat.unavailablePhotos=[];cat.reset=set()
 for folder in ROOTS.values():cat.aliases.update({m.norm(k):v for k,v in m.load(folder/'fuentes/identidades-revisadas.json',{}).items()})
else:
 cat=m.Catalog(revision=REVISION,alias_files=[folder/'fuentes/identidades-revisadas.json'for folder in ROOTS.values()],portrait_stem='retrato-autonomico')
 c.write(baselineFile,[dict(id=id,folder=str(folder),meta=meta)for id,(folder,meta)in cat.people.items()]);print('CATALOGO BASE',len(cat.people),flush=True)
previousAudit=m.load(pathlib.Path('Políticos/revisiones')/REVISION/'informe.json',{})
if '--sin-reintentar-retratos'in sys.argv:
 failedResources={row['resource']for row in previousAudit.get('portraitErrors',[])}
 originalPhoto=cat.photo
 def selectedPhoto(id,image,*args,**kwargs):
  if image not in failedResources:originalPhoto(id,image,*args,**kwargs)
 cat.photo=selectedPhoto

def loose(name):return re.sub(r'\b(?:i|y)\b',' ',m.norm(name)).split()
def clean_name(name):
 name=c.clean(name).replace(' I ',' i ').replace(' Y ',' y ').replace(' De ',' de ').replace(' Del ',' del ').replace(' La ',' la ').replace('Mª','María').replace('M.ª','María')
 return name.replace('·L','·l').strip(' )•✓➢')
equivalences=[];existing=collections.defaultdict(set)
for id,(folder,meta)in cat.people.items():
 for name in[meta['fullName'],meta['name'],*meta.get('knownAs',[])]:existing[tuple(loose(name))].add(id)
def resolve(name,region,source,role):
 name=clean_name(name);target=cat.aliases.get(m.norm(name),name)
 candidates=existing.get(tuple(loose(target)),set())
 if len(candidates)==1:
  id=next(iter(candidates));canonical=cat.people[id][1]['fullName']
  if canonical!=name:cat.aliases[m.norm(name)]=canonical;equivalences.append(dict(name=name,canonical=canonical,person=id,source=source,reason='Nombre completo coincidente, con distinta presencia de las conjunciones i/y o tildes.'))
 id=cat.resolve(name,region,source,role);existing[tuple(loose(name))].add(id);return id
def term(id,role,source,**kwargs):return {**dict(person=id,name=cat.people[id][1]['fullName'],start=None,end=None,role=role,source=source),**kwargs}
def unique(rows):return list({(r['person'],r.get('role'),r.get('formationLabel'),r.get('period')):r for r in rows}.values())
def groups(rows):
 result=collections.defaultdict(list)
 for row in rows:result[row.get('groupLabel',row['formationLabel'])].append(row)
 return[dict(name=label,source=members[0]['source'],members=members)for label,members in result.items()]
def group_name(label):
 label=re.sub(r'^(?:GRUP PARLAMENTARI|Grup Parlamentari|Grupo Parlamentario)\s+(?:de\s+)?','',label).strip()
 return label.title().replace('Pp','PP').replace('Psoe','PSOE').replace('Vox','Vox')if label.isupper()else label
def organization(label):
 label=m.norm(label)
 if 'popular'in label or label in['pp','ap pdp ul']:return'pp'
 if 'socialista'in label or'psoe'in label:return'psoe'
 if 'vox'in label:return'vox'
 if 'ciudadanos'in label:return'ciudadanos'
 if 'podemos'in label or'unidas'in label:return'podemos'
 return None
def affiliation(id,region,label,period,source):
 label=group_name(label)
 if label and not re.search(r'no precisada|pendiente',label,re.I):cat.group(id,region,label,period,source,organization(label))
def save_stage(region,section,data):outputs.append((ROOTS[region]/section/(data['start'][:4]+' '+data['label'])/'composicion.json',data))
def board_order(role):
 title=m.norm(role);rank=0 if title.startswith('presiden')else 1 if title.startswith('vice')else 2
 order=1 if re.search(r'primer|primera|1r|1a',title)else 2 if re.search(r'segon|segund|2n|2a',title)else 3 if 'tercer'in title else 0
 return rank,order

def profiles():
 for file in sorted((CACHE/'extremadura/perfiles').glob('*.json')):
  row=m.load(file);id=resolve(row['name'],'extremadura',row['source'],'Asamblea de Extremadura');cat.photo(id,row.get('image'),row['source'],'Asamblea de Extremadura · retrato institucional de la ficha personal')
 for row in read('baleares/perfiles-preparados.json'):
  if not any(role['Càrrec']in['DIPUTAT','DIPUTADA']for role in row['roles']):continue
  id=resolve(row['name'],'baleares',row['source'],'Parlament de les Illes Balears');image=next((i['src']for i in row['images']if '/imatges/diputats/'in i['src']),None);cat.photo(id,image,row['source'],'Parlament de les Illes Balears · retrato institucional de la ficha personal')
  for role in row['roles']:
   if role.get('nonParliamentary'):
    title=role['Càrrec'].capitalize()+' · '+role['Organisme'];period=role.get('Inici','Fecha inicial no publicada')+' — '+role.get('Final','sin fecha final publicada')+' · Legislatura '+role['Legislatura'];cat.event(id,'cargos-autonomias.json','baleares',title,period,row['source'])
  cv=m.load(CACHE/f'baleares/curriculos/{row["key"]}.json')
  if cv:
   text=c.clean(cv['text']);source=m.ref(cv['source'],'Currículo público del Parlament de les Illes Balears')
   education={'253':['Licenciado en Derecho por la Universidad Complutense de Madrid.'],'16':['Licenciado en Filosofía y Letras (Historia), Universidad de Valencia, 1976.','Licenciado en Derecho, Universitat de les Illes Balears, 1985.'],'365':['Llicenciat en Ciències Econòmiques, Universitat de les Illes Balears.','Especialista universitari en Dret Urbanístic i Ordenació del Territori, Universitat de les Illes Balears, 2007–2008.']}.get(str(row['key']),[])
   if education:cat.add(id,'formacion.json',education);cat.add(id,'fuentes-formacion.json',[source])
   birth=re.search(r'(?:naixement|NACIMIENTO)[^\n]{0,130}?(\d{1,2})\s+de\s+(\w+)\s+de\s+(?:l.any\s+)?(\d{4})',text,re.I)
   if birth:
    months={'enero':1,'gener':1,'febrero':2,'febrer':2,'marzo':3,'març':3,'abril':4,'mayo':5,'maig':5,'junio':6,'juny':6,'julio':7,'juliol':7,'agosto':8,'agost':8,'septiembre':9,'setembre':9,'octubre':10,'noviembre':11,'novembre':11,'diciembre':12,'desembre':12}
    if birth[2].lower()in months:
     import datetime
     date=datetime.date(int(birth[3]),months[birth[2].lower()],int(birth[1])).isoformat();personal=cat.files.get((id,'datos-personales.json'),m.load(cat.people[id][0]/'datos-personales.json',{}))
     if not personal.get('birthDate'):personal.update(birthDate=date,birth=birth[0],personalSources=[*personal.get('personalSources',[]),source]);cat.files[id,'datos-personales.json']=personal
def chambers():
 chronology='https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=CRONOL_LEGISL_EXTREMADURA&lang=gl_ES'
 p=c.soup(chronology);table=next(t for t in p.select('table')if'CONSTITUCIÓN DEL PARLAMENTO'in t.get_text());starts=[]
 for tr in table.select('tr'):
  cells=tr.select('td');ds=[c.iso(t.get_text())for t in cells]
  if any(ds):starts.append(next(d for d in reversed(ds)if d))
 starts=sorted(starts);assert len(starts)==12,starts
 extProfiles={p['key']:p for p in[m.load(f)for f in(CACHE/'extremadura/perfiles').glob('*.json')]}
 balProfiles=read('baleares/perfiles-preparados.json')
 for region in ROOTS:
  data=read(region+'/camara-preparada.json')
  for stage in data:
   n=stage['legislature'];label='Legislatura '+r.ROMANS[n-1];current=n==len(data);start=starts[n-1]if region=='extremadura'else stage['start'];end=(starts[n]if region=='extremadura'else data[n]['start'])if not current else None;records=[];chosen=[];board=[]
   for entry in stage['members']:
    id=resolve(entry['name'],region,entry['source'],'Diputado/a de '+m.REGIONS[region]);group=group_name(entry.get('formationLabel',entry.get('group','Adscripción no precisada')));row=term(id,'Diputado/a de '+('la Asamblea de Extremadura'if region=='extremadura'else'el Parlament de les Illes Balears'),entry['source'],formationLabel=group,constituency=entry.get('constituency')or m.REGIONS[region],period=label+' · '+entry.get('period','archivo nominal institucional'));records.append(row)
    if entry.get('party'):row.update(groupLabel=group,formation=entry['party'],formationLabel='Candidatura documentada')
    cat.event(id,'mandatos-autonomias.json',region,row['role'],row['period'],row['source']);affiliation(id,region,group,label,row['source'])
   for entry in stage['chosen']:
    id=resolve(entry['name'],region,entry.get('source',stage['source']),'Diputado/a de '+m.REGIONS[region]);row=next(r for r in records if r['person']==id);chosen.append(row)
    if current:cat.active(id,stage['source'])
   chosen=list({r['person']:r for r in chosen}.values());capacity=54 if region=='baleares'and n==1 else 59 if region=='baleares'else 65
   assert len(chosen)<=capacity,(region,n,len(chosen))
   if region=='extremadura':
    for entry in stage['members']:
     profile=extProfiles[entry['key']]
     for raw in profile['roles']:
      match=re.match(r'(.+?)\s+Mesa de la Asamblea\s+\('+r.ROMANS[n-1]+r' Legislatura\)',raw)
      if match:
       id=resolve(profile['name'],region,profile['source'],match[1]);role=match[1]+' de la Asamblea de Extremadura';board.append(term(id,role,profile['source'],**(dict(observedAt=CHECKED)if current else dict(period=label+' · Mesa documentada en el archivo institucional'))))
   else:
    for b in stage['board']:
     id=resolve(b['name'],region,b['source'],b['role']);board.append(term(id,b['role'],b['source'],period=b['period']))
    for profile in balProfiles:
     for role in profile['roles']:
      if role['Legislatura']==str(n)and role['Organisme']=='MESA DEL PARLAMENT'and(not current or not role.get('Final')):
       id=resolve(profile['name'],region,profile['source'],role['Càrrec']);title=role['Càrrec'].capitalize()+' del Parlament de les Illes Balears';board.append(term(id,title,profile['source'],**(dict(observedAt=CHECKED)if current else dict(period=role.get('Inici','Inicio no publicado')+' — '+role.get('Final','Final no publicado')))))
   board=unique(board);merged={}
   for row in board:
    title=m.norm(row['role']);office=('vice-'if title.startswith('vice')else'secretaria-'if title.startswith('secret')else'presidencia-')+('1'if re.search(r'primer|primera|1r|1a',title)else'2'if re.search(r'segon|segund|2n|2a',title)else'')
    key=(row['person'],office)
    if key in merged:
     previous=merged[key];periods=list(dict.fromkeys([previous.get('period',''),row.get('period','')]));row={**row,'period':'; '.join(p for p in periods if p)}
    merged[key]=row
   board=sorted(merged.values(),key=lambda row:board_order(row['role']))
   for row in board:cat.event(row['person'],'cargos-autonomias.json',region,row['role'],row.get('period',label+' · consulta de '+CHECKED),row['source'])
   result=dict(id=region+'-parlamento-'+str(n),label=label,start=start,end=end,checkedAt=CHECKED,source=stage['source'],capacity=capacity,currentOnly=current,records=unique(records),board=board if current else[],groups=groups(chosen),note='Composición vigente contrastada en el directorio institucional; no se proyecta hacia el inicio de la legislatura.'if current else'Relación nominal archivada y agrupada. Se conservan los relevos en el archivo; no se atribuyen asientos físicos ni simultaneidad a las distintas adscripciones históricas.')
   if not current:result.update(nominalOnly=True,archivedComposition=dict(source=stage.get('electoralSource',stage['source']),checkedAt=CHECKED,note=f'Relación de electos contrastada: {len(chosen)} de {capacity} escaños identificados. Composición archivada, sin reconstrucción diaria de todos los relevos ni asignación física de asientos.',groups=[dict(name=g['name'],source=g['source'],members=[p['person']for p in g['members']])for g in groups(chosen)]),archiveBoard=board,archiveBoardNote='Cargos documentados en la legislatura; incluye relevos. Los intervalos no publicados no se inventan.')
   save_stage(region,'Parlamento',result);print('PARLAMENTO',region,n,len(chosen),len(records),'MESA',len(board),flush=True)
  outputs.append((ROOTS[region]/'fuentes/camaras-revisadas.json',data))
def governments():
 for region in ROOTS:
  presidencies=read(region+'/presidencias.json');tables=read(region+'/gabinetes-complementarios.json');currentMembers=read(region+'/gobierno-vigente.json')
  for i,p in enumerate(presidencies):
   id=resolve(p['name'],region,p['source'],'Presidencia autonómica');start=p['date'];end=presidencies[i+1]['date']if i+1<len(presidencies)else None;n=p['legislature'];label='Legislatura '+r.ROMANS[n-1]+' · '+cat.people[id][1]['fullName'];terms=[term(id,'Presidencia de '+m.REGIONS[region],p['source'],start=start,end=end,level='president',period='Nombramiento por Real Decreto de '+start)];archive=[]
   for table in tables:
    match=re.search(r'\b([IVX]+) Legislatura',table['heading'])
    if not match or r.ROMANS.index(match[1])+1!=n or end is None:continue
    for row in table['rows']:
     if len(row)<2 or not row[0]or row[0]in['Partido Político','Partido político','Consejería','Consejerías']or'Presidencia del Gobierno'in row[0]or'Presidente de la Junta'in row[0]or'Presidenta de la Junta'in row[0]:continue
     name=row[1]if region=='extremadura'else row[-1];name=re.split(r'\s+(?:Desde el|\d{1,2}\s+de\s+)',name)[0].strip()
     name=re.sub(r'\s*\([^)]*\)','',name).strip()
     if len(name.split())<2 or name in['Nombre','Se suprime en el año 1996']or re.search(r'\d|;|—|Legislatura|Junta de Extremadura|Gobierno de las',name):continue
     role=row[0]if row[0].startswith(('Vicepresiden','Consejer','Secretar','Portavoz'))else'Consejería de '+row[0];member=resolve(name,region,table['source'],role);period='Legislatura '+r.ROMANS[n-1]+' · relación histórica complementaria; intervalo individual pendiente de contraste oficial';archive.append(term(member,role,table['source'],level='vice'if role.startswith('Vicepresiden')else'minister',period=period));cat.event(member,'cargos-autonomias.json',region,role,period,table['source'])
   if end is None:
    for member in currentMembers:
     if member['role'].startswith('Presidencia'):continue
     mid=resolve(member['name'],region,member['source'],member['role']);terms.append(term(mid,member['role'],member['source'],level='vice'if member['role'].startswith('Vicepresidencia')else'minister',observedAt=CHECKED,period='Composición vigente consultada el '+CHECKED));cat.active(mid,member['source']);cat.event(mid,'cargos-autonomias.json',region,member['role'],'Consulta de '+CHECKED,member['source']);cat.photo(mid,member.get('image'),member.get('portraitSource',member['source']),'Retrato institucional publicado por '+('la Junta de Extremadura'if region=='extremadura'else'el Govern de les Illes Balears'))
    cat.active(id,p['source'])
   cat.event(id,'cargos-autonomias.json',region,terms[0]['role'],start+' — '+(end or'actualidad'),p['source']);result=dict(id=region+'-gobierno-'+start,label=label,start=start,end=end,checkedAt=CHECKED,name=cat.people[id][1]['fullName'],source=p['source'],terms=terms,archiveTerms=unique(archive),incidents=['La fecha presidencial corresponde al Real Decreto de nombramiento, no a la toma de posesión.','Las relaciones históricas complementarias conservan cargos documentados de la legislatura; no acreditan una composición simultánea para todos sus días.'])
   if end is None:result['preferredDate']=CHECKED
   save_stage(region,'Gobierno',result);print('GOBIERNO',region,start,len(terms),len(archive),flush=True)
  outputs.extend([(ROOTS[region]/'fuentes/nombramientos-presidenciales.json',presidencies),(ROOTS[region]/'fuentes/composicion-vigente.json',[{k:v for k,v in row.items()if k!='biography'}for row in currentMembers])])
if __name__=='__main__':
 for region in ROOTS:
  for member in read(region+'/gobierno-vigente.json'):
   id=resolve(member['name'],region,member['source'],member['role']);cat.photo(id,member.get('image'),member.get('portraitSource',member['source']),'Retrato institucional de '+m.REGIONS[region])
 profiles();chambers();governments();c.write(CACHE/'plan-integracion.json',dict(newPeople=cat.new,reviewedPeople=len(cat.used),equivalences=m.unique(equivalences),outputs=len(outputs)))
 if '--plan'in sys.argv:
  c.write(CACHE/'salidas-preparadas.json',[dict(path=str(file),data=data)for file,data in outputs]);print('PLAN',len(cat.used),'PERSONAS',len(cat.new),'NUEVAS',flush=True)
 else:
  cat.save()
  auditPath=pathlib.Path('Políticos/revisiones')/REVISION/'informe.json';audit=m.load(auditPath)
  if '--sin-reintentar-retratos'in sys.argv:
   audit['portraitErrors']=m.unique([*audit['portraitErrors'],*[row for row in previousAudit.get('portraitErrors',[])if row['person']in audit['missingPortraits']]]);c.write(auditPath,audit)
  for file,data in outputs:c.write(file,data)
  c.write(pathlib.Path('Gobiernos/revisiones')/REVISION/'equivalencias-nominales.json',m.unique(equivalences))
  c.write(ROOTS['extremadura']/'fuentes/electos-correspondencias.json',read('extremadura/electos-correspondencias.json'))
  c.write(ROOTS['baleares']/'fuentes/abreviaturas-contrastadas.json',read('baleares/abreviaturas-contrastadas.json'))
