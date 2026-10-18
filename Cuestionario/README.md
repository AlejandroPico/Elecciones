# Cuestionario: propuestas y preguntas

[Resumen Preguntas.txt](Resumen%20Preguntas.txt) unifica **22 organizaciones**: PP, PSOE, Vox, ERC, Junts, EH Bildu, PNV, BNG, PACMA, Escaños en Blanco, Frente Obrero, PCTE, Iustitia Europa, Se Acabó La Fiesta, Podemos, Soria ¡Ya!, Teruel Existe, Adelante Andalucía, Drago Canarias, democracia21, Coalición Canaria y Sumar (programa común de 2023). Agrupa decisiones por conceptos, aunque los documentos utilicen títulos distintos. Los **23 documentos** mezclan quince antecedentes de julio de 2023, Podemos 2019, cuatro textos políticos generales, un artículo permanente y dos programas autonómicos. No constituyen programas nacionales de una misma convocatoria. La vista «Cuestionario → Coordenadas políticas» permite explorar evidencia; el banco no sustituye las preguntas ni las afinidades del test vigente.

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

Los originales electorales permanecen en la carpeta de su edición: `Elecciones/Generales Julio 2023/programas/<partido>/` y `Elecciones/Generales Noviembre 2019/programas/podemos/`. Los documentos generales y permanentes consultados para la convocatoria activa se conservan en `Elecciones/Generales Noviembre 2026/programas/<partido>/`, identificando que no son programas específicos de esa elección. Esta carpeta raíz de investigación se crea por petición expresa del usuario. No duplicar originales ni mantener otro catálogo de preguntas editable en `docs` o bajo un partido.

## Cobertura y organización

Se conservan las 365 propuestas y las 678 preguntas del primer análisis del PP, incluidos sus identificadores, enunciados, reservas y evidencia. El programa de Vox tiene 381 medidas numeradas. El PSOE no ofrece esa numeración: **S0001–S1191 son anclas editoriales de viñetas**, no 1191 medidas oficiales. Los pasajes adicionales por página recogen propuestas con otras viñetas o en párrafos, especialmente vivienda y derechos. La cobertura de anclas no asegura el desdoblamiento exhaustivo de cada subcláusula.

`sourceUnits` identifica localizadores y páginas. `proposals` reúne unidades relacionadas y redacta un resumen propio; una agrupación puede proponer varias preguntas o quedar como contexto sin puntuar. Los pasajes adicionales pueden solaparse con otras unidades. Nunca sumarlos como evidencia independiente. `sourceUnits.extractedTextSha256` es una huella de control del fragmento extraído, no una cita literal ni una huella del archivo completo. La huella del original está en `sources.sha256`.

ERC, Junts, EH Bildu, PNV y BNG se inventarían por páginas físicas: **132, 151, 16, 52 y 68** respectivamente. Son anclas editoriales, no medidas oficiales numeradas ni promesas independientes. EH Bildu es un compromiso breve. ERC separa horizontes políticos y propuestas a las Cortes; las preguntas se centran en sus apartados operativos. Las introducciones y balances quedan clasificados como contexto. El inventario por página no garantiza haber desdoblado todas las subcláusulas.

PACMA y Frente Obrero se inventarían por sus 76 y 64 páginas físicas. Frente Obrero declara expresamente que su documento es político, no electoral. Escaños en Blanco se referencia por su artículo único en la línea 6 de la transcripción HTML local: no tiene páginas PDF ficticias. No se le atribuyen posiciones sectoriales ni se convierte la renuncia voluntaria a sus subvenciones en una prohibición para otros partidos. La esterilización propuesta por PACMA conserva la excepción veterinaria; una crítica genérica a la nuclear no acredita un calendario de cierre concreto.

PCTE, Iustitia Europa y SALF añaden 24, 28 y 22 páginas físicas inventariadas. El PCTE define su texto como programa de lucha, no electoral; Iustitia Europa no identifica una edición de convocatoria. SALF corresponde a las autonómicas de Castilla y León del **15 de marzo de 2026**, conservado en `Elecciones/Autonómicas Castilla y León Marzo 2026/`. Sus preguntas tienen `territorialScope`: nunca se usan como evidencia nacional ni se introducen en los ejes generales. No se localizó un programa nacional en la revisión del 18 de octubre. Las consultas sobre permanencia en UE y OTAN de Iustitia Europa no acreditan un voto por salir; las propuestas sobre terapias naturales no validan su eficacia clínica. Las referencias legales o medidas insuficientemente delimitadas quedan indeterminadas.

