"""Consulta los electos (S) de Ceuta/Melilla en microdatos oficiales históricos.

No importa el intérprete de terceros. Lee los campos del formato publicado por
Interior; el espejo conserva los originales y su huella Git se verifica.
No extrae ni guarda DNI, sexo, nacimiento ni candidatos no elegidos.
"""
import concurrent.futures, hashlib, importlib.util, json, pathlib, urllib.request
spec=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-canarias-ceuta-melilla.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
BASE='https://raw.githubusercontent.com/JaimeObregon/infoelectoral/main/'

def collect(year):
    month='06' if year==1999 else '05';stem=f'04{year}{month}_TOTA'
    inventory=json.loads((r.CACHE/'microdatos-archivos.json').read_text('utf8'))
    paths=[row for row in inventory if f'/municipales/{stem}/' in row['path'] and row['path'].split('/')[-1].startswith(('03','04'))]
    if len(paths)!=2:raise ValueError('Ficheros no documentados: '+stem)
    documents={}
    for row in paths:
        # El fichero de candidatos se procesa en memoria, sin persistir campos ajenos.
        raw=urllib.request.urlopen(BASE+row['path'],timeout=40).read()
        sha=hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
        if sha!=row['sha']:raise ValueError('Original modificado: '+row['path'])
        documents[row['path'].split('/')[-1][:2]]=(raw,row)
    formations={line[8:14].decode():{'label':line[14:64].decode('latin1').strip(),'name':line[64:214].decode('latin1').strip()} for line in documents['03'][0].splitlines()}
    output={'Ceuta':[],'Melilla':[]}; row=documents['04'][1]
    original=f'https://infoelectoral.interior.gob.es/estaticos/docxl/apliextr/{stem}.zip'
    for line in documents['04'][0].splitlines():
        region={'51':'Ceuta','52':'Melilla'}.get(line[9:11].decode())
        if not region or line[119:120]!=b'S':continue
        name=' '.join(line[25:100].decode('latin1').split())
        output[region].append({'name':name,'formation':formations[line[15:21].decode()],'order':int(line[21:24]),'source':original,'mirror':BASE+row['path'],'gitBlob':row['sha'],'year':year})
    for region,rows in output.items():
        if len(rows)!=25:raise ValueError(f'{region} {year}: {len(rows)} electos')
        r.write(r.CACHE/f'{region.lower()}-interior-{year}.json',rows)
    return year,{k:len(v)for k,v in output.items()}

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(3)as pool:
        for result in pool.map(collect,range(1995,2020,4)):print(result,flush=True)
