import importlib.util,pathlib,re,sys
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-extremadura-balears.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
for url in sys.argv[1:]:
 p=c.soup(url);print('\nURL',url)
 for selector in ['#tab_legislaturas','a[href*="dipslegis-12-"]','a[href*="Fitxa"]','a[href*="legislatura"]','a[href*="webgtp"]']:
  values=p.select(selector)
  print('SELECTOR',selector,'COUNT',len(values))
  for a in values[:2]:print(str(a.parent)[:4300])
 for script in p.select('script'):
  if 'showDiputado'in script.get_text():print('SCRIPT',script.get_text()[:7000])
 print('SCRIPTS',[a.get('src')for a in p.select('script[src]')])
 if 'parlamentib'in url:
  for a in p.select('script[src*="sitemaster"]'):
   code=c.fetch(r.urljoin(url,a['src'])).decode('utf8');match=re.search(r'function showDiputado',code)
   if match:print('SHOW DIPUTADO',code[match.start():match.start()+3000])
