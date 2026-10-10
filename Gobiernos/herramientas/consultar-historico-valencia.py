"""Localiza normas del DOGV por fechas conocidas; no infiere nombramientos.

Guarda las respuestas originales en la caché ignorada. El resultado requiere
lectura de las disposiciones y comprobación de sus efectos antes de integrarse.
"""
import concurrent.futures, datetime, hashlib, io, json, pathlib, re, subprocess, sys
from urllib.parse import urljoin
sys.path.insert(0,'test-results/libraries')
from bs4 import BeautifulSoup
from pypdf import PdfReader
ROOT=pathlib.Path('test-results/valencia/historico');ROOT.mkdir(parents=True,exist_ok=True)
def fetch(url, payload=None):
    path=ROOT/(hashlib.sha256((url+json.dumps(payload)).encode()).hexdigest()+'.raw')
    if not path.exists():
        args=['curl.exe','--fail','--silent','--show-error','--location','--max-time','35']
        if payload is not None:
            body=path.with_suffix('.request.json');body.write_text(json.dumps(payload),'utf8')
            args+=['--header','Content-Type: application/json','--data-binary','@'+str(body)]
        result=subprocess.run(args+[url],capture_output=True)
        if result.returncode or not result.stdout:raise ValueError('Documento no disponible: '+url)
        path.write_bytes(result.stdout)
    return path.read_bytes()
def portal(day):
    url='https://dogv.gva.es/dogv-portal/dogv?date='+day+'&lang=es'
    try:
        data=json.loads(fetch(url));items=[]
        for a in data.get('disposiciones',[]):
            label=a['titulo']
            if re.search(r'consellers?\b|conselleras?\b|vicepresiden|presidente|titularidad de las conseller',label,re.I) and re.search(r'nombra|cese|cesa|cess|asigna|designa|consellerias|consellerías',label,re.I):
                link='https://dogv.gva.es/dogv-portal/disposicion/'+str(a['id'])+'?lang=es';items.append({'date':day,'label':label,'url':link,'id':a['id']})
        return {'date':day,'portal':url,'documents':items}
    except Exception as e:return {'date':day,'error':str(e),'documents':[]}
def text(url):
    raw=fetch(url)
    if raw.startswith(b'%PDF'):return '\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(raw)).pages)
    if raw.startswith(b'{'):return BeautifulSoup(json.loads(raw).get('texto',''),'html.parser').get_text('\n',strip=True)
    return BeautifulSoup(raw,'html.parser').get_text('\n',strip=True)
if __name__=='__main__':
    if '--search' in sys.argv:
        payload={'texto':sys.argv[2],'soloTitulo':True,'fechaInicioPublicacion':'01-01-1983','fechaFinPublicacion':'20-07-2023','isPortalLegislativo':False}
        url='https://dogv.gva.es/dogv/search?lang=es&page=0&size=100&sort=fechaPublicacion,asc'
        data=json.loads(fetch(url,payload));(ROOT/'search-example.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8');print(str(data)[:5000])
    elif '--text' in sys.argv:
        for url in sys.argv[2:]:
            result=text(url);dest=ROOT/(hashlib.sha256(url.encode()).hexdigest()+'.txt');dest.write_text(result,encoding='utf8');print(url+'\n'+result[:18000])
    else:
        dates=set(sys.argv[1:])
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:result=list(pool.map(portal,sorted(dates)))
        path=ROOT/'portales.json';previous=json.loads(path.read_text('utf8')) if path.exists() else []
        merged={r['date']:r for r in previous+result};path.write_text(json.dumps(list(merged.values()),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        for r in result:
            if r['documents']:print(json.dumps(r,ensure_ascii=False),flush=True)
        print('Consultados:',len(result),'con normas:',sum(bool(r['documents']) for r in result),'no disponibles:',sum('error' in r for r in result),flush=True)
