"""Completa una composición fechada sin proyectarla al resto de la legislatura.

Ejecutar después de incorporar-murcia.py y las correcciones de identidades.
Solo modifica las fichas relacionadas; no vuelve a importar el catálogo completo.
"""
import importlib.util,pathlib,json,io
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-murcia.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
from PIL import Image
ROOT=pathlib.Path('Políticos');BASE=pathlib.Path('Gobiernos/Autonomías/Región de Murcia')
ACTA='https://transparencia.carm.es/wres/transparencia/doc/Consejo_Gobierno/actas/2023_10_19_actasCG.pdf'
APPOINTMENTS='https://www.borm.es/services/suplemento/ano/2023/numero/12/pdf'
DAY='2023-10-19'
def load(file,default=None):
 return json.loads(file.read_text('utf8'))if file.exists()else default
def add(folder,file,rows):
 values=load(folder/file,[])
 for row in rows:
  if row not in values:values.append(row)
 c.write(folder/file,values)
def ref(label,url):return dict(label=label,url=url)
def portrait(name,url,source,credit):
 folder=ROOT/name
 if (folder/'retrato.json').exists():return
 raw=c.fetch(url);im=Image.open(io.BytesIO(raw));assert min(im.size)>50;im.verify()
 file='retrato-murcia.'+{'JPEG':'jpg','PNG':'png','WEBP':'webp'}[im.format]
 (folder/file).write_bytes(raw);c.write(folder/'retrato.json',dict(file=file,credit=credit,source=source,original=url,reviewedAt=c.CHECKED))

