"""Fuentes complementarias de Aragón: históricos oficiales y fichas sin foto.

Solo extrae información profesional y recursos gráficos identificados.
Los documentos íntegros permanecen en la caché ignorada.
"""
import importlib.util,json,pathlib,re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin,quote,urlencode
s=importlib.util.spec_from_file_location('a','Gobiernos/herramientas/consultar-aragon.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c

def extract(url):
 try:
  p=c.soup(url);main=p.select_one('section.info-tema')
  if main is None:raise ValueError('Falta el contenido histórico; no aceptar el pie como documento')
  departments=[]
  for x in main.descendants:
   if getattr(x,'name',None)=='h2':departments.append({'department':c.clean(x.get_text(' ',strip=True)),'peopleInSource':[]})
   elif getattr(x,'name',None)=='div'and 'component-paragraph'in x.get('class',[])and departments:
    text=c.clean(x.get_text(' ',strip=True))
    if text:departments[-1]['peopleInSource'].append(text)
  return {'source':url,'text':c.clean(main.get_text(' ',strip=True)),'departments':departments,'images':[{'alt':x.get('alt',''),'url':urljoin(url,x['src'])}for x in main.select('img[src]')],'links':[{'label':c.clean(x.get_text(' ',strip=True)),'source':urljoin(url,x['href'])}for x in main.select('a[href]')]}
 except Exception as error:return {'source':url,'error':str(error)}

def main():
 root='https://www.aragon.es/gobierno/historico-de-legislaturas';p=c.soup(root)
 urls=sorted({urljoin(root,x['href'])for x in p.select('a[href]')if '/gobierno/historico-de-legislaturas/'in x['href']})
 with ThreadPoolExecutor(3)as pool:rows=list(pool.map(extract,urls))
 c.write(c.CACHE/'historico-oficial-detalle.json',rows)
 c.write('Gobiernos/Autonomías/Aragón/fuentes/gabinetes-historico-oficial.json',{'checkedAt':c.CHECKED,'source':root,'note':'Titulares y departamentos publicados por el Gobierno. La relación no fecha todas las remodelaciones y menciona también viceconsejerías; no supone simultaneidad.','periods':[{'source':r['source'],'departments':r['departments']}for r in rows if r.get('departments')and re.search(r'/[ivx]+-legislatura-',r['source'])]})
 for r in rows:print('HISTORICO',r['source'],r.get('text','')[:650],r.get('error'),flush=True)
 audit=json.loads(pathlib.Path('Políticos/revisiones/2026-10-16-aragon/informe.json').read_text('utf8'));missing=set(audit['allMissingPortraits']);people={}
 for file in pathlib.Path('Gobiernos/Autonomías/Aragón').glob('*/*/composicion.json'):
  period=json.loads(file.read_text('utf8'))
  for key in ['terms','archiveTerms','records','board','archiveBoard']:
   for r in period.get(key,[]):
    if r['person']in missing:people[r['person']]={'id':r['person'],'name':r['name'],'folder':r['name'],'institutionalSource':r['source']}
 c.write(c.CACHE/'retratos-pendientes-revision.json',list(people.values()));print('SIN FOTO',[(r['id'],r['name'])for r in people.values()],flush=True)

if __name__=='__main__':main()
