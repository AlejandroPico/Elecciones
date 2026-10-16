"""Transcripción por columnas de los cuadros de la Biblioteca del Parlamento.

Conserva texto de altas, bajas y cambios para revisión; no repara años por conjetura.
"""
import importlib.util,pathlib,re,sys,json
sys.path.insert(0,'test-results/libraries');import pymupdf
s=importlib.util.spec_from_file_location('g',pathlib.Path(__file__).with_name('consultar-galicia.py'));g=importlib.util.module_from_spec(s);s.loader.exec_module(g);c=g.c
MONTHS=['xaneiro','febreiro','marzo','abril','maio','xuño','xullo','agosto','setembro','outubro','novembro','decembro']
def date(text):
 m=re.search(r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',text,re.I)
 if m and m[2].lower()in MONTHS:return f'{m[3]}-{MONTHS.index(m[2].lower())+1:02}-{int(m[1]):02}'
def lines(page):
 return [dict(text=c.clean(''.join(s['text']for s in l['spans'])),box=l['bbox'])for b in page.get_text('dict')['blocks']for l in b.get('lines',[])if c.clean(''.join(s['text']for s in l['spans']))]
out=[]
for leg in range(1,12):
 doc=pymupdf.open(c.CACHE/f'parlamento-{leg}.pdf');alltext='\n'.join(p.get_text()for p in doc);members=[];group=None;enabled=False;left=None;datecol=260;rightcol=330
 for pi,page in enumerate(doc):
  text=page.get_text()
  if 'RELACIÓN DE DEPUTAD'in text:enabled=True
  if not enabled:continue
  ls=lines(page);heads=[l for l in ls if re.match(r'^G\.P\.',l['text']) and l['box'][0]<160]
  if heads:left=heads[0]['box'][0];group=heads[0]['text']
  for l in ls:
   if re.match(r'^Alta\s*/\s*baixa$',l['text']):datecol=l['box'][0]-15
   if l['text'].startswith('En substitución'):rightcol=l['box'][0]-8
  limit=min([l['box'][1]for l in ls if l['text'].startswith('Renuncias anticipadas')]+[1000])
  header=max([l['box'][1]+9 for l in ls if l['text']in ['Deputado ou deputada','Deputado/a']and l['box'][1]<limit]+[0])
  names=[l for l in ls if l['box'][0]<datecol and header<l['box'][1]<limit and (','in l['text']or(leg==7 and abs(l['box'][0]-90)<2))and not re.search(r'^(?:\(|Deputad|En substit|G\.P\.|\*|Paso |Por |Alta|Baixa)',l['text'])and len(l['text'].split())>=2]
  for i,r in enumerate(names):
   prior=[h for h in heads if h['box'][1]<r['box'][1]]
   if prior:group=prior[-1]['text']
   assert group,(leg,pi,r)
   # I–VI y VIII alinean las celdas arriba; VII y IX–XI centran el nombre
   # frente a las dos líneas de fecha y estado. No mezclar con la fila vecina.
   offset=7 if leg>=9 else 5 if leg==7 else 0.5
   lo=r['box'][1]-offset
   hi=names[i+1]['box'][1]-offset if i+1<len(names)else r['box'][1]+24
   cells=[l['text']for l in ls if lo<=l['box'][1]<hi and datecol<l['box'][0]<rightcol]
   detail=' '.join(l['text']for l in ls if lo<=l['box'][1]<hi and l['box'][0]>=rightcol)
   label=re.sub(r'\s*\([^)]*\)?','',r['text'])
   if ','in label:surname,first=label.split(',',1);name=c.clean(first+' '+surname)
   else:name=label
   name=c.clean(re.sub(r'[*¾,]+',' ',name)).replace('Mª','María').replace('M.ª','María')
   members.append(dict(name=name,group=group,dates=' '.join(cells),detail=detail,page=pi+1,initial=not any('alta'in cell.lower()for cell in cells)))
 start=date(alltext.split('DATA DE CONSTITUCIÓN DO PARLAMENTO:')[1])
 end=date(alltext.split('DATA DE DISOLUCIÓN DO PARLAMENTO:')[1])
 row=dict(legislature=leg,constitutionAt=start,dissolutionAt=end,source=f'https://www.parlamentodegalicia.es/sitios/web/BibliotecaResultadoAnteriores/{leg}.pdf',members=members,boardText=alltext.split('Mesa do Parlamento')[1].split('Composición dos grupos parlamentarios')[0])
 assert start and end,(leg,start,end)
 out.append(row);print('GALICIA',leg,'filas',len(members),'iniciales',sum(r['initial']for r in members),'nombres',len({r['name']for r in members}),flush=True)
c.write(c.CACHE/'parlamentos-transcritos.json',out)
