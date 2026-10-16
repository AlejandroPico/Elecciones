"""Extrae hechos breves de las fuentes del norte. No publica contactos ni biografías completas."""
import importlib.util,pathlib,json,re
from urllib.parse import urljoin
s=importlib.util.spec_from_file_location('n',pathlib.Path(__file__).with_name('consultar-norte.py'));n=importlib.util.module_from_spec(s);s.loader.exec_module(n);c=n.c

def government_facts():
    history=[];current=[]
    for f in sorted((c.CACHE/'gobiernos').glob('pais-vasco-*.json')):
        key=f.stem.replace('pais-vasco-','')
        if key not in n.ROMANS:continue
        data=json.loads(f.read_text('utf8'));url=data['source'];p=c.soup(url);rows=[]
        for box in p.select('.predecesors-members'):
            h=box.select_one('h2');role=box.select_one('p')
            if h and role:
                dates=[c.clean(li.get_text())for li in box.select('li')if re.search(r'BOPV|Cesa',li.get_text(),re.I)]
                image=box.select_one('img[src]')
                parent=box.parent
                if not image and len(parent.select('.predecesors-members'))==1:image=parent.select_one('img[src]')
                rows.append({'name':c.clean(h.get_text()),'role':c.clean(role.get_text()),'period':f'Legislatura {key}'+(' · '+' · '.join(dates)if dates else' · relación nominal archivada'),'source':url,'legislature':n.ROMANS.index(key)+1,'image':urljoin(url,image['src'])if image else None})
        if not rows:
            text=data['text'];begin=re.search(r'\bLEHENDAKARI\b',text);text=text[begin.start():]if begin else''
            # Archivo antiguo: una entrada por separador, con rol, titular y BOPV.
            for block in re.split(r'_{5,}',text):
                block=c.clean(block);m=re.search(r'^(LEHENDAKARI|(?:VICEPRESIDENTE|CONSEJER[OA]|SECRETARIO)[A-ZÁÉÍÓÚÜÑ ,º/\-]+?)\s+([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ].+?)\s+(EAJ/?PNV|EAJ/PNV|PSE(?:-EE)?/PSOE)\s*\(',block)
                if m:rows.append({'name':c.clean(m[2]),'role':m[1].capitalize(),'period':block,'source':url,'legislature':n.ROMANS.index(key)+1})
        history.extend(rows);print('HISTORICO VASCO',key,len(rows),flush=True)
    url='https://www.euskadi.eus/miembros-del-consejo-de-gobierno/web01-s1ezaleh/es/';p=c.soup(url)
    for box in p.select('.boardMemberItems > li'):
        a=box.select_one('a.data');name=box.select_one('.name');role=box.select_one('.position');image=box.select_one('img[src]')
        if not(a and name and role):continue
        extras=[c.clean(x.get_text())for x in box.select('.positionExtra')if c.clean(x.get_text())!='Lehendakari']
        current.append({'name':c.clean(name.get_text()),'role':' · '.join([*extras,c.clean(role.get_text())]),'image':urljoin(url,image['src'])if image else None,'source':urljoin(url,a['href']),'directory':url})
    assert len(current)==16,len(current)
    c.write(c.CACHE/'pais-vasco-consejerias-historicas.json',history);c.write(c.CACHE/'pais-vasco-gobierno-vigente.json',current)
    history=[];current=[];url='https://www.navarra.es/es/gobierno-de-navarra/gobiernos-anteriores';p=c.soup(url)
    for box in p.select('.tab-pane'):
        head=box.select_one('h2')
        if not head:continue
        period=c.clean(head.get_text());m=re.match(r'(\d{4})-(\d{4})',period)
        if not m:continue
        for li in box.select('li'):
            title=li.select_one('strong');text=c.clean(li.get_text(' ',strip=True))
            if not title or ':'not in text:continue
            role=c.clean(title.get_text());name=text.split(':',1)[1].split('(')[0].strip(' .')
            if role=='Presidentes':continue
            if not name:continue
            history.append({'name':name,'role':role,'period':period,'startYear':int(m[1]),'endYear':int(m[2]),'source':url})
    url='https://gobiernoabierto.navarra.es/es/transparencia/gobierno';p=c.soup(url)
    for box in p.select('.ficha-gobierno'):
        a=box.select_one('a.enlace-directo');image=box.select_one('img[src]');role=box.select_one('strong')
        if a and role:current.append({'name':c.clean(a.get_text()),'role':c.clean(role.get_text()),'image':urljoin(url,image['src'])if image else None,'source':urljoin(url,a['href']),'directory':url})
    assert len(current)==14,len(current)
    c.write(c.CACHE/'navarra-consejerias-historicas.json',history);c.write(c.CACHE/'navarra-gobierno-vigente.json',current)
    print('GOBIERNOS',len(history),'Navarra históricos;',len(current),'Navarra vigentes',flush=True)

if __name__=='__main__':government_facts()
