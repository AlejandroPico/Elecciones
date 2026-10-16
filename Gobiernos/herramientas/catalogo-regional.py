"""Integración regional conservadora: identidades exactas y recursos en su ficha personal."""
import collections,concurrent.futures,importlib.util,pathlib,json,re,unicodedata,io
s=importlib.util.spec_from_file_location('n',pathlib.Path(__file__).with_name('consultar-norte.py'));n=importlib.util.module_from_spec(s);s.loader.exec_module(n);c=n.c
from PIL import Image
ROOT=pathlib.Path('.');PERSONS=ROOT/'Políticos';CHECKED=c.CHECKED
REGIONS={'pais-vasco':'País Vasco','navarra':'Navarra','asturias':'Asturias','cantabria':'Cantabria','galicia':'Galicia','la-rioja':'La Rioja'}

def load(path,default=None):
 p=pathlib.Path(path);return json.loads(p.read_text('utf8'))if p.exists()else default
def norm(value):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().lower()).strip()
def unique(rows):
 seen=set();out=[]
 for row in rows:
  k=json.dumps(row,sort_keys=True,ensure_ascii=False)
  if k not in seen:out.append(row);seen.add(k)
 return out
def ref(url,label):return {'label':label,'url':url,'kind':'encyclopedic'if 'wikipedia.org/'in url else'institutional'}

