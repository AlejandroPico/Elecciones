"""Añade cuadros nominales del BOME y del dossier institucional del Senado."""
import importlib.util,json
spec=importlib.util.spec_from_file_location('consulta','Gobiernos/herramientas/consultar-canarias-ceuta-melilla.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
rows=json.loads((c.CACHE/'consejerias-ciudades.json').read_text('utf8'))
source='https://www.melilla.es/mandar.php/n/9/2535/Extra28_718.pdf'
pairs=[
 ('Manuel Ángel Quevedo Mateos','Vicepresidencia primera y Consejería de Medio Ambiente'),
 ('María de la Paz Velázquez Clavarana','Vicepresidencia segunda y Consejería de Presidencia y Participación Ciudadana'),
 ('Daniel Conesa Mínguez','Consejería de Hacienda, Administraciones Públicas y Contratación'),
 ('Francisco Javier González García','Consejería de Fomento'),
 ('Sofía Acedo Reyes','Consejería de Economía y Empleo'),
 ('Antonio Miranda Montilla','Consejería de Educación, Juventud y Deportes'),
 ('Fadela Mohatar Maanan','Consejería de Cultura y Festejos'),
 ('Daniel Ventura Rizo','Consejería de Bienestar Social'),
 ('Isidoro Francisco González Peláez','Consejería de Seguridad Ciudadana'),
]
rows += [{'region':'Melilla','date':'2015-07-20','name':name,'role':role,'source':source} for name,role in pairs]
source='https://www.senado.es/brsweb/CALEX/textos/pdf/parlagobi.pdf'
pairs=[
 ('Miguel Marín Cobos','Vicepresidencia primera y Consejería de Fomento, Juventud y Deportes'),
 ('Daniel Conesa Mínguez','Vicepresidencia segunda y Consejería de Economía y Hacienda'),
 ('Esther Donoso García-Sacristán','Consejería de Presidencia y Participación Ciudadana'),
 ('Catalina Muriel García','Consejería de Administraciones Públicas'),
 ('José Ángel Pérez Calabuig','Consejería de Medio Ambiente'),
 ('Simi Chocrón Chocrón','Consejería de Cultura y Festejos'),
 ('Antonio Miranda Montilla','Consejería de Educación y Colectivos Sociales'),
 ('María Antonia Garbín Espigares','Consejería de Bienestar Social y Sanidad'),
 ('Francisco Javier Calderón Carrillo','Consejería de Seguridad Ciudadana'),
]
rows += [{'region':'Melilla','date':'2014-01','documentedPeriod':'Cuadro del Senado · enero de 2014','name':name,'role':role,'source':source} for name,role in pairs]
# Aplicación repetible sin duplicar disposiciones.
unique={json.dumps(r,sort_keys=True,ensure_ascii=False):r for r in rows}
c.write(c.CACHE/'consejerias-ciudades.json',list(unique.values()))
print('Consejerías documentadas',len(unique))
