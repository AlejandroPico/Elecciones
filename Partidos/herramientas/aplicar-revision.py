"""Incorpora un plan contrastado y recursos descargados; conserva inscripciones e IDs.

Uso: python Partidos/herramientas/aplicar-revision.py
La investigación y los planes están en test-results/revision-partidos (ignorado).
No descarga recursos ni atribuye coaliciones a sus integrantes por semejanza.
"""
import pathlib,json,re,unicodedata,sys,shutil,urllib.parse,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'test-results/libraries'))
from bs4 import BeautifulSoup
C=ROOT/'test-results/revision-partidos'; DATE='2026-10-08'
def read(path,fallback=None):return json.loads(path.read_text(encoding='utf-8')) if path.exists() else fallback
def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def norm(s):return re.sub('[^a-z0-9]','',unicodedata.normalize('NFD',s).encode('ascii','ignore').decode().lower())
def date_claim(entity,prop):
    claims=[c for c in entity.get('claims',{}).get(prop,[]) if c.get('rank')!='deprecated' and c.get('mainsnak',{}).get('datavalue')]
    if len(claims)!=1:return None
    value=claims[0]['mainsnak']['datavalue']['value'];date=value['time'].lstrip('+').split('T')[0]
    if not 1800 <= int(date[:4]) <= 2026:return None
    return {'date':date.replace('-00','-01'),'precision':value['precision'],'source':{'label':'Wikidata · fecha documentada','url':'https://www.wikidata.org/wiki/'+entity['id']+'#'+prop,'kind':'encyclopedic'}}
