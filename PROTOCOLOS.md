# Protocolos de Elecciones

Revisión: 8 de octubre de 2026. Aplicable a personas y agentes que amplíen este repositorio.

## Carpetas y nombres

- Toda información específica de una convocatoria pertenece a `Elecciones/<convocatoria>/`.
- Generales: `Generales <Mes> <AAAA>`, por ejemplo `Generales Noviembre 2026`.
- Autonómicas: `Autonómicas <territorio oficial> <Mes> <AAAA>`; municipales: `Municipales <territorio> <Mes> <AAAA>`.
- Meses en español con inicial mayúscula. Si hay dos convocatorias del mismo ámbito y mes, ambas incorporarán el día con dos cifras antes del mes. No improvisar otros patrones.
- Separar contenido común y contenido electoral. `Elecciones/<convocatoria>/` contiene cuestionario, contextos, candidaturas, resultados y programas de ESA elección. No almacenar allí biografías ni históricos generales de partidos o gobiernos.
- Cada persona vive en `Políticos/<Nombre completo>/`. Usar nombre y todos los apellidos acreditados, con espacios, tildes y guiones originales; nunca notas al pie o comentarios del documento de procedencia. Una carpeta por persona, aunque cambie de partido o cargo. El ID se conserva al corregir el nombre o mover la carpeta.
- Cada organización vive en `Partidos/<Nombre completo>/`. Si un nombre contiene un carácter incompatible con el sistema de archivos (como `/`), sustituirlo por `—` solo en la carpeta; conservar el nombre íntegro en `ficha.json`.
- Los gobiernos viven en `Gobiernos/<legislatura>/composiciones.json`, con el nombre institucional, por ejemplo `XV Legislatura` o `Legislatura Constituyente`. Órganos adicionales en `estructura.ts` dentro de la legislatura correspondiente. No duplicar una biografía dentro de un gobierno: enlazar su ID.
- Archivos de datos en minúsculas y con guiones. Retrato y sus fuentes permanecen en la carpeta de su persona; logotipo y procedencia, en la carpeta de su partido. Programas originales electorales en `Elecciones/<convocatoria>/programas/<partido-id>/<AAAA-MM-DD>-<documento>.pdf`. Los enlaces históricos del partido pueden apuntar a ese archivo sin duplicarlo.
- Cada dominio conserva también su código en una subcarpeta reservada `interfaz`: `Elecciones/interfaz/{cuestionario,perfil}/`, `Políticos/interfaz/`, `Partidos/interfaz/` y `Gobiernos/interfaz/`. `src/app/` contiene únicamente la aplicación común; `src/main.tsx` y `src/vite-env.d.ts` son el arranque y los tipos del entorno. No crear carpetas de archivo, partidos, gobiernos ni perfil dentro de `src`. `Elecciones/index.ts` selecciona la convocatoria activa. El mosaico de convocatorias queda pendiente.
- Los cargos viven en `Gobiernos/Cargos/<Nombre del cargo — Departamento>/ficha.json`; incluir el departamento cuando distingue órganos con el mismo nombre. Guardar denominación, ID estable, grupo, departamento, fuente y estado de cobertura. La carpeta reservada `interfaz` no es una entidad del catálogo.
- IDs nuevos: `es-<tipo>-<territorio-si-procede>-<AAAA-MM-DD>`. El ID existente `es-generales-2026` se mantiene por compatibilidad. Personas y organizaciones conservan IDs estables aunque cambien de cargo o nombre.
- No reutilizar IDs de preguntas con significado distinto. Cambiar la versión del cuestionario si cambia la propuesta, escala, eje o dirección. Ampliar una explicación sin cambiar su significado no modifica su puntuación.

## Fichas y lectura automática

Los lectores están en `Políticos/interfaz/datos/catalogo.ts`, `Partidos/interfaz/catalogo.ts` y `Gobiernos/interfaz/catalogo.ts`. Gobiernos y recursos se descubren mediante `import.meta.glob`. Para miles de fichas, `Partidos/interfaz/lectura.ts` y `Políticos/interfaz/lectura.ts` leen las carpetas originales y generan módulos virtuales durante la compilación, evitando un módulo por cada archivo de datos. No mantener un segundo catálogo manual de nombres ni una copia física de todas las fichas. Una nueva carpeta con `ficha.json` válido aparece en la siguiente compilación; GitHub Pages no enumera directorios en tiempo de ejecución.

