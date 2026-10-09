# Comunidad de Madrid

Archivo del Gobierno y de la Asamblea desde la constitución de la comunidad en 1983. La interfaz utiliza el visor regional común: biblioteca horizontal, cronología, organigrama, hemiciclo y enlaces a las identidades de `Políticos/`. Consulta: 9 de octubre de 2026.

## Gobierno

Se conservan catorce etapas presidenciales, las suplencias documentadas y el relevo de Educación de febrero de 2026. Las fechas de los decretos se distinguen de su publicación y de la toma de posesión. El gabinete vigente se contrasta con el directorio oficial de la Comunidad.

Los nombramientos modernos enlazan al BOCM cuando el documento confirma a la persona. Las composiciones enciclopédicas complementan la cronología: `fuentes/contraste-nombramientos.json` identifica los documentos comprobados. No presentar una referencia fallida como una comprobación positiva.

Las siete primeras etapas conservan sus consejerías en `archiveTerms`: los cuadros históricos identifican titulares, pero no todos sus intervalos diarios. Esos cargos se muestran como archivo de la etapa, separado del organigrama fechado. No afirmar que todos ejercieron simultáneamente ni inventar fechas.

## Asamblea

Las trece legislaturas tienen carpeta propia; VI y VII corresponden ambas a 2003. Las fichas individuales y las listas históricas proceden de la Asamblea, consultadas en su portal oficial de datos abiertos. Se ha podido recuperar el contenido de 789 fichas; las respuestas temporalmente indisponibles figuran en el informe de revisión. Esto no acredita que el archivo oficial publicado sea exhaustivo.

El CSV de ocupaciones contiene numeraciones de legislatura desplazadas y mandatos históricos superpuestos. `fuentes/correcciones-legislaturas.json` documenta cada reasignación inequívoca. Las legislaturas que exceden su capacidad física se presentan mediante un archivo nominal (`nominalOnly`), sin truncar personas para simular un reparto diario. Las demás usan el hemiciclo compartido. El registro de mandatos posterior a una disolución no prueba que existiera un Pleno en funcionamiento.

Las disoluciones anticipadas de 2003 y 2021 se cortan en la fecha oficial, recogida en `fuentes/disoluciones-anticipadas.json`. Para las demás etapas se conserva el límite de la constitución siguiente del archivo legislativo. El visor ofrece únicamente fechas con mandatos documentados, sin convertir un final común de registros en un hemiciclo vacío. Las fechas de convocatoria ordinaria no se interpretan como una disolución.

Los 135 diputados y los siete cargos de la Mesa del registro vigente tienen identidad enlazada. El hemiciclo agrupa personas, sin asignarles un asiento físico. Los grupos parlamentarios se conservan separados de la militancia política.

## Personas y fotografías

`identidades.json` contiene las variantes contrastadas del catálogo nacional. Cada persona guarda sus mandatos, cargos, grupos y comisiones en su carpeta; todos sus cargos propios se reúnen en la ficha. Las discrepancias de nacimiento constan en `fuentes/nacimientos-discrepantes.json` y se explican en las fichas correspondientes.

Se conservan los retratos previos. Los nuevos retratos institucionales corresponden a imágenes personales; `default.jpg` y las siluetas reconocidas se excluyen. Las fotografías de Commons necesitan autor, licencia y enlace al archivo. Las ausencias no se sustituyen por fotos de otra persona. No se recopilan contactos, patrimonio ni datos familiares.

## Actualización

Las herramientas están en `Gobiernos/herramientas/`: consultar las fuentes con `consultar-madrid.py`, contrastar los cuadros con `transcribir-gobierno-madrid.py`, migrar mediante `incorporar-madrid.py` y completar retratos disponibles con `completar-retratos-madrid.py`. La caché y las respuestas originales se guardan en `test-results/madrid/`, excluido de Git. El informe reproducible queda en `Gobiernos/revisiones/2026-10-09-madrid/`.
