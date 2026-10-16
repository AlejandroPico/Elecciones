"""Consulta del archivo público de la Asamblea Regional de Murcia y de la CARM."""
import importlib.util,pathlib,re,json,concurrent.futures
from urllib.parse import urljoin
s=importlib.util.spec_from_file_location('c',pathlib.Path(__file__).with_name('consultar-castillas.py'));c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
c.CACHE=pathlib.Path('test-results/murcia');c.CHECKED='2026-10-16'
BASE='https://www.asambleamurcia.es'

def main(url):
 p=c.soup(url);return p.select_one('main')or p.select_one('#contenido')or p.select_one('#content')or p

def inspect(url):
 p=c.soup(url);body=p.select_one('main')or p
 print('URL',url,'\nTEXT',c.clean(body.get_text(' ',strip=True))[:5500])
 print('LINKS',[(c.clean(a.get_text(' ',strip=True))or a.get('title')or a.get('alt'),a.get('href'))for a in p.select('a[href],area[href]')][-180:])

def chamber(n):
 url=BASE+f'/diputados?leg={n}';p=main(url);rows=[]
 for card in p.select('.arm-diputado-card'):
  a=card.select_one('.arm-diputado-name a');image=card.select_one('.arm-diputado-image-wrap > img');badge=card.select_one('.arm-diputado-party-badge')
  preceding=card.find_previous('h2');ceased=bool(preceding and 'baja'in preceding.get_text().lower())
  rows.append(dict(name=c.clean(a.get_text(' ',strip=True)),source=urljoin(url,a['href']),image=urljoin(url,image['src'])if image else None,group=badge.get('title')if badge else None,ceased=ceased))
 result=dict(legislature=n,source=url,members=rows)
 c.write(c.CACHE/f'parlamentos/{n}.json',result);print('PARLAMENTO',n,len(rows),sum(not r['ceased']for r in rows),flush=True);return result

def profile(row):
 url=row['source'];p=main(url);h=p.select_one('h1')
 result={**row,'name':c.clean(h.get_text(' ',strip=True))if h else row['name'],'text':p.get_text('\n',strip=True)}
 key=re.sub(r'[^a-z0-9-]+','-',url.split('/diputado/')[-1].lower())
 c.write(c.CACHE/f'perfiles/{key}.json',result);return result

def legacy(n):
 directory=BASE+'/legacy/es/los-diputados-regionales.html';p=c.soup(directory)
 a=next(a for a in p.select('a[href]')if c.clean(a.get_text())=='Diputados - '+['I','II','III','IV','V','VI','VII','VIII','IX'][n-1]+' Legislatura')
 url=urljoin(directory,a['href']);p=main(url);rows=[]
 for a in p.select('.diputados_ul a[href]'):
  text=c.clean(a.get_text());rawname=re.split(r'\s*-\s*(?:[IVX]+ Legislatura|GP )',text)[0]
  if rawname=='VIGUERAS PALLARÉS Mª DEL CARMEN':rawname='VIGUERAS PALLARÉS, Mª DEL CARMEN'
  surname,given=rawname.split(',',1);name=c.clean(given+' '+surname).title();source=urljoin(url,a['href'])
  # Los dos bloques separan titulares al cierre y bajas; no son todos simultáneos.
  ul=a.find_parent('ul');previous=ul.find_previous(string=lambda t:t and 'Han causado baja'in t);ceased=bool(previous)
  gp=re.search(r'GP (.+?)(?:\s*\(|$)',text);dates=re.search(r'\((\d{4}(?:-\d{4})?)\)',text)
  formation=gp[1]if gp else('Popular'if'parlamentario-popular/'in source else'Socialista'if'parlamentario-socialista/'in source else'Izquierda Unida'if'parlamentario-izquierda-unida/'in source else'Mixto'if'parlamentario-mixto/'in source else None)
  rows.append(dict(name=name,source=source,group=formation,period=dates[1]if dates else'Legislatura '+str(n),ceased=ceased,legislature=n))
 rows=list({r['source']:r for r in rows}.values())
 result=dict(legislature=n,source=url,members=rows);c.write(c.CACHE/f'parlamentos/{n if n<9 else "9-legacy"}.json',result)
 print('LEGACY',n,len(rows),sum(not r['ceased']for r in rows),flush=True);return result

def legacy_profile(row):
 p=main(row['source']);im=next((i for i in p.select('img[src]')if re.search(r'/diputados[^/]*(?:/|%2f)',i['src'],re.I)),None)
 result={**row,'image':urljoin(BASE,im['src'])if im else None,'text':'\n'.join(c.clean(li.get_text(' ',strip=True))for li in p.select('table.contentpaneopen:last-of-type li'))}
 key='legacy-'+str(row['legislature'])+'-'+row['source'].split('/')[-1].split('.')[0]
 c.write(c.CACHE/f'perfiles/{key}.json',result);return result

def safe_profile(row):
 try:return legacy_profile(row)if '/legacy/'in row['source'] else profile(row)
 except Exception as e:print('ERROR PERFIL',row['source'],str(e),flush=True)

if __name__=='__main__':
 import sys
 if len(sys.argv)>1:inspect(sys.argv[1])
 else:
  with concurrent.futures.ThreadPoolExecutor(3)as pool:stages=list(pool.map(legacy,range(1,9)))+list(pool.map(chamber,[9,10,11]))
  rows={r['source']:r for d in stages for r in d['members']}
  with concurrent.futures.ThreadPoolExecutor(3)as pool:
   for i,r in enumerate(pool.map(safe_profile,rows.values())):
    if(i+1)%50==0:print('PERFILES',i+1,'de',len(rows),flush=True)
