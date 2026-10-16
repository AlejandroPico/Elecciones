"""Relaciones nominales y Mesas del documento de la Biblioteca del Parlamento.

Los listados fueron actualizados durante cada legislatura. No son altas individuales
ni se interpreta la fecha del boletín citado como fecha de toma de posesión.
"""
import importlib.util,pathlib,re,json,sys
sys.path.insert(0,'test-results/libraries')
import pymupdf
s=importlib.util.spec_from_file_location('x',pathlib.Path(__file__).with_name('consultar-cantabrico.py'));x=importlib.util.module_from_spec(s);s.loader.exec_module(x);c=x.c
SOURCE='https://parlamento-cantabria.es/sites/default/files/5.%20Diputados%20y%20Mesas%20por%20Legislaturas_0.pdf'

def extract():
 doc=pymupdf.open(stream=c.fetch(SOURCE),filetype='pdf');out=[];leg=None;board_mode=False
 for number,page in enumerate(doc):
  if number<5:continue
  text=page.get_text(sort=True);heading=re.search(r'^\s*([IVX]+) LEGISLATURA\s*$',text,re.M)
  if heading:
   leg={'legislature':x.ROMANS.index(heading[1])+1,'label':'Legislatura '+heading[1],'source':SOURCE+'#page='+str(number+1),'members':[],'board':[],'notes':[],'publishedAt':None,'archiveCheckedAt':'2026-04-28'};out.append(leg);board_mode=False
   first=re.search(r'(?:BOARC|BOPCA)[^\n]+',text)
   if first:leg['publishedAt']=x.dated(first[0])
  if leg is None:continue
  last_role=None
  for line in text.splitlines():
   clean=c.clean(line)
   if re.fullmatch(r'MESA\d*',clean):board_mode=True
   if re.fullmatch(r'(?:President[ae]|Vicepresident[ae] (?:Primer[oa]|Segund[oa])|Secretari[oa] (?:Primer[oa]|Segund[oa]))',clean):last_role=clean
   if re.match(r'^(?:D[.ª]|Excmo|Excma|Ilmo|Ilma)',clean):
    bits=re.split(r'\s{3,}',line.strip());name=bits[0];group=c.clean(' '.join(bits[1:]))
    name=re.sub(r'^(?:(?:Excmo\.?|Excma\.?|Ilmo\.?|Ilma\.?)\s*(?:Sr\.?|Sra\.?)\s*)?(?:D\.?\s*ª?\.?\s*)','',name).strip();name=re.sub(r'\d+$','',name).strip()
    if not group or len(name)<6:continue
    row={'name':name,'group':group.rstrip('*'),'page':number+1}
    if board_mode:row['role']=last_role;leg['board'].append(row)
    else:leg['members'].append(row)
   elif re.match(r'^\d+\s',clean):leg['notes'].append({'page':number+1,'text':clean})
 for i,li in enumerate(out):
  first=li['members'][0]['page']-1;last=out[i+1]['members'][0]['page']-1 if i+1<len(out)else len(doc)
  chapter=c.clean(' '.join(doc[p].get_text(sort=True)for p in range(first,last)))
  header=re.search(r'\(de\s+(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',chapter,re.I)
  mesa=re.search(r'Queda constituida.{0,80}?(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',chapter,re.I)
  li['constitutionAt']=x.dated((header or mesa)[1])if(header or mesa)else None
  assert li['constitutionAt'],li['legislature']
  print(li['legislature'],len(li['members']),len(li['board']),li['constitutionAt'],flush=True)
 c.write(c.CACHE/'cantabria-relaciones-biblioteca.json',out)

if __name__=='__main__':extract()
