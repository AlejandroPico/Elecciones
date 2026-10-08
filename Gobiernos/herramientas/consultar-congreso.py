"""Consulta Mesa y adscripciones fechadas del Congreso desde 1977.

Endpoints públicos expuestos por /opendata/organos y /grupos/composicion-en-la-legislatura.
El plano público de /hemiciclo muestra el aviso de disolución; no se inventan asientos.
Reanudar reutiliza la caché. HTTP 429 detiene nuevas consultas.
"""
from pathlib import Path
import json, urllib.request, urllib.parse, time, threading, concurrent.futures

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / 'test-results/congreso-estructura'
CACHE.mkdir(parents=True, exist_ok=True)
ROMANS = ['0','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII','XIII','XIV','XV']
lock = threading.Lock()
last = 0
stopped = threading.Event()

def query(file, url, params):
    global last
    target = CACHE / file
    if target.exists():
        return json.loads(target.read_text(encoding='utf8'))
    for attempt in range(3):
        if stopped.is_set():
            raise RuntimeError('La fuente solicita una pausa')
        with lock:
            time.sleep(max(0, .35 - (time.monotonic() - last)))
            last = time.monotonic()
        try:
            request = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode(), headers={'User-Agent':'Mozilla/5.0'})
            raw = urllib.request.urlopen(request, timeout=40).read()
            data = json.loads(raw)
            target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
            return data
        except urllib.error.HTTPError as error:
            if error.code == 429:
                stopped.set()
                raise
            if attempt == 2: raise
        except Exception:
            if attempt == 2: raise
        time.sleep(2 * (attempt + 1))

def legislature(leg):
    roman = ROMANS[leg]
    mesa_url = 'https://www.congreso.es/es/mesa?p_p_id=organos&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=searchOrgano&p_p_cacheability=cacheLevelPage&_organos_selectedLegislatura='+roman+'&_organos_statusOpenData=true'
    query(f'mesa-{leg}.json', mesa_url, {'_organos_selectedLegislatura':roman,'_organos_compoHistorica':'true','_organos_selectedOrganoSup':'100','_organos_selectedSuborgano':''})
    url = 'https://www.congreso.es/es/grupos/composicion-en-la-legislatura?p_p_id=grupos&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=gruposSearch&p_p_cacheability=cacheLevelPage'
    groups = query(f'grupos-{leg}.json',url,{'_grupos_currentLegislatura':'15','_grupos_idLegislatura':roman})
    for group in groups['data']:
        code = group['codOrg']
        url = 'https://www.congreso.es/es/grupos/composicion-en-la-legislatura?p_p_id=grupos&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=diputadosSearch&p_p_cacheability=cacheLevelPage&_grupos_idLegislatura='+roman+'&_grupos_mostrarFicha=true&_grupos_gruposView=true&_grupos_idGrupo='+str(code)
        query(f'grupo-{leg}-{code}.json',url,{'_grupos_currentLegislatura':'15','_grupos_idLegislatura':roman,'_grupos_grupo':str(code),'_grupos_radioControl':'5' if leg == 15 else '2','_grupos_ini':'false','_grupos_altaBajaP':'true' if leg != 15 else 'false','_grupos_fin':'false','_grupos_actu':'false','_grupos_altaBajaA':'true' if leg == 15 else 'false'})
    print(f'Legislatura {roman}: Mesa y {len(groups["data"])} grupos', flush=True)

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        for _ in executor.map(legislature, reversed(range(16))): pass
