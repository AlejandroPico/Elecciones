"""Deriva los trazados web del WFS del IGN. No necesita servicios en ejecución.

La caché original es ignorada; la cartografía derivada y su procedencia se publican.
Tolerancia visual máxima 0,075 unidades del viewBox; conserva islas y huecos.
"""
import importlib.util,json,math,pathlib
from urllib.parse import urlencode
s=importlib.util.spec_from_file_location('a','Gobiernos/herramientas/consultar-aragon.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);c=a.c
OUT=pathlib.Path('Gobiernos/Autonomías/Mapa')
REGIONS={'andalucia':'04 11 14 18 21 23 29 41','aragon':'22 44 50','asturias':'33','baleares':'07','canarias':'35 38','cantabria':'39','castilla-la-mancha':'02 13 16 19 45','castilla-y-leon':'05 09 24 34 37 40 42 47 49','cataluna':'08 17 25 43','valencia':'03 12 46','extremadura':'06 10','galicia':'15 27 32 36','madrid':'28','murcia':'30','navarra':'31','pais-vasco':'01 20 48','la-rioja':'26','ceuta':'51','melilla':'52'}
TERRITORY={code:region for region,codes in REGIONS.items()for code in codes.split()}
FILTER='<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0" xmlns:au="http://inspire.ec.europa.eu/schemas/au/4.0" xmlns:xlink="http://www.w3.org/1999/xlink"><fes:PropertyIsEqualTo><fes:ValueReference>au:nationalLevel/@xlink:href</fes:ValueReference><fes:Literal>https://inspire.ec.europa.eu/codelist/AdministrativeHierarchyLevel/3rdOrder</fes:Literal></fes:PropertyIsEqualTo></fes:Filter>'
IGN='https://www.ign.es/wfs-inspire/unidades-administrativas?'+urlencode({'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':'au:AdministrativeUnit','count':100,'outputFormat':'application/geo+json','srsName':'EPSG:4258','filter':FILTER})
NE='https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson'
def original(file,url):
 p=c.CACHE/file
 if not p.exists():c.write(p,json.loads(c.fetch(url)))
 return json.loads(p.read_text('utf8'))
def polygons(feature):
 g=feature['geometry'];return g['coordinates']if g['type']=='MultiPolygon'else[g['coordinates']]
def lambert(point):
 # Lambert conformal cónica esférica, paralelos 35°/43°, meridiano -3,5°.
 lon,lat=map(math.radians,point[:2]);p1,p2=map(math.radians,[35,43]);n=math.log(math.cos(p1)/math.cos(p2))/math.log(math.tan(math.pi/4+p2/2)/math.tan(math.pi/4+p1/2));f=math.cos(p1)*math.tan(math.pi/4+p1/2)**n/n
 # El eje vertical de SVG crece hacia abajo: el norte debe disminuir y.
 rho=f/math.tan(math.pi/4+lat/2)**n;theta=n*(lon-math.radians(-3.5));return(rho*math.sin(theta),rho*math.cos(theta))
def fit(points,box):
 xy=[lambert(p)for p in points];xs,ys=zip(*xy);xmin,xmax,ymin,ymax=min(xs),max(xs),min(ys),max(ys);x,y,w,h=box;scale=min(w/(xmax-xmin),h/(ymax-ymin));ox=x+(w-(xmax-xmin)*scale)/2;oy=y+(h-(ymax-ymin)*scale)/2
 return lambda p:((lambert(p)[0]-xmin)*scale+ox,(lambert(p)[1]-ymin)*scale+oy)
def simplify(points,tolerance=.075):
 if len(points)<4:return points
 keep={0,len(points)-1};stack=[(0,len(points)-1)];limit=tolerance*tolerance
 while stack:
  lo,hi=stack.pop();ax,ay=points[lo];bx,by=points[hi];dx,dy=bx-ax,by-ay;length=dx*dx+dy*dy;far=-1;distance=limit
  for i in range(lo+1,hi):
   px,py=points[i];t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/length))if length else 0;d=(px-ax-t*dx)**2+(py-ay-t*dy)**2
   if d>distance:distance=d;far=i
  if far>=0:keep.add(far);stack.extend([(lo,far),(far,hi)])
 return[points[i]for i in sorted(keep)]
