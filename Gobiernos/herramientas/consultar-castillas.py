"""Consulta institucional de las dos Castillas; caché de trabajo fuera del catálogo."""
import concurrent.futures, hashlib, json, pathlib, re, ssl, subprocess, sys, time, urllib.request
from urllib.parse import urljoin
from urllib.parse import parse_qs,urlparse,quote
sys.path.insert(0,'test-results/libraries')
from bs4 import BeautifulSoup
CACHE=pathlib.Path('test-results/castillas');CHECKED='2026-10-15'
TLS=ssl.create_default_context()
if sys.platform=='win32':
    for store in ['ROOT','CA']:
        for certificate,encoding,trust in ssl.enum_certificates(store):
            if encoding=='x509_asn':
                try:TLS.load_verify_locations(cadata=ssl.DER_cert_to_PEM_cert(certificate))
                except ssl.SSLError:pass
def write(path,value):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    if not path.exists() or path.read_text('utf8')!=text:path.write_text(text,'utf8')
def fetch(url):
    url=quote(url,safe=':/?&=%+#')
    path=CACHE/'documents'/hashlib.sha256(url.encode()).hexdigest()
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True)
        request=urllib.request.Request(url,headers={'User-Agent':'Elecciones/1.0 (consulta de fuentes institucionales)'})
        for attempt in range(3):
            try:raw=urllib.request.urlopen(request,timeout=40,context=TLS).read();break
            except urllib.error.URLError as error:
                if sys.platform=='win32' and isinstance(error.reason,ssl.SSLCertVerificationError):
                    subprocess.run(['powershell','-NoProfile','-File',str(pathlib.Path(__file__).with_name('consultar-fuente-windows.ps1')),url,str(path)],check=True,capture_output=True)
                    return path.read_bytes()
                if attempt==2:raise
                time.sleep(attempt+1)
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    return path.read_bytes()
def soup(url):
    raw=fetch(url)
    try:text=raw.decode('utf8')
    except UnicodeDecodeError:text=raw.decode('windows-1252',errors='replace')
    return BeautifulSoup(text,'html.parser')
def inspect(url):
    try:
        page=soup(url);main=page.select_one('main') or page.select_one('#content') or page
        links=[{'text':a.get_text(' ',strip=True),'url':urljoin(url,a['href'])}for a in main.select('a[href]')]
        result={'url':url,'text':main.get_text(' ',strip=True),'links':links}
        write(CACHE/'inspeccion'/ (hashlib.sha256(url.encode()).hexdigest()+'.json'),result)
        return {'url':url,'text':result['text'][:1800],'links':links[:90]}
    except Exception as e:return {'url':url,'error':str(e)}
