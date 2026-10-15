"""Instantánea nominal de las presidencias; fechas de decreto, no de posesión."""
import importlib.util,json,pathlib,re
from concurrent.futures import ThreadPoolExecutor
s=importlib.util.spec_from_file_location('a','Gobiernos/herramientas/consultar-aragon.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
MONTHS=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
# ID institucional del dosier, territorio, identidad canónica y partido de la
# presidencia. Las alianzas de investidura no alteran esta identificación.
ROWS=[(1,'pais-vasco','imanol-pradales','Imanol Pradales Gil','pnv','EAJ-PNV'),(2,'cataluna','salvador-illa-roca-el-boe-publica-su-cese-el-27-de-enero-de-2021','Salvador Illa Roca','psc','PSC'),(3,'galicia','alfonso-rueda','Alfonso Rueda Valenzuela','pp','PP'),(4,'andalucia','juan-manuel-moreno','Juan Manuel Moreno Bonilla','pp','PP'),(5,'asturias','adrian-barbon','Adrián Barbón Rodríguez','psoe','PSOE'),(6,'cantabria','maria-jose-saenz-de-buruaga','María José Sáenz de Buruaga Gómez','pp','PP'),(7,'la-rioja','gonzalo-capellan','Gonzalo Capellán de Miguel','pp','PP'),(8,'murcia','fernando-lopez-miras','Fernando López Miras','pp','PP'),(9,'valencia','juanfran-perez-llorca','Juan Francisco Pérez Llorca','pp','PP'),(10,'aragon','jorge-azcon','Jorge Antonio Azcón Navarro','pp','PP'),(11,'castilla-la-mancha','emiliano-garcia-page','Emiliano García-Page Sánchez','psoe','PSOE'),(12,'canarias','fernando-clavijo-batlle','Fernando Clavijo Batlle','cc','CC'),(13,'navarra','maria-chivite','María Victoria Chivite Navascués','psoe','PSN-PSOE'),(14,'extremadura','maria-guardiola','María Guardiola Martín','pp','PP'),(15,'baleares','congreso-243-14','Margarita Prohens Rigo','pp','PP'),(16,'madrid','isabel-diaz-ayuso','Isabel Natividad Díaz Ayuso','pp','PP'),(17,'castilla-y-leon','alfonso-fernandez-manueco','Alfonso Fernando Fernández Mañueco','pp','PP'),(18,'ceuta','juan-vivas','Juan Jesús Vivas Lara','pp','PP'),(19,'melilla','juan-jose-imbroda','Juan José Imbroda Ortiz','pp','PP')]
def source(row):
 number,territory,person,name,party,label=row
 if territory=='ceuta':person='ceuta-juan-jesus-vivas-lara'
 if territory=='melilla':person='senado-12833'
 dossier=f'https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_{number:02}'
 if territory=='aragon':url='https://www.boe.es/buscar/doc.php?id=BOE-A-2026-9361'
 elif territory in ['ceuta','melilla']:
  p=pathlib.Path('Gobiernos/Autonomías')/('Ceuta'if territory=='ceuta'else'Melilla')/'fuentes/nombramientos-presidencias.json';url=json.loads(p.read_text('utf8'))[-1]['source'];dossier=url
 else:
  p=c.soup(dossier);h=p.select_one('h3');para=h.find_next('p');url=a.urljoin(dossier,para.select_one('a[href]')['href'])
 boe=re.search(r'BOE-A-\d{4}-\d+',url)
 if boe:url='https://www.boe.es/buscar/doc.php?id='+boe[0]
 p=c.soup(url);titles=[c.clean(x.get_text(' ',strip=True))for x in p.select('h3')];title=next(t for t in titles if 'Real Decreto'in t)
 m=re.search(r'Real Decreto \d+/(\d{4}), de (\d{1,2}) de (\w+)',title);assert m,(territory,title)
 date=f'{m[1]}-{MONTHS.index(m[3])+1:02}-{int(m[2]):02}'
 nameInDecree='Alfonso Fernández Mañueco'if territory=='castilla-y-leon'else name
 assert nameInDecree.lower()in c.clean(p.get_text(' ',strip=True)).lower(),(name,url)
 partySource='https://www.ceuta.es/gobiernodeceuta/index.php/el-gobierno/la-asamblea'if territory=='ceuta'else'https://sede.melilla.es/sta/CarpetaPublic/doEvent?APP_CODE=STA&PAGE_CODE=PTS2_MIEMBROS'if territory=='melilla'else dossier
 return {'territory':territory,'person':person,'name':name,'party':party,'partyLabel':label,'appointedAt':date,'dateBasis':'Fecha del real decreto del mandato actual; no equivale a toma de posesión ni al primer mandato.','source':url,'title':title,'partySource':partySource,'checkedAt':c.CHECKED}
def main():
 with ThreadPoolExecutor(3)as pool:rows=list(pool.map(source,ROWS))
 c.write('Gobiernos/Autonomías/Mapa/presidencias.json',{'checkedAt':c.CHECKED,'colorBasis':'Partido de la presidencia autonómica, no diputación provincial, reparto electoral ni coalición de gobierno.','presidencies':rows})
 print('PRESIDENCIAS',[(r['territory'],r['appointedAt'])for r in rows],flush=True)
if __name__=='__main__':main()
