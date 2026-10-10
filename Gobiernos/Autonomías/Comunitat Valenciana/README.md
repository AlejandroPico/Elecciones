# Comunitat Valenciana

Archivo del Consell y de Les Corts desde las primeras elecciones autonómicas de 1983. Revisión complementaria: 10 de octubre de 2026. Comparte biblioteca horizontal, cronología, organigrama, hemiciclo, filtros y navegación con Cataluña y Madrid.

## Consell

Catorce etapas presidenciales, desde Lerma I hasta Pérez Llorca. El inicio corresponde a la toma de posesión presidencial: no se confunde con la publicación del nombramiento ni con la formación del gabinete. Las fuentes individuales se conservan en `fuentes/posesiones-presidencia.json`. Los diarios de sesiones confirman los relevos de 1999, 2002, 2003, 2007 y 2011; las tomas de posesión de 1987, 1991 y 1995 se contrastan en el estudio académico alojado por la Universidad de Sevilla. El cese de Zaplana de julio de 2002 se conserva sin prolongarlo hasta la toma de posesión de Olivas.

Las doce primeras etapas incorporan ahora 275 intervalos individuales de 97 titulares, contrastados con nombramientos, ceses, asignaciones de competencias y suplencias del DOGV. `fuentes/consell-historico.json` conserva los eventos transcritos, el articulado y la justificación de las fechas. Se distingue el día del decreto de su publicación y de los efectos de la disposición final. Los cuadros nominales anteriores se sustituyen por estos periodos en la cronología.

La composición saliente se conserva cuando continúa en funciones durante una nueva etapa presidencial: la toma de posesión del president no provoca un cese ficticio de todos sus consellers. Los periodos mostrados se recortan a cada etapa, conservando las fechas originales del nombramiento. Se representan también las asignaciones temporales y los días en que un nombramiento todavía no tiene cartera asignada.

Los gabinetes de Mazón y Pérez Llorca utilizan los efectos de los decretos del DOGV de 2023, julio y noviembre de 2024, noviembre y diciembre de 2025. Se preservan los cambios de competencia y las vacantes de un día que producen esas normas. El Consell vigente contiene doce titulares, con fotografía y fuentes biográficas, educativas y de nombramiento.

## Les Corts

Once legislaturas, 1.286 registros parlamentarios y 669 perfiles oficiales únicos recuperados, sin errores de consulta. La Cámara pasa de 89 a 99 escaños desde la VII legislatura. El registro vigente tiene 99 diputados, todos enlazados y con retrato: Popular 40, Socialista 31, Compromís 15 y Vox 13.

Las altas y bajas se conservan como aparecen en la fuente. La baja inclusiva se convierte al día siguiente para la comparación. La constitución de una Cámara no sustituye la fecha de una credencial. Las disoluciones se contrastan en `fuentes/limites-legislaturas.json`; el mandato de 1987 expira el 8 de mayo. Los registros posteriores de Diputación Permanente no prolongan la representación del Pleno.

El inventario oficial contiene tres intervalos invertidos y otras fechas anteriores a la constitución o posteriores a la disolución. El informe identifica cada caso. Se conservan las fechas originales, sin corregirlas por conjetura ni inventar ocupantes para forzar una suma. El visor ofrece únicamente instantáneas con mandatos documentados. El hemiciclo es esquemático: no atribuye asientos físicos.

La Mesa consultada en el portal es la vigente, incluso al solicitar legislaturas antiguas; esa respuesta no se utiliza como histórico. La publicación institucional de miembros de las Mesas y las crónicas parlamentarias permiten incorporar 69 intervalos de 48 personas en las once legislaturas. `fuentes/mesa-cronologia.json` identifica las fuentes de constitución y relevo, y conserva las vacantes documentadas. Cuando una crónica solo acredita la fecha del relevo, se explica el límite de precisión. Los finales por disolución delimitan el Pleno; no se presentan como cese de la Diputación Permanente.

## Personas y retratos

Se añaden 610 personas y se enlazan las identidades ya documentadas en el catálogo nacional. La variante Ximo Puig corresponde a Joaquín Francisco Puig Ferrer, con los registros del Congreso, Senado y OCDE. No se crea una segunda ficha. Los datos biográficos, formación, mandatos, grupos y comisiones viven en la carpeta propia. Todos los cargos propios se reúnen en una única sección de relaciones.

La incorporación inicial añadió 592 retratos; esta revisión recupera otros 14, identificados en publicaciones universitarias, municipales, profesionales y entrevistas de la etapa en el cargo. `fuentes/retratos-complementados.json` documenta cada complemento. Se mantienen las fotografías anteriores. Los recursos de Commons conservan autor, licencia y archivo original; se excluye el retrato de un poeta homónimo de Javier Zamora. El retrato de Ramon Vilar se identifica por el pie de foto de la publicación de Les Corts.

Siguen pendientes de un retrato individual identificable José Manuel Castellá Almiñana, Salvador Manuel Ortells Rosell, Miguel Doménech Pastor y José María Coll Comín. Las fotografías de grupo de baja resolución y las imágenes de homónimos no se utilizan como retratos individuales. No se copian contactos, patrimonio ni datos familiares.

## Herramientas y revisión

`Gobiernos/herramientas/consultar-valencia.py` consulta el archivo parlamentario; `consultar-consell.py` contrasta cuadros y Mesa; `transcribir-consell.py` conserva la transcripción con sus excepciones; `incorporar-valencia.py` integra personas, mandatos y composiciones. `consultar-historico-valencia.py` localiza normas originales del DOGV; sus resultados requieren lectura y contraste antes de transcribirlos. `integrar-cronologia-valencia.py` regenera el histórico diario y los cargos personales desde las fuentes publicadas, sin red ni caché. La incorporación ejecuta este último paso automáticamente para no restaurar los cuadros sin fechas.

Las respuestas originales y la caché se guardan en `test-results/valencia/`, excluido de Git. Las transcripciones verificadas y los documentos de control permanecen en `fuentes/`. Se conservan la auditoría inicial de `Gobiernos/revisiones/2026-10-09-valencia/` y la revisión complementaria de `Gobiernos/revisiones/2026-10-10-valencia/`.
