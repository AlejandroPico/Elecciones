# Cuestionario: propuestas y preguntas

[Resumen Preguntas.txt](Resumen%20Preguntas.txt) es el documento unificado de **PP, PSOE, Vox, ERC, Junts, EH Bildu, PNV y BNG**. Agrupa decisiones por conceptos, aunque los programas utilicen títulos diferentes. Es una investigación editorial de los **programas de las generales de julio de 2023**. La vista previa «Cuestionario → Coordenadas políticas» permite explorar posiciones documentadas; el banco todavía no sustituye las preguntas ni las afinidades del test vigente.

## Archivos

- `analisis.json`: base editable y única fuente de verdad. Propuestas, preguntas, posiciones por partido, conceptos, reservas y evidencia.
- `Resumen Preguntas.txt`: documento legible generado desde la base, con índice, comparación por pregunta, cálculo e inventario de propuestas.
- `cobertura.json`: recuentos y límites verificables; se genera junto al texto.
- `Resumen Categorías.txt`: informe breve de categorías y recuentos, generado desde la misma base.
- `ejes.json`: selección editorial explícita de indicadores, signos y método de los ocho mapas temáticos. No contiene posiciones propias: referencia preguntas de la base.
- `coordenadas.json`: extracto generado para la vista previa, con sus posiciones y evidencia; nunca editarlo a mano.
- `interfaz/`: gráficos, consulta de cálculos, fuentes y pruebas del modelo.
- `herramientas/generar-resumen.py`: generador y verificador, sin dependencias externas.

Los originales permanecen en `Elecciones/Generales Julio 2023/programas/<partido>/`. Esta carpeta raíz de investigación se crea por petición expresa del usuario. No duplicar originales ni mantener otro catálogo de preguntas editable en `docs` o bajo un partido.

## Cobertura y organización

Se conservan las 365 propuestas y las 678 preguntas del primer análisis del PP, incluidos sus identificadores, enunciados, reservas y evidencia. El programa de Vox tiene 381 medidas numeradas. El PSOE no ofrece esa numeración: **S0001–S1191 son anclas editoriales de viñetas**, no 1191 medidas oficiales. Los pasajes adicionales por página recogen propuestas con otras viñetas o en párrafos, especialmente vivienda y derechos. La cobertura de anclas no asegura el desdoblamiento exhaustivo de cada subcláusula.

`sourceUnits` identifica localizadores y páginas. `proposals` reúne unidades relacionadas y redacta un resumen propio; una agrupación puede proponer varias preguntas o quedar como contexto sin puntuar. Los pasajes adicionales pueden solaparse con otras unidades. Nunca sumarlos como evidencia independiente. `sourceUnits.extractedTextSha256` es una huella de control del fragmento extraído, no una cita literal ni una huella del archivo completo. La huella del original está en `sources.sha256`.

ERC, Junts, EH Bildu, PNV y BNG se inventarían por páginas físicas: **132, 151, 16, 52 y 68** respectivamente. Son anclas editoriales, no medidas oficiales numeradas ni promesas independientes. EH Bildu es un compromiso breve. ERC separa horizontes políticos y propuestas a las Cortes; las preguntas se centran en sus apartados operativos. Las introducciones y balances quedan clasificados como contexto. El inventario por página no garantiza haber desdoblado todas las subcláusulas.

`concepts` reúne preguntas de los ocho partidos por asunto. `questions.originConcepts` conserva las denominaciones editoriales de origen. Cada pregunta conserva un ID estable: su prefijo identifica dónde nació, **no qué partido es propietario de la pregunta**. Si una decisión coincide en alcance, población, instrumento y condiciones, compartir pregunta y añadir evidencia. Si cambia una condición relevante, mantener preguntas distintas dentro del mismo concepto. No igualar, por ejemplo, devolución y exención del IBI, jornadas de 32 y 35 horas o convenios autonómicos incondicionados y condicionados a ser más favorables. `unificationAudit` registra fusiones semánticas revisadas; la fusión literal no basta para resolver todos los solapamientos.

`selectionGroup` señala una familia temática que requiere revisar solapamientos. Es un aviso conservador, no una instrucción para seleccionar una sola pregunta de todo el tema ni un algoritmo de corrección ya aplicado. `legacySelectionGroup` conserva los avisos anteriores del PP. Antes de puntuar, decidir qué formulaciones representan la misma decisión y cuáles son dimensiones independientes.

## Posiciones y comparación

Todas las preguntas son `editorial-draft`, `liveEligible: false` y `axisAssignment: null`. Cada una tiene una posición para los ocho partidos analizados:

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

## Edición y comprobación

Editar `analisis.json`, conservando relaciones y fuentes, y ejecutar desde la raíz:

```text
python Cuestionario/herramientas/generar-resumen.py
python Cuestionario/herramientas/generar-resumen.py --check
```

La comprobación valida originales por huella, cobertura de unidades, referencias bidireccionales, páginas, ausencia de preguntas literales duplicadas, posiciones, reglas por partido, conservación del PP y sincronización del texto. También comprueba los ejemplos de importancia, neutralidad, omisión y falta de evidencia. La automatización comprueba integridad; no sustituye una lectura editorial independiente, pruebas de comprensión o la revisión de sesgos de selección.

Antes de incorporar un nuevo partido, usar la pregunta existente cuando corresponda, conservar las reservas y añadir otras categorías o conceptos si son necesarios. Antes de publicar afinidades de otra elección, analizar su propio programa fechado: este antecedente no acredita una postura de 2026. No modificar el cuestionario público como efecto de regenerar este cuaderno.
