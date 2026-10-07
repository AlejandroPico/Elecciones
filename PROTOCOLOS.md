# Protocolos de Elecciones

Revisión: 7 de octubre de 2026. Aplicable a personas y agentes que amplíen este repositorio.

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
- Código en `src/app/`, `src/cuestionario/`, `src/perfil/`, `src/archivo/`, `src/partidos/`, `src/gobiernos/` y `src/datos/`; solo el arranque y tipos de Vite en la raíz de `src`. `Elecciones/index.ts` selecciona la convocatoria activa. El mosaico de convocatorias queda pendiente.
- IDs nuevos: `es-<tipo>-<territorio-si-procede>-<AAAA-MM-DD>`. El ID existente `es-generales-2026` se mantiene por compatibilidad. Personas y organizaciones conservan IDs estables aunque cambien de cargo o nombre.
- No reutilizar IDs de preguntas con significado distinto. Cambiar la versión del cuestionario si cambia la propuesta, escala, eje o dirección. Ampliar una explicación sin cambiar su significado no modifica su puntuación.

## Fichas y lectura automática

`src/datos/catalogo.ts` descubre las carpetas mediante `import.meta.glob` durante la construcción. No mantener un segundo catálogo manual de nombres. Una nueva carpeta con `ficha.json` válido aparece en la siguiente compilación; GitHub Pages no enumera directorios en tiempo de ejecución.

Si la revisión identifica dos fichas de la misma persona, reunir sus datos en una carpeta, conservar el ID canónico y declarar los otros en `legacyIds`. Actualizar las relaciones al ID canónico; `findPerson` resuelve también los alias. No crear dos personas por una nota al pie ni descartar las trayectorias de la ficha duplicada.

En cada persona:

- `ficha.json`: ID estable, nombre, nombre completo, iniciales, vinculación acreditada o `null`, cargo/resumen, IDs de cargos y fecha de revisión.
- `datos-personales.json`: nacimiento, fecha ISO completa cuando se conoce, año, fallecimiento y `personalSources`.
- `formacion.json`: lista de estudios e instituciones; referencias en `fuentes-formacion.json`.
- `trayectoria.json`: lista de `{period, title, source: {label, url}}`.
- `actuaciones.json`: hechos con fecha, descripción, estado y fuentes. No crear un archivo vacío como sustituto de investigación.
- `fuentes.json`: referencias generales de la ficha.
- `retrato.jpg` (o PNG/WebP/SVG) y `retrato.json`: `{file, credit, source}`. Un solo retrato activo; no recursos huérfanos.

Si una unificación reúne retratos institucionales diferentes, conservar el alternativo como `retrato-historico-<id>.<ext>` y sus créditos en `retrato-historico-<id>.json`. La interfaz actual presenta solo el retrato activo; no perder el archivo alternativo durante una migración.

En cada partido: `ficha.json`, `fuentes.json`, y los apartados disponibles `historia.json`, `dirigentes.json` y `programas.json`. Los dirigentes declaran `{period, title, person, source}`; `person` es el ID de una ficha existente. Distinguir presidente, secretario general y gestora. El logotipo se acompaña de `logotipo.json: {file, source}`.

La interfaz presenta los apartados en vertical y únicamente cuando contienen datos. Sin formación o actuaciones no se imprime un encabezado vacío ni un mensaje de relleno. Ausencia de archivo significa falta de cobertura, no inexistencia del hecho. Los cargos se derivan de composiciones y enlazan personas por ID.

Para una migración: inventariar IDs, relaciones, textos, referencias y recursos antes de mover; comprobar su conservación con el catálogo nuevo antes de retirar el anterior. `docs/migracion-2026-10-07.json` registra las 275 identidades, 15 partidos y 72 composiciones iniciales. Mantener las pruebas que evitan perderlos.

## Cuestionario y neutralidad

Una pregunta plantea una sola propuesta comprensible. Su contexto ampliado delimita alcance, conceptos, exclusiones y consideraciones de ambos sentidos. No atribuir superioridad moral a una respuesta ni introducir hechos recientes sin fuente y fecha. No confundir las propuestas hipotéticas con legislación vigente. La escala y dirección deben ser explícitas; omitir es distinto de responder neutral. Las ponderaciones son elección del usuario. El banco actual es piloto, no un instrumento validado.

