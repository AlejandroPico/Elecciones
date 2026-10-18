# Cuestionario: propuestas y preguntas

[Resumen Preguntas.txt](Resumen%20Preguntas.txt) es el documento unificado de **PP, PSOE, Vox, ERC, Junts, EH Bildu, PNV, BNG, PACMA, Escaños en Blanco y Frente Obrero**. Agrupa decisiones por conceptos, aunque los documentos utilicen títulos diferentes. Reúne nueve programas de las generales de julio de 2023, un programa político general de Frente Obrero y el artículo único permanente de Escaños en Blanco. No son once programas de una misma convocatoria. La vista previa «Cuestionario → Coordenadas políticas» permite explorar posiciones documentadas; el banco todavía no sustituye las preguntas ni las afinidades del test vigente.

## Archivos

- `analisis.json`: base editable y única fuente de verdad. Propuestas, preguntas, posiciones por partido, conceptos, reservas y evidencia.
- `Resumen Preguntas.txt`: documento legible generado desde la base, con índice, comparación por pregunta, cálculo e inventario de propuestas.
- `cobertura.json`: recuentos y límites verificables; se genera junto al texto.
- `Resumen Categorías.txt`: informe breve de categorías y recuentos, generado desde la misma base.
- `ejes.json`: selección editorial explícita de indicadores, signos y método de los ocho mapas temáticos. No contiene posiciones propias: referencia preguntas de la base.
- `coordenadas.json`: extracto generado para la vista previa, con sus posiciones y evidencia; nunca editarlo a mano.
- `interfaz/`: gráficos, consulta de cálculos, fuentes y pruebas del modelo.
- `herramientas/generar-resumen.py`: generador y verificador, sin dependencias externas.
- `agrupacion.json`: revisión editorial de relaciones entre IDs del banco, sin copiar preguntas ni posiciones. Fija la edición revisada mediante una huella canónica.
- `agrupacion-cobertura.json`: auditoría generada de equivalencias propuestas, referencias de posiciones y cobertura por categoría. Las unidades no agrupadas quedan implícitas.
- `Plan de selección.txt`: informe generado con criterios de reducción, cobertura pendiente y registro de los pares revisados. También se añade al final de `Resumen Preguntas.txt` y se descarga desde «Cómo se calcula».
- `herramientas/agrupacion.py` y `test_agrupacion.py`: compilación y pruebas de la revisión. No ejecutan un sorteo ni calculan afinidades de usuarios.

Los originales electorales permanecen en `Elecciones/Generales Julio 2023/programas/<partido>/`. Los documentos generales y permanentes consultados para la convocatoria activa se conservan en `Elecciones/Generales Noviembre 2026/programas/<partido>/`, identificando que no son programas específicos de esa elección. Esta carpeta raíz de investigación se crea por petición expresa del usuario. No duplicar originales ni mantener otro catálogo de preguntas editable en `docs` o bajo un partido.

## Cobertura y organización

Se conservan las 365 propuestas y las 678 preguntas del primer análisis del PP, incluidos sus identificadores, enunciados, reservas y evidencia. El programa de Vox tiene 381 medidas numeradas. El PSOE no ofrece esa numeración: **S0001–S1191 son anclas editoriales de viñetas**, no 1191 medidas oficiales. Los pasajes adicionales por página recogen propuestas con otras viñetas o en párrafos, especialmente vivienda y derechos. La cobertura de anclas no asegura el desdoblamiento exhaustivo de cada subcláusula.

`sourceUnits` identifica localizadores y páginas. `proposals` reúne unidades relacionadas y redacta un resumen propio; una agrupación puede proponer varias preguntas o quedar como contexto sin puntuar. Los pasajes adicionales pueden solaparse con otras unidades. Nunca sumarlos como evidencia independiente. `sourceUnits.extractedTextSha256` es una huella de control del fragmento extraído, no una cita literal ni una huella del archivo completo. La huella del original está en `sources.sha256`.

ERC, Junts, EH Bildu, PNV y BNG se inventarían por páginas físicas: **132, 151, 16, 52 y 68** respectivamente. Son anclas editoriales, no medidas oficiales numeradas ni promesas independientes. EH Bildu es un compromiso breve. ERC separa horizontes políticos y propuestas a las Cortes; las preguntas se centran en sus apartados operativos. Las introducciones y balances quedan clasificados como contexto. El inventario por página no garantiza haber desdoblado todas las subcláusulas.

PACMA y Frente Obrero se inventarían por sus 76 y 64 páginas físicas. Frente Obrero declara expresamente que su documento es político, no electoral. Escaños en Blanco se referencia por su artículo único en la línea 6 de la transcripción HTML local: no tiene páginas PDF ficticias. No se le atribuyen posiciones sectoriales ni se convierte la renuncia voluntaria a sus subvenciones en una prohibición para otros partidos. La esterilización propuesta por PACMA conserva la excepción veterinaria; una crítica genérica a la nuclear no acredita un calendario de cierre concreto.

