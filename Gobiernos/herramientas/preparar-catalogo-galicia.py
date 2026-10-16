"""Normaliza originales consultados; las erratas se corrigen con otra fuente explícita.

No integra identidades ni publica fechas individuales inferidas. Las proclamaciones
electorales se conservan como tales, separadas de los mandatos posteriores.
"""
import importlib.util,pathlib,re,json,collections
s=importlib.util.spec_from_file_location('g',pathlib.Path(__file__).with_name('consultar-galicia.py'));g=importlib.util.module_from_spec(s);s.loader.exec_module(g);c=g.c
ROOT=pathlib.Path('test-results/galicia')
def read(f):return json.loads((ROOT/f).read_text('utf8'))
def write(f,v):c.write(ROOT/f,v)
def clean(s):return c.clean(s).strip(' .–-¾')

def elected(year):
 text=(ROOT/f'electos-{year}.txt').read_text('utf8');text=text.split('Deputados e deputadas electos')[-1] if year==2012 else text
 # Solo las listas numeradas del apartado de proclamación: las tablas electorales
 # previas no empiezan por una numeración seguida de nombre propio.
 out=[];group=None;province=None
 for line in text.splitlines():
  line=clean(line)
  if re.match(r'^(?:Provincia|• Provincia) de ',line):province=line.split(' de ',1)[1].strip('.')
  if re.search(r'Polo Partido Popular|Polo PARTIDO POPULAR',line):group='Popular de Galicia'
  elif re.search(r'Polo Partido dos Socialistas|Polo PARTIDO DOS SOCIALISTAS',line):group='Socialistas de Galicia'
  elif re.search(r'Polo Bloque Nacionalista|Polo BLOQUE NACIONALISTA',line):group='Bloque Nacionalista Galego'
  elif 'Pola coalición electoral Alternativa'in line:group='Alternativa Galega de Esquerda'
  match=re.match(r'^\d+\.\s+(?:(?:Don|Dona)\s+)?(.+)$',line)
  if match and group:
   name=re.sub(r'\s*«[^»]*»','',match[1]).rstrip('.')
   out.append(dict(name=name,group=group,constituency=province))
 assert len(out)==75,(year,len(out))
 return out

def main():
 parliaments=read('parlamentos-transcritos.json')
 # La relación VI imprime «baixa» para la incorporación de Novo Arrojo; la
 # propia fila de Tello León identifica a su sustituta. No es titular inicial.
 for row in parliaments[5]['members']:
  if row['name']=='María Tereixa dos Anxos Novo Arrojo':row['initial']=False
 # XI: la proclamación oficial permite contrastar el grupo de Martín Seco y
 # recuperar a Mercedes Queixas, omitida en la tabla nominal de la Biblioteca.
 proclamation='https://www.xunta.gal/dog/Publicados/2020/20200729/AnuncioG2453-280720-0003_gl.pdf'
 for row in parliaments[10]['members']:
  if row['name']=='Martín Seco García':row['group']='G.P. Socialistas de Galicia';row['correctionSource']=proclamation
 parliaments[10]['members'].append(dict(name='Mercedes Queixas Zas',group='G.P. do Bloque Nacionalista Galego',initial=True,dates='',detail='Omisión contrastada con la proclamación electoral',page=0,correctionSource=proclamation))
 # IV: transcripción visual del DOG 217, 11-11-1993, p. 7369. El documento
 # escaneado también publica los nombres completos de los electos.
 parliaments[3]['members'].append(dict(name='José Carlos Baños Márquez',group='G.P. Socialistas de Galicia',initial=True,dates='',detail='Omisión de la relación nominal; proclamación electoral, p. 7369',page=0,correctionSource='https://www.xunta.gal/dog/Publicados/1993/19931111/Anuncio326DA_gl.pdf#page=3'))
 # No se deducen fechas de toma de posesión a partir de la lista de electos.
 for year,num in [(2012,9),(2020,11)]:
  parliaments[num-1]['elected']=elected(year)
  parliaments[num-1]['electedSource']=next(r['url'].replace('http:','https:')for r in read('elecciones-anteriores-enlaces.json')if f'/Publicados/{year}/'in r['url'])
 for row in parliaments:
  board=[];role=None
  for line in row['boardText'].splitlines():
   line=clean(line)
   if re.match(r'^(?:Presidente|Presidenta|Vicepresidente|Vicepresidenta|Secretario|Secretaria|Vicesecretario|Vicesecretaria)(?:/a)?(?:\s+[12][ºª])?$',line):role=line;continue
   if not line or not role or line.startswith('(*)'):continue
   if len(line.split())<2 or not re.match(r'^[A-ZÁÉÍÓÚÑ]',line):continue
   label=re.sub(r'\s*\([^)]*\)','',line).strip()
   board.append(dict(name=label,role=role,note=line))
  assert len(board)>=5,(row['legislature'],board)
  row['board']=board
 write('parlamentos-preparados.json',parliaments)
 cabinets=[]
 for decree in read('decretos-gabinetes-originales.json'):
  if decree['title'].startswith('CORRECCIÓN'):continue
  rows=[]
  for line in decree['paragraphs']:
   match=re.match(r'^[–-]\s*([^,]+),\s*(.+)',line)
   if not match:continue
   name=match[1].replace('José Mª','José María').replace('Jesús C. Palmou','Jesús Carlos Palmou')
   if name=='María José Rubio Vilar':name='María José Rubio Vidal'
   rows.append(dict(name=name,role=match[2].removeprefix('como ').rstrip('.')))
  if rows:
   stamp=re.search(r'/Publicados/(\d{4})/(\d{4})(\d{2})(\d{2})/',decree['source'])
   cabinets.append(dict(source=decree['source'],title=decree['title'],date=f'{stamp[2]}-{stamp[3]}-{stamp[4]}',members=rows))
 assert len(cabinets)==9,len(cabinets)
 write('gabinetes-preparados.json',sorted(cabinets,key=lambda x:x['date']))
 print('Parlamentos',len(parliaments),'decretos de nombramientos',len(cabinets),'electos contrastados',150)
if __name__=='__main__':main()
