"""Aplica la revisión documental publicada, sin red ni dependencia de la caché.

No completa intervalos por deducción ni sustituye retratos anteriores.
"""
import json,pathlib,unicodedata,re
ROOT=pathlib.Path('.');REGION=ROOT/'Gobiernos/Autonomías/Aragón';PERSONS=ROOT/'Políticos';DATE='2026-10-16'
def read(p):return json.loads(pathlib.Path(p).read_text('utf8'))
def write(p,d):
 p=pathlib.Path(p);text=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
 if not p.exists()or p.read_text('utf8')!=text:p.write_text(text,'utf8')
def norm(v):return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',v).encode('ascii','ignore').decode().lower()).strip()
def append(path,row):
 rows=read(path)if path.exists()else[]
 if row not in rows:rows.append(row);write(path,rows)
def contrast_history():
 base=REGION/'fuentes';history=read(base/'consejerias-historicas.json');archive=read(base/'gabinetes-historico-oficial.json')['periods'];aliases=read(base/'identidades-revisadas.json')
 periods={11:'i-legislatura-1983',10:'ii-legislatura-1987',9:'iii-legislatura-1991',8:'iii-legislatura-1993',7:'iii-legislatura-1995',6:'iv-legislatura-1995',5:'v-legislatura-1999',4:'vi-legislatura-2003',3:'vii-legislatura-2007',21:'viii-legislatura-2011',24:'ix-legislatura-2015',25:'x-legislatura-2019'}
 def canonical(name):
  value=aliases.get(name,name);return norm(value.get('fullName',name)if isinstance(value,dict)else value)
 rows=[]
 for r in history:
  key=periods.get(r['legislatureKey']);p=next((p for p in archive if key and '/'+key+'/'in p['source']),None)
  matches=[d['department']for d in p['departments']for name in d['peopleInSource']if canonical(r['name'])==canonical(re.sub(r'\s*\(.*?\)','',name))]if p else[]
  rows.append({'name':r['name'],'role':r['role'],'department':r['entity'],'period':r['period'],'source':r['source'],'confirmationSource':p['source']if p else None,'departmentsInOfficialHistory':matches,'result':'nombre confirmado en el periodo; no acredita fechas diarias'if matches else'sin periodo publicado en el histórico consultado'if not p else'variante nominal o titular no confirmado en esta relación'})
 write(base/'contraste-gabinetes.json',{'checkedAt':DATE,'records':len(rows),'namesConfirmed':sum(bool(r['departmentsInOfficialHistory'])for r in rows),'criterion':'Contraste exacto de nombres completos o alias expresamente revisados. Esta comprobación no confirma fechas, cargos simultáneos ni equivalencia entre consejero y viceconsejero.','rows':rows})
