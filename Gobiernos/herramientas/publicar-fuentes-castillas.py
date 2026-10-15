import importlib.util
s=importlib.util.spec_from_file_location('c','Gobiernos/herramientas/consultar-castillas.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
import json
def load(name):return json.loads((c.CACHE/name).read_text('utf8'))
for r,folder in [('clm','Castilla-La Mancha'),('cyl','Castilla y León')]:
    root=c.pathlib.Path('Gobiernos/Autonomías')/folder/'fuentes'
    c.write(root/'mesas-publicadas.json',{'checkedAt':c.CHECKED,'records':load('clm-mesas.json')if r=='clm'else load('cyl-composiciones.json')})
    errors=[{'source':p['source'],'name':p['name'],'error':p['sourceError']}for p in load(r+'-perfiles.json')if p.get('sourceError')]
    c.write(root/'incidencias-consulta.json',{'checkedAt':c.CHECKED,'profiles':errors,'historicalReferences':load('referencias-historicas-incidencias.json')})
    corrected=load(r+'-listas.json')
    c.write(root/'listados-parlamentarios.json',corrected)
print('Fuentes publicadas')
