"""Prepara relaciones nominales y mantiene separados electos, relevos y vigentes."""
import importlib.util,pathlib,re,json,unicodedata,difflib,collections,sys
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-extremadura-balears.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c;CACHE=c.CACHE
def load(file):return json.loads(pathlib.Path(file).read_text('utf8'))
def norm(text):
 text=text.replace('M.ª','María').replace('Mª','María').replace('M. ','Maria ').replace('Al∙lès','Al·lès')
 return re.sub(r'\b(?:i|y|d|dª|sr|sra|don|dona)\b',' ',re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',text).encode('ascii','ignore').decode().lower())).split()
def key(text):return' '.join(norm(text))
def initial_name(value):
 value=c.clean(value).replace(' I ',' i ').replace(' Y ',' y ').replace(' De ',' de ').replace(' Del ',' del ').replace(' De La ',' de la ')
 return value
def clean_bullet(text):
 return c.clean(re.sub(r'^(?:[•✓➢]|\d+[.)])?\s*Sr(?:a)?\.\s*','',text)).replace('Al∙lès','Al·lès')
def balear_roles(text):
 segments=re.split(r'Càrrecs (?:no )?parlamentaris\s*:',text);out=[]
 for group,part in enumerate(segments[1:]):
  part=re.split(r"Nombre d.iniciatives",part)[0]
  for block in re.split(r'\n\d+\n(?=Càrrec:)',part):
   fields={}
   for label,val in re.findall(r'(Càrrec|Legislatura|Organisme|Illa|Candidatura|Partit Polític|Inici|Final):\s*\n(.+)',block):fields[label]=val.strip()
   if fields.get('Legislatura','').isdigit()and fields.get('Càrrec'):out.append(dict(fields,nonParliamentary=group==1))
 return out
def baleares():
 profiles=[];bykey={}
 for file in sorted((CACHE/'baleares/perfiles').glob('*.json')):
  data=load(file);name=re.search(r'(?:Sr\.|Sra\.)\s+([^\n]+)',data['text']);data['name']=initial_name(name[1].title())if name else initial_name(data['name']);data['roles']=balear_roles(data['text']);bykey[data['key']]=data;profiles.append(data)
 index={key(p['name']):p for p in profiles};aliases=[];unresolved=[]
 manual=load('Gobiernos/Autonomías/Illes Balears/fuentes/variantes-nominales.json')
 def resolve(name):
  name=c.clean(name).strip(' )•✓➢')
  name=re.split(r'\s+(?:Senador|Parlament de les|i per la renúncia|no es correspon|\* La renúncia)',name)[0].strip(' )•✓➢')
  if name in manual:
   target=manual[name];profile=index.get(key(target));aliases.append(dict(name=name,canonical=target,source=profile['source']if profile else'PDF institucional de la legislatura',reason='Variante revisada entre los documentos nominales institucionales.'));return target
  normalized=key(name)
  if normalized in index:return index[normalized]['name']
  # Solo equivalencias nominales de las fuentes del propio Parlament. Las
  # propuestas aproximadas se guardan para revisión, nunca se aceptan solas.
  tokens=norm(name);matches=[]
  for k,p in index.items():
   words=norm(p['name'])
   if len(tokens)==len(words)and all(a==b or(len(a)==1 and b.startswith(a))for a,b in zip(tokens,words)):matches.append(p)
  if len(matches)==1:
   canonical=matches[0]['name'];aliases.append(dict(name=name,canonical=canonical,source=matches[0]['source'],reason='Abreviatura unívoca dentro del índice institucional.'));return canonical
  unresolved.append(dict(name=name,candidates=[index[k]['name']for k in difflib.get_close_matches(normalized,index,n=2,cutoff=.68)]));return initial_name(name)
 stages=[]
 for n in range(1,11):
  data=load(CACHE/f'baleares/legislaturas/{n}.json');document=next(d for d in data['documents']if d['label']=='Relació de diputats i senadors');text='\n'.join(document['pages']);roster=[];chosen=[];district=None;mode='electes'
  # Los saltos de página no interrumpen una viñeta; los nombres del apartado
  # de senadores no son diputados autonómicos por esa sola mención.
  text=text.split('Senadors')[0];flat=re.sub(r'\s+',' ',text)
  for match in re.finditer(r'(?:Sr\.|Sra\.)\s+(.+?)(?=\s*(?:Sr\.|Sra\.)|$)',flat):
   value=match[1];prefix=flat[:match.start()];heads=list(re.finditer(r'(Mallorca|Menorca|Eivissa|Formentera)\s*\(\d+\)',prefix))
   if heads:district=heads[-1][1]
   name=value.split('(',1)[0].strip(' •✓➢');name=re.sub(r'\s+(?:Renúncies|Nous diputats|Noves|Baixes|Diputats que|Diputades que|Senador|Parlament de les).*$','',name).strip(' )•✓➢')
   if len(name.split())<2:continue
   canonical=resolve(name);party=re.search(r'\(([^()]*)\)',value)
   # Homónimos acreditados en las fichas GTP 106 (socialista) y 65 (PSM).
   if canonical=='Damià Pons i Pons'and(n<=3 or(n==4 and party and party[1]=='PSOE')):canonical='Damià Ferrà Pons i Pons'
   entry=dict(name=canonical,nameInSource=name,source=document['source'],constituency=district,formationLabel=party[1]if party else'Adscripción no precisada',period='Relación de electos de '+r.ROMANS[n-1]+' legislatura'if not re.search(r'Renúncies|Nous diputats|Noves incorporacions|Diputats que han',prefix,re.I)else'Relevo documentado en la legislatura')
   roster.append(entry)
   if not re.search(r'Renúncies|Nous diputats|Noves incorporacions|Diputats que han',prefix,re.I):chosen.append(entry)
  boardDoc=next(d for d in data['documents']if d['label']=='Composició dels òrgans parlamentaris');boardText=re.sub(r'\s+',' ','\n'.join(boardDoc['pages'])).split('JUNTA')[0];board=[]
  for match in re.finditer(r'(President(?:a)?|Vicepresident(?:a)?\s+(?:primer[ao]?|segon[ao]?)|Secret[àa]ri(?:a)?\s+(?:primer[ao]?|segon[ao]?))\s*:\s*(.+?)(?=(?:President|Vicepresident|Secret[àa]ri)[^:]{0,25}:|$)',boardText,re.I):
   role=match[1]
   for m in re.finditer(r'(?:Sr\.|Sra\.)\s+([^()]+)(?:\(([^)]*)\))?',match[2]):
    name=m[1].strip(' •✓➢');board.append(dict(name=resolve(name),role=role+' del Parlament de les Illes Balears',period=c.clean(m[2]or'Cargo documentado en la legislatura'),source=boardDoc['source']))
  ds=re.search(r'es constituí dia (\d+)\s+d[e’\']?\s*(\w+)\s+de\s+(\d{4})',data['text']);assert ds,(n,data['text'][-4500:-3000]);start=f'{ds[3]}-{["gener","febrer","març","abril","maig","juny","juliol","agost","setembre","octubre","novembre","desembre"].index(ds[2])+1:02}-{int(ds[1]):02}'
  stages.append(dict(legislature=n,start=start,source=data['source'],members=roster,chosen=chosen,board=board,documents=data['documents']))
  print('BAL PARLAMENT',n,start,len(chosen),len(roster),len(board),flush=True)
 current=load(CACHE/'baleares/vigente.json');currentRows=[]
 for row in current['members']:
  p=bykey[row['key']];roles=[role for role in p['roles']if role['Legislatura']=='11'and role['Càrrec']in['DIPUTAT','DIPUTADA']and not role.get('Final')]
  assert len(roles)==1,(p['name'],roles);role=roles[0];currentRows.append(dict(name=p['name'],key=p['key'],source=p['source'],formationLabel=role['Organisme'],party=role.get('Partit Polític'),constituency=role.get('Illa'),period='Composición vigente consultada el '+c.CHECKED))
 stages.append(dict(legislature=11,start='2023-06-20',source=current['source'],members=currentRows,chosen=currentRows,board=[]))
 c.write(CACHE/'baleares/camara-preparada.json',stages);c.write(CACHE/'baleares/perfiles-preparados.json',profiles);c.write(CACHE/'baleares/nombres-pendientes.json',list({p['name']:p for p in unresolved}.values()));c.write(CACHE/'baleares/abreviaturas-contrastadas.json',aliases)
 print('BAL NOMBRES PENDIENTES',len(set(r['name']for r in unresolved)),flush=True)
def extremadura():
 stages=[];report=[]
 for n in range(1,13):
  data=load(CACHE/f'extremadura/listas/{n}.json');byname={key(row['name']):row for row in data['members']};document=load(CACHE/f'extremadura/elecciones/{n}.json');text='\n'.join(document['pages']+[p for d in document.get('additionalDocuments',[])for p in d['pages']]);chosen={};unmatched=[]
  for raw in text.splitlines():
   line=c.clean(raw);line=re.sub(r'^\s*(?:\d+[.)]?\s+)?(?:D[ªaº.]?\s*|Doña\s+|Don\s+)','',line);line=line.strip(' ,;:.-0123456789')
   if len(line.split())<2 or len(line)>110:continue
   normalized=key(line);ranked=sorted([(difflib.SequenceMatcher(None,normalized,k).ratio(),k)for k in byname],reverse=True)
   score,k=ranked[0]
   if score>=.86 and score-ranked[1][0]>.035:
    row=byname[k];chosen[row['key']]={**row,'electoralSource':document['source'],'nameInElectoralSource':line};report.append(dict(legislature=n,text=line,name=row['name'],score=round(score,4),source=document['source']))
  normalizedDocument=' '+key(text)+' '
  for normalized,row in byname.items():
   if ' '+normalized+' 'in normalizedDocument:
    chosen[row['key']]={**row,'electoralSource':document['source'],'nameInElectoralSource':row['name']};report.append(dict(legislature=n,text=row['name'],name=row['name'],score=1,source=document['source'],method='Nombre completo encontrado en el documento electoral, incluidas columnas de OCR.'))
  if n==12:chosen={row['key']:row for row in data['members']}
  manual={1:{'216':'Francisco España Fuentes'},3:{'114':'Emilia María Manzano Pereira','128':'María del Carmen de la Montaña Franco'},6:{'63':'TERESA BRAVO DURÁN','68':'ROSARIO HONTORIA BARBERO','56':'RAFAEL D. LEMUS RUBIALES'},7:{'63':'TERESA BRAVO DURÁN','270':'CARMEN M.ª REYES SEDA'}}
  for id,spelling in manual.get(n,{}).items():
   assert key(spelling)in key(text),(n,spelling)
   row=next(row for row in data['members']if row['key']==id);chosen[id]={**row,'electoralSource':document['source'],'nameInElectoralSource':spelling};report.append(dict(legislature=n,text=spelling,name=row['name'],source=document['source'],method='Variante o abreviatura revisada expresamente frente a la ficha institucional de esa legislatura.'))
  if n==4:
   correction='https://doe.juntaex.es/pdfs/doe/1995/730o/730o.pdf'
   row=next(row for row in data['members']if row['key']=='106');chosen['106']={**row,'electoralSource':correction,'nameInElectoralSource':'BIBIANO JARONES VENTURA'}
   report.append(dict(legislature=n,name=row['name'],source=correction,method='Proclamación de 16 de junio de 1995, anterior a la constitución de la Cámara: sustituye al electo Germán García Tomé tras su renuncia. DOE 73, página 2985.'))
  print('EXT ELECTOS IDENTIFICADOS',n,len(chosen),'/',65,flush=True)
  stages.append(dict(legislature=n,source=data['source'],members=data['members'],chosen=list(chosen.values()),electoralSource=document['source']))
 c.write(CACHE/'extremadura/camara-preparada.json',stages);c.write(CACHE/'extremadura/electos-correspondencias.json',report)
if __name__=='__main__':
 if '--extremadura'in sys.argv:extremadura()
 else:baleares()