Si la revisión identifica dos fichas de la misma persona, reunir sus datos en una carpeta, conservar el ID canónico y declarar los otros en `legacyIds`. Resolver todas las relaciones mediante `findPerson`, incluidos gobiernos y dirigentes de partidos; permite conservar enlaces anteriores sin reescribir los datos de otros dominios. No crear dos personas por una nota al pie ni descartar las trayectorias de la ficha duplicada.

En cada persona:

- `ficha.json`: ID estable, nombre completo, iniciales, vinculación acreditada o `null`, cargo/resumen, IDs de cargos y fecha de revisión. `knownAs` conserva nombres habituales para búsqueda, `wikidata` identifica la persona contrastada y `affiliationStatus` distingue `documented`, `independent` y `pending`.
- `afiliaciones.json`: historial de `{organization, name, period?, kind, source}`. `organization` enlaza un partido del catálogo o es `null` para una organización histórica sin ficha; `kind` distingue `membership` (militancia documentada), `association` (candidatura o colaboración sin acreditar militancia) e `independent` (independencia expresamente documentada). Ausencia de prueba no significa independencia. Las federaciones regionales se vinculan al partido correspondiente, conservando su nombre. No confundir el Partido Popular de 1976 con el PP actual. El filtro consulta también vínculos históricos, sin certificar su vigencia.
- `datos-personales.json`: nacimiento, fecha ISO completa cuando se conoce, año, fallecimiento y `personalSources`.
- `formacion.json`: lista de estudios e instituciones; referencias en `fuentes-formacion.json`.
- `trayectoria.json`: lista de `{period, title, source: {label, url}}`.
- `actuaciones.json`: hechos con fecha, descripción, estado y fuentes. No crear un archivo vacío como sustituto de investigación.
- `fuentes.json`: referencias generales de la ficha.
- `retrato.jpg` (o PNG/WebP/SVG/GIF) y `retrato.json`: `{file, credit, source, original?, license?, licenseUrl?, date?, description?}`. Un solo retrato activo; no recursos huérfanos. Conservar los créditos y la licencia que figure en la procedencia, sin inventar autoría, licencia o fecha. Diferenciar fecha de publicación y fecha de la fotografía.
- `revision.json`: fecha, identidad contrastada, apartados revisados, IDs anteriores, correcciones y datos pendientes. La carpeta reservada `Políticos/revisiones/<AAAA-MM-DD>/` contiene informe, correcciones y comprobación de conservación; no es una persona ni sustituye sus fuentes individuales.

Si una unificación reúne retratos institucionales diferentes, conservar el alternativo como `retrato-historico-<id>.<ext>` y sus créditos en `retrato-historico-<id>.json`. La interfaz actual presenta solo el retrato activo; no perder el archivo alternativo durante una migración.

Priorizar un retrato oficial de la época de ejercicio del cargo. Si no está disponible, utilizar una fotografía individual identificada en una fuente institucional, Wikimedia Commons o una publicación con pie de foto inequívoco. Comprobar la identidad visual, el recurso descargado y su presentación; no asignar una imagen por coincidencia de apellidos, extraer caras sin identificación ni generar retratos ficticios. Las fotografías son recursos locales de la carpeta personal. La revisión de 8 de octubre de 2026 conserva retratos anteriores y documenta las identidades y recursos reunidos; su cobertura no constituye un censo completo de España.

En cada partido: `ficha.json`, `fuentes.json`, y los apartados disponibles `historia.json`, `dirigentes.json` y `programas.json`. Los dirigentes declaran `{period, title, person, source}`; `person` es el ID de una ficha existente. Distinguir presidente, secretario general y gestora. El logotipo se acompaña de `logotipo.json: {file, source}`. `logoBackground` permite presentar marcas claras sobre un fondo adecuado sin modificar el original.

