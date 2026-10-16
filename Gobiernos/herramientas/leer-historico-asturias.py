"""Archivo de Biblioteca JGPA: redonda = titulares iniciales; cursiva = incorporaciones.

Se aplica la nota de redacción del propio documento. Las incidencias conservan su
texto y no se convierten en intervalos diarios cuando no publican ambos límites.
"""
import importlib.util,pathlib,re,sys
sys.path.insert(0,'test-results/libraries')
import pymupdf
s=importlib.util.spec_from_file_location('x',pathlib.Path(__file__).with_name('consultar-cantabrico.py'));x=importlib.util.module_from_spec(s);s.loader.exec_module(x);c=x.c
SOURCE='https://www.jgpa.es/documents/11156/104641/Relaci%C3%B3n+general+de+Parlamentarios.pdf/eaa674bd-e5a7-437e-8cb9-e459925305c1'

def extract():
 doc=pymupdf.open(c.CACHE/'asturias-historico.pdf');out=[];current=None;mode=None;role=None;last=None
 for pi,page in enumerate(doc):
  if pi<6 or pi>36:continue
  lines=sorted([line for b in page.get_text('dict')['blocks']for line in b.get('lines',[])],key=lambda l:(round(l['bbox'][1],1),l['bbox'][0]))
  for line in lines:
   text=c.clean(''.join(s['text']for s in line['spans']));heading=re.match(r'^([IVX]+) LEGISLATURA,',text)
   if heading:
    current=dict(legislature=x.ROMANS.index(heading[1])+1,source=SOURCE,archiveCheckedAt='2026-03-31',members=[],board=[]);out.append(current);mode='board';last=None;continue
   if not current:continue
   if re.match(r'^DIPUTAD[OA]S',text):mode='members';last=None;continue
   if text.startswith('PRESIDENT'):role='Presidencia';last=None;continue
   if text.startswith('VICEPRESIDENT'):role='Vicepresidencia';last=None;continue
   if text.startswith('SECRETARI'):role='Secretaría';last=None;continue
   match=re.match(r'(.+?),\s*(.+?)\s*(?:\.{3,}|…+)\s*(\S.*)',text)
   if match and any(s['flags']&16 for s in line['spans']):
    surname=re.sub(r'^\d[ºª°]?\s*[.\-–]+\s*','',match[1]).strip();first=match[2].replace('†','').strip();group=re.sub(r'\d+$','',match[3]).strip()
    name=c.clean(first+' '+surname);italic=bool(next(s for s in line['spans']if ','in s['text'])['flags']&2)
    row=dict(name=name,group=group,initial=not italic,page=pi+1,notes=[])
    if mode=='board':row['role']=role+(' primera'if re.match(r'^1',text)else' segunda'if re.match(r'^2',text)else'')
    current[mode].append(row);last=row
   elif last and 130<line['bbox'][1]<740 and not text.startswith(('Servicio de','♦')) and text and not re.fullmatch(r'\d+',text):
    # Solo las incidencias situadas debajo de un nombre; excluye encabezados y notas al pie.
    if not re.match(r'^\d+\s',text):last['notes'].append(text)
 for li in out:print(li['legislature'],len(li['members']),sum(r['initial']for r in li['members']),'mesa',len(li['board']),flush=True)
 c.write(c.CACHE/'asturias-relaciones-biblioteca.json',out)
if __name__=='__main__':extract()
