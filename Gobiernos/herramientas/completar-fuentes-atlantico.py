"""Recoge fichas públicas de los ejecutivos y las asambleas; no guarda contactos."""
import importlib.util, json, re
from urllib.parse import urljoin
spec=importlib.util.spec_from_file_location('consulta','Gobiernos/herramientas/consultar-canarias-ceuta-melilla.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def main():
    ceuta='https://www.ceuta.es/gobiernodeceuta/index.php/el-gobierno/el-equipo'
    page=c.soup(ceuta); people=[]
    for a in page.select('a[href]'):
        i=a.select_one('img[alt][src]')
        if not i or '/consejeros/' not in i['src']:continue
        source=urljoin(ceuta,a['href']);p=c.soup(source)
        article=p.select_one('.item-page') or p
        title=article.select_one('h2')
        texts=[e.get_text(' ',strip=True) for e in article.select('p')]
        role=next((t for t in texts if re.search(r'^Consejer[oa] de',t)),None)
        people.append({'name':i['alt'].strip(),'source':source,'image':urljoin(ceuta,i['src']),'role':role,'text':texts})
    c.write(c.CACHE/'ceuta-gobierno.json',people)
    asamblea='https://www.ceuta.es/gobiernodeceuta/index.php/el-gobierno/la-asamblea'
    p=c.soup(asamblea);article=p.select_one('.item-page') or p
    c.write(c.CACHE/'ceuta-asamblea-texto.json',{'source':asamblea,'lines':[e.get_text(' ',strip=True) for e in article.select('p,h2,h3,h4,li')],'images':[{'alt':i.get('alt'),'url':urljoin(asamblea,i['src'])} for i in article.select('img[src]')]})
    melilla='https://www.melilla.es/melillaportal/contenedor.jsp?codMenu=255&codMenuPN=600&codMenuSN=253&codbusqueda=19&seccion=s_ldes_d4_v2.jsp&tamanoPagina=20'
    p=c.soup(melilla); people=[]
    links={urljoin(melilla,a['href']):a.get_text(' ',strip=True) for a in p.select('a[href]') if re.search(r':\s*Exc[m]?a?o?\.',a.get_text(' ',strip=True))}
    for source,heading in links.items():
        role,name=re.split(r':\s*Exc',heading,maxsplit=1)
        name=re.sub(r'^.*?(?:D\.|Dª\.|Sra\.)\s*','',name)
        page=c.soup(source)
        texts=[e.get_text(' ',strip=True) for e in page.select('p')]
        images=[{'alt':i.get('alt'),'url':urljoin(source,i['src'])} for i in page.select('img[src]') if any(x in i.get('alt','').lower() for x in ['foto','imbroda','marín','conesa','mohatar','ventura','randa','fernández','quevedo'])]
        people.append({'name':name,'role':role,'source':source,'text':texts,'images':images})
    c.write(c.CACHE/'melilla-gobierno.json',people)
    canarias='https://www.gobiernodecanarias.org/principal/consejerias/'
    p=c.soup(canarias);paths=['eica','opvm','hacienda','papjs','efpafd','politicaterritorial','turemp','ucic','transicionecologica','bienestarsocial','sanidad','agpsa']
    links={'https://www.gobiernodecanarias.org/'+path+'/' for path in paths}
    sources={'https://www.gobiernodecanarias.org/organigrama/ficha-altos-cargos/?ou=42091'}
    for u in sorted(links):
        try:
            page=c.soup(u)
            for a in page.select('a[href]'):
                if 'ficha-altos-cargos' in a['href']:sources.add(urljoin(u,a['href']))
                elif 'organigrama' in a['href'] and 'ou=' in a['href']:
                    ou=re.search(r'ou=(\d+)',a['href'])[1]
                    sources.add('https://www.gobiernodecanarias.org/organigrama/ficha-altos-cargos/?ou='+ou)
        except Exception as e:print('Enlace pendiente',u,str(e),flush=True)
    people=[]
    for source in sorted(sources):
        p=c.soup(source);main=p.select_one('main') or p
        texts=[e.get_text(' ',strip=True) for e in main.select('h1,h2,h3,p,li')]
        images=[{'alt':i.get('alt'),'src':i['src']} for i in main.select('img[src]') if i['src'].startswith('data:image')]
        people.append({'source':source,'text':texts,'images':images})
    c.write(c.CACHE/'canarias-gobierno-actual.json',people)
    print('Fichas',len(people),'Canarias,',len(links),'enlaces',flush=True)

if __name__=='__main__':main()
