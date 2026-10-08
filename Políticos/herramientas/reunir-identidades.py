"""Reúne coincidencias revisadas de nombre y nacimiento sin perder IDs ni recursos.

Las carpetas retiradas se conservan fuera del catálogo en test-results. El informe
publicado documenta cada unión y los recursos originales quedan también en la ficha.
"""
import pathlib, json, shutil, hashlib, unicodedata, re, collections
ROOT = pathlib.Path(__file__).resolve().parents[2]
PEOPLE = ROOT / 'Políticos'
def read(p, default=None):
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def union(a, b):
    result = list(a)
    seen = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in a}
    for item in b:
        key = json.dumps(item, sort_keys=True, ensure_ascii=False)
        if key not in seen: result.append(item); seen.add(key)
    return result
original = {r['id'] for r in read(PEOPLE/'revisiones/2026-10-08/informe.json')['records']}
pairs = [
 ('aitor-esteban','congreso-304-15'), ('senado-10468','congreso-22-1'),
 ('congreso-65-15','senado-12969'), ('eduardo-zaplana-hernandez-soro','congreso-68-9'),
 ('senado-10270','congreso-153-2'), ('congreso-356-5','congreso-384-3'),
 ('francisco-caamano-dominguez','congreso-66-10'), ('francisco-fernandez-ordonez','congreso-249-3'),
 ('congreso-379-15','senado-15905'), ('senado-10009','congreso-375-2'),
 ('juan-lerma-blasco','congreso-77-2'), ('senado-10562','congreso-277-10'),
 ('leopoldo-calvo-sotelo-y-bustelo','congreso-372-2'), ('manuel-chaves-gonzalez','congreso-252-10'),
 ('senado-15244','congreso-46-14'), ('senado-10492','congreso-86-9'),
 ('oriol-junqueras','congreso-333-13'), ('senado-10368','congreso-147-7'),
 ('senado-10500','congreso-282-7'), ('santiago-carrillo','congreso-293-2'),
 ('congreso-182-6','senado-10262'),
]
folders = {read(p)['id']: p.parent for p in PEOPLE.glob('*/ficha.json')}
reports = []
for keep, discard in pairs:
    if discard not in folders: continue
    source, target = folders[discard], folders[keep]
    assert source.resolve().parent == PEOPLE.resolve() and target.resolve().parent == PEOPLE.resolve()
    first, second = read(target/'ficha.json'), read(source/'ficha.json')
    a, b = read(target/'datos-personales.json', {}), read(source/'datos-personales.json', {})
    assert a.get('birthDate') and a.get('birthDate') == b.get('birthDate'), (keep, discard)
    first['legacyIds'] = union(first.get('legacyIds', []), [discard, *second.get('legacyIds', [])])
    first['knownAs'] = union(first.get('knownAs', []), [second['name'], second['fullName'], *second.get('knownAs', [])])
    first['offices'] = union(first.get('offices', []), second.get('offices', []))
    files = []
    for p in source.iterdir():
        if p.name == 'ficha.json': continue
        dest = target/p.name
        if not dest.exists(): shutil.copyfile(p, dest)
        elif p.suffix == '.json':
            left, right = read(dest), read(p)
            if isinstance(left, list) and isinstance(right, list): save(dest, union(left, right))
            elif p.name == 'datos-personales.json':
                combined = {**right, **left}
                combined['personalSources'] = union(left.get('personalSources', []), right.get('personalSources', []))
                save(dest, combined)
        elif hashlib.sha256(p.read_bytes()).digest() != hashlib.sha256(dest.read_bytes()).digest():
            shutil.copyfile(p, target/('recurso-'+discard+'-'+p.name))
        files.append({'file': p.name, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    save(target/'ficha.json', first)
    backup = ROOT/'test-results/revision-partidos/fichas-reunidas'/source.name
    assert backup.resolve().is_relative_to((ROOT/'test-results').resolve()) and not backup.exists()
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(backup))
    reports.append({'id': keep, 'previousId': discard, 'names': [first['fullName'], second['fullName']], 'birthDate': a['birthDate'], 'evidence': 'Nombre completo compatible y fecha de nacimiento coincidente; fuentes individuales conservadas.', 'resources': files})
    del folders[discard]
# Los titulares pueden ser mujeres o personas fallecidas. No se infiere género ni
# situación vital de una denominación antigua de la credencial.
for folder in folders.values():
    p = folder/'ficha.json'; meta = read(p)
    if meta['id'] not in original and meta.get('role') in ['Senador','Diputado']:
        meta['role'] = 'Miembro del Senado' if meta['role']=='Senador' else 'Miembro del Congreso'; save(p, meta)
    timeline = read(folder/'trayectoria.json', [])
    updated = [{**r, 'title': re.sub(r'^Senador(?: incluido)?', 'Miembro del Senado', r['title'])} for r in timeline]
    if updated != timeline: save(folder/'trayectoria.json', updated)
auditPath = PEOPLE/'revisiones/2026-10-08-parlamento/informe.json'
audit = read(auditPath)
aliases = {alias: m['id'] for folder in folders.values() for m in [read(folder/'ficha.json')] for alias in [m['id'], *m.get('legacyIds', [])]}
for r in audit['records']:
    r['id'] = aliases[r['id']]
    r['portrait'] = (folders[r['id']]/'retrato.json').exists()
audit['uniquePeople'] = len(folders)
save(auditPath, audit)
previous = read(PEOPLE/'revisiones/2026-10-08-parlamento/identidades-reunidas.json', [])
save(PEOPLE/'revisiones/2026-10-08-parlamento/identidades-reunidas.json', union(previous, reports))
print('Identidades reunidas:', len(reports), 'personas conservadas:', len(folders))
