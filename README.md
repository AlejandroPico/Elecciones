# Elecciones

Proyecto personal de Alejandro Pico Perez. Versión 0.35.0 · 20 de octubre de 2026.

La revisión electoral incorpora treinta anuncios y acuerdos documentados, diferenciados de las listas proclamadas. Veintitrés documentos se descargan desde el propio sitio: quince antecedentes de julio de 2023, Podemos 2019, cuatro documentos políticos generales, la propuesta permanente de Escaños en Blanco y dos programas autonómicos (SALF Castilla y León 2026 y Drago Canarias 2023). Se conservan originales, procedencia y huellas; las copias de prensa se identifican. [Alcance y fuentes](Elecciones/Generales%20Noviembre%202026/investigacion/README.md). Las papeletas definitivas y los programas específicos del 29N siguen pendientes de incorporar; no se inventan afinidades a partir de documentos antiguos.

El cuestionario permite elegir entre 40 temas, agrupados en seis bloques visuales. Sortea diez preguntas por tema y conserva el sorteo durante la visita, hasta un máximo de 400. Las tarjetas mantienen cinco respuestas, omisión, importancia 1/2/3 y avance tras tres segundos. «Mi perfil» puede consultarse desde la primera respuesta: muestra coincidencia documental, cobertura, comparación parcial por tema, las coordenadas de los indicadores definidos y el desglose con fuentes. Se puede reanudar y cambiar de temas sin perder las respuestas; al recargar se comienza de nuevo. [Método, configuración y límites del sistema experimental](Cuestionario/README.md#cuestionario-por-temas--18-de-octubre-de-2026).


## Revisión del perfil · 20 de octubre de 2026

El gráfico personal que cruzaba dos preguntas se ha retirado: no resumía un tema ni la ideología de sus partidos. Perfil y coordenadas documentales comparten ahora índices fijos y un desglose de sus indicadores. Se incorpora Control del Gobierno, con dos dimensiones operativas distintas. Una media ponderada puede producir valores intermedios; no se introduce dispersión artificial para separar partidos que respaldan las mismas medidas.

La [revisión reproducible del modelo](Cuestionario/Revisión%20del%20modelo.txt) documenta la limitación estructural: 6.079 de 128.942 cruces pregunta/partido tienen posición con evidencia, y solo 245 formulaciones tienen posiciones de al menos dos organizaciones. El +2 codifica respaldo de una propuesta, no extremismo. Los 40 temas no equivalen a 40 ejes ideológicos terminados: hay 124 formulaciones asignadas a índices y 5.737 pendientes. No se presenta esta corrección como un test completo o validado.

La comparación distingue decisiones comparables, cobertura y coincidencia parcial. Si solo se comparan dos de treinta, el porcentaje no se publica como afinidad global; se explica su denominador y se muestran límites matemáticos para las posiciones ausentes. Las fuentes autonómicas no se proyectan a índices nacionales. La barra separa dos intensidades de rojo y dos de verde, manteniendo gris para neutral y grosor por importancia.

La auditoría se regenera con `python Cuestionario/herramientas/auditar-perfil.py`; CI comprueba su vigencia con `--check`. La matriz común de posiciones y la asignación del resto del banco siguen pendientes de investigación y contraste documental.

## Claridad del cuestionario · 19 de octubre de 2026

«Nueva encuesta», «Continuar encuesta» y «Coordenadas políticas» forman el submenú del cuestionario. Continuar se habilita cuando se inicia una muestra y recupera sus preguntas pendientes, incluso después de volver al selector de temas.

«Mi perfil» destaca un mapa de dos ejes con marca **Tú**, doble aro animado y siglas de partidos. La vista «Por propuestas» cruza dos respuestas de un mismo tema con las posiciones documentadas sobre esas mismas preguntas. La pareja inicial prioriza cobertura común, sin depender de las respuestas ni de la afinidad con un partido; se puede cambiar. «Ejes temáticos» mantiene los índices y signos documentados de los ocho mapas. Un eje pendiente no se rellena con cero y los partidos coincidentes comparten marcador. Cada posición ofrece cálculo y documentos de origen. La comparación horizontal de coincidencia y cobertura queda como información secundaria, identificada como tal.

Las 5.861 preguntas tienen ampliaciones con reformulación, pasaje de la propuesta de origen, explicación de conceptos, ejemplo y distinciones. Se combinan el enunciado individual con 155 perfiles específicos, 40 perfiles de tema y 159 definiciones. Se aclaran individualmente 26 referencias como «ese fondo». Los ejemplos no añaden compromisos a los programas ni describen necesariamente la ley vigente. La generación verifica todos los IDs, cifras, negaciones y ámbitos, pero no equivale a una validación humana independiente de cada texto. Las correcciones individuales se mantienen por ID. [Contenido, revisión y mantenimiento](Cuestionario/explicaciones/README.md).

## Investigación del cuestionario · 18 de octubre de 2026

El [Resumen Preguntas](Cuestionario/Resumen%20Preguntas.txt) reúne **22 organizaciones, 5.861 formulaciones, 109 conceptos y 40 categorías**. La última tanda incorpora Soria ¡Ya!, Teruel Existe, Adelante Andalucía, Drago Canarias, democracia21 y Coalición Canaria, con 780 formulaciones nuevas. Los 23 documentos analizados distinguen su convocatoria y ámbito: no se extrapolan los programas autonómicos a posiciones nacionales ni se presentan antecedentes como programas actuales. Los originales y las transcripciones conservan procedencia, huellas y localizadores; las discrepancias internas quedan sin puntuación. Sumar incorpora ahora su programa común de 2023, con 443 formulaciones nuevas, conservando todas las anteriores. Movimiento Sumar aparece vinculado al Frente Amplio en el directorio, con acceso a su ficha y al antecedente de 2023; el programa de esa coalición histórica no se atribuye al proyecto de 2026. Es un banco documental para posterior revisión y reducción, no la longitud de una encuesta individual. [Recuento por categorías](Cuestionario/Resumen%20Categorías.txt) y [criterios de edición](Cuestionario/README.md).

La vista inicial de «Cuestionario → Coordenadas políticas» utilizaba ocho mapas. Desde la revisión del 20 de octubre, comparte con Mi perfil nueve índices documentales fijos y su auditoría de cobertura. Cada eje publica sus indicadores y signos; la selección de partido permite consultar cálculo, cobertura y fuentes originales en su formato real. Las ausencias no son neutralidad ni centro del gráfico. Los puntos coincidentes no se desplazan y el rango de indicadores faltantes se distingue de una probabilidad. La vista mezcla ediciones documentales explícitas: es independiente de la sesión personal y no acredita programas de una misma convocatoria actual.

El [Plan de agrupación y selección](Cuestionario/Plan%20de%20selección.txt) revisa 189 pares de preguntas y propone 16 equivalencias y 12 familias de variantes sin borrar originales. Conserva cifras, condiciones y decisiones independientes; no activa un cuestionario aleatorio. La auditoría identifica la comparación cruzada que aún falta antes de calcular afinidades. El plan se incluye en el resumen descargable y en «Cómo se calcula».

## Histórico de presidencias · 0.25

«Gobiernos centrales» conserva el gráfico de duración y los retratos de las siete presidencias. Las legislaturas y sus acontecimientos aparecen de más reciente a más antiguo; el selector de orden invierte ambos niveles. Búsqueda, presidencia, tipo, materia, año y legislatura se combinan. La lista carga progresivamente al desplazarse.

La ampliación contiene 200 acontecimientos desarrollados y 3.085 registros normativos del BOE, diferenciados como «Leyes y medidas». Los segundos proceden del título oficial y la fecha de publicación: no se presentan como análisis de impacto ni éxitos demostrados. Un mismo acontecimiento puede verse en varias etapas relacionadas, con un único registro canónico, sin multiplicar los casos ni transmitir culpabilidad. Se amplían Gürtel, Bárcenas, Roldán, CESID, Gescartera, crisis sociales, emergencias y causas de 2026, incluidas las posiciones de las defensas y los archivos.

## Legislaturas y mapa histórico · 0.23

Los selectores autonómicos muestran año y ordinal romano, sin nombres presidenciales. Gobierno y Parlamento comparten los ordinales institucionales; los relevos del Ejecutivo permanecen dentro de la misma legislatura. Se conservan XIII–XIV en Cataluña, la VI de Madrid sin nueva investidura, el periodo foral navarro y las etapas provisionales sin inventarles un ordinal.

El mapa incorpora navegación por cambios documentados entre 1977 y 2026: flechas, deslizador y vuelta a la instantánea actual. Se actualizan color, nombre y retrato, conservando el realce conjunto de las comunidades y sus límites provinciales. Sus enlaces abren el Gobierno de la fecha consultada y el historial del navegador recupera la fecha del mapa. Los vacíos se representan en gris; la fuente del mandato no acredita militancia diaria.

## Investigación de presidencias centrales · 17 de octubre de 2026

La investigación y sus fuentes permanecen en [Gobiernos/investigacion/presidencias-centrales](Gobiernos/investigacion/presidencias-centrales/). El [dossier](Gobiernos/investigacion/presidencias-centrales/cronologia.md) desarrolla los acontecimientos editoriales. El catálogo normativo conserva procedencia, consultas reproducibles, exclusiones y relaciones con el índice de etapas. El registro de 2.657 semanas identifica entradas y lagunas: no acredita una revisión hemerográfica exhaustiva de cincuenta años. Los [criterios](Gobiernos/investigacion/presidencias-centrales/investigacion.md) y [pendientes](Gobiernos/investigacion/presidencias-centrales/pendientes.md) distinguen esta cobertura del análisis profundo todavía necesario.


## Extremadura e Illes Balears · 0.22

La ampliación revisa 1.008 identidades y añade 903 fichas, conservando las anteriores. Los integrantes actuales de ambos gobiernos y parlamentos tienen fotografía contrastada. Las dos comunidades incorporan Gobierno y Parlamento con la presentación compartida, Mesas, cronología, hemiciclo, filtros y fichas enlazadas. Extremadura comprende doce legislaturas y doce nombramientos presidenciales; Illes Balears, once legislaturas y trece nombramientos. Las composiciones actuales identifican 65 y 59 diputados, respectivamente, y doce integrantes de cada Ejecutivo. Los archivos electorales históricos se distinguen de los relevos y de las composiciones vigentes, sin atribuir asientos físicos ni fechas individuales desconocidas. Fuentes, correcciones nominales y límites de cobertura: [Extremadura](Gobiernos/Autonomías/Extremadura/README.md) e [Illes Balears](Gobiernos/Autonomías/Illes%20Balears/README.md).

## Región de Murcia · 0.21

Murcia incorpora Gobierno y Asamblea Regional: once legislaturas parlamentarias desde 1983 y dieciséis etapas presidenciales desde 1982. Conserva la presentación, la navegación histórica, las Mesas, el hemiciclo y los filtros compartidos. La composición vigente distingue 45 diputados y recoge la remodelación del Ejecutivo de mayo de 2026. La revisión abarca 404 identidades y añade 350 fichas. Los datos y retratos se guardan en `Políticos/`, conservando los identificadores anteriores. Fuentes, correcciones y límites del archivo: [Región de Murcia](Gobiernos/Autonomías/Región%20de%20Murcia/README.md).

## La Rioja · 0.20

La Rioja incorpora Gobierno y Parlamento con once legislaturas desde 1983 y catorce etapas presidenciales desde 1982. Mesas, cronología, hemiciclo, filtros y fichas mantienen la presentación compartida. La primera legislatura tiene 35 escaños; desde la segunda son 33. Los cuadros de Transparencia documentan 141 registros históricos de consejerías y vicepresidencias con sus fechas individuales. Fuentes, correcciones y límites de cobertura: [La Rioja](Gobiernos/Autonomías/La%20Rioja/README.md).

## Galicia · 0.19

Galicia incorpora doce legislaturas parlamentarias desde 1981 y catorce etapas presidenciales desde 1982, con Mesas, cronología, hemiciclo y fichas enlazadas. Se revisan 621 identidades y se añaden 505 personas conservando las 11.556 anteriores. Los 75 parlamentarios y los trece integrantes del Gobierno vigente tienen retrato documentado.

Los hemiciclos históricos distinguen los 71 escaños de I y II de los 75 posteriores. La IX utiliza la proclamación electoral de 2012 como referencia explícita; las demás relaciones nominales archivadas conservan los titulares y sus relevos por separado. Nueve decretos del DOG documentan gabinetes desde 1997; las consellerías anteriores se mantienen como archivo complementario con sus límites de precisión visibles. Fuentes, erratas y fotografías históricas aún ausentes: [Galicia](Gobiernos/Autonomías/Galicia/README.md).

## Asturias y Cantabria · 0.18

Ambas comunidades incorporan Gobierno y Parlamento con el selector de legislaturas, cronología, Mesas y hemiciclo compartidos. Asturias contiene doce legislaturas y trece etapas presidenciales; Cantabria, once y trece respectivamente. La ampliación revisa 666 identidades e incorpora 588 fichas nuevas, conservando todas las anteriores. Los gobiernos y parlamentos vigentes tienen retrato de todos sus integrantes.

Los hemiciclos históricos proceden de las relaciones de las bibliotecas parlamentarias: Asturias muestra los 45 titulares iniciales y conserva los relevos; Cantabria muestra sus cuadros nominales archivados, con 35 o 39 miembros según legislatura. No se atribuyen asientos físicos ni fechas individuales desconocidas. Las consejerías históricas se identifican como archivo complementario pendiente de contraste completo de sus relevos con los decretos originales. Véanse [Asturias](Gobiernos/Autonomías/Asturias/README.md) y [Cantabria](Gobiernos/Autonomías/Cantabria/README.md), incluidas las erratas resueltas y las ausencias fotográficas históricas.

País Vasco y Navarra incorporan sus gobiernos y parlamentos con la presentación compartida, cronología, filtros y fichas personales. Se consultan las trece legislaturas vascas desde 1980 y las doce etapas navarras desde 1979. Los gobiernos conservan catorce y quince marcos presidenciales, respectivamente, y los gabinetes vigentes incluyen dieciséis y catorce integrantes. Los listados nominales antiguos se distinguen de las composiciones fechadas y de las instantáneas actuales. Fuentes, cobertura y límites en [País Vasco](Gobiernos/Autonomías/País%20Vasco/README.md) y [Navarra](Gobiernos/Autonomías/Navarra/README.md).

Aragón incorpora las doce legislaturas de sus Cortes y catorce etapas presidenciales, con 470 fichas individuales consultadas. La composición archivada conserva 66 escaños en la I legislatura y 67 en las siguientes, separada del registro de sustituciones. El Gobierno vigente contiene diez titulares; las consejerías históricas proceden del organigrama oficial de Aragón Open Data. Se añaden 413 personas y 373 retratos sin retirar identidades anteriores. La revisión complementaria recupera otros dieciocho retratos, completa los cinco cargos de la primera Mesa y corrige tres intervalos contradictorios del catálogo histórico. Las 23 fotografías aún no localizadas conservan un informe individual. Véanse [cobertura y fuentes de Aragón](Gobiernos/Autonomías/Arag%C3%B3n/README.md).

«Gobiernos autonómicos» abre ahora un mapa propio y mantiene el desplegable lateral. Las 50 provincias y Ceuta y Melilla toman el color del partido de la presidencia de su comunidad o ciudad. Cada contorno permite consultar foto, nombre y nombramiento, con apertura del Gobierno autonómico y regreso mediante el historial. Los límites detallados proceden del IGN; Canarias utiliza una inserción y las ciudades se amplían. Los países vecinos se muestran atenuados. [Datos, cartografía y licencias](Gobiernos/Autonomías/Mapa/README.md).

Castilla-La Mancha y Castilla y León incorporan Gobierno y Cortes con la presentación compartida, cronología, filtros y fichas enlazadas. Se consultan las once legislaturas castellanomanchegas (553 fichas de legislatura) y las doce castellanas y leonesas (1.114 fichas), con 33 y 82 miembros en las composiciones vigentes. Los doce y quince nombramientos presidenciales se contrastan con el BOE y el dosier del Senado. Los gabinetes actuales se limitan a la fecha de consulta; los cuadros históricos conservan fuentes primarias y complementos enciclopédicos identificados, sin fingir una reconstrucción diaria completa. Cobertura e incidencias en los archivos de [Castilla-La Mancha](Gobiernos/Autonomías/Castilla-La%20Mancha/README.md) y [Castilla y León](Gobiernos/Autonomías/Castilla%20y%20León/README.md).

Andalucía incorpora dieciséis etapas presidenciales de la Junta y las trece legislaturas desde 1982, con 1.602 fichas parlamentarias consultadas y los cargos, grupos, comisiones y fuentes individuales. El Gobierno y los 109 diputados vigentes tienen retrato. La Mesa conserva sus relevos fechados, incluidos los representantes de grupos con voz y sin voto. Comparte navegación, cronología, organigrama y visor parlamentario con las demás comunidades. Las legislaturas históricas ofrecen la composición archivada por la Cámara, sin atribuirle una fecha diaria; el archivo nominal completo conserva también las sustituciones. Cobertura y límites en [el archivo andaluz](Gobiernos/Autonomías/Andalucía/README.md).

La Comunitat Valenciana incorpora el Consell y Les Corts desde 1983: catorce etapas presidenciales, once legislaturas y 669 fichas institucionales consultadas. La revisión complementaria fecha las carteras de las doce primeras etapas mediante 95 eventos contrastados del DOGV, incorpora 69 intervalos históricos de la Mesa y recupera 14 de los 18 retratos pendientes. El Consell actual y los 99 diputados vigentes tienen fotografía. Cada mandato, grupo, cargo, comisión y fuente vive en su carpeta correspondiente. Cobertura y límites en [el archivo valenciano](Gobiernos/Autonomías/Comunitat%20Valenciana/README.md).

Madrid incorpora Gobierno y Asamblea desde 1983, con trece legislaturas, catorce etapas del Ejecutivo y las fichas personales enlazadas. Comparte cronología, organigrama y visor parlamentario con Cataluña. Las fuentes históricas que no permiten reconstruir una composición diaria se presentan como archivo nominal, con sus limitaciones documentadas en `Gobiernos/Autonomías/Madrid/README.md`. El menú lateral permite recorrer las autonomías con rueda, tacto y teclado, sin barra visual y con indicación de contenido pendiente.

Cuestionario de 48 preguntas piloto, 8 temas y 16 ejes. Ficha centrada de esquinas rectas, respuestas sin cajetines, importancia y omisión. Cada pregunta permite ampliar su contexto. «Mi perfil» se actualiza con las respuestas. Al responder, una microbarra de tres segundos permite ajustar la importancia antes del avance automático. Cambiar la respuesta o la importancia no reinicia ese plazo; navegar cancela el avance pendiente. La última respuesta abre el perfil.

El favicon abre y cierra la barra lateral manteniendo su imagen. «Cuestionario» despliega «Consultar cuestionario», «Nueva encuesta» y «Coordenadas políticas». El control inferior de apariencia alterna automático, mañana, tarde y noche con texto e icono. El modo automático usa la hora del sistema. Se respeta la reducción de movimiento.

La barra inferior es fina, con nombre de tema y número de pregunta. El tramo activo muestra una línea continua con crecimiento suave; las preguntas siguen siendo navegables por separado. Los otros temas se compactan conservando sus respuestas: rojo para desacuerdo, verde para acuerdo, gris para neutral y el acento de la apariencia para omisión. El grosor representa la importancia.

**No existe guardado ni exportación de respuestas.** Respuestas, preferencias e importaciones solo viven en memoria; recargar empieza de nuevo. Se eliminan únicamente las dos claves locales de una versión anterior. No hay estadísticas centrales, autenticación ni recogida de respuestas.

## Organización

- `Elecciones/Generales Noviembre 2026/`: cuestionario, contextos, candidaturas y resultado del Congreso usado como referencia.
- `Políticos/<Nombre completo>/`: ficha, datos personales, formación, trayectoria, actuaciones, fuentes y retrato de cada persona.
- `Partidos/<Nombre completo>/`: ficha, historia, dirigentes, programas históricos, fuentes y logotipo.
- `Gobiernos/<legislatura>/`: composiciones y estructura documentada; `Gobiernos/Cargos/<cargo — departamento>/`: fichas de cargos y órganos.
- Cada dominio contiene su código en `interfaz/`. Cuestionario y perfil pertenecen a `Elecciones/interfaz/`; archivo, partidos y gobiernos a sus respectivas carpetas raíz.
- `src/app/`: interfaz común; `src/main.tsx` y `src/vite-env.d.ts`: arranque y tipos del entorno.

El catálogo descubre las carpetas al compilar. La presentación vertical solo muestra apartados con datos. No hay un segundo índice manual de nombres. Se entra directamente a la única convocatoria; el mosaico de elecciones sigue pendiente. Patrones, formatos, fuentes y reglas de migración en [PROTOCOLOS.md](PROTOCOLOS.md).

La primera revisión individual de 8 de octubre de 2026 repasa las 276 fichas existentes, reúne nueve duplicados y añade 33 dirigentes nacionales y autonómicos: 300 personas con retrato local identificado, 295 fechas de nacimiento completas y formación documentada en 292 fichas. Conserva todas las identidades anteriores mediante alias y todos sus recursos gráficos; el informe está en `Políticos/revisiones/2026-10-08/`. Cada carpeta contiene sus fuentes y `revision.json`, con correcciones y datos pendientes. Wikipedia complementa las fuentes institucionales con atribución expresa. No se inventan fechas completas, títulos académicos ni militancia; los historiales mantienen distinta cobertura y no constituyen un censo exhaustivo de España.

La ampliación parlamentaria incorpora las 3.023 identidades del archivo del Congreso y las 2.521 del Senado desde 1977. Tras reunir personas que aparecen en ambas cámaras, el catálogo contiene **5.114 personas y 5.108 retratos**. Las seis ausencias quedan identificadas en `Políticos/revisiones/2026-10-08-parlamento/informe.json`. Cada mandato del Congreso conserva alta, baja, circunscripción y candidatura. En el Senado se distinguen fechas personales del mandato y límites generales de la legislatura; no se sustituyen unas por otras. Se conservan las 300 fichas anteriores, los IDs alternativos y sus recursos. Las discrepancias biográficas se explican junto al dato y sus fuentes. La formación electoral acredita candidatura, no militancia actual.

«Archivo político» combina búsqueda, vinculación acreditada y orden aleatorio, por nombre, actividad más reciente, actividad más antigua o rango de cargo. El orden inicial cambia al entrar desde otra sección: Fisher–Yates con números de Web Crypto y rechazo del sobrante evita sesgos entre índices. Conserva la prioridad de actividad y permanece estable al filtrar, cargar más fichas o regresar desde una biografía. La búsqueda incluye nombres habituales y todos los cargos documentados. El filtro consulta cambios de partido y federaciones regionales; las fichas diferencian militancia, colaboración electoral e independencia documentada. Las tarjetas compactas muestran el nombre bajo el retrato y despliegan partido y cargos al pasar el ratón o enfocarlas con teclado. Carga más fichas al acercarse al final, sin botón adicional. La antigüedad procede de la actividad documentada, no de la edad.

«Partidos» reúne las 4.027 inscripciones que devuelve el [Registro de Partidos Políticos del Ministerio del Interior](https://servicio.mir.es/nfrontal/webpartido_politico.html) con fecha hasta el 7 de octubre de 2026, incluidas organizaciones regionales y municipales. Cada ficha conserva identidad registral, localidad y fuente. Inscripción no equivale a actividad actual ni a candidatura. Hay 260 logotipos documentados, 172 webs y 517 enlaces a documentación pública: programas, estatutos, historia, transparencia y organización. Se contrastan 484 identidades con fuentes adicionales y se descartan 22 coincidencias homónimas. Búsqueda, filtro territorial, cobertura y orden por escaños, votos, nombre o antigüedad. El orden inicial usa el resultado oficial del Congreso de 2023, conservando separadas las coaliciones y sus integrantes; los resultados desconocidos no se interpretan como cero. Fundación e inscripción son fechas distintas. Carga progresiva. Los recursos desconocidos permanecen pendientes, con identificación textual; no se inventan marcas ni se enlazan dominios antiguos reconvertidos. Las candidaturas confirmadas se presentan primero y el resto en «Otros partidos»; actualmente no se ha incorporado ninguna proclamación oficial de 2026.

Se conservan las presidencias de AP/PP desde 1979 y secretarías generales y gestoras del PSOE desde 1974, enlazadas a personas. Estas selecciones no reúnen todos los dirigentes desde la fundación ni todas las sustituciones temporales. Los programas están fechados por convocatoria y no alimentan la puntuación. Los de 2023 no se presentan como programas de 2026.

«Gobiernos» ofrece 16 legislaturas y 72 composiciones desde julio de 1977, con cronología interactiva, organigrama y fichas vinculadas. La precisión antigua puede ser mensual; no equivale a un registro diario. El segundo y tercer nivel incluyen una instantánea de tres órganos de Defensa consultada el 7 de octubre de 2026. Los demás departamentos siguen pendientes. El Congreso tiene ahora una sección propia, con mandatos individuales y adscripciones fechadas desde 1977.

«Cargos e historia» tiene su propia entrada y 251 fichas de cargos y órganos: Gobierno, Cortes, secretarías de Estado, subsecretarías, secretarías generales, direcciones generales y otras instituciones. Las sucesiones ministeriales se derivan de las composiciones conservadas; los cargos sin historia indican que su ficha está pendiente. La estructura de órganos ministeriales usa el [Real Decreto 1009/2023](https://www.boe.es/buscar/act.php?id=BOE-A-2023-24842), actualizado el 29 de julio de 2026. Esa norma acredita órganos, no inventa biografías ni históricos de titulares.

Atrás y Adelante del navegador recorren secciones, fichas de personas, partidos, cargos y composiciones de gobierno. Cada ficha tiene una dirección propia que permite recargarla o compartirla. Al volver al directorio se mantienen los filtros y la carga progresiva. La ficha personal solo reúne sus propios cargos y periodos; el historial completo de titulares pertenece a «Cargos e historia».

## Desarrollo y publicación

Node.js 22 o superior y pnpm 11.

```sh
pnpm install
pnpm dev
pnpm test
pnpm build
pnpm preview
```

React, TypeScript y Vite. GitHub Actions valida y publica main en [la web](https://alejandropico.github.io/Elecciones/). Partidos, archivo y gobiernos se cargan al abrir sus secciones. Rutas relativas compatibles con `/Elecciones/`. `favicon.svg` es el icono canónico en la raíz del repositorio y se copia a la raíz del sitio al construir.

Las pruebas cubren cálculo, importancia, omisiones, importaciones, navegación, avance de tres segundos, contexto, ordenación, identidad registral, relaciones, conservación de identidades, apartados ausentes, cumpleaños, relevos y suma de escaños. La revisión visual verifica escritorio, teclado, carga progresiva, recursos gráficos y ausencia de desbordamientos móviles.

- [Preguntas, posiciones y fuentes](docs/catalogo.md).
- [Estadísticas para una fase futura](docs/estadisticas.md).
- [Archivo político y cobertura](docs/archivo-politico.md).

[Portfolio](https://alejandropico.github.io/Portfolio/) · [Repositorio](https://github.com/AlejandroPico/Elecciones)

## Actividad y Senado

Personas y partidos priorizan actividad documentada, después los casos por confirmar y finalmente el archivo histórico. La prioridad se conserva con cualquier orden secundario y con los filtros. No se utiliza la edad, la ausencia de fotografía ni la inscripción registral para inferir retirada o actividad. Una disolución de las Cámaras no convierte automáticamente a sus integrantes en retirados. Los criterios contrastados se conservan en `actividad.json` junto a cada ficha, con fuentes y fecha; las biografías explican su alcance.

«Gobiernos centrales» despliega «Gobierno», «Congreso» y «Senado». El Senado ofrece las 16 legislaturas desde 1977, con Presidencia, vicepresidencias, secretarías de la Mesa, portavoces de grupos, presidencias de comisión y mandatos individuales. Las composiciones se guardan en `Gobiernos/Senado/<legislatura>/`, sus herramientas en `Gobiernos/herramientas/` y sus informes en `Gobiernos/revisiones/`. `mandatos-senado.json` y `cargos-senado.json` pertenecen a la carpeta de cada persona. El historial del navegador conserva el punto elegido.

La cronología utiliza altas y bajas individuales, con baja inclusiva. No inventa fechas de cargo. El Pleno agrupa la última adscripción publicada para cada mandato; no reconstruye traslados internos sin fechas. La XV legislatura se representa antes de su disolución. Todos los cargos propios de una persona se reúnen en un único apartado de relaciones, incluidos los cargos del Senado.


## Congreso y menú autonómico · 0.8

El Congreso reúne 6.323 mandatos de las 16 legislaturas desde la Constituyente, 125 grupos parlamentarios y 6.547 adscripciones fechadas. Cada posición del hemiciclo identifica al diputado, grupo, circunscripción y periodo, con enlace a su ficha y a la fuente oficial. Incluye búsqueda, filtro de grupo, legislatura, etapa del Ejecutivo, cronología y reproducción. El último Pleno documentado es el del 5 de octubre de 2026; no se confunde con la Diputación Permanente tras la disolución.

La distribución es **esquemática**, no un plano de asientos físicos. El plano público del Congreso muestra actualmente el aviso de disolución y no aporta matrices históricas de ubicaciones. No se inventan números de asiento. Las fechas individuales pueden dejar posiciones sin mandato acreditado; se indican expresamente. La III legislatura contiene coincidencias temporales de hasta 352 mandatos en la fuente: se conservan y señalan, sin recortar personas para forzar una suma. Las fechas de pertenencia a un grupo no acreditan militancia en un partido.

`Gobiernos/Congreso/<ordinal> Legislatura/` contiene composiciones y fuentes. La carpeta Constituyente se llama `Legislatura Constituyente`. En cada carpeta de `Políticos/` están `mandatos-congreso.json`, `grupos-congreso.json` y, cuando corresponde, `cargos-congreso.json`. Se contrastaron quince mandatos con variantes de nombre y fechas de nacimiento coincidentes en dos fichas oficiales; la revisión se conserva en `Gobiernos/revisiones/2026-10-08-congreso/`. Los cargos de la Mesa se integran en la única sección personal «Relaciones por cargo».

«Gobiernos autonómicos» ofrece las 17 comunidades y Ceuta y Melilla, con Gobierno y Parlamento (Asamblea en las ciudades). Cataluña, Madrid, la Comunitat Valenciana, Andalucía, Canarias, Ceuta y Melilla tienen contenido documentado; los demás territorios conservan sus rutas pendientes. «Cargos e historia» conserva su entrada independiente. El historial permite volver desde una ficha al punto parlamentario que se estaba consultando.

## Hemiciclos y Cataluña · 0.9

Congreso, Senado y Parlament comparten un visor de ancho completo: seleccionar una persona no desplaza el diagrama. Debajo se reúnen los filtros compactos y una ficha breve sin scroll interno. Los escaños se dibujan como butacas orientadas sobre filas curvas. El visor permanece fijo, sin zoom ni arrastre, con consulta al pasar el puntero, recorrido con teclado, búsqueda y selección simultánea de grupos. El contador muestra las coincidencias sobre el total documentado. La Mesa queda bajo el hemiciclo. Gobierno, Congreso y Senado mantienen el selector horizontal de legislaturas en ambas vistas, sin un segundo desplegable de legislatura. La fila no muestra barras de scroll: admite arrastre con el ratón y desplazamiento táctil nativo.

El archivo de Cataluña consulta las **1.073 fichas individuales** disponibles en el Parlament e incorpora **14 registros de legislaturas** desde 1980 y **15 etapas del Govern** desde el gobierno provisional de 1977. El Parlament publica un registro conjunto de XIII y XIV: se conserva esa cobertura, sin dividirla por conjetura. Cada periodo guarda mandatos, Mesa, grupos o competencias y sus fuentes en `Gobiernos/Autonomías/Cataluña/`. El Govern procede del dossier institucional DT02, con nombramientos y ceses documentados, incluidas las sustituciones y el relevo de Derechos Sociales de julio de 2026. Los límites de cuadro sin cese individual se identifican expresamente. Los cambios de 2017–2018 distinguen nombramiento y toma de posesión.

La XV legislatura catalana se muestra como registro nominal vigente consultado el **8 de octubre de 2026**, con 135 personas. No se atribuye esa lista a fechas anteriores sin registros fechados. Los históricos conservan altas, bajas y cambios de adscripción publicados; un grupo parlamentario no acredita militancia. Los nuevos datos personales, retratos y cargos propios viven en cada carpeta de `Políticos/`; se conservan identidades anteriores y se contrastan variantes nominales. Los retratos de Commons incluyen autor y licencia. La revisión de cobertura y las ausencias se conservan en `Gobiernos/revisiones/2026-10-08-catalunya/informe.json`.

Las legislaturas históricas I–XII de Andalucía incluyen el hemiciclo de la composición archivada por la Cámara, separado del registro de bajas. Es una referencia sin fecha diaria; se conserva el archivo completo de relevos. La VIII documenta 108 personas, sin inventar la restante.

## Canarias, Ceuta y Melilla · 0.14

Canarias incorpora las once legislaturas desde 1983 y quince nombramientos presidenciales, incluida la etapa provisional. Se consultaron las 577 fichas individuales de IV–XI; los cuadros nominales del Instituto Canario de Igualdad añaden I–III. El Pleno actual contiene 70 personas y su Mesa, cinco. Los históricos muestran la relación archivada y conservan los relevos aparte: las legislaturas V y IX identifican 59 y 58 posiciones respectivamente, sin inventar las restantes. Desde X, la capacidad es 70; antes, 60.

Cada ciudad autónoma incorpora ocho legislaturas desde 1995 y diez etapas presidenciales. Los históricos contienen los 25 electos de cada convocatoria de 1995–2019; la composición vigente de cada Asamblea contiene 25 personas y tres miembros de la Mesa. Los resultados electorales no reconstruyen los cambios internos de todo el mandato. El esquema identifica personas y candidaturas, con los mismos filtros y consulta de fichas que las otras cámaras.

Los organigramas vigentes reúnen 13 integrantes en Canarias, ocho en Ceuta y nueve documentados en Melilla, todos con retrato. Se contrasta la reorganización ceutí de 2025 y los relevos melillenses de 2023, 2024 y julio de 2026: se incorpora Fomento Universitario, se corrigen las vicepresidencias y competencias y se excluyen del gabinete vigente los titulares cesados. Las presidencias históricas están documentadas; las consejerías antiguas conservan los nombramientos y cuadros localizados como archivo separado, con sus límites de precisión. No se presenta ese archivo como una cronología exhaustiva de todos los gabinetes ni se proyectan las listas actuales sobre 2023.

Los datos y notas de cobertura residen en `Gobiernos/Autonomías/{Canarias,Ceuta,Melilla}/`; los retratos, mandatos, adscripciones y cargos propios, en cada carpeta de `Políticos/`. Los microdatos de Interior se contrastan en una copia pública con huella Git; solo se conservan nombres, candidaturas y cargos, sin DNI ni contactos. Véanse los README regionales y el informe de revisión de 12 de octubre de 2026.
