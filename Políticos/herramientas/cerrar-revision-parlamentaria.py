"""Contraste de discrepancias, fallecimientos oficiales y retratos recuperados."""
import pathlib,json,datetime,re,shutil,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parents[2]; PEOPLE=ROOT/'Políticos'; CACHE=ROOT/'test-results/revision-partidos/parlamento'
def read(p,default=None):return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def save(p,data):
    text=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    if not p.exists() or p.read_text(encoding='utf-8')!=text:p.write_text(text,encoding='utf-8')
folders={read(p)['id']:p.parent for p in PEOPLE.glob('*/ficha.json')}
keys={};changes=read(PEOPLE/'revisiones/2026-10-08-parlamento/correcciones.json',[])
for id,folder in folders.items():
    for entry in read(folder/'institucional.json',[]):keys[(entry['chamber'],entry['key'])]=id
for (chamber,key),id in keys.items():
    folder=folders[id];meta=read(CACHE/chamber/(key+'.json'));personal=read(folder/'datos-personales.json',{})
    death=meta.get('personal',{}).get('fallecidoFecha','');match=re.search(r'(\d{2})/(\d{2})/(\d{4})',death)
    if match and not personal.get('deathDate'):
        date=datetime.date(int(match[3]),int(match[2]),int(match[1])).isoformat()
        personal.update({'deathDate':date,'deathYear':int(date[:4])})
        source={'label':'Senado de España · datos personales','url':meta.get('xmlSource') or meta['source'],'kind':'institutional'}
        personal['personalSources']=[*personal.get('personalSources',[]),source];save(folder/'datos-personales.json',personal);changes.append({'id':id,'field':'deathDate','value':date,'source':source})
    photo=read(CACHE/'retratos'/(chamber+'-'+key+'.json'),{})
    if photo.get('file') and not (folder/'retrato.json').exists():
        file='retrato'+photo['extension'];shutil.copyfile(ROOT/photo['file'],folder/file)
        save(folder/'retrato.json',{'file':file,'source':photo['source'],'original':photo['original'],'credit':photo['credit'],'context':'Retrato de la ficha institucional del mandato consultado; fecha de toma no publicada.'})
# Se conserva la discrepancia visible cuando las fuentes publican fechas distintas.
corrections={
 'Agustín Rodríguez Sahagún':('1932-04-27','La ficha del Congreso indica 27 de abril; algunas referencias enciclopédicas indican marzo, incluso dentro del mismo artículo. Se conserva la fecha de la ficha institucional.'),
 'Santiago López Valdivielso':('1950-02-07','El Senado indica 7 de febrero de 1950; la ficha antigua del Congreso contiene 4 de julio de 1949. Se adopta el dato del Senado, concordante con la información biográfica posterior.'),
 'Francisco Moreno Franco':('1949-07-08','El Senado indica 8 de julio de 1949; el Congreso publica 8 de junio. Se conserva el dato del Senado y se enlazan ambas fuentes.'),
 'María Paz Lago Martínez':('1975-08-17','El Senado indica 17 de agosto de 1975; el Congreso publica el día 16. Se conserva el dato del Senado y se enlazan ambas fuentes.'),
 'César Antonio Molina Sánchez':(None,'El Congreso publica 1951; su biografía y otras fuentes institucionales, 1952. Se mantiene el año 1952 documentado en la revisión biográfica.'),
 'Santiago Rodríguez-Miranda Gómez':(None,'La fecha biográfica conservada es de 1940; el Congreso publica 1941. Ambas referencias quedan disponibles para contraste.'),
 'Diana Morant Ripoll':(None,'La fecha biográfica conservada es 25 de junio de 1980; la ficha del Congreso publica 25 de mayo. Se mantiene la fecha de la revisión biográfica y se enlazan las fuentes.'),
 'Alfonso Guerra González':(None,'Nacimiento declarado: 30 de mayo de 1940; inscripción registral: 31 de mayo, fecha que figura en el Congreso.'),
 'María Teresa de Lara Carbó':(None,'La ficha posterior del Congreso indica 1942; una ficha anterior del Senado publica 1944. Se conserva 1942, correspondiente a la información biográfica corregida.'),
 'Isidro Fernández Rozada':(None,'La fecha biográfica conservada y el Congreso indican 23 de diciembre de 1943; el Senado publica el día 26. Se conservan ambas referencias.'),
}
for name,(date,note) in corrections.items():
    matches=[(id,p) for id,p in folders.items() if read(p/'ficha.json')['fullName']==name]
    if not matches:
        matches=[(id,p) for id,p in folders.items() if name in read(p/'ficha.json').get('knownAs',[])]
    if len(matches)!=1:raise ValueError('Identidad no resuelta: '+name)
    id,folder=matches[0];personal=read(folder/'datos-personales.json',{});old=personal.get('birthDate')
    if date:personal.update({'birthDate':date,'birthYear':int(date[:4]),'birth':datetime.date.fromisoformat(date).strftime('%d/%m/%Y')})
    personal['birthNote']=note
    for entry in read(folder/'institucional.json',[]):
        reference={'label':('Congreso de los Diputados' if entry['chamber']=='congreso' else 'Senado de España')+' · ficha individual','url':entry['source'],'kind':'institutional'}
        if not any(r['url']==reference['url'] for r in personal.get('personalSources',[])):personal.setdefault('personalSources',[]).append(reference)
    if name=='Santiago López Valdivielso':
        personal.update({'deathDate':'2024-01-09','deathYear':2024})
        personal.setdefault('personalSources',[]).append({'label':'Santiago López Valdivielso · Wikipedia','url':'https://es.wikipedia.org/wiki/Santiago_L%C3%B3pez_Valdivielso','kind':'encyclopedic'})
    save(folder/'datos-personales.json',personal)
    if not any(c['id']==id and c['field']=='birthDate' for c in changes):changes.append({'id':id,'field':'birthDate','previous':old,'value':personal.get('birthDate'),'note':note,'sources':personal['personalSources']})
auditPath=PEOPLE/'revisiones/2026-10-08-parlamento/informe.json';audit=read(auditPath)
for record in audit['records']:
    meta=read(CACHE/record['chamber']/(record['key']+'.json'))
    record['sourceError']=meta.get('error');record['portrait']=(folders[record['id']]/'retrato.json').exists()
    record['portraitLocated']=bool(meta.get('portrait'))
audit['uniquePeople']=len(folders);audit['portraitPeople']=sum((p/'retrato.json').exists() for p in folders.values())
audit['missingPortraits']=[{'id':id,'name':read(p/'ficha.json')['fullName'],'sources':read(p/'fuentes.json',[])} for id,p in folders.items() if not (p/'retrato.json').exists()]
audit['identityConflicts']=changes;save(auditPath,audit)
save(PEOPLE/'revisiones/2026-10-08-parlamento/correcciones.json',changes)
print('Personas',len(folders),'con retrato',audit['portraitPeople'],'correcciones documentadas',len(changes))