entities={}
for p in (C/'entidades').glob('*.json'):entities.update(read(p)['entities'])
plan=read(C/'plan.json');reports=[]
# Hay nombres reutilizados. Una entidad disuelta antes de la inscripción no se
# une al partido posterior; tampoco se transfieren marcas de esas entidades.
rejected={'registro-3087','registro-925','registro-2319','registro-6672','registro-1003','registro-1370','registro-1266','registro-1883','registro-3131','registro-306','registro-813','registro-824','registro-1625','registro-3370','registro-534','registro-420','registro-272','registro-480','registro-1250','registro-101','registro-1710','registro-3995'}
for item in plan:
    if item['id'] in rejected:
        folder=ROOT/item['folder'];relative=folder.relative_to(ROOT).as_posix()
        for name in ['ficha.json','fuentes.json','documentacion.json','logotipo.json']:
            previous=subprocess.run(['git','show','HEAD:'+relative+'/'+name],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
            if previous.returncode==0:(folder/name).write_bytes(previous.stdout)
            elif name in ['documentacion.json','logotipo.json'] and (folder/name).exists():
                if name=='logotipo.json':
                    image=folder/read(folder/name)['file']
                    if image.resolve().parent==folder.resolve() and image.exists():image.unlink()
                (folder/name).unlink()
        save(folder/'revision.json',{'date':DATE,'identity':'sin correspondencia confirmada','rejectedCandidate':item['qid'],'reason':'Nombre reutilizado o cronología incompatible con la inscripción. No se transfieren fechas, marcas ni datos de otra entidad homónima.'})
        continue
    folder=ROOT/item['folder'];meta=read(folder/'ficha.json');entity=entities[item['qid']]
    meta['wikidata']=item['qid'];meta['aliases']=sorted(set(x['value'] for x in list(entity.get('labels',{}).values())+sum(entity.get('aliases',{}).values(),[]) if len(x['value'])<120))
    for prop,key in [('P571','founding'),('P576','dissolution')]:
        meta.pop(key,None)
        value=date_claim(entity,prop)
        if value:meta[key]=value
    refs=read(folder/'fuentes.json',[]);wiki='https://www.wikidata.org/wiki/'+item['qid']
    if not any(r['url']==wiki for r in refs):refs.append({'label':'Wikidata · identidad y referencias de la organización','url':wiki,'kind':'encyclopedic'})
    site=entity.get('sitelinks',{}).get('eswiki')
    if site:
        from urllib.parse import quote
        url='https://es.wikipedia.org/wiki/'+quote(site['title'].replace(' ','_'))
        if not any(r['url']==url for r in refs):refs.append({'label':site['title']+' · Wikipedia','url':url,'kind':'encyclopedic'})
    description=entity.get('descriptions',{}).get('es',{}).get('value')
    if description and (meta.get('summary','').startswith('Formación incluida') or not meta.get('summary')):
        meta['summary']=description[:1].upper()+description[1:]+'. La ficha conserva la inscripción y enlaza las fuentes documentadas.'
    web=read(C/'webs'/(item['id']+'.json'),{})
    if web.get('website'):
        meta['website']=web['website'];resources=[]
        checked=read(C/'enlaces'/(item['id']+'.json'),[])
        resourcesByUrl={r['url']:r for r in checked}
        for resource in web.get('resources',[]):
            if resourcesByUrl.get(resource['url'],{}).get('error'):continue
            if re.search(r'/actualidad/|/noticias/',resource['url']) and not resource['url'].lower().endswith('.pdf'):continue
            title=resource['title']
            if title.lower() in ['ver más','ver mas','aquí','aqui','leer más','leer mas','descargar','saber más','saber mas','institucional','continuar comprando','{title}','descarrega document']:
                title=resource['url'].rstrip('/').split('/')[-1].replace('-',' ').replace('_',' ').capitalize()
            kind=resource['kind']
            if re.search(r'programa|manifest',title+' '+resource['url'],re.I):kind='programa'
            elif re.search(r'estatut',title+' '+resource['url'],re.I):kind='estatutos'
            resources.append({**resource,'title':urllib.parse.unquote(title),'kind':kind})
        resources.sort(key=lambda r:({'programa':0,'estatutos':1,'historia':2,'transparencia':3,'organización':4}[r['kind']],-int(r.get('date','0')[:4]) if r.get('date','')[:4].isdigit() else 0))
        save(folder/'documentacion.json',resources[:20])
    if web.get('rejected'):meta.pop('website',None)
    mark=read(C/'marcas'/(item['id']+'.json'),{})
    if mark.get('file') and not (folder/'logotipo.json').exists():
        file='logotipo'+mark['extension'];shutil.copyfile(ROOT/mark['file'],folder/file)
        save(folder/'logotipo.json',{k:v for k,v in {'file':file,'source':mark['source'],'original':mark['original'],'credit':mark.get('credit'),'license':mark.get('license'),'licenseUrl':mark.get('licenseUrl'),'identity':mark.get('identity'),'background':'dark' if mark.get('background')=='#182c49' else mark.get('background')}.items() if v})
    save(folder/'ficha.json',meta);save(folder/'fuentes.json',refs)
    review={'date':DATE,'identity':wiki,'matching':'Denominación o alias completo, sin coincidencias ambiguas; principales partidos contrastados por identidad específica.','logo':'documentado' if (folder/'logotipo.json').exists() else 'no localizado en las fuentes consultadas','website':'contrastada' if web.get('website') else 'sin nueva confirmación','documents':len(read(folder/'documentacion.json',[]))}
    save(folder/'revision.json',review);reports.append({'id':meta['id'],**review})

# El BOE separa partidos, federaciones y coaliciones. No repartir sus votos entre integrantes.
folders={read(p)['id']:p.parent for p in (ROOT/'Partidos').glob('*/ficha.json')}
index={norm(read(p)['fullName']):read(p)['id'] for p in (ROOT/'Partidos').glob('*/ficha.json')}
aliases={'Partido Popular':'pp','Partido Socialista Obrero Español':'psoe','VOX':'vox','Partit dels Socialistes de Catalunya (PSC-PSOE)':'psc','Esquerra Republicana de Catalunya':'erc','Junts':'junts','Euskal Herria Bildu':'eh-bildu','Euzko Alderdi Jeltzalea-Partido Nacionalista Vasco':'pnv','Bloque Nacionalista Galego':'bng','Coalición Canaria':'cc','Unión del Pueblo Navarro':'upn','Partido Animalista con el Medio Ambiente':'pacma','Nueva Canarias-Bloque Canarista':'registro-4478','Unión del Pueblo Leones':None}
# Solo usar una correspondencia manual si el ID existe y su nombre corresponde.
aliases.pop('Nueva Canarias-Bloque Canarista')
aliases.pop('Unión del Pueblo Leones')
soup=BeautifulSoup((C/'resultados-boe.html').read_bytes(),'html.parser');results=[]
for tableIndex,table in enumerate(soup.select('table')):
    rows=table.select('tr');headers=[c.get_text(' ',strip=True) for c in rows[0].find_all(['td','th'],recursive=False)];totals=[c.get_text(' ',strip=True) for c in rows[-1].find_all(['td','th'],recursive=False)]
    seats=tableIndex<3;labels=headers[2:] if seats else headers[1:];values=totals[2:] if seats else totals[1:]
    for i,label in enumerate(labels):
        name=re.sub(r'\s*\([^()]*\)\s*$','',label).strip();votes=int(re.sub('[^0-9]','',values[i*(2 if seats else 1)]));count=int(values[2*i+1]) if seats else 0
        organization=aliases.get(name) or index.get(norm(name))
        if name=='Sumar':organization='sumar-coalicion-2023'
        if not organization:
            organization='candidatura-2023-'+re.sub('[^a-z0-9]+','-',unicodedata.normalize('NFD',name).encode('ascii','ignore').decode().lower()).strip('-')
        if organization not in folders:
            safeName=re.sub(r'[<>:"/\\|?*]','—',name).rstrip('. ')
            if organization=='sumar-coalicion-2023':safeName='Sumar — Coalición electoral 2023'
            folder=ROOT/'Partidos'/safeName
            if folder.exists():folder=ROOT/'Partidos'/(safeName+' [Candidatura 2023]')
            folder.mkdir(exist_ok=True);folders[organization]=folder
            save(folder/'ficha.json',{'id':organization,'name':name,'fullName':name+(' · coalición electoral de 2023' if organization=='sumar-coalicion-2023' else ''),'summary':'Candidatura documentada en los resultados oficiales de las elecciones generales de 2023. Sus cifras corresponden a esta candidatura y no se atribuyen por separado a sus integrantes.'})
            save(folder/'fuentes.json',[{'label':'Junta Electoral Central · resultados de 2023','url':'https://www.boe.es/buscar/doc.php?id=BOE-A-2023-18907','kind':'institutional'}])
        result={'election':'Elecciones generales · 23 de julio de 2023','date':'2023-07-23','chamber':'congreso','votes':votes,'seats':count,'candidature':label,'source':{'label':'Junta Electoral Central · BOE, cuadro '+('II' if seats else 'III'),'url':'https://www.boe.es/buscar/doc.php?id=BOE-A-2023-18907','kind':'institutional'}}
        file=folders[organization]/'resultados.json';previous=read(file,[]);previous=[r for r in previous if not (r['date']==result['date'] and r['chamber']==result['chamber'])];save(file,previous+[result]);results.append({'organization':organization,**result})
assert sum(r['seats'] for r in results)==350
save(ROOT/'Partidos/revisiones'/DATE/'informe.json',{'date':DATE,'scope':'Conservación del registro completo; identidades contrastadas por denominación completa, webs consultadas individualmente y recursos con procedencia. Una ausencia de correspondencia no prueba inexistencia de web, marca o actividad.','registered':len([p for p in (ROOT/'Partidos').glob('*/ficha.json') if read(p).get('registration')]),'enriched':len(reports),'records':reports,'electoralCandidatures':results})
print('Partidos contrastados',len(reports),'candidaturas con cifras',len(results),'escaños',sum(r['seats'] for r in results))
