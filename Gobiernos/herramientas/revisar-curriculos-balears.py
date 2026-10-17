"""Localiza exclusivamente currículos públicos, sin descargar declaraciones patrimoniales."""
import importlib.util,pathlib,re,json,concurrent.futures
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-extremadura-balears.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
import pymupdf
def cv(row):
 try:
  p=c.soup(row['source']);a=next((a for a in p.select('a[href]')if re.search(r'curr.culum',a.get_text(),re.I)),None)
  if not a:return
  url=r.urljoin(row['source'],a['href']);raw=c.fetch(url);text='\n'.join(p.get_text()for p in pymupdf.open(stream=raw,filetype='pdf'))
  c.write(c.CACHE/f'baleares/curriculos/{row["key"]}.json',dict(name=row['name'],source=url,text=text));print('CV',row['key'],row['name'],text[:420].replace('\n',' '),flush=True)
 except Exception as error:print('CV NO DISPONIBLE',row['name'],str(error),flush=True)
if __name__=='__main__':
 rows=[json.loads(f.read_text('utf8'))for f in(c.CACHE/'baleares/perfiles').glob('*.json')];rows=[row for row in rows if re.search(r'\b[A-ZÀ-Ÿ]\.\s',row['name'])]
 with concurrent.futures.ThreadPoolExecutor(3)as pool:list(pool.map(cv,rows))
