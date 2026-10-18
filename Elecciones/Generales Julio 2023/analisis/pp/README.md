# Análisis del programa del Partido Popular de 2023

Primera versión editorial del 18 de octubre de 2026. Antecedente para preparar la comparación de programas, sin incorporación al cuestionario público.

- [Cuaderno descargable en texto](cuaderno-pp-2023.txt).
- [Cuaderno en Markdown](cuaderno-pp-2023.md).
- [Base editorial de propuestas y preguntas](analisis.json).
- [Recuento y límites de cobertura](cobertura.json).
- [Programa original](../../programas/pp/2026-10-17-programa.pdf).

Se inventarían las 365 medidas numeradas en 38 categorías. Hay 678 preguntas únicas, con 637 propuestas de codificación de respaldo, 5 de oposición y 36 sin determinar; además se reservan tres conceptos sin atribución partidista. Diez preguntas comparten varias medidas de origen. No se afirma que toda subcláusula tenga ya una pregunta final independiente ni que estos borradores constituyan un instrumento validado.

## Fuente y alcance

La fuente original es el programa de las generales del 23 de julio de 2023 descargado del servidor oficial del PP. El prefijo 2026-10-17 del PDF indica su descarga, no una publicación ni una convocatoria nueva. Se identifica por su SHA256 y por sus 112 páginas de archivo. La paginación impresa comienza dos páginas después del comienzo del PDF.

No se incorporan noticias, declaraciones posteriores, posiciones de otros partidos ni inferencias por ideología. Los borradores no certifican la legislación vigente, el cumplimiento de promesas o candidaturas de 2026. La posición de los demás partidos queda pendiente de su propio análisis.

## Base editorial

`analisis.json` es la fuente de verdad. No editar a mano las versiones legibles ni el recuento: se regeneran desde el JSON.

- `sources`: versión, convocatoria, archivo local, procedencia y huella del original.
- `categories`: taxonomía ampliable. Cada propuesta conserva también su concepto específico, por ejemplo aborto y consentimiento de menores.
- `proposals`: identificador, número original, resumen propio, categoría, medida y páginas de evidencia, preguntas relacionadas y notas de lectura. El número identifica una unidad del programa, no una unidad de puntuación.
- `questions`: identificador estable, afirmación para la escala de acuerdo, propuestas de origen y posiciones por partido. Varias medidas pueden enlazar una sola pregunta.
- `positions.<partido>.proposedValue`: codificación editorial propuesta, no aprobada para el cuestionario. Un valor nulo significa que no se puede determinar con suficiente precisión. Una organización que no aparece en `positions` todavía no se ha analizado.
- `comparisonRule`: A para respaldo de la opción exacta con valor +2, B para oposición con valor -2 y nulo sin atribución suficiente. Los extremos no miden intensidad retórica. No se asigna neutralidad por falta de evidencia ni valores intermedios por impresiones.
- `selectionGroup`: grupo para revisar preguntas solapadas. Aún no aplica un algoritmo de corrección o ponderación al cuestionario.
- `pendingConcepts`: conceptos adicionales reservados sin atribución al PP, separados del inventario de preguntas.
- `status`, `reviewStatus` y `liveEligible`: distinguen borrador de investigación de un banco aprobado. Todas las preguntas de esta entrega son borradores y `liveEligible` es falso.

Las páginas de evidencia corresponden a la medida completa, incluyendo continuaciones. La referencia no es una cita literal y el resumen no sustituye la lectura del original. Las notas explican límites de atribución; no deben aparecer como hechos introducidos en el programa.

## Ampliación con otros partidos

Conservar los identificadores aunque su origen contenga `pp23`. Si otro programa se pronuncia sobre la misma decisión y con idéntico alcance, añadir su propuesta, documento y evidencia a esa pregunta. Si cambia la decisión, la población, la condición o el umbral, crear una pregunta distinta o revisar expresamente la anterior; no mezclar alcances para fabricar una coincidencia. Los conceptos transversales pueden etiquetarse en categorías nuevas sin alterar lo que pregunta el ítem.

No trasladar estas posiciones de 2023 a 2026. Un programa de otra convocatoria requiere una atribución fechada independiente. No mezclar un estudio documental con los originales en `programas.json` ni marcar un original como apto para puntuación por haber creado este cuaderno.

La importancia conserva los pesos normal 1, alta 2 y esencial 3. La coincidencia utiliza distancia por pregunta, evidencia común y ponderación declarada; las coordenadas ideológicas requieren una decisión posterior sobre ejes. Omitir no equivale a neutral. El documento contiene las reglas y ejemplos completos.

## Regeneración y validación

Desde la raíz del repositorio, con Python 3:

```text
python Elecciones/herramientas/generar-cuaderno-programa.py
python Elecciones/herramientas/generar-cuaderno-programa.py --check
```

El verificador comprueba cobertura numérica, referencias bidireccionales, páginas, huella del programa, preguntas literales duplicadas, escalas, posiciones reservadas y coherencia de los documentos generados. Comprueba asimismo las tablas de coincidencia y los ejemplos ponderados. Estos controles no sustituyen la revisión política y editorial independiente ni las pruebas de comprensión.