`concepts` reúne preguntas de los once partidos por asunto. `questions.originConcepts` conserva las denominaciones editoriales de origen. Cada pregunta conserva un ID estable: su prefijo identifica dónde nació, **no qué partido es propietario de la pregunta**. Si una decisión coincide en alcance, población, instrumento y condiciones, compartir pregunta y añadir evidencia. Si cambia una condición relevante, mantener preguntas distintas dentro del mismo concepto. No igualar, por ejemplo, devolución y exención del IBI, jornadas de 32 y 35 horas o convenios autonómicos incondicionados y condicionados a ser más favorables. `unificationAudit` registra fusiones semánticas revisadas; la fusión literal no basta para resolver todos los solapamientos.

`selectionGroup` señala una familia temática que requiere revisar solapamientos. Es un aviso conservador, no una instrucción para seleccionar una sola pregunta de todo el tema ni un algoritmo de corrección ya aplicado. `legacySelectionGroup` conserva los avisos anteriores del PP. Antes de puntuar, decidir qué formulaciones representan la misma decisión y cuáles son dimensiones independientes.

Las **40 categorías serán los apartados del cuestionario**, no cuarenta encuestas completas. Las 3.673 formulaciones son un banco documental que se reducirá mediante agrupación de decisiones equivalentes. Se prevé una selección aleatoria equilibrada por categorías y conceptos, evitando repetir la misma decisión y manteniendo cobertura comparable entre partidos. No exige igual número de preguntas en todos los temas. `surveyDesign` documenta esta intención: todavía no hay algoritmo, cupos ni longitud definitiva implementados. No confundir el tamaño del banco con las preguntas que responderá cada persona.

La [primera propuesta de agrupación y selección](Plan%20de%20selección.txt) revisa **189 pares de 280 formulaciones**: 16 equivalencias propuestas, 102 variantes con diferencias, 69 pares de decisiones independientes y 2 opciones contrapuestas. Coincidencia léxica solo sirve para localizar candidatos; no los fusiona. Es una pasada acotada, no una revisión semántica exhaustiva del banco. Confirmar las 16 equivalencias evitaría 16 repeticiones, pero la reducción principal de una sesión vendrá de seleccionar decisiones. No se borran preguntas ni se alteran posiciones.

La revisión conserva diferencias como jornadas de 32/35 horas, educación universal/gratuita, IVA veterinario del 10/4 %, prórroga nuclear con/sin aval del CSN y devolución/exención de IBI. Ampliar y suprimir un servicio tampoco son negaciones exactas: una persona puede rechazar ambas opciones. No se invierten puntuaciones por semejanza de vocabulario.

Se proponen **12 familias de variantes** para evitar preguntar varios umbrales del mismo debate en una encuesta breve: jornada, cuotas bajo SMI, prórroga nuclear, IVA veterinario, horizonte climático, cálculo de pensiones, edad de jubilación, aforamientos, cobertura bucodental, parque público de alquiler, indemnización por despido y barreras electorales. La propuesta es elegir como máximo una variante de cada familia en esa modalidad. Esto no declara equivalentes las alternativas ni reúne sus posiciones. Las familias incluyen los alias equivalentes para impedir que otra redacción eluda el límite futuro; los solapamientos entre familias requieren revisión. No es una restricción activada en el test piloto.

La auditoría detecta **225 formulaciones con posiciones propuestas para dos o más partidos**. Reunir provisionalmente referencias de las equivalencias ofrece 239 unidades de ese tipo, todavía sin aprobación de producción. No hay un conjunto común para los once partidos; Turismo y hostelería aún no tiene una unidad con dos partidos documentados. Antes de una selección real, ampliar la comparación cruzada sobre las mismas decisiones, sin deducir posiciones por ideología. El artículo institucional de Escaños en Blanco no se fuerza a un programa sectorial.

La propuesta valora un núcleo común comparable y una parte aleatoria adicional. No fija longitud, cupos ni algoritmo. La selección futura deberá construirse al iniciar la encuesta y mantener su versión y semilla para auditoría; la importancia ponderará respuestas, no probabilidades de sorteo. No presentar rankings equiparables con preguntas o coberturas diferentes.

## Posiciones y comparación

Todas las preguntas son `editorial-draft`, `liveEligible: false` y `axisAssignment: null`. Cada una tiene una posición para los once partidos analizados:

- `proposed-coding`: respaldo +2 o rechazo −2 a la decisión exacta, con evidencia. No mide entusiasmo ideológico.
- `undetermined`: hay un pasaje relacionado, pero no permite atribuir un valor suficientemente preciso. Una evaluación o estudio no acredita su resultado.
- `not-determined-in-corpus`: no se ha vinculado evidencia suficiente a esta decisión exacta. No significa que el partido carezca de posición ni que se oponga o sea neutral.