Podemos aporta **289 medidas oficiales de su programa nacional del 10N de 2019**, en 119 páginas. Se añaden **598 formulaciones nuevas**, conservando las 4.040 anteriores y todas sus atribuciones. El original se conserva desde el archivo de 20minutos, con su URL oficial bloqueada y su huella; el PDF incluye texto anterior pintado en blanco y la extracción se contrastó con las páginas visibles. Las remisiones a medidas anteriores comparten pregunta cuando procede; no suman peso independiente. Las cantidades, plazos, entidades y normas se mantienen en contexto de 2019, sin presentarlos como promesas actuales ni garantizar un desdoblamiento exhaustivo de cada subcláusula. Las 34 horas, el cambio gradual del eje de defensa hacia la UE o el referéndum catalán con defensa de un nuevo encaje dentro de España no se convierten respectivamente en 32/35 horas, salida explícita de la OTAN o apoyo a la independencia.

La ampliación regional incorpora **780 formulaciones nuevas** y conserva las 4.638 anteriores con sus atribuciones: **5.418 formulaciones, 109 conceptos, 40 categorías, 2.075 grupos de propuestas y 3.938 unidades documentales**. Soria mantiene las 73 medidas oficiales de su HTML; CC, los 52 compromisos del manifiesto conjunto del que es firmante. Teruel y Adelante Andalucía se anclan en las 29 y 85 páginas físicas de sus programas nacionales de 2023. Drago se conserva como HTML y transcripción autonómica de 2023, con referencias por línea, ámbito Canarias y exclusión de los ejes generales. Su captura actual no prueba una versión inmutable de aquella campaña.

Democracia21 aporta dos documentos: el manifiesto y los títulos de soluciones quedan como contexto; las políticas concretas contra la corrupción proceden de las 13 páginas de *España Limpia*. Es un documento sectorial sin edición electoral acreditada, no un programa completo. No se confunde con la inscripción DEM `registro-7631`. Los seis partidos conservan sus logotipos locales y ofrecen las copias descargables desde sus fichas.

El análisis de esta tanda usa agrupaciones condensadas y no certifica la atomización de cada subcláusula. Las líneas, páginas y medidas son unidades de referencia, no una métrica comparable de promesas. Los pasajes no atomizados permanecen en los originales y sin puntuación automática. Las discrepancias de Adelante Andalucía sobre jubilación (62/64 años) y conciertos educativos quedan sin puntuación. Su límite de alquiler sobre renta media del distrito no equivale a uno sobre ingresos de cada hogar. El objetivo 30-30 de Soria usa minutos para las vías rápidas; el de Teruel usa kilómetros. España Limpia mantiene un aforamiento penal funcional del Gobierno y propone consecuencias por no presentar presupuestos, no por no lograr su aprobación.

Sumar añade **443 formulaciones nuevas** a las 5.418 anteriores, sin alterar sus textos ni atribuciones. La edición actual reúne **5.861 formulaciones, 109 conceptos, 40 categorías, 2.183 grupos de propuestas y 4.120 unidades documentales**, con 23 fuentes para 22 organizaciones. El programa común del 23J de 2023 conserva la identidad `sumar-coalicion-2023`, sus 182 páginas físicas y su original sin modificar. La copia se ha contrastado con el enlace actual de Movimiento Sumar y coincide byte a byte. `referencedBy: ["sumar"]` habilita la descarga también desde la ficha actual: es una relación documental, no una transferencia de posiciones a Movimiento Sumar ni al Frente Amplio.

El análisis es condensado por temas y no certifica la atomización de cada subcláusula. Las páginas son anclas, no promesas; la numeración reinicia entre apartados. Se preservan las discrepancias del bono hipotecario (dos años en página 8, diez en 77), sin asignar valor a esos plazos. El diálogo hacia 32 horas no se fusiona con una reducción inmediata; estudiar una circunscripción exterior no equivale a aprobarla y votar un pacto territorial acordado no equivale a apoyar independencia. Los gravámenes prorrogados hasta reformar sociedades no se convierten en permanentes. Los porcentajes sobre PNB en cooperación no se sustituyen por PIB.

`concepts` reúne preguntas de las veintidós organizaciones por asunto. `questions.originConcepts` conserva las denominaciones editoriales de origen. Cada pregunta conserva un ID estable: su prefijo identifica dónde nació, **no qué partido es propietario de la pregunta**. Si una decisión coincide en alcance, población, instrumento y condiciones, compartir pregunta y añadir evidencia. Si cambia una condición relevante, mantener preguntas distintas dentro del mismo concepto. No igualar, por ejemplo, devolución y exención del IBI, jornadas de 32, 34 y 35 horas o convenios autonómicos incondicionados y condicionados a ser más favorables. `unificationAudit` registra fusiones semánticas revisadas; la fusión literal no basta para resolver todos los solapamientos.

`selectionGroup` señala una familia temática que requiere revisar solapamientos. Es un aviso conservador, no una instrucción para seleccionar una sola pregunta de todo el tema ni un algoritmo de corrección ya aplicado. `legacySelectionGroup` conserva los avisos anteriores del PP. Antes de puntuar, decidir qué formulaciones representan la misma decisión y cuáles son dimensiones independientes.