Los datos registrales se guardan en `ficha.json.registration`: ID del Ministerio del Interior, denominación, fecha ISO, localidad/provincia, enlace a la inscripción y fecha de consulta. Las entidades nuevas usan `registro-<id ministerial>`; las fichas ya existentes conservan su ID. Si una marca conocida y una inscripción corresponden a la misma organización, reunirlas en una sola carpeta y conservar el otro identificador en `legacyIds`. No confundir una coalición y sus integrantes. `Partidos/registro-2026-10-07.json` conserva parámetros, IDs y huella de la consulta, no es el catálogo que lee la interfaz. No incorporar domicilios particulares, contactos ni documentos personales del registro.

La interfaz presenta los apartados en vertical y únicamente cuando contienen datos. Sin formación o actuaciones no se imprime un encabezado vacío ni un mensaje de relleno. Ausencia de archivo significa falta de cobertura, no inexistencia del hecho. Los cargos se derivan de composiciones y enlazan personas por ID.

Para una migración: inventariar IDs, relaciones, textos, referencias y recursos antes de mover; comprobar su conservación con el catálogo nuevo antes de retirar el anterior. `docs/migracion-2026-10-07.json` registra las 275 identidades, 15 partidos y 72 composiciones iniciales. Mantener las pruebas que evitan perderlos.

## Cuestionario y neutralidad

Una pregunta plantea una sola propuesta comprensible. Su contexto ampliado delimita alcance, conceptos, exclusiones y consideraciones de ambos sentidos. No atribuir superioridad moral a una respuesta ni introducir hechos recientes sin fuente y fecha. No confundir las propuestas hipotéticas con legislación vigente. La escala y dirección deben ser explícitas; omitir es distinto de responder neutral. Las ponderaciones son elección del usuario. El banco actual es piloto, no un instrumento validado.

Responder inicia un plazo fijo de tres segundos, representado en el separador sobre la importancia. Cambiar respuesta o importancia durante ese plazo no lo reinicia; navegar o salir del cuestionario cancela el avance pendiente. Volver a pulsar una respuesta ya seleccionada inicia un nuevo plazo cuando no hay uno activo. Al terminar la última pregunta se abre «Mi perfil». Importancia por defecto: normal. El movimiento reducido conserva el plazo y evita una animación innecesaria.

## Partidos y candidaturas

El directorio de partidos NO acredita presentación a una elección. Solo marcar una candidatura como confirmada con proclamación oficial y su enlace, circunscripción, cámara, orden y suplencias. No confundir un líder de partido con cabeza de todas sus listas. Programas históricos deben mostrar su año. No asignar posiciones desconocidas como cero ni inferirlas del logotipo o de una etiqueta ideológica. Cada posición de programa necesita referencia precisa y fuente.

La consulta del Registro de Partidos Políticos del 7 de octubre de 2026 devuelve 4.027 inscripciones con fecha hasta ese día. Una inscripción no acredita actividad actual, presencia territorial real ni candidatura. Presentar las candidaturas confirmadas primero y el resto como «Otros partidos», nunca como «partidos que no se presentan» sin prueba. Conservar la fecha y alcance de cada nueva consulta. Las webs y marcas requieren verificación individual: dominios antiguos pueden caducar o redirigir a contenidos ajenos. Cuando no existe un recurso gráfico contrastado, mostrar identificación textual y estado pendiente; no inventar un icono oficial.

Logotipos: usar recursos publicados por la organización, conservar procedencia y formato. Preferir SVG genuinos; no redibujar imitaciones ni convertir automáticamente una imagen en un vector ficticio. Retratos: ficha institucional individual, crédito y procedencia; no fotos de actos ni caras generadas. Si falta un retrato, mostrar iniciales y señalarlo.

## Biografías, actuaciones y controversias

Registrar nombre completo, nacimiento cuando esté acreditado, formación e instituciones, carrera profesional y cargos con fechas y fuentes. Ausencia de un dato no equivale a ausencia del hecho. La edad exacta se calcula con la fecha local y solo si hay día, mes y año; no mostrar un intervalo inventado. Para fallecidos mostrar el fallecimiento. Diferenciar el titular de un departamento, su partido, su vinculación electoral y la responsabilidad de una actuación.

