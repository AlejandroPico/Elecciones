"""Recupera el índice estatal del BOE, conserva procedencia y registra cobertura semanal normativa.

No transforma metadatos en análisis de resultados ni acredita una revisión semanal de prensa.
Solo biblioteca estándar. Ejecutar expresamente con --fetch para renovar la consulta de red.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date, timedelta
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1] / 'investigacion' / 'presidencias-centrales'
CUTOFF = '2026-10-17'
RANKS = {1300: 'Ley', 1290: 'Ley Orgánica', 1320: 'Real Decreto-ley', 1310: 'Real Decreto Legislativo', 1500: 'Decreto-ley'}
# Se usa la publicación para ordenar el catálogo. Los relevos se contrastan en
# las investiduras oficiales enlazadas por etapas.json; en funciones no hay Gobierno nuevo.
BOUNDARIES = [
 ('1975-11-20','pre-arias'),('1976-07-01','pre-santiago'),('1976-07-03','pre-suarez'),
 ('1977-07-13','constituyente-suarez'),('1979-03-23','i-suarez'),('1981-02-25','i-calvo-sotelo'),
 ('1982-12-01','ii-gonzalez'),('1986-07-15','iii-gonzalez'),('1989-11-21','iv-gonzalez'),
 ('1993-06-29','v-gonzalez'),('1996-05-04','vi-aznar'),('2000-04-05','vii-aznar'),
 ('2004-04-17','viii-zapatero'),('2008-04-01','ix-zapatero'),('2011-12-21','x-rajoy'),
 ('2016-01-13','xi-rajoy'),('2016-07-19','xii-rajoy'),('2018-06-01','xii-sanchez'),
 ('2019-05-21','xiii-sanchez'),('2019-12-03','xiv-sanchez'),('2023-08-17','xv-sanchez')]
TOPICS = {
 'vivienda': r'viviend|alquil|arrendam|hipotec|suelo|urbaníst',
 'trabajo': r'trabaj|laboral|empleo|salari|desemple|sindical|huelga',
 'pensiones-y-proteccion-social': r'pension|seguridad social|dependencia|protección social|ingreso mínimo|familia|discapacidad',
 'educacion-y-ciencia': r'educa|enseñanza|universidad|universitari|investigación científica|ciencia|becas',
 'sanidad': r'sanitari|sanidad|salud|medicament|covid|pandemia|hospital|vacun',
 'economia-y-presupuestos': r'presupuest|crédito|financ|económ|economí|banc|fiscal|tribut|impuest|hacienda|inversi|deuda|inflación',
 'energia-y-medio-ambiente': r'energ|eléctric|electric|ambiente|climát|agua|hidrológ|residuo|nuclear|hidrocarbur|montes|costas|incendio|sequía',
 'justicia-y-derechos': r'justicia|judicial|penal|derecho|libertad|igualdad|discrimina|violencia|amnistía|enjuiciamiento|aborto|sexual|matrimonio|consumidor|protección de datos',
 'interior-y-seguridad': r'seguridad ciudadana|terroris|policía|guardia civil|penitenciari|extranjer|inmigr|refugiad|asilo|protección civil',
 'exterior-y-defensa': r'defensa|militar|fuerzas armadas|otan|europea|exterior|internacional|tratado|cooperación',
 'territorio-e-instituciones': r'autonom|estatuto|electoral|gobierno|administraci|constituc|congreso|senado|municip|local|partidos|transparencia|función pública',
 'infraestructuras-y-sectores': r'transport|ferroviar|carretera|puerto|aeropuert|telecom|agric|pesca|ganader|industr|comerci|turis|cultura|deporte|cine|patrimonio|propiedad intelectual',
}

def dump(name, obj):
 (ROOT/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def clean(raw):
 return unescape(re.sub(r'<[^>]+>', ' ', raw)).strip()

def stage_for(value):
 return next(stage for start,stage in reversed(BOUNDARIES) if value >= start)

def topics_for(text):
 found=[topic for topic,pattern in TOPICS.items() if re.search(pattern,text,re.I)]
 if re.search(r'capitán general|ejércitos?|fuerzas armadas',text,re.I):
  found=[topic for topic in found if topic!='trabajo']
  if 'exterior-y-defensa' not in found: found.append('exterior-y-defensa')
 return found or ['otras-materias']

def fetch_catalog(rank):
 fields=['ID_SRC','NOVIGENTE','CONSO','TITULOS','ID_RNGS','ID_DEMS','MAT.DESCRIPCION','DOC','NBOS','NOF','TITULOS','FPU','FAP']
 query={}
 for i,field in enumerate(fields):
  query[f'campo[{i}]']=field
  query[f'operador[{i}]']='and'
  if i in (11,12):
   query[f'dato[{i}][0]']='1975-11-20' if i==11 else ''
   query[f'dato[{i}][1]']=CUTOFF if i==11 else ''
  else: query[f'dato[{i}]']='1' if i==0 else str(rank) if i==4 else ''
 query.update({'page_hits':'2000','sort_field[0]':'FPU','sort_order[0]':'asc','accion':'Buscar'})
 url='https://www.boe.es/buscar/legislacion_ava.php?'+urlencode(query)
 raw=urlopen(Request(url,headers={'User-Agent':'Elecciones/0.25 historical public records'}),timeout=90).read()
 html=raw.decode('utf-8')
 label=re.search(r'Resultados\s+(\d+)\s+a\s+([\d.]+)\s+de\s+([\d.]+)',clean(html))
 if not label or int(label[3].replace('.',''))>2000:
  raise ValueError('Respuesta incompleta: adaptar la paginación antes de continuar')
 items=[]
 for row in html.split('<li class="resultado-busqueda">')[1:]:
  paras=re.findall(r'<p(?:\s[^>]*)?>(.*?)</p>',row,re.S)
  if len(paras)<2: raise ValueError('Formato de resultado desconocido')
  ref=re.search(r'BOE-[A-Z]-\d{4}-\d+',row).group()
  day=re.search(r'(\d{2})/(\d{2})/(\d{4})',clean(paras[0]))
  items.append({'id':ref,'title':clean(paras[1]),'published':f'{day[3]}-{day[2]}-{day[1]}',
    'department':clean(paras[0]).split('(BOE')[0].strip(),'rank':rank,
    'url':'https://www.boe.es/diario_boe/txt.php?id='+ref})
 if len(items)!=int(label[3].replace('.','')): raise ValueError('Faltan resultados')
 return {'rank':rank,'url':url,'count':len(items),'sha256':sha256(raw).hexdigest(),'items':items,'resultLabel':label[0]}

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--fetch',action='store_true')
 parser.add_argument('--catalog',type=Path,help='Catálogo bruto ya recuperado, para reproducción sin red')
 args=parser.parse_args()
 if args.fetch:
  catalogs=[fetch_catalog(rank) for rank in RANKS]
  dump('catalogos-boe.json',{'checkedAt':CUTOFF,'catalogs':catalogs})
 elif args.catalog:
  data=json.loads(args.catalog.read_text(encoding='utf-8-sig'))
  catalogs=data['catalogs'] if isinstance(data,dict) else data
  dump('catalogos-boe.json',{'checkedAt':CUTOFF,'catalogs':catalogs})
 else: catalogs=json.loads((ROOT/'catalogos-boe.json').read_text(encoding='utf8'))['catalogs']
 # La búsqueda de Decreto-ley incluye también los reales decretos-leyes: deduplicar por ID.
 rows={item['id']:item for cat in catalogs for item in cat['items']}
 existing=json.loads((ROOT/'fuentes.json').read_text(encoding='utf-8-sig'))['sources']
 curated=json.loads((ROOT/'eventos.json').read_text(encoding='utf-8-sig'))['events']
 used={sid for event in curated for sid in event['sources']}
 existing_refs=set()
 existing_eli=set()
 for source in existing:
  if source['id'] in used:
   existing_refs.update(re.findall(r'BOE-[A-Z]-\d{4}-\d+',source['url']))
   match=re.search(r'/eli/es/(lo|l|rdl|rdlg|dl)/(\d{4})/\d{2}/\d{2}/(\d+)',source['url'])
   if match: existing_eli.add((match[1],f'{match[3]}/{match[2]}'))
 norms=[]
 excluded=[]
 for row in sorted(rows.values(),key=lambda x:(x['published'],x['id'])):
  reason=None
  if row['published'] < '1975-11-20' or row['published']>CUTOFF: reason='fuera-del-periodo'
  # Norma fechada antes de la muerte de Franco: no atribuirla al periodo posterior por su publicación.
  if re.match(r'^(?:Ley|Decreto-ley)\s+\d+/1975,\s+de 19 de noviembre',row['title']): reason='disposicion-anterior-al-periodo'
  if row['id'] in existing_refs: reason='ya-desarrollada-en-eventos'
  citation=re.match(r'(Ley Orgánica|Ley|Real Decreto-ley|Real Decreto [Ll]egislativo|Decreto-ley)\s+(\d+/\d{4})',row['title'])
  types={'Ley Orgánica':'lo','Ley':'l','Real Decreto-ley':'rdl','Real Decreto Legislativo':'rdlg','Real Decreto legislativo':'rdlg','Decreto-ley':'dl'}
  if citation and (types[citation[1]],citation[2]) in existing_eli: reason='ya-desarrollada-en-eventos-eli'
  if reason:
   excluded.append({'id':row['id'],'reason':reason});continue
  # No afirmar efectos ni resumir artículos no leídos: el asunto procede del título oficial.
  subject=re.sub(r'^(?:Ley(?: Orgánica)?|Real Decreto(?:-ley| [Ll]egislativo)|Decreto-ley)\s+[^,]+,\s+de\s+\d+\s+de\s+\w+(?:\s+de\s+\d{4})?,?\s*','',row['title'],flags=re.I)
  subject=re.sub(r'^(?:por (?:el|la) que|sobre|de)\s+','',subject,flags=re.I)
  subject=subject[:1].upper()+subject[1:]
  # No cortar ni omitir el objeto oficial; el título completo permanece accesible en la fuente.
  norms.append({'id':row['id'],'date':row['published'],'stage':stage_for(row['published']),
   'title':subject,'officialTitle':row['title'],'department':row['department'],
   'rank':next((label for label in ['Ley Orgánica','Ley','Real Decreto-ley','Real Decreto Legislativo','Decreto-ley'] if row['title'].lower().startswith(label.lower())),'Norma estatal'),
   'topics':topics_for(row['title'])})
 dump('normativa.json',{'checkedAt':CUTOFF,'basis':'Índice documental del BOE: título, rango y fecha de publicación. No equivale a lectura íntegra, evaluación de impacto ni revisión semanal de prensa.',
  'excluded':excluded,'norms':norms})
 # Cada semana tiene estado explícito: no inferir que una semana sin entradas careció de crisis.
 weeks=[];first=date(1975,11,20);d=first-timedelta(days=first.weekday());last=date.fromisoformat(CUTOFF)
 all_dates=[(n['date'],n['id'],'normativa') for n in norms]+[(e['date'],e['id'],'editorial') for e in curated if len(e['date'])==10]
 while d<=last:
  end=min(d+timedelta(days=6),last);start=max(d,first)
  related=[(identity,kind) for value,identity,kind in all_dates if start.isoformat()<=value<=end.isoformat()]
  weeks.append({'from':start.isoformat(),'until':end.isoformat(),'norms':[i for i,k in related if k=='normativa'],'events':[i for i,k in related if k=='editorial'],
   'pressReview':'pendiente-de-barrido-semanal-completo'})
  d+=timedelta(days=7)
 dump('cobertura-semanal.json',{'checkedAt':CUTOFF,'scope':'Registro semanal de entradas del archivo. Catálogo normativo consultado por todo el periodo; revisión hemerográfica exhaustiva pendiente. No interpretar ausencia de entradas como ausencia de acontecimientos.', 'weeks':weeks})
 report={'checkedAt':CUTOFF,'catalogs':[ {k:v for k,v in c.items() if k!='items'} for c in catalogs],
  'uniqueDocuments':len(rows),'normsPublished':len(norms),'excluded':len(excluded),
  'byStage':dict(Counter(n['stage'] for n in norms)), 'byYear':dict(sorted(Counter(n['date'][:4] for n in norms).items())),
  'weeks':len(weeks),'weeksWithNorms':sum(bool(w['norms']) for w in weeks)}
 dump('revision-normativa.json',report)
 print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
