"""Transcripción factual de cuadros históricos; contrasta referencias primarias cuando existen."""
import importlib.util,json,re
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
spec=importlib.util.spec_from_file_location('g','Gobiernos/herramientas/consultar-gobiernos-castillas.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
c=g.c
def normalize(s):
    import unicodedata
    return re.sub(r'[^a-z0-9]+',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()).strip()
def prepare():
    pages=json.loads((c.CACHE/'gobiernos-historicos-consulta.json').read_text('utf8'));out=[];errors=[]
    def official(url):
        host=urlparse(url).hostname or ''
        return any(host==d or host.endswith('.'+d)for d in ['boe.es','jcyl.es','jccm.es','castillalamancha.es'])
    references={r['url']for p in pages for r in p.get('officialReferences',[])if official(r['url'])}
    def read(url):
        try:return url,normalize(g.text(url))
        except Exception as e:errors.append({'source':url,'error':str(e)});return url,''
    with ThreadPoolExecutor(4)as pool:texts=dict(pool.map(read,references))
    years={'Gobierno_de_Demetrio_Madrid':1983,'Gobierno_de_José_Constantino_Nalda':1986,'Gobierno_de_José_María_Aznar_(Castilla_y_León)':1987,'Gobierno_de_Jesús_Posada':1989,'Primer_gobierno_de_Juan_José_Lucas':1991,'Segundo_gobierno_de_Juan_José_Lucas':1995,'Tercer_gobierno_de_Juan_José_Lucas':1999,'Primer_gobierno_de_Juan_Vicente_Herrera':2001,'Segundo_gobierno_de_Juan_Vicente_Herrera':2003,'Tercer_gobierno_de_Juan_Vicente_Herrera':2007,'Cuarto_gobierno_de_Juan_Vicente_Herrera':2011,'Quinto_gobierno_de_Juan_Vicente_Herrera':2015,'Primer_Gobierno_Fernández_Mañueco':2019,'Segundo_Gobierno_Fernández_Mañueco':2022,'Gobierno_Cospedal':2011,'Primer_Gobierno_García-Page':2015,'Segundo_Gobierno_García-Page':2019}
    for page in pages:
        slug=page['source'].split('/')[-1];region='clm'if any(k in slug for k in ['García-Page','Cospedal'])else'cyl';year=years[slug]
        for table in page.get('tables',[]):
            layout=None
            for row in table:
                if not row:continue
                if row[0]=='Nombre':layout='name';continue
                if row[0]in ['Función','Cargo']:layout='role';continue
                if layout=='name' and len(row)>=5:name,role=row[0],row[2];period=row[3]+' — '+row[4]
                elif layout=='role' and len(row)>=2:
                    role,name=row[:2];period=' — '.join(x for x in row[2:]if re.search(r'\d{4}',x))or'Cuadro histórico del gobierno de '+str(year)
                elif len(row)==4 and row[2]and re.search(r'\d{4}',row[2]):
                    role=row[0];m=re.search(r'\d{1,2} de \w+ de \d{4}',row[2]);name=row[2][:m.start()].strip()if m else'';period=row[2][m.start():]if m else''
                else:continue
                if role.lower().startswith(('presidente','presidenta'))or '←'in role or '→'in role or not name or name in ['Nombre','Titular']:continue
                for n in re.split(r'\([^)]*\)',name):
                    n=re.sub(r'\[[^]]*\]','',n).strip(' .')
                    if not n or len(n)>100 or len(n.split())<2:continue
                    originalRole=role
                    if not re.match(r'^(?:Consejer|Vicepresiden|Segundo vicepresidente|Portavoz)',role,re.I):role='Consejería de '+role
                    primary=[];key=normalize(n)
                    words=[w for w in normalize(originalRole).split()if len(w)>5 and w not in ['consejero','consejera','vicepresidente','vicepresidenta','primero','segunda','segundo','primera']]
                    for reference in page.get('officialReferences',[]):
                        document=texts.get(reference['url'],'');index=document.find(key)
                        if index>=0 and (not words or any(w in document[max(0,index-260):index+len(key)+260]for w in words)):primary.append(reference['url'])
                    out.append({'territory':region,'stageYear':year,'name':n,'role':role,'period':period,'source':primary[0]if primary else page['source'],'discovery':page['source'],'primaryMatched':bool(primary)})
    # El anexo antiguo contiene erratas y nombres incompletos: se admiten solo
    # correspondencias exactas ya documentadas en el catálogo, nunca nombres deducidos.
    source='https://es.wikipedia.org/wiki/Anexo:Composici%C3%B3n_del_Consejo_de_Gobierno_de_la_Junta_de_Comunidades_de_Castilla-La_Mancha';p=c.soup(source);main=p.select_one('.mw-parser-output')or p
    stage={'Primer Gobierno Bono':1983,'Segundo Gobierno Bono':1987,'Tercer Gobierno Bono':1991,'Cuarto Gobierno Bono':1995,'Quinto Gobierno Bono':1999,'Sexto Gobierno Bono':2003,'Primer Gobierno Barreda':2004,'Segundo Gobierno Barreda':2007}
    for node in main.select('table.wikitable,li'):
        h=node.find_previous('h2');heading=re.sub(r'\s*\[.*','',h.get_text(' ',strip=True))if h else''
        if heading not in stage:continue
        d=node.find_previous('dt');period=c.clean(d.get_text(' ',strip=True))if d else'Cuadro histórico · '+str(stage[heading])
        pairs=[]
        if node.name=='table':
            for tr in node.select('tr'):
                td=tr.find_all(['td','th'],recursive=False)
                if len(td)==2:pairs.append((td[0].get_text(' ',strip=True),td[1].get_text(' ',strip=True)))
        else:
            text=c.clean(node.get_text(' ',strip=True))
            if ':'in text:pairs.append(text.split(':',1))
        for role,name in pairs:
            role=c.clean(role);name=c.clean(name).strip(' .:')
            if role.lower().startswith(('presidente','presidencia:'))or role=='Presidencia' or not name or len(name)>100:continue
            if not re.match(r'^(?:Consejer|Vicepresiden|Portavoz)',role,re.I):role='Consejería de '+role
            out.append({'territory':'clm','stageYear':stage[heading],'name':name,'role':role,'period':period,'source':source+'#'+heading.replace(' ','_'),'primaryMatched':False,'existingIdentityOnly':True})
    c.write(c.CACHE/'consejerias-historicas.json',out);c.write(c.CACHE/'referencias-historicas-incidencias.json',errors)
    print('ARCHIVO',len(out),'contraste primario',sum(r['primaryMatched']for r in out),'incidencias de consulta',len(errors),flush=True)
if __name__=='__main__':prepare()