Las **40 categorías serán los apartados del cuestionario**, no cuarenta encuestas completas. Las 5.861 formulaciones son un banco documental que se reducirá mediante agrupación de decisiones equivalentes. Se prevé una selección aleatoria equilibrada por categorías y conceptos, evitando repetir la misma decisión y manteniendo cobertura comparable entre partidos. No exige igual número de preguntas en todos los temas. `surveyDesign` documenta esta intención: todavía no hay algoritmo, cupos ni longitud definitiva implementados. No confundir el tamaño del banco con las preguntas que responderá cada persona.

La [primera propuesta de agrupación y selección](Plan%20de%20selección.txt) revisa **189 pares de 280 formulaciones**: 16 equivalencias propuestas, 102 variantes con diferencias, 69 pares de decisiones independientes y 2 opciones contrapuestas. Coincidencia léxica solo sirve para localizar candidatos; no los fusiona. Es una pasada acotada, no una revisión semántica exhaustiva del banco. Sus pares y familias se revalidaron sobre los enunciados conservados al ampliar el banco; las nuevas formulaciones de esta tanda no están incluidas en esa pasada. Confirmar las 16 equivalencias evitaría 16 repeticiones, pero la reducción principal de una sesión vendrá de seleccionar decisiones. No se borran preguntas ni se alteran posiciones.

La revisión conserva diferencias como jornadas de 32/34/35 horas, educación universal/gratuita, IVA veterinario del 10/4 %, prórroga nuclear con/sin aval del CSN y devolución/exención de IBI. Ampliar y suprimir un servicio tampoco son negaciones exactas: una persona puede rechazar ambas opciones. No se invierten puntuaciones por semejanza de vocabulario.

Se proponen **12 familias de variantes** para evitar preguntar varios umbrales del mismo debate en una encuesta breve: jornada, cuotas bajo SMI, prórroga nuclear, IVA veterinario, horizonte climático, cálculo de pensiones, edad de jubilación, aforamientos, cobertura bucodental, parque público de alquiler, indemnización por despido y barreras electorales. La propuesta es elegir como máximo una variante de cada familia en esa modalidad. Esto no declara equivalentes las alternativas ni reúne sus posiciones. Las familias incluyen los alias equivalentes para impedir que otra redacción eluda el límite futuro; los solapamientos entre familias requieren revisión. No es una restricción activada en el test piloto.

La auditoría detecta **245 formulaciones con posiciones propuestas para dos o más partidos**. Reunir provisionalmente referencias de las equivalencias ofrece 258 unidades de ese tipo, todavía sin aprobación de producción. No hay un conjunto común para las veintidós organizaciones; Turismo y hostelería aún no tiene una unidad con dos partidos documentados. Antes de una selección real, ampliar la comparación cruzada sobre las mismas decisiones, sin deducir posiciones por ideología. El artículo institucional de Escaños en Blanco no se fuerza a un programa sectorial.

La propuesta valora un núcleo común comparable y una parte aleatoria adicional. No fija longitud, cupos ni algoritmo. La selección futura deberá construirse al iniciar la encuesta y mantener su versión y semilla para auditoría; la importancia ponderará respuestas, no probabilidades de sorteo. No presentar rankings equiparables con preguntas o coberturas diferentes.

## Posiciones y comparación

Todas las preguntas son `editorial-draft`, `liveEligible: false` y `axisAssignment: null`. Cada una tiene una posición para las veintidós organizaciones analizados:

- `proposed-coding`: respaldo +2 o rechazo −2 a la decisión exacta, con evidencia. No mide entusiasmo ideológico.
- `undetermined`: hay un pasaje relacionado, pero no permite atribuir un valor suficientemente preciso. Una evaluación o estudio no acredita su resultado.
- `not-determined-in-corpus`: no se ha vinculado evidencia suficiente a esta decisión exacta. No significa que el partido carezca de posición ni que se oponga o sea neutral.

`comparisonRule` pertenece a la **posición de cada partido**, pues una pregunta puede tener regla A para uno y B para otro. `proposalIds` reúne todos sus orígenes; cada posición solo cita las propuestas del partido correspondiente. No asignar ±1 por impresiones ni 0 por silencio.

Las respuestas van de −2 a +2. Normal, alta y esencial pesan 1, 2 y 3. No lo sé y omisión no participan. La afinidad utiliza distancia ponderada y cobertura documental; el documento explica la fórmula y ejemplos. No comparar como un ranking equivalente porcentajes calculados sobre coberturas distintas. Las coordenadas ideológicas requieren definir y justificar ejes por separado.

Los programas describen compromisos de sus autores: no prueban resultados, culpabilidades, la exactitud de sus diagnósticos o la vigencia actual de una ley. Los originales PSOE, Vox, Junts y Podemos se conservaron desde archivos de prensa; se mantiene su procedencia y huella, sin atribuirles una descarga actual del servidor oficial.

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