## Partidos y candidaturas

El directorio de partidos NO acredita presentación a una elección. Solo marcar una candidatura como confirmada con proclamación oficial y su enlace, circunscripción, cámara, orden y suplencias. No confundir un líder de partido con cabeza de todas sus listas. Programas históricos deben mostrar su año. No asignar posiciones desconocidas como cero ni inferirlas del logotipo o de una etiqueta ideológica. Cada posición de programa necesita referencia precisa y fuente.

Logotipos: usar recursos publicados por la organización, conservar procedencia y formato. Preferir SVG genuinos; no redibujar imitaciones ni convertir automáticamente una imagen en un vector ficticio. Retratos: ficha institucional individual, crédito y procedencia; no fotos de actos ni caras generadas. Si falta un retrato, mostrar iniciales y señalarlo.

## Biografías, actuaciones y controversias

Registrar nombre completo, nacimiento cuando esté acreditado, formación e instituciones, carrera profesional y cargos con fechas y fuentes. Ausencia de un dato no equivale a ausencia del hecho. La edad exacta se calcula con la fecha local y solo si hay día, mes y año; no mostrar un intervalo inventado. Para fallecidos mostrar el fallecimiento. Diferenciar el titular de un departamento, su partido, su vinculación electoral y la responsabilidad de una actuación.

Priorizar la ficha individual institucional. Wikipedia puede completar datos biográficos ausentes, identificándola como fuente enciclopédica y enlazando el artículo concreto. Ante contradicciones no copiar automáticamente: contrastar otra fuente individual, documentar la elección y conservar la precisión real. Ejemplo revisado: el Congreso sitúa el nacimiento de Margarita Robles el 10 de noviembre de 1956, mientras una ficha de La Moncloa recoge 1957. La ficha personal utiliza el dato individual del Congreso. No inferir un estudio por asistir a un curso ni atribuir un título de máster a formación breve.

Las biografías institucionales describen la trayectoria pero no bastan para una evaluación. Separar actuaciones, críticas políticas, investigaciones, acusaciones, sentencias y resoluciones firmes; indicar fecha, órgano, estado procesal y respuesta documentada cuando corresponda. Una reprobación parlamentaria no es una condena. No atribuir culpabilidad por asociación. No denominar «éxito» a un resultado sin criterio y evidencia. Mantener fuentes por afirmación y fecha de revisión; no copiar artículos extensos.

## Gobiernos y Congreso

Ordenar gobiernos del más reciente al más antiguo. Distinguir legislatura, mandato presidencial y remodelación del gabinete. Intervalos de composición `[desde, hasta)` con fechas ISO: el día de relevo corresponde a la composición nueva. Diferenciar anuncio, publicación, toma de posesión y cese; citar el criterio usado. Gobierno en funciones sigue existiendo, no generar huecos artificiales. Descripciones históricas de La Moncloa son el punto de partida; contrastar límites con BOE antes de incorporar nombramientos individuales.

Organigrama: Presidencia, vicepresidencias, departamentos ministeriales y sus órganos superiores/directivos. No dibujar a todos los ministros como subordinados de una vicepresidencia. Segundo/tercer nivel requieren norma de estructura y nombramientos; no inventar relaciones. La vista temporal cambia en fechas documentadas, no interpola personas. Indicar cobertura cuando faltan biografías, retratos o niveles.

El hemiciclo identifica cámara, elección/fecha, partidos o coaliciones y fuente; sus escaños deben sumar el tamaño de la cámara de ese periodo. La distribución por candidatura electoral no equivale al grupo parlamentario posterior ni a apoyos del Gobierno. La posición de cada punto es esquemática, no el asiento físico de un diputado. No trasladar cifras de una legislatura a otra.

## Estado, privacidad y publicación

Respuestas y preferencias permanecen en memoria; no hay guardado, exportación ni recogida estadística. No añadir autenticación o persistencia sin nueva instrucción. El favicon canónico está en `/favicon.svg` y debe publicarse en la raíz del sitio.

Verificar cálculo, cobertura de contextos, referencias cruzadas, intervalos temporales y suma de escaños. Comprobar también interfaz, teclado, móvil, reducción de movimiento y temas. Construir y ejecutar las pruebas antes de publicar. Mantener fuentes y límites de cobertura visibles, sin llenar el cuestionario de texto ornamental.