def main():
 auditFile=ROOT/'revisiones/2026-10-16-murcia/informe.json';audit=load(auditFile);created=[]
 new=[('Sara Rubira Martínez','murcia-sara-rubira-martinez','SR',None,'Consejera de Agua, Agricultura, Ganadería y Pesca'),('José Manuel Pancorbo de la Torre','murcia-jose-manuel-pancorbo-de-la-torre','JM','vox','Consejero de Fomento e Infraestructuras')]
 for name,id,initials,party,role in new:
  folder=ROOT/name;folder.mkdir(exist_ok=True)
  if not(folder/'ficha.json').exists():
   c.write(folder/'ficha.json',dict(id=id,name=name,fullName=name,initials=initials,organization=party,affiliationStatus='documented'if party else'pending',relation='Trayectoria institucional documentada',role=role,summary='Integrante del Consejo de Gobierno de la Región de Murcia documentado en 2023.',offices=[],reviewedAt=c.CHECKED));created.append(dict(id=id,name=name))
  add(folder,'fuentes.json',[ref('Acta del Consejo de Gobierno de 19 de octubre de 2023',ACTA),ref('Nombramientos del BORM de 14 de septiembre de 2023',APPOINTMENTS)])
 partySource='https://www.voxespana.es/noticias/pancorbo-portman-no-puede-convertirse-en-un-chernobil-20260523'
 folder=ROOT/'José Manuel Pancorbo de la Torre';source=ref('Presidencia regional identificada por Vox, 23 de mayo de 2026',partySource)
 add(folder,'afiliaciones.json',[dict(organization='vox',name='Vox',period='Presidencia regional documentada en 2026',kind='association',source=source)])
 c.write(folder/'actividad.json',dict(state='active',reason='Presidencia regional de Vox documentada en 2026.',checkedAt=c.CHECKED,sources=[source]))
 add(folder,'fuentes.json',[source])
 portrait('Sara Rubira Martínez','https://www.agronegocios.es/wp-content/uploads/2023/09/SaraRubira.jpg','https://www.agronegocios.es/agronegocios/autonomias/la-periodista-sara-rubira-martinez-nueva-consejera-de-agua-agricultura-ganaderia-y-pesca-de-la-region-de-murcia/','Retrato identificado de Sara Rubira publicado por Agronegocios en septiembre de 2023; autor y licencia no especificados.')
 portrait('José Manuel Pancorbo de la Torre','https://www.diariodelpuerto.com/binrepository/1200x1200/0c164/1200d597/none/5351385/FTUU/imagen-jose-manuel-pancorbo-de-la-torre_201-2935472_20230913213232.jpg','https://www.diariodelpuerto.com/logistica/jose-manuel-pancorbo-nuevo-consejero-de-fomento-e-infraestructuras-de-murcia-MP16919948','Retrato identificado de José Manuel Pancorbo publicado por Diario del Puerto en septiembre de 2023; autor y licencia no especificados.')
 portrait('Juan José Pedreño Planes','https://doihojqqs770p.cloudfront.net/articulos/articulos-10782.jpeg','https://www.consalud.es/Especiales/anuario-consalud/juan-jose-pedreno-consejero-sanidad-murcia.html','Retrato identificado de Juan José Pedreño publicado por ConSalud; autor y licencia no especificados.')
 rows=[('José Ángel Antelo Paredes','Vicepresidente y Consejero de Interior, Emergencias y Ordenación del Territorio','vice'),('María de la Concepción Ruiz Caballero','Consejera de Política Social, Familias e Igualdad','minister'),('Marcos Ortuño Soto','Consejero de Presidencia, Portavocía y Acción Exterior','minister'),('Sara Rubira Martínez','Consejera de Agua, Agricultura, Ganadería y Pesca','minister'),('Luis Alberto Marín González','Consejero de Economía, Hacienda y Empresa','minister'),('Juan María Vázquez Rojas','Consejero de Medio Ambiente, Universidades, Investigación y Mar Menor','minister'),('Carmen María Conesa Nieto','Consejera de Turismo, Cultura, Juventud y Deportes','minister'),('José Manuel Pancorbo de la Torre','Consejero de Fomento e Infraestructuras','minister'),('Víctor Javier Marín Navarro','Consejero de Educación, Formación Profesional y Empleo','minister'),('Juan José Pedreño Planes','Consejero de Salud','minister')]
 file=BASE/'Gobierno/2023 Legislatura XI · Fernando López Miras/composicion.json';government=load(file);government['terms']=[row for row in government['terms']if row.get('observedAt')!=DAY];snapshot=[]
 for name,role,level in rows:
  folder=ROOT/name;id=load(folder/'ficha.json')['id']
  term=dict(person=id,name=name,start=None,end=None,role=role,level=level,source=ACTA,observedAt=DAY,period='Composición acreditada por acta de 19 de octubre de 2023');snapshot.append(term)
  add(folder,'cargos-autonomias.json',[dict(territory='murcia',title=role,period='Cargo acreditado el 19/10/2023',source=ref('Acta del Consejo de Gobierno de 19 de octubre de 2023',ACTA))]);add(folder,'fuentes.json',[ref('Acta del Consejo de Gobierno de 19 de octubre de 2023',ACTA)])
 government['terms']+=snapshot;c.write(file,government)
 c.write(BASE/'fuentes/composicion-2023-10-19.json',dict(date=DAY,source=ACTA,appointments=APPOINTMENTS,note='Composición institucional: incluye miembros que excusaron su asistencia. La presidencia por sustitución de la sesión no sustituye al presidente titular. No se infieren intervalos diarios.',members=snapshot))
 for row in created:
  if not any(item['id']==row['id']for item in audit['newPeople']):audit['newPeople'].append(row);audit['totalPeople']+=1;audit['peopleReviewed']+=1
 id=load(ROOT/'Juan José Pedreño Planes/ficha.json')['id']
 for key in ['missingPortraits','allMissingPortraits']:
  audit[key]=[item for item in audit[key]if(item if isinstance(item,str)else item.get('id',item.get('person')))!=id]
 c.write(auditFile,audit);print('GABINETE 2023',len(snapshot)+1,'NUEVAS FICHAS',len(created),'TOTAL',audit['totalPeople'],flush=True)
if __name__=='__main__':main()