def clean(text):return re.sub(r'\s+',' ',text).strip()
def iso(text):
    m=re.search(r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b',text)
    return f'{m[3]}-{int(m[2]):02}-{int(m[1]):02}' if m else None
def clm_list(leg):
    url=f'https://www.cortesclm.es/web2/paginas/resul_diputados.php?legislatura={leg}'
    p=soup(url);rows={};current=[]
    for a in p.select('a[href]'):
        m=re.search(r'abrirventana\([\'\"]?(\d+)[\'\"]?,[\'\"]?(\d+)',a['href'])
        if not m:continue
        key=m[1];cells=a.find_parent('tr').find_all('td',recursive=False);label=clean(a.get_text(' ',strip=True))
        ordered=', ' in label and len(cells)>=4
        if ordered:
            surname,first=label.split(',',1);name=clean(first+' '+surname)
            province=clean(cells[1].get_text(' ',strip=True));group=clean(cells[3].get_text(' ',strip=True));current.append(key)
        else:
            name=re.sub(r'^(?:Dña\.|D\.|Doña|Don)\s*','',label);province=None;group=None
        source=f'https://www.cortesclm.es/web2/paginas/detalle_diputado{"Old" if leg<9 else ""}.php?id={key}'
        if key not in rows or ordered:rows[key]={'key':key,'legislature':leg,'name':name,'constituency':province,'group':group,'source':source,'listSource':url}
    return {'legislature':leg,'source':url,'listed':current,'records':list(rows.values())}
def clm_profile(row):
    p=soup(row['source']);heading=p.select_one('#nombreDiputado h1');text=p.get_text(' ',strip=True)
    name=clean(heading.get_text(' ',strip=True)) if heading else row['name']
    if row['legislature']<9:
        h=next((n for n in p.select('td,p,b,strong')if clean(n.get_text(' ',strip=True))==row['name']),None)
        if h:name=clean(h.get_text(' ',strip=True))
    image=p.select_one('#fotoDiputado img') or next((i for i in p.select('img[src]')if i['src'].startswith('data:image')),None)
    photo=image['src'] if image else None
    if photo and ';base64,' in photo:photo='data:image/jpeg;base64,'+photo.split(';base64,',1)[1]
    elif photo:photo=urljoin(row['source'],photo)
    other=p.select_one('#otros');bio=other.get_text(' ',strip=True) if other else text
    education=re.search(r'Titulación\s*:\s*(.+?)(?=\s+(?:Cargos|Cerrar|Profesión|Iniciativas)|$)',bio)
    roles=[]
    for tr in p.select('tr'):
        td=tr.find_all('td',recursive=False)
        if len(td)==4 and iso(td[2].get_text()):
            roles.append({'role':clean(td[0].get_text(' ',strip=True)),'organ':clean(td[1].get_text(' ',strip=True)),'start':iso(td[2].get_text()),'endInSource':iso(td[3].get_text())})
    biography=[]
    for part in re.split(r'\s+-\s+',bio):
        m=re.match(r'(.{3,190}?)\s*[\[(](\d{4}(?:\s*[-–]\s*\d{4})?)[\])]',part.strip(' -'))
        if m and not any(k in m[1].lower()for k in ['email','teléfono','nacid']):biography.append({'title':m[1].strip(),'period':m[2]})
    return {**row,'name':name,'image':photo,'education':[education[1].strip()] if education and len(education[1])<260 else [],'roles':roles,'biography':biography,'checkedAt':CHECKED}
def cyl_list(leg):
    url=f'http://www.ccyl.es/Organizacion/Procuradores?Legislatura={leg}'
    p=soup(url);rows=[]
    for a in p.select('a[href]'):
        if a.get_text(' ',strip=True)!='Detalle Procurador':continue
        tr=a.find_parent('tr');n=tr.select_one('.cc_org_Procurador');g=tr.select_one('.cc_org_ProcuradorGrupoParlamentario');province=tr.select_one('.cc_org_ProcuradorGrupoProvincia');note=tr.select_one('.cc_org_ProcuradorNotas')
        source=urljoin(url,a['href']);key=parse_qs(urlparse(source).query)['CodigoPersona'][0]
        rows.append({'key':key,'legislature':leg,'name':clean(n.get_text(' ',strip=True)),'group':re.sub(r'^G\.P\.\s*','',clean(g.get_text(' ',strip=True))) if g else None,'constituency':re.sub(r'^G\.P\.\s*','',clean(province.get_text(' ',strip=True))) if province else None,'note':clean(note.get_text(' ',strip=True))if note else '', 'source':source,'listSource':url})
    return {'legislature':leg,'source':url,'records':rows}
def cyl_profile(row):
    p=soup(row['source']);main=p.select_one('#fichaprocurador') or p
    heading=main.select_one('#rotuloprocurador h3');name=clean(heading.get_text(' ',strip=True))if heading else row['name']
    image=next((i for i in main.select('img[src]')if '/procuradores/' in i['src']),None)
    bio=main.select_one('#bioprocurador');education=[]
    if bio:
        for n in bio.select('p,li,div'):
            t=clean(n.get_text(' ',strip=True))
            if re.match(r'^(?:Licenciad[oa]|Diplomad[oa]|Graduad[oa]|Grado en|Doctor[ao]?|Ingenier[oa]|Máster|Master|Arquitect[oa])\b',t,re.I) and len(t)<240:education.append(t)
    roles=[clean(a.get_text(' ',strip=True))for a in main.select('#organosprocurador a')]
    return {**row,'name':name,'image':urljoin(row['source'],image['src'])if image else None,'education':list(dict.fromkeys(education))[:6],'roles':roles,'checkedAt':CHECKED}
def collect():
    with concurrent.futures.ThreadPoolExecutor(4)as pool:
        clm=list(pool.map(clm_list,range(1,12)));cyl=list(pool.map(cyl_list,range(1,13)))
    write(CACHE/'clm-listas.json',clm);write(CACHE/'cyl-listas.json',cyl)
    print('Listas CLM',[(r['legislature'],len(r['listed']),len(r['records']))for r in clm],flush=True)
    print('Listas CYL',[(r['legislature'],len(r['records']))for r in cyl],flush=True)
    for kind,lists,fn in [('clm',clm,clm_profile),('cyl',cyl,cyl_profile)]:
        seen={}
        for leg in lists:
            for r in leg['records']:seen[r['source']]=r
        records=[]
        def reviewed(row):
            try:return fn(row)
            except Exception as error:return {**row,'checkedAt':CHECKED,'sourceError':str(error),'image':None,'education':[],'roles':[],'biography':[]}
        with concurrent.futures.ThreadPoolExecutor(6)as pool:
            for i,r in enumerate(pool.map(reviewed,seen.values())):
                records.append(r)
                if (i+1)%100==0:print(kind,i+1,flush=True)
        write(CACHE/f'{kind}-perfiles.json',records);print(kind,'PERFILES',len(records),flush=True)
if __name__=='__main__':
    if sys.argv[1:]==['--collect']:collect()
    else:
        with concurrent.futures.ThreadPoolExecutor(4) as pool:
            for row in pool.map(inspect,sys.argv[1:]):print(json.dumps(row,ensure_ascii=False),flush=True)
