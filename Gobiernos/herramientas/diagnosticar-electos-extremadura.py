import importlib.util,pathlib,difflib,re
s=importlib.util.spec_from_file_location('p',pathlib.Path(__file__).with_name('preparar-camaras-extremadura-balears.py'));p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
for stage in p.load(p.CACHE/'extremadura/camara-preparada.json'):
 n=stage['legislature']
 if len(stage['chosen'])==65:continue
 doc=p.load(p.CACHE/f'extremadura/elecciones/{n}.json');text='\n'.join(doc['pages']);lines=[p.c.clean(r)for line in text.splitlines()for r in line.split('|')if 8<len(r)<120];chosen={r['key']for r in stage['chosen']};bykey={r['key']:r for r in stage['members']}
 print('LEGISLATURA',n)
 for row in bykey.values():
  if row['key']in chosen:continue
  k=p.key(row['name']);ranked=sorted([(difflib.SequenceMatcher(None,k,p.key(re.sub(r'^\s*(?:\d+[.)]?\s+)?(?:Don|Doña|D[ªaº.]?)\s+','',line))).ratio(),line)for line in lines],reverse=True)
  if ranked[0][0]>.67:print(row['key'],row['name'],[(round(score,3),line)for score,line in ranked[:2]])