def path(polys,project):
 result=[]
 for poly in polys:
  for ring in poly:
   xy=simplify([project(p)for p in ring])
   if len(xy)<4:continue
   result.append('M'+'L'.join(f'{x:.2f},{y:.2f}'for x,y in xy)+'Z')
 return ''.join(result)
def points(features):return[p for f in features for poly in polygons(f)for ring in poly for p in ring]
def main():
 raw=original('ign-provincias.json',IGN);countries=original('paises-geografia.json',NE)
 features=raw['features'];bycode={f['properties']['nationalCode'][4:6]:f for f in features};assert set(TERRITORY)<=set(bycode)
 # El IGN publica un elemento 54: territorios no adscritos a una provincia.
 # Se conserva como contexto neutro, nunca se asigna una presidencia inventada.
 mainFeatures=[f for code,f in bycode.items()if code not in ['35','38','51','52','54']]
 mainProject=fit(points(mainFeatures),(80,36,940,635));canaryProject=fit(points([bycode['35'],bycode['38']]),(62,706,340,115))
 projects={'main':mainProject,'canarias':canaryProject,'ceuta':fit(points([bycode['51']]),(657,739,130,69)),'melilla':fit(points([bycode['52']]),(877,739,100,69))}
 provinces=[]
 for code in sorted(TERRITORY):
  f=bycode[code];region=TERRITORY[code];panel=region if region in ['canarias','ceuta','melilla']else'main';geometry=path(polygons(f),projects[panel]);assert geometry
  provinces.append({'id':code,'name':f['properties']['name']['GeographicalName']['spelling']['SpellingOfName']['text'],'territory':region,'panel':panel,'path':geometry})
 neighbours=[]
 for f in countries['features']:
  name=f['properties']['ADMIN']
  if name not in ['Portugal','France','Andorra','Morocco']:continue
  # Excluir territorios de ultramar antes de proyectar; el recorte final es SVG.
  polys=[poly for poly in polygons(f)if any(-20<p[0]<10 and 25<p[1]<50 for p in poly[0])]
  neighbours.append({'name':name,'panel':'main','path':path(polys,mainProject)})
  if name=='Morocco':
   for panel in ['ceuta','melilla']:neighbours.append({'name':name,'panel':panel,'path':path(polys,projects[panel])})
 c.write(OUT/'cartografia.json',{'viewBox':'0 0 1100 850','provinces':provinces,'neighbours':neighbours,'unassigned':path(polygons(bycode['54']),mainProject)if '54'in bycode else''})
 c.write(OUT/'procedencia-cartografica.json',{'checkedAt':c.CHECKED,'projection':'Lambert conformal cónica esférica; paralelos 35 y 43; meridiano -3.5. Inserciones con encuadre propio.','maximumSimplification':0.075,'viewBox':'0 0 1100 850','provinces':{'source':IGN,'credit':'© Instituto Geográfico Nacional de España','license':'CC BY 4.0','licenseUrl':'https://creativecommons.org/licenses/by/4.0/','catalog':'https://centrodedescargas.cnig.es/CentroDescargas/detalleArchivo?sec=12408588','sha256':__import__('hashlib').sha256(c.fetch(IGN)).hexdigest()},'neighbours':{'source':NE,'credit':'Natural Earth','license':'Dominio público','licenseUrl':'https://www.naturalearthdata.com/about/terms-of-use/','sha256':__import__('hashlib').sha256(c.fetch(NE)).hexdigest()}})
 print('MAPA',len(provinces),'provincias',sum(len(r['path'])for r in provinces),'bytes de trazados',flush=True)
if __name__=='__main__':main()