class Catalog:
 def __init__(self,revision='2026-10-16-norte',alias_files=None,portrait_stem='retrato-norte'):
  self.revision=revision;self.portrait_stem=portrait_stem
  def read(folder):
   meta=load(folder/'ficha.json');return(folder,meta)if meta else None
  with concurrent.futures.ThreadPoolExecutor(16)as pool:rows=[r for r in pool.map(read,[p for p in PERSONS.iterdir()if p.is_dir()])if r]
  self.people={m['id']:(p,m)for p,m in rows};assert len(self.people)==len(rows)
  audit=load(ROOT/'Gobiernos/revisiones'/revision/'conservacion.json')
  self.baseline=set(audit['baselineIds'])if audit else set(self.people)
  self.names=collections.defaultdict(set)
  for folder,meta in rows:
   for name in[meta['name'],meta['fullName'],*meta.get('knownAs',[])]:self.names[norm(name)].add(meta['id'])
  self.aliases={}
  for file in alias_files or ['Gobiernos/Autonomías/País Vasco/fuentes/identidades-revisadas.json','Gobiernos/Autonomías/Navarra/fuentes/identidades-revisadas.json']:
   self.aliases.update(load(file,{}))
  self.aliases={norm(k.replace('M.ª','María').replace('Mª','María')):v for k,v in self.aliases.items()}
  self.used=set();self.files={};self.photos={};self.correspondences=[];self.errors=[];self.new=[];self.unavailablePhotos=[];self.reset=set()
 def resolve(self,name,region,source,role):
  name=unicodedata.normalize('NFC',c.clean(name));expanded=name.replace('M.ª','María').replace('Mª','María');target=self.aliases.get(norm(expanded),expanded)
  matches=self.names.get(norm(target),set())
  exact={id for id in matches if norm(self.people[id][1]['fullName'])==norm(target)}
  if exact:matches=exact
  assert len(matches)<2,(name,'Identidad ambigua',matches)
  if matches:id=next(iter(matches))
  else:
   folder=PERSONS/target;assert not folder.exists(),target
   id=region+'-'+norm(target).replace(' ','-');assert id not in self.people
   meta={'id':id,'name':target,'fullName':target,'initials':''.join(w[0]for w in target.split()[:2]),'organization':None,'affiliationStatus':'pending','relation':'Trayectoria institucional documentada','role':role,'summary':role+'.','offices':[],'reviewedAt':CHECKED}
   self.people[id]=(folder,meta);self.names[norm(target)].add(id);self.new.append({'id':id,'name':target})
  self.used.add(id);folder,meta=self.people[id]
  if name!=meta['fullName']:meta['knownAs']=unique([*meta.get('knownAs',[]),name])
  self.add(id,'fuentes.json',[ref(source,role)])
  self.correspondences.append({'nameInSource':name,'person':id,'source':source,'territory':region})
  return id
 def add(self,id,file,rows):
  key=(id,file)
  if key not in self.files:self.files[key]=load(self.people[id][0]/file,[])
  self.files[key]=unique([*self.files[key],*rows])
 def prepare(self,id,file,region):
  key=(id,file,region)
  if key not in self.reset:
   self.reset.add(key)
   current=self.files.get((id,file),load(self.people[id][0]/file,[]))
   self.files[id,file]=[r for r in current if r.get('territory')!=region]
 def event(self,id,file,region,title,period,source):
  self.prepare(id,file,region);self.add(id,file,[{'territory':region,'title':title,'period':period,'source':ref(source,'Registro enciclopédico complementario'if 'wikipedia.org/'in source else'Registro institucional')}])
 def group(self,id,region,name,period,source,organization=None):
  self.event(id,'grupos-autonomias.json',region,REGIONS[region]+' · '+name,period,source)
  self.prepare(id,'afiliaciones.json',region)
  self.add(id,'afiliaciones.json',[{'organization':organization,'name':name,'period':period,'kind':'association','source':ref(source,'Adscripción publicada por la institución'),'note':'Adscripción en el periodo documentado; no certifica por sí sola militancia ni vigencia actual.','territory':region}])
 def photo(self,id,image,source,credit,**metadata):
  if image and '/jgpa-portlet/css/images/user.jpg' in image:
   self.unavailablePhotos.append({'person':id,'source':source,'reason':'La institución publica un icono genérico, no un retrato personal.'});return
  if image and image.rstrip('/').endswith('/pvgune_descargar/default'):
   self.unavailablePhotos.append({'person':id,'source':source,'reason':'La ficha contiene una ruta de retrato sin identificador de imagen.'});return
  if image and not(self.people[id][0]/'retrato.json').exists()and id not in self.photos:self.photos[id]=(image,source,credit,metadata)
 def active(self,id,source):
  personal=load(self.people[id][0]/'datos-personales.json',{});assert not(personal.get('deathDate')or personal.get('deathYear')),id
  self.files[id,'actividad.json']={'state':'active','reason':'Miembro de la composición institucional vigente consultada.','checkedAt':CHECKED,'sources':[ref(source,'Directorio institucional vigente')]}
 def save(self):
  c.write(ROOT/'Gobiernos/revisiones'/self.revision/'conservacion.json',{'checkedAt':CHECKED,'baselineIds':sorted(self.baseline)})
  writes=[(self.people[id][0]/'ficha.json',self.people[id][1])for id in self.used]+[(self.people[id][0]/file,rows)for(id,file),rows in self.files.items()if rows]
  with concurrent.futures.ThreadPoolExecutor(12)as pool:list(pool.map(lambda r:c.write(*r),writes))
  def image(item):
   id,(url,source,credit,meta)=item
   try:
    raw=c.fetch(url);im=Image.open(io.BytesIO(raw));fmt=im.format;im.verify();assert im.width>20 and im.height>20
    suffix={'JPEG':'jpg','PNG':'png','WEBP':'webp','GIF':'gif'}[fmt];file=self.portrait_stem+'.'+suffix;folder=self.people[id][0];(folder/file).write_bytes(raw)
    c.write(folder/'retrato.json',{'file':file,'source':source,'credit':credit,'original':url,'reviewedAt':CHECKED,**meta});return id
   except Exception as error:self.errors.append({'person':id,'source':source,'resource':url,'error':str(error)});return None
  with concurrent.futures.ThreadPoolExecutor(4)as pool:
   for i,result in enumerate(pool.map(image,self.photos.items())):
    if(i+1)%50==0:print('RETRATOS',i+1,'de',len(self.photos),flush=True)
  missing=[id for id in self.used if not(self.people[id][0]/'retrato.json').exists()]
  added=[{'id':id,'name':meta['fullName']}for id,(folder,meta)in self.people.items()if id not in self.baseline]
  all_missing=sorted(id for id,(folder,meta)in self.people.items()if not(folder/'retrato.json').exists())
  audit={'checkedAt':CHECKED,'baselinePeople':len(self.baseline),'totalPeople':len(self.people),'peopleReviewed':len(self.used),'newPeople':added,'missingPortraits':sorted(missing),'allMissingPortraits':all_missing,'portraitErrors':self.errors,'unavailablePortraits':self.unavailablePhotos}
  c.write(PERSONS/'revisiones'/self.revision/'informe.json',audit)
  c.write(ROOT/'Gobiernos/revisiones'/self.revision/'identidades.json',unique(self.correspondences))
  assert self.baseline<=set(self.people)
  print('INTEGRACION',len(self.used),'nuevas',len(self.new),'sin retrato',len(missing),'errores retrato',len(self.errors),flush=True)