Priorizar la ficha individual institucional. Wikipedia puede completar datos biográficos ausentes, identificándola como fuente enciclopédica y enlazando el artículo concreto. Ante contradicciones no copiar automáticamente: contrastar otra fuente individual, documentar la elección y conservar la precisión real. Ejemplo revisado: el Congreso sitúa el nacimiento de Margarita Robles el 10 de noviembre de 1956, mientras una ficha de La Moncloa recoge 1957. La ficha personal utiliza el dato individual del Congreso. No inferir un estudio por asistir a un curso ni atribuir un título de máster a formación breve.

Las biografías institucionales describen la trayectoria pero no bastan para una evaluación. Separar actuaciones, críticas políticas, investigaciones, acusaciones, sentencias y resoluciones firmes; indicar fecha, órgano, estado procesal y respuesta documentada cuando corresponda. Una reprobación parlamentaria no es una condena. No atribuir culpabilidad por asociación. No denominar «éxito» a un resultado sin criterio y evidencia. Mantener fuentes por afirmación y fecha de revisión; no copiar artículos extensos.

## Gobiernos y Congreso

Ordenar gobiernos del más reciente al más antiguo. Distinguir legislatura, mandato presidencial y remodelación del gabinete. Intervalos de composición `[desde, hasta)` con fechas ISO: el día de relevo corresponde a la composición nueva. Diferenciar anuncio, publicación, toma de posesión y cese; citar el criterio usado. Gobierno en funciones sigue existiendo, no generar huecos artificiales. Descripciones históricas de La Moncloa son el punto de partida; contrastar límites con BOE antes de incorporar nombramientos individuales.

Organigrama: Presidencia, vicepresidencias, departamentos ministeriales y sus órganos superiores/directivos. No dibujar a todos los ministros como subordinados de una vicepresidencia. Segundo/tercer nivel requieren norma de estructura y nombramientos; no inventar relaciones. La vista temporal cambia en fechas documentadas, no interpola personas. Indicar cobertura cuando faltan biografías, retratos o niveles.

«Cargos e historia» es una sección independiente. Las sucesiones conocidas se derivan de las composiciones conservadas, y su último intervalo se identifica como «última composición», sin afirmar que sigue vigente. Los cargos pendientes tienen una fuente institucional y ningún titular inventado. La ampliación de órganos usa el Real Decreto 1009/2023, texto consolidado actualizado el 29 de julio de 2026 (BOE-A-2023-24842), y enlaza su artículo: documenta la existencia del órgano, no su historial de titulares. Al interpretar nombres, distinguir Cultura de Agricultura y un ministro de una vicepresidencia con responsabilidades sobre ese ámbito.

El archivo permite búsqueda y filtro de vinculación acreditada, combinados con orden alfabético, actividad reciente, actividad antigua o rango de cargo. La antigüedad se calcula a partir de trayectorias y composiciones documentadas, no de la edad de la persona. Una fecha desconocida queda al final. Personas y partidos se cargan por lotes al acercarse al final de la pantalla; el buscador consulta el catálogo completo, no solo el lote visible.

El hemiciclo identifica cámara, elección/fecha, partidos o coaliciones y fuente; sus escaños deben sumar el tamaño de la cámara de ese periodo. La distribución por candidatura electoral no equivale al grupo parlamentario posterior ni a apoyos del Gobierno. La posición de cada punto es esquemática, no el asiento físico de un diputado. No trasladar cifras de una legislatura a otra.

## Estado, privacidad y publicación

Respuestas y preferencias permanecen en memoria; no hay guardado, exportación ni recogida estadística. No añadir autenticación o persistencia sin nueva instrucción. El favicon canónico está en `/favicon.svg` y debe publicarse en la raíz del sitio.

Verificar cálculo, cobertura de contextos, referencias cruzadas, intervalos temporales y suma de escaños. Comprobar también interfaz, teclado, móvil, reducción de movimiento y temas. Construir y ejecutar las pruebas antes de publicar. Mantener fuentes y límites de cobertura visibles, sin llenar el cuestionario de texto ornamental.

## Ampliación parlamentaria y navegación