`comparisonRule` pertenece a la **posición de cada partido**, pues una pregunta puede tener regla A para uno y B para otro. `proposalIds` reúne todos sus orígenes; cada posición solo cita las propuestas del partido correspondiente. No asignar ±1 por impresiones ni 0 por silencio.

Las respuestas van de −2 a +2. Normal, alta y esencial pesan 1, 2 y 3. No lo sé y omisión no participan. La afinidad utiliza distancia ponderada y cobertura documental; el documento explica la fórmula y ejemplos. No comparar como un ranking equivalente porcentajes calculados sobre coberturas distintas. Las coordenadas ideológicas requieren definir y justificar ejes por separado.

Los programas describen compromisos de sus autores: no prueban resultados, culpabilidades, la exactitud de sus diagnósticos o la vigencia actual de una ley. Los originales PSOE, Vox y Junts se conservaron desde archivos de prensa; se mantiene su procedencia y huella, sin atribuirles una descarga actual del servidor oficial.

## Coordenadas documentales

La vista previa se publica por petición expresa del usuario y utiliza una selección de decisiones, no todas las preguntas. Sus ocho agrupaciones gráficas **no sustituyen las 40 categorías** del inventario. No es un ranking de afinidad ni un mapa total de ideologías: las etiquetas explican qué políticas concretas componen cada eje.

Cada indicador pesa uno. Su puntuación es `50 × posición × dirección`, con posición −2 o +2 y dirección explícita +1 o −1. La media se calcula solo con indicadores documentados. La falta de datos no vale cero. Para dibujar un punto se exige evidencia en ambos ejes; la tabla muestra valores y cobertura incluso si no hay punto. Las atribuciones contradictorias entre variantes quedan sin determinar, nunca se deciden por mayoría. Varias referencias de un indicador no aumentan su peso. Las decisiones distintas dentro de un eje mantienen sus condiciones visibles; una coordenada compartida no implica programas equivalentes.

El intervalo de datos ausentes completa cada indicador desconocido con −100 o +100 y divide entre el total del eje. Es un rango de resultados posibles, **no confianza estadística ni probabilidad**. Los puntos coincidentes comparten marcador sin mover coordenadas para separarlos. Los cálculos desglosados y enlaces a páginas del PDF se consultan seleccionando partido e indicador.

Los indicadores de esta vista pesan uno y no utilizan respuestas personales. Normal/alta/esencial conservan los pesos 1/2/3 del futuro cuestionario. No interpretar valores con coberturas diferentes como distancias equivalentes o como recomendación de voto. Las decisiones definitivas y una selección equilibrada siguen requiriendo revisión editorial.

Pendiente de presentación: revisar los rectángulos de datos ausentes, que pueden confundirse con amplitud ideológica, y estudiar marcadores con el logotipo de cada partido. La incorporación de fuentes de esta tanda no rediseña los mapas ni convierte datos desconocidos en coordenadas precisas.

## Edición y comprobación

Editar `analisis.json`, conservando relaciones y fuentes, y ejecutar desde la raíz:

```text
python Cuestionario/herramientas/generar-resumen.py
python Cuestionario/herramientas/generar-resumen.py --check
```

La comprobación valida originales por huella, cobertura de unidades, referencias bidireccionales, páginas, ausencia de preguntas literales duplicadas, posiciones, reglas por partido, conservación del PP y sincronización del texto. También comprueba los ejemplos de importancia, neutralidad, omisión y falta de evidencia. La automatización comprueba integridad; no sustituye una lectura editorial independiente, pruebas de comprensión o la revisión de sesgos de selección.

La agrupación es una capa de revisión, no otro catálogo editable. Sus grupos derivan únicamente de pares declarados equivalentes y exigen revisar cada par cuando hay más de dos miembros: no fusionar una cadena de parecidos por transitividad. Una relación distinta dentro de un grupo es un error. Los valores candidatos citan los IDs originales; contradicción o evidencia ambigua bloquean el valor del partido. Nunca promediar votos entre fuentes ni transferir estas atribuciones al banco automáticamente. Si cambia el banco, actualizar la huella solo después de revalidar la revisión con esa edición.

Ejecutar también las pruebas de la revisión:

```text
python -m unittest discover -s Cuestionario/herramientas -p 'test_*.py'
```

Antes de incorporar un nuevo partido, usar la pregunta existente cuando corresponda, conservar las reservas y añadir otras categorías o conceptos si son necesarios. Antes de publicar afinidades de otra elección, analizar su propio programa fechado: este antecedente no acredita una postura de 2026. No modificar el cuestionario público como efecto de regenerar este cuaderno.
