"""Documentos históricos y acceso oficial; ninguna propuesta se atribuye a 2026."""
import pathlib,json,shutil
ROOT=pathlib.Path(__file__).resolve().parents[2]
def read(p,default=None):return json.loads(p.read_text(encoding='utf-8')) if p.exists() else default
def save(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
folders={read(p)['id']:p.parent for p in (ROOT/'Partidos').glob('*/ficha.json')}
coalition=folders['sumar-coalicion-2023']; movement=folders['sumar']
meta=read(coalition/'ficha.json');meta['website']='https://movimientosumar.es/';save(coalition/'ficha.json',meta)
logo=read(movement/'logotipo.json');shutil.copyfile(movement/logo['file'],coalition/logo['file'])
save(coalition/'logotipo.json',{**logo,'context':'Marca Sumar del portal de la candidatura; la coalición electoral de 2023 se mantiene separada de Movimiento Sumar.'})
program={'title':'Un programa para ti · elecciones generales de 2023','url':'https://movimientosumar.es/transparencia/wp-content/uploads/sites/6/2023/12/un-programa-para-ti.pdf','kind':'programa','date':'2023','format':'PDF'}
save(coalition/'documentacion.json',[program,{'title':'Acuerdo de la coalición Sumar · generales de 2023','url':'https://movimientosumar.es/transparencia/wp-content/uploads/sites/6/2025/07/PactoCoalicionSumar23J.pdf','kind':'organización','date':'2023','format':'PDF'}])
extras={
 'pp':[{'title':'Programa electoral de las generales · 2023','url':'https://www.pp.es/wp-content/uploads/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf','kind':'programa','date':'2023','format':'PDF'}],
 'psoe':[{'title':'Archivo oficial de programas electorales','url':'https://www.psoe.es/transparencia/informacion-politica-organizativa/programa/','kind':'programa'}],
 'vox':[{'title':'Programa electoral oficial · generales de 2023','url':'https://www.voxespana.es/programa/programa-electoral-Vox','kind':'programa','date':'2023'}],
}
for id,items in extras.items():
 p=folders[id]/'documentacion.json';old=read(p,[]);urls={x['url'] for x in items};save(p,items+[x for x in old if x['url'] not in urls])
print('Programas históricos y candidatura Sumar incorporados')