- Herramientas de incorporación en `Políticos/herramientas/`; informes, conservación e incidencias en `Políticos/revisiones/`. Ambas carpetas están reservadas y quedan fuera del catálogo web. Lo mismo se aplica a `Partidos/herramientas/` y `Partidos/revisiones/`.
- `institucional.json` conserva cámara, identificador de la consulta, fuente individual, fecha y huella del documento. En Congreso el código parlamentario depende de la legislatura: nunca tratarlo como un ID personal estable. Senado utiliza su ID histórico. Una persona que aparece en varias fuentes mantiene una sola carpeta e IDs anteriores en `legacyIds`.
- `biografia-institucional.json` es una lista de `{text, source}` con información profesional pública. No copiar contactos, familia ni declaraciones patrimoniales. El resto de secciones conserva sus formatos. `birthNote` explica discrepancias de fechas en datos personales, con las fuentes enlazadas. No completar datos desconocidos por conjetura.
- Las fechas generales de una legislatura no son las fechas individuales de toma de posesión o baja. Indicar la precisión de lo documentado. La formación electoral del Congreso no demuestra militancia; los grupos parlamentarios del Senado tampoco.
- `resultados.json` en cada partido contiene elección, fecha, cámara, candidatura, votos, escaños y fuente. Las coaliciones electorales llevan identidad propia: no repartir sus cifras entre integrantes. `documentacion.json` contiene enlaces públicos con título, tipo, fecha y formato cuando consten. Una inscripción no prueba actividad actual; un dominio antiguo puede haber cambiado de propietario. Un nombre reutilizado no autoriza copiar historia ni logotipo de otra entidad.
- `src/app/navigation.ts` gobierna las rutas `#/archivo/person/<id>`, `#/partidos/party/<id>`, `#/cargos/office/<id>` y `#/gobiernos/government/<id>`. Toda apertura interna debe pasar por ese historial central. Nunca sustituirlo por un estado local sin actualizar la dirección. Conservar filtros y posición al retroceder. Los enlaces de salto al contenido no cambian la ruta.
- En fichas personales, «Relaciones por cargo» muestra exclusivamente los periodos del propio titular. Las sucesiones completas pertenecen a la sección de cargos.


## Actividad y archivo histórico

Personas y partidos conservan todas sus fichas. El orden principal es actividad acreditada, actividad por confirmar y archivo histórico; el orden secundario elegido se aplica dentro de cada grupo. Los filtros permiten consultar los tres estados. No usar edad, ausencia de fotografía, inscripción registral ni fin de una legislatura como prueba de retirada. Un fallecimiento o una disolución documentados sí acreditan el estado histórico. La actividad parlamentaria inmediatamente anterior a una disolución acredita participación reciente, no un escaño vigente tras ella.

`actividad.json` en la carpeta propia conserva `{state, reason, checkedAt, sources}`. Estados: `active`, `historical`, `unknown`. Toda afirmación de actividad actual necesita fuentes individuales o institucionales y fecha de consulta. Una trayectoria cerrada no acredita retirada y queda por confirmar si no hay evidencia adicional. Una trayectoria con periodo abierto sin contraste reciente queda por confirmar. La ausencia de clasificación no elimina ninguna ficha.

## Senado

`Gobiernos/Senado/<ordinal romano> Legislatura/` conserva `composicion.json` y `fuentes.json`; la Constituyente tiene carpeta propia. `Gobiernos/herramientas/` y `Gobiernos/revisiones/` están reservadas para incorporación y auditoría. La navegación `#/senado/senate/<composición>` comparte el historial central y aparece bajo el desplegable Gobiernos centrales, junto a Gobierno y Congreso, como secciones independientes.

Consultar todas las legislaturas desde 1977 y cada ficha individual. `mandatos-senado.json` y `cargos-senado.json` pertenecen a la carpeta de cada persona. Conservar fechas individuales, órgano, función y enlace. La fecha de baja publicada por el Senado es inclusiva: el relevo se representa al día siguiente cuando corresponde. La fecha general de la legislatura nunca sustituye un alta individual desconocida. El cronograma incorpora cambios documentados tanto de cargos como de mandatos del Pleno.