def run():
 # Correspondencia expresa: ficha de las Cortes y nombre completo publicado
 # en el BOE y las actas. El ID permanece estable.
 before=PERSONS/'Soledad Navarro Pratsavall';after=PERSONS/'María Soledad Navarro Pratsavall'
 if before.exists():
  assert not after.exists()and before.resolve().parent==PERSONS.resolve()and after.resolve().parent==PERSONS.resolve()
  before.rename(after)
 meta=read(after/'ficha.json');id=meta['id'];meta.update({'name':after.name,'fullName':after.name,'knownAs':sorted(set([*meta.get('knownAs',[]),'Soledad Navarro Pratsavall']))});write(after/'ficha.json',meta)
 identitySource='https://www.boe.es/boe/dias/1983/04/13/pdfs/A10096-10100.pdf'
 append(after/'fuentes.json',{'label':'Nombre completo · candidaturas proclamadas de 1983','url':identitySource,'kind':'institutional'})
 aliases=read(REGION/'fuentes/identidades-revisadas.json');aliases['Soledad Navarro Pratsavall']=after.name;write(REGION/'fuentes/identidades-revisadas.json',aliases)
 names={id:after.name}
 # El convenio del BOE identifica al consejero con ambos apellidos completos.
 old=PERSONS/'Rafael Gómez Lus';full=PERSONS/'Rafael Gómez-Lus Lafita'
 if old.exists():
  assert not full.exists()and old.resolve().parent==PERSONS.resolve()and full.resolve().parent==PERSONS.resolve();old.rename(full)
 r=read(full/'ficha.json');r.update({'name':full.name,'fullName':full.name,'knownAs':sorted(set([*r.get('knownAs',[]),'Rafael Gómez Lus']))});write(full/'ficha.json',r);names[r['id']]=full.name
 append(full/'fuentes.json',{'label':'Nombre completo y cargo de consejero · BOE de 10 de febrero de 1995','url':'https://www.boe.es/boe/dias/1995/02/10/pdfs/A04685-04685.pdf','kind':'institutional'})
 aliases['Rafael Gómez Lus']=full.name;write(REGION/'fuentes/identidades-revisadas.json',aliases)
 mesa=read(REGION/'fuentes/mesa-primera-legislatura.json')
 for m in mesa['members']:
  if m['person']==id:m['name']=after.name
 write(REGION/'fuentes/mesa-primera-legislatura.json',mesa)
 for file in REGION.glob('*/*/composicion.json'):
  p=read(file)
  for key in ['records','terms','archiveTerms','board','archiveBoard']:
   for r in p.get(key,[]):
    if r['person']in names:r['name']=names[r['person']]
  for group in p.get('groups',[]):
   for r in group['members']:
    if r['person']in names:r['name']=names[r['person']]
  if p['id']=='aragon-cortes-1':p['archiveBoard']=mesa['members'];p['archiveBoardNote']=mesa['note']
  write(file,p)
 # Cargos propios reunidos por persona; no añadir sucesiones de terceros.
 for m in mesa['members']:
  folder=PERSONS/m['name'];assert read(folder/'ficha.json')['id']==m['person']
  source={'label':'Mesa de las Cortes · BOCA 185 de 1987','url':m['source'],'kind':'institutional'}
  append(folder/'fuentes.json',source)
  append(folder/'cargos-autonomias.json',{'title':m['role'],'period':m['period'],'source':source,'territory':'aragon'})
 # Anomalías conservadas con los valores de origen. No invertir fechas ni
 # convertir las fechas generales de legislatura en mandatos individuales.
 history=read(REGION/'fuentes/consejerias-historicas.json');anomalies=[]
 for r in history:
  start,end=r.get('start'),r.get('endInSource');reason=None
  if start and end and start>=end:reason='Fin anterior o igual al inicio'
  if reason:anomalies.append({'name':r['name'],'role':r['role'],'department':r['entity'],'startInSource':start,'endInSource':end,'reason':reason,'source':r['source']})
 for file in (REGION/'Gobierno').glob('*/composicion.json'):
  p=read(file)
  for t in p.get('archiveTerms',[]):
   dates=re.search(r'(\d{4}-\d{2}-\d{2}) — (\d{4}-\d{2}-\d{2})',t.get('period',''))
   if dates and dates[1]>=dates[2]:
    t['datesInSource']={'start':dates[1],'end':dates[2]};t['period']=t['period'].split(' · ')[0]+' · intervalo inconsistente en el catálogo de origen'
  write(file,p)
 report={'checkedAt':DATE,'historicalRecordsReviewed':len(history),'inconsistentIntervals':anomalies,'criterion':'No se atribuyen fechas diarias a cargos sin intervalo individual contrastado. El histórico oficial del Gobierno confirma titulares y carteras, pero no publica un inventario diario de remodelaciones.','firstBoardPeople':len(mesa['members'])}
 write(REGION/'fuentes/revision-cronologica.json',report)
 auditFile=ROOT/'Gobiernos/revisiones/2026-10-16-aragon/informe.json';audit=read(auditFile);audit['legislatures'][0]['board']=len(mesa['members']);audit['supplementaryReview']=report;write(auditFile,audit)
 # El catálogo no incorpora ni elimina personas en esta revisión. Ajustar la
 # auditoría de ausencias únicamente por recursos identificados y existentes.
 photoRows=read(REGION/'fuentes/retratos-complementados.json')['portraits'];available=set()
 for row in photoRows:
  folder=PERSONS/row['name'];assert read(folder/'ficha.json')['id']==row['id'];photo=read(folder/'retrato.json');assert(folder/photo['file']).is_file();available.add(row['id'])
 auditFile=PERSONS/'revisiones/2026-10-16-aragon/informe.json';audit=read(auditFile);audit['allMissingPortraits']=[id for id in audit['allMissingPortraits']if id not in available];audit['supplementaryPortraits']=sorted(available);write(auditFile,audit)
 contrast_history()
 print('Mesa I:',len(mesa['members']),'Retratos complementados:',len(available),'Intervalos inconsistentes:',len(anomalies),flush=True)
if __name__=='__main__':run()
