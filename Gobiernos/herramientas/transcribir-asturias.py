"""Lee los cuadros nominales oficiales por posición de texto, grupo y circunscripción."""
import importlib.util,pathlib,re,json,sys
sys.path.insert(0,'test-results/libraries')
import pymupdf
s=importlib.util.spec_from_file_location('x',pathlib.Path(__file__).with_name('consultar-cantabrico.py'));x=importlib.util.module_from_spec(s);s.loader.exec_module(x);c=x.c

def lines(page):
 return sorted([(line['bbox'],c.clean(''.join(s['text']for s in line['spans'])))for block in page.get_text('dict')['blocks']for line in block.get('lines',[])],key=lambda r:(round(r[0][1],1),r[0][0]))

def extract():
 downloads=json.loads((c.CACHE/'asturias-resultados-descargas.json').read_text('utf8'));out=[]
 for num,download in enumerate(downloads,1):
  doc=pymupdf.open(c.CACHE/f'asturias-resultados-{num}.pdf');text=' '.join(p.get_text(sort=True)for p in doc)
  constitution=re.search(r'se constituye.{0,160}?el día\s+(.{0,45})',c.clean(text),re.I)
  if not constitution:constitution=re.search(r'se constituye.{0,80}?(\d{1,2} de \w+ de \d{4})',c.clean(text),re.I)
  data=dict(legislature=num,label='Legislatura '+x.ROMANS[num-1],source=download['href'],constitutionAt=x.dated(constitution[1])if constitution else None,members=[],former=[],board=[],notes=[])
  for pi,page in enumerate(doc):
   ls=lines(page);groups=[(box[1],txt)for box,txt in ls if txt.startswith('GRUPO PARLAMENTARIO')]
   if groups:
    foot_y=min([box[1]for box,txt in ls if re.match(r'^(?:\*\s*(?:Don|Doña|Estos)|\. )',txt)],default=10000)
    for box,txt in ls:
     if not groups[0][0]<box[1]<foot_y or txt.startswith('GRUPO')or txt.upper()==txt or not re.match(r'^[A-ZÁÉÍÓÚÑÜ\[]',txt)or len(txt.split())<2:continue
     group=next((g for y,g in reversed(groups)if y<box[1]),None)
     if not group or 'circunscrip' in txt.lower():continue
     name=txt.strip('[] *').strip();center=(box[0]+box[2])/2
     row=dict(name=name,group=group.title().replace('Parlamentario','Parlamentario'),constituency='Occidental'if center<210 else'Oriental'if center>390 else'Central',page=pi+1)
     data['former'if txt.startswith('[')else'members'].append(row)
   roles=[(box[1],txt.rstrip(':'))for box,txt in ls if re.fullmatch(r'(?:Presidente|Vicepresident[ae] (?:Primer[oa]|Segund[oa])|Secretari[oa] (?:Primer[oa]|Segund[oa])):',txt,re.I)]
   if roles:
    for y,role in roles:
     candidates=[(b,t)for b,t in ls if abs(b[1]-y)<3 and b[0]>250 and len(t.split())>1]
     if candidates:data['board'].append(dict(name=re.sub(r'\s*\([^)]*\)','',candidates[0][1]).strip(),role=role,page=pi+1))
  print(num,'constitucion',data['constitutionAt'],'miembros',len(data['members']),'previos',len(data['former']),'mesa',len(data['board']),flush=True)
  out.append(data)
 c.write(c.CACHE/'asturias-relaciones-electorales.json',out)
if __name__=='__main__':extract()