La jerarquía distingue Presidencia, vicepresidencias y secretarías de la Mesa, portavoces de grupos y presidencias de comisión. Un portavoz de comisión no es un portavoz de grupo. Los cargos sin fecha de alta se conservan en un apartado aparte del último registro, con fecha de consulta, sin integrarlos en la cronología. Intervalos invertidos en la fuente se excluyen y documentan en el informe de incidencias, sin corregirlos por conjetura. El grupo de cada mandato corresponde a la última adscripción conservada en la ficha; no reconstruir cambios internos sin fechas acreditadas. El hemiciclo cuenta personas únicas con mandato acreditado en la fecha mostrada, no todos los participantes de una legislatura.

En la ficha personal, reunir todos los periodos propios en una única sección «Relaciones por cargo», ordenados por fecha; mostrar cargo y periodo una vez por entrada. Las sucesiones completas siguen perteneciendo a Cargos e historia. Los cambios del Senado no introducen autonomías sin una petición posterior.


## Congreso y autonomías

- `Gobiernos/Congreso/<ordinal romano> Legislatura/composicion.json` conserva la Mesa, mandatos, adscripciones a grupos y fuentes de cada periodo. La Constituyente usa `Legislatura Constituyente`. Herramientas y auditorías permanecen en sus subcarpetas reservadas; nunca mover contenido parlamentario a `src/`.
- El código de diputado depende de la legislatura. Enlazar con la identidad canónica de `Políticos/`; contrastar variantes de nombre con fuentes individuales y fecha de nacimiento, nunca fusionar por parecido automático. `identidades.json` documenta las quince correspondencias revisadas. No copiar familia ni contactos de la ficha pública.
- `mandatos-congreso.json`, `grupos-congreso.json` y `cargos-congreso.json` pertenecen a cada persona. La lectura combina los mandatos con la trayectoria anterior, evitando repetir los mandatos institucionales. Los cargos de la Mesa se reúnen con los demás cargos propios en una única sección de relaciones. La adscripción parlamentaria es una sección distinta de la afiliación partidista.
- En Congreso las altas son inclusivas y las bajas exclusivas: una sustitución efectiva ese día no cuenta dos personas, y la disolución cierra el Pleno. No cambiar el criterio inclusivo del Senado sin contrastar su fuente. Fechas desconocidas no se convierten en inicios de legislatura. El recorrido empieza en la fecha de constitución de la Mesa publicada por el Congreso (14 de julio de 1977 para la Constituyente), no se afirma que sea la primera sesión de la Cámara.
- Los cambios fechados de grupo, mandato, Mesa y fechas exactas de gabinete generan instantáneas. Las fechas mensuales de gabinete conservan esa precisión en la etiqueta y en la comparación; no inventar un nombramiento el día 1. La falta de adscripción fechada se muestra como tal, sin reutilizar la última adscripción para épocas anteriores.
- El hemiciclo es un diagrama de personas únicas, agrupadas para lectura. **No asignar números de asiento físico por orden alfabético, tamaño de grupo ni candidatura.** `physicalSeating` registra la fuente pendiente y la fecha de consulta. Solo incorporar un plano real cuando haya posiciones fechadas y acreditadas. Los excesos temporales del inventario histórico se conservan y señalan; las posiciones sin mandato acreditado no se presentan como vacantes verificadas.
- `#/congreso/congress/<composición>` y `#/autonomias/autonomy/<territorio:sección>` usan el historial central. Abrir una persona desde el Congreso conserva primero la composición que se estaba viendo, incluidos los pasos reproducidos. Mantener búsqueda y filtros al retroceder.
- `Gobiernos/Autonomías/territorios.json` contiene las 17 comunidades y las dos ciudades autónomas, con IDs estables sin tildes. El menú distingue Gobierno y Parlamento; Madrid, Ceuta y Melilla usan Asamblea. Cataluña y Madrid están documentadas; las demás rutas siguen pendientes y no deben mostrar datos de otro territorio.

## Madrid y navegación lateral

