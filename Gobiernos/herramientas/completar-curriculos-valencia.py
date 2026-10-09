"""Aplicar transcripciones verificadas de currículos, sin contactos ni familia.

Cada dato añadido conserva su referencia. No convertir estudios en una
titulación, una edad relativa en fecha de nacimiento, ni un grupo en militancia.
"""
import concurrent.futures,json,pathlib
ROOT=pathlib.Path('.');DEST=ROOT/'Gobiernos/Autonomías/Comunitat Valenciana'
def read(p,default=None):return json.loads(p.read_text('utf8')) if p.exists() else default
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def append(p,rows):
 old=read(p,[]);known={json.dumps(r,sort_keys=True) for r in old}
 for r in rows:
  if json.dumps(r,sort_keys=True) not in known:old.append(r)
 write(p,old)
for r in read(DEST/'fuentes/curriculos-transcritos.json',[]):
 for term in r.get('career',[]):
  if not isinstance(term,dict) or not all(k in term for k in ['title','period','source']):raise ValueError('Trayectoria sin formato de cargo y periodo: '+r['folder'])
 folder=ROOT/'Políticos'/r['folder'];assert (folder/'ficha.json').exists(),folder
 for section,file in [('education','formacion.json'),('career','trayectoria.json')]:
  if r.get(section):append(folder/file,r[section]);append(folder/('fuentes-formacion.json' if section=='education' else 'fuentes.json'),r['sources'])
 append(folder/'fuentes.json',r['sources'])
 if r.get('personal'):
  data=read(folder/'datos-personales.json',{})
  for k,v in r['personal'].items():
   if not data.get(k):data[k]=v
   elif data[k]!=v:raise ValueError('Discrepancia personal pendiente: '+r['folder']+' '+k)
  if data.get('birthDate'):data.pop('birthYear',None);data.pop('birthNote',None)
  data['personalSources']=list({s['url']:s for s in [*data.get('personalSources',[]),*r['sources']]}.values());write(folder/'datos-personales.json',data)
 # Un cargo actual más específico facilita la consulta de las nuevas fichas.
 if r.get('role'):
  meta=read(folder/'ficha.json');meta.update(role=r['role'],summary=r.get('summary',meta['summary']));write(folder/'ficha.json',meta)
print('Currículos completados:',len(read(DEST/'fuentes/curriculos-transcritos.json',[])))
