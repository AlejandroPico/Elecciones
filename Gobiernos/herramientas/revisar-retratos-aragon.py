"""Busca candidatos a retrato; la integración exige revisión individual posterior.

No cambia ninguna ficha. Conserva contexto de identidad, procedencia y licencia.
"""
import importlib.util,json,re,unicodedata
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote,urljoin,urlencode,unquote
s=importlib.util.spec_from_file_location('a','Gobiernos/herramientas/consultar-aragon.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
def norm(s):return re.sub(r'[^a-z0-9 ]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def review(row):
 result={**row,'checkedAt':c.CHECKED,'candidates':[]}
 # Son rutas candidatas, no correspondencias personales. La API respondió 429;
 # leer los artículos públicos sin insistir sobre el servicio limitado.
 words=row['name'].split();titles=[row['name'].replace(' ','_'),'_'.join(words[:2]),'_'.join(words[:3])]
 aliases={'José Ramón Bada Panillo':'José_Bada_Panillo','María Pilar Ventura Contreras':'Pilar_Ventura','María Teresa Perales Fernández':'Teresa_Perales','Luisa María Noeno Ceamanos':'Luisa_Noeno'}
 if row['name']in aliases:titles.append(aliases[row['name']])
 for title in dict.fromkeys(titles):
  source='https://es.wikipedia.org/wiki/'+quote(title)
  try:
   p=c.soup(source);main=p.select_one('.mw-parser-output');box=main.select_one('table.infobox') if main else None
   if not main:continue
   lead=[c.clean(x.get_text(' ',strip=True))for x in main.select('p')if x.find(['b','strong']) and len(x.get_text(' ',strip=True))>60]
   identity=' '.join(lead[:1]);context=c.clean(box.get_text(' ',strip=True))if box else''
   item={'source':source,'identity':identity,'infobox':context[:5000]}
   image=next((im for im in (box or main).select('a[href] img')if int(im.get('width',0))>=90 and im.get('data-file-type')!='drawing'),None)
   if image:
    link=urljoin(source,image.find_parent('a')['href']);filename=unquote(link.split('/wiki/',1)[-1]);filename=re.sub(r'^(?:Archivo|File):','File:',filename)
    if filename.startswith('File:'):
     commons='https://commons.wikimedia.org/wiki/'+quote(filename);file=c.soup(commons);original=file.select_one('.fullImageLink a');artist=file.select_one('#fileinfotpl_aut');license=file.select_one('.licensetpl_short');licenseUrl=file.select_one('.licensetpl_link')
     if original and artist and license and licenseUrl:
      author=c.clean(artist.find_next_sibling('td').get_text(' ',strip=True));lic=c.clean(license.get_text())
      item['photo']={'url':original['href'].split('?')[0],'source':commons,'credit':author+' · '+lic,'license':lic,'licenseUrl':c.clean(licenseUrl.get_text()),'width':int(image.get('data-file-width',0)),'height':int(image.get('data-file-height',0))}
   result['candidates'].append(item)
  except Exception as e:result.setdefault('errors',[]).append({'source':source,'error':str(e)})
 print(row['name'],[(r['identity'][:80],bool(r.get('photo')))for r in result['candidates']],flush=True)
 return result
def main():
 rows=json.loads((c.CACHE/'retratos-pendientes-revision.json').read_text('utf8'))
 with ThreadPoolExecutor(4)as pool:results=list(pool.map(review,rows))
 c.write(c.CACHE/'retratos-candidatos.json',results)
if __name__=='__main__':main()