- Madrid sigue el mismo patrón de carpetas regionales. Las dos legislaturas de 2003 son VI y VII, con IDs distintos. Las etiquetas con `/` se escriben con `y` en el nombre de carpeta para evitar rutas accidentales. Los IDs siguen estables.
- `mandatos-madrid.json`, `cargos-madrid.json`, `grupos-madrid.json` y `comisiones-madrid.json` pertenecen a la persona. El lector virtual debe admitir esos nombres y las imágenes `retrato-madrid.jpg`; crear archivos sin registrarlos en el lector impide mostrarlos en la web.
- No deducir militancia a partir del grupo ni retirada a partir de la última legislatura. Conservar las discrepancias biográficas con ambas fuentes. No fusionar homónimos; las correspondencias explícitas se registran en `identidades.json`.
- Los cuadros históricos sin intervalo diario usan `archiveTerms` y aparecen separados de la composición simultánea. Un registro parlamentario que supera la capacidad de escaños usa `nominalOnly`: conservar nombres y fuentes sin inventar un reparto. Las anomalías del CSV y los documentos contrastados quedan en `fuentes/`.
- La navegación lateral utiliza desplazamiento nativo con rueda, tacto y teclado, con la barra visual oculta. Los indicadores de continuación y el degradado aparecen únicamente cuando queda contenido en esa dirección. La cabecera y la apariencia permanecen fuera del área desplazable. Respetar la reducción de movimiento.

## Cataluña y panel parlamentario

- Guardar cada composición en `Gobiernos/Autonomías/<territorio>/Gobierno/<año> <etapa>/composicion.json` o `Parlamento/<año> <legislatura>/composicion.json`. Los IDs no cambian con los textos de presentación. `identidades.json` registra las variantes personales contrastadas; los informes pertenecen a `Gobiernos/revisiones/` y las herramientas a `Gobiernos/herramientas/`. Mantener contenido fuera de `src/`.
- El DT02 del Parlament documenta los cuadros históricos del Govern desde 1977. `Gobierno/transcripcion.json` conserva la transcripción, excepciones y discrepancias. No convertir el límite de un cuadro en cese individual: `endBasis` diferencia cese publicado de siguiente composición. Distinguir nombramiento, toma de posesión, suplencia y presidente electo. La sustitución de la presidencia en 2020 no acredita una investidura nueva. Conservar y explicar contradicciones de la fuente.
- Las fichas del Parlament enlazan por `p_codi`; contrastar la persona con el catálogo existente antes de crear carpeta. `mandatos-catalunya.json`, `grupos-catalunya.json` y `cargos-catalunya.json` pertenecen a cada persona. Regenerar esos documentos sin acumular versiones. Todos sus cargos propios se reúnen en una sola sección de relaciones. La afiliación procede únicamente del campo partidista o de otra fuente expresa, nunca del grupo.
- Respetar el registro conjunto XIII–XIV publicado por la Cámara. Altas inclusivas y bajas exclusivas en este catálogo, documentando límites. El registro vigente sin fechas individuales usa `currentOnly` y se representa exclusivamente en `checkedAt`; no proyectarlo hacia 2024. No inventar una cronología nominal actual donde la fuente solo ofrece una instantánea.
- Fotos personales identificadas, preferentemente institucionales de la etapa. La imagen genérica de la Cámara no es un retrato. Commons requiere autor, licencia y enlace al archivo. Los recursos previos se conservan; las ausencias y errores quedan en el informe. No publicar biografías completas copiadas ni datos de contacto.
- El panel de hemiciclo es común a las tres cámaras. El visor ocupa todo el ancho y, debajo, los filtros compactos comparten una fila con la ficha breve (foto, nombre, circunscripción y afiliación documentada), sin scroll interno: ningún cambio de nombre o foto debe mover las posiciones. Mantener zoom, arrastre, teclado y reducción de movimiento. La rueda amplía alrededor del puntero; al reducir desde el 100 % deja desplazarse la página. No confundir candidatura, grupo y militancia ni proyectar afiliaciones actuales sobre fechas históricas. El filtro combina varios grupos por unión; el contador muestra coincidencias / total. Mantener selector horizontal de legislaturas tanto en biblioteca como en cronología.
- Rutas autonómicas: `#/autonomias/autonomy/<territorio:sección:instantánea>`. Antes de abrir una persona, conservar la fecha que se estaba viendo. Atrás y Adelante deben recuperar esa composición; no usar cambios locales que omitan el historial.
