"""Comprueba disponibilidad HTTP de las referencias, sin validar su contenido histórico."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1] / 'investigacion' / 'presidencias-centrales'


def probe(source: dict) -> dict:
    result = {'source': source['id'], 'url': source['url']}
    for method in ('HEAD', 'GET'):
        request = urllib.request.Request(
            source['url'],
            method=method,
            headers={'User-Agent': 'Elecciones-source-link-check/1.0', 'Range': 'bytes=0-1023'},
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                result.update(method=method, httpStatus=response.status,
                              resolvedUrl=response.url, result='available')
                return result
        except urllib.error.HTTPError as error:
            result.update(method=method, httpStatus=error.code, result='not-verified', error=str(error))
            if method == 'HEAD' and error.code in (403, 405, 501):
                continue
            return result
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            result.update(method=method, result='not-verified', error=str(error))
            return result
    return result


def main() -> None:
    sources = json.loads((ROOT / 'fuentes.json').read_text(encoding='utf-8'))['sources']
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(probe, sources))
    report = {
        'checkedAt': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'scope': 'Disponibilidad HTTP. No comprueba afirmaciones, identidad del documento ni actualización judicial. Un error puede corresponder a restricciones de acceso o del cliente.',
        'sources': len(results),
        'available': sum(row['result'] == 'available' for row in results),
        'results': results,
    }
    (ROOT / 'comprobacion-enlaces.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n'
    )
    print(json.dumps({key: report[key] for key in ('sources', 'available')}, ensure_ascii=False))
    for result in results:
        if result['result'] != 'available':
            print(result['source'], result.get('httpStatus', ''), result.get('error', ''))


if __name__ == '__main__':
    main()
