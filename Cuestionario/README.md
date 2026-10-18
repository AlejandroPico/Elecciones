# Cuestionario: propuestas y preguntas

[Resumen Preguntas.txt](Resumen%20Preguntas.txt) es el documento unificado de PP, PSOE y Vox. Agrupa decisiones por conceptos, aunque los programas utilicen títulos diferentes. Es una investigación editorial de los **programas de las generales de julio de 2023**, todavía sin incorporar al cuestionario público ni a las afinidades de 2026.

## Archivos

- `analisis.json`: base editable y única fuente de verdad. Propuestas, preguntas, posiciones por partido, conceptos, reservas y evidencia.
- `Resumen Preguntas.txt`: documento legible generado desde la base, con índice, comparación por pregunta, cálculo e inventario de propuestas.
- `cobertura.json`: recuentos y límites verificables; se genera junto al texto.
- `herramientas/generar-resumen.py`: generador y verificador, sin dependencias externas.

Los originales permanecen en `Elecciones/Generales Julio 2023/programas/<partido>/`. Esta carpeta raíz de investigación se crea por petición expresa del usuario. No duplicar originales ni mantener otro catálogo de preguntas editable en `docs` o bajo un partido.

## Cobertura y organización

Se conservan las 365 propuestas y las 678 preguntas del primer análisis del PP, incluidos sus identificadores, enunciados, reservas y evidencia. El programa de Vox tiene 381 medidas numeradas. El PSOE no ofrece esa numeración: **S0001–S1191 son anclas editoriales de viñetas**, no 1191 medidas oficiales. Los pasajes adicionales por página recogen propuestas con otras viñetas o en párrafos, especialmente vivienda y derechos. La cobertura de anclas no asegura el desdoblamiento exhaustivo de cada subcláusula.

`sourceUnits` identifica localizadores y páginas. `proposals` reúne unidades relacionadas y redacta un resumen propio; una agrupación puede proponer varias preguntas o quedar como contexto sin puntuar. Los pasajes adicionales pueden solaparse con otras unidades. Nunca sumarlos como evidencia independiente. `sourceUnits.extractedTextSha256` es una huella de control del fragmento extraído, no una cita literal ni una huella del archivo completo. La huella del original está en `sources.sha256`.

`concepts` reúne preguntas de los tres partidos por asunto. `questions.originConcepts` conserva las denominaciones editoriales de origen. Cada pregunta conserva un ID estable: el prefijo `pp23`, `psoe23` o `vox23` identifica dónde nació, **no qué partido es propietario de la pregunta**. Si una decisión coincide en alcance, población, instrumento y condiciones, compartir pregunta y añadir evidencia. Si cambia una condición relevante, mantener preguntas distintas dentro del mismo concepto. No igualar, por ejemplo, devolución y exención del IBI, desalojo en 24 y 48 horas o elección judicial de doce y de todos los vocales del CGPJ.

`selectionGroup` señala una familia temática que requiere revisar solapamientos. Es un aviso conservador, no una instrucción para seleccionar una sola pregunta de todo el tema ni un algoritmo de corrección ya aplicado. `legacySelectionGroup` conserva los avisos anteriores del PP. Antes de puntuar, decidir qué formulaciones representan la misma decisión y cuáles son dimensiones independientes.

## Posiciones y comparación

Todas las preguntas son `editorial-draft`, `liveEligible: false` y `axisAssignment: null`. Cada una tiene las tres claves `positions.pp`, `positions.psoe` y `positions.vox`:

- `proposed-coding`: respaldo +2 o rechazo −2 a la decisión exacta, con evidencia. No mide entusiasmo ideológico.
- `undetermined`: hay un pasaje relacionado, pero no permite atribuir un valor suficientemente preciso. Una evaluación o estudio no acredita su resultado.
- `not-determined-in-corpus`: no se ha vinculado evidencia suficiente a esta decisión exacta. No significa que el partido carezca de posición ni que se oponga o sea neutral.

`comparisonRule` pertenece a la **posición de cada partido**, pues una pregunta puede tener regla A para uno y B para otro. `proposalIds` reúne todos sus orígenes; cada posición solo cita las propuestas del partido correspondiente. No asignar ±1 por impresiones ni 0 por silencio.

Las respuestas van de −2 a +2. Normal, alta y esencial pesan 1, 2 y 3. No lo sé y omisión no participan. La afinidad utiliza distancia ponderada y cobertura documental; el documento explica la fórmula y ejemplos. No comparar como un ranking equivalente porcentajes calculados sobre coberturas distintas. Las coordenadas ideológicas requieren definir y justificar ejes por separado.

Los programas describen compromisos de sus autores: no prueban resultados, culpabilidades, la exactitud de sus diagnósticos o la vigencia actual de una ley. Los originales PSOE y Vox se conservaron desde archivos de prensa; se mantiene su procedencia y huella, sin atribuirles una descarga actual del servidor oficial.

## Edición y comprobación

Editar `analisis.json`, conservando relaciones y fuentes, y ejecutar desde la raíz:

```text
python Cuestionario/herramientas/generar-resumen.py
python Cuestionario/herramientas/generar-resumen.py --check
```

La comprobación valida originales por huella, cobertura de unidades, referencias bidireccionales, páginas, ausencia de preguntas literales duplicadas, posiciones, reglas por partido, conservación del PP y sincronización del texto. También comprueba los ejemplos de importancia, neutralidad, omisión y falta de evidencia. La automatización comprueba integridad; no sustituye una lectura editorial independiente, pruebas de comprensión o la revisión de sesgos de selección.

Antes de incorporar un nuevo partido, usar la pregunta existente cuando corresponda, conservar las reservas y añadir otras categorías o conceptos si son necesarios. Antes de publicar afinidades de otra elección, analizar su propio programa fechado: este antecedente no acredita una postura de 2026. No modificar el cuestionario público como efecto de regenerar este cuaderno.
