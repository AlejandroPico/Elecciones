# Protocolos de Elecciones

Revisión: 7 de octubre de 2026. Aplicable a personas y agentes que amplíen este repositorio.

## Carpetas y nombres

- Toda información específica de una convocatoria pertenece a `Elecciones/<convocatoria>/`.
- Generales: `Generales <Mes> <AAAA>`, por ejemplo `Generales Noviembre 2026`.
- Autonómicas: `Autonómicas <territorio oficial> <Mes> <AAAA>`; municipales: `Municipales <territorio> <Mes> <AAAA>`.
- Meses en español con inicial mayúscula. Si hay dos convocatorias del mismo ámbito y mes, ambas incorporarán el día con dos cifras antes del mes. No improvisar otros patrones.
- Archivos de datos en minúsculas y con guiones: `cuestionario.ts`, `contextos.ts`, `partidos.json`, `gobiernos.json`, `biografias.json`. Recursos en `logotipos/` y `retratos/`. Programas descargados en `programas/<partido-id>/<AAAA-MM-DD>-<documento>.pdf`.
- Mantener una sola copia de cada recurso dentro de la convocatoria. Código de presentación y cálculo común en `src/`. `Elecciones/index.ts` selecciona la convocatoria activa. El mosaico de convocatorias queda pendiente.
- IDs nuevos: `es-<tipo>-<territorio-si-procede>-<AAAA-MM-DD>`. El ID existente `es-generales-2026` se mantiene por compatibilidad. Personas y organizaciones conservan IDs estables aunque cambien de cargo o nombre.
- No reutilizar IDs de preguntas con significado distinto. Cambiar la versión del cuestionario si cambia la propuesta, escala, eje o dirección. Ampliar una explicación sin cambiar su significado no modifica su puntuación.

## Cuestionario y neutralidad

Una pregunta plantea una sola propuesta comprensible. Su contexto ampliado delimita alcance, conceptos, exclusiones y consideraciones de ambos sentidos. No atribuir superioridad moral a una respuesta ni introducir hechos recientes sin fuente y fecha. No confundir las propuestas hipotéticas con legislación vigente. La escala y dirección deben ser explícitas; omitir es distinto de responder neutral. Las ponderaciones son elección del usuario. El banco actual es piloto, no un instrumento validado.

## Partidos y candidaturas

El directorio de partidos NO acredita presentación a una elección. Solo marcar una candidatura como confirmada con proclamación oficial y su enlace, circunscripción, cámara, orden y suplencias. No confundir un líder de partido con cabeza de todas sus listas. Programas históricos deben mostrar su año. No asignar posiciones desconocidas como cero ni inferirlas del logotipo o de una etiqueta ideológica. Cada posición de programa necesita referencia precisa y fuente.

Logotipos: usar recursos publicados por la organización, conservar procedencia y formato. Preferir SVG genuinos; no redibujar imitaciones ni convertir automáticamente una imagen en un vector ficticio. Retratos: ficha institucional individual, crédito y procedencia; no fotos de actos ni caras generadas. Si falta un retrato, mostrar iniciales y señalarlo.

## Biografías, actuaciones y controversias

Registrar nombre completo, nacimiento cuando esté acreditado, formación e instituciones, carrera profesional y cargos con fechas y fuentes. Ausencia de un dato no equivale a ausencia del hecho. La edad se calcula a la fecha de consulta. Diferenciar el titular de un departamento, su partido, su vinculación electoral y la responsabilidad de una actuación.

Las biografías institucionales describen la trayectoria pero no bastan para una evaluación. Separar actuaciones, críticas políticas, investigaciones, acusaciones, sentencias y resoluciones firmes; indicar fecha, órgano, estado procesal y respuesta documentada cuando corresponda. Una reprobación parlamentaria no es una condena. No atribuir culpabilidad por asociación. No denominar «éxito» a un resultado sin criterio y evidencia. Mantener fuentes por afirmación y fecha de revisión; no copiar artículos extensos.

## Gobiernos y Congreso

Ordenar gobiernos del más reciente al más antiguo. Distinguir legislatura, mandato presidencial y remodelación del gabinete. Intervalos de composición `[desde, hasta)` con fechas ISO: el día de relevo corresponde a la composición nueva. Diferenciar anuncio, publicación, toma de posesión y cese; citar el criterio usado. Gobierno en funciones sigue existiendo, no generar huecos artificiales. Descripciones históricas de La Moncloa son el punto de partida; contrastar límites con BOE antes de incorporar nombramientos individuales.

Organigrama: Presidencia, vicepresidencias, departamentos ministeriales y sus órganos superiores/directivos. No dibujar a todos los ministros como subordinados de una vicepresidencia. Segundo/tercer nivel requieren norma de estructura y nombramientos; no inventar relaciones. La vista temporal cambia en fechas documentadas, no interpola personas. Indicar cobertura cuando faltan biografías, retratos o niveles.

El hemiciclo identifica cámara, elección/fecha, partidos o coaliciones y fuente; sus escaños deben sumar el tamaño de la cámara de ese periodo. La distribución por candidatura electoral no equivale al grupo parlamentario posterior ni a apoyos del Gobierno. La posición de cada punto es esquemática, no el asiento físico de un diputado. No trasladar cifras de una legislatura a otra.

## Estado, privacidad y publicación

Respuestas y preferencias permanecen en memoria; no hay guardado, exportación ni recogida estadística. No añadir autenticación o persistencia sin nueva instrucción. El favicon canónico está en `/favicon.svg` y debe publicarse en la raíz del sitio.

Verificar cálculo, cobertura de contextos, referencias cruzadas, intervalos temporales y suma de escaños. Comprobar también interfaz, teclado, móvil, reducción de movimiento y temas. Construir y ejecutar las pruebas antes de publicar. Mantener fuentes y límites de cobertura visibles, sin llenar el cuestionario de texto ornamental.
