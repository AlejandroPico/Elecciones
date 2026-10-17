# Revisión de presidencias · 0.25

Corte documental: 17 de octubre de 2026.

## Contenido y procedencia

- 200 acontecimientos desarrollados y 185 fuentes editoriales; la primera selección tenía 80 acontecimientos y 79 fuentes.
- 3.085 disposiciones estatales catalogadas por título, rango, departamento emisor y fecha de publicación. Su categoría es «Leyes y medidas», diferenciada del análisis de efectos. Total canónico: 3.285 entradas.
- 3.983 resultados de cinco consultas al BOE, 3.118 documentos únicos tras deduplicar y 33 exclusiones por periodo o por estar ya desarrollados con referencia BOE/ELI.
- 2.657 semanas registradas de forma continua, con referencias normativas/editoriales y estado de revisión hemerográfica pendiente. El registro no demuestra revisión íntegra semana a semana.
- Las disposiciones y sus metadatos proceden de la base general de legislación, no solo de la colección consolidada ni de normas vigentes. El importador rechaza respuestas incompletas en vez de publicar una primera página como catálogo completo.

## Cambios de consulta

El orden predeterminado es descendente entre presidencias y legislaturas y dentro de cada etapa. El selector lo invierte conjuntamente y los empates se resuelven por ID estable. Se añaden materia y año; la búsqueda actúa antes de la carga progresiva.

Los hitos compartidos conservan un único registro y se presentan en las etapas vinculadas. Las tarjetas tienen identificador de etapa y evento para evitar IDs de pantalla duplicados. La relación biográfica de antiguos ministros o la fecha de una sentencia no transmite culpabilidad al presidente. Plus Ultra aparece en Zapatero con aviso de actividad posterior al mandato y en las etapas de Sánchez relacionadas con el rescate y la investigación.

## Alcance histórico

Se amplían democratización y violencia política de la Transición, mociones e investiduras, huelgas, crisis financieras, emergencias sanitarias y naturales, espionaje y conflictos diplomáticos. Se desarrollan fases de los casos Juan Guerra, Filesa, Roldán, Ibercorp, CESID, Gescartera, Bárcenas, Gürtel, Génova, Púnica, Lezo, Faisán, Campeón, tarjetas black, Palma Arena y Erial. Las causas de 2026 incluyen fallos, recursos, defensas y distinción entre investigaciones diferentes.

La profundidad de la revisión sigue siendo desigual. El incremento total se debe principalmente al catálogo normativo: no equivale a treinta veces más análisis de corrupción ni a una hemeroteca completa. Los pendientes continúan en `pendientes.md`.

## Comprobaciones

La batería completa ha superado 142 pruebas en 38 archivos. La validación del expediente comprueba fuentes, fechas, etapas, vínculos, continuidad del registro semanal y la correspondencia de la cronología generada.

Se ha repetido una consulta orgánica con el importador reproducible: 397 resultados, coincidentes con el inventario. Las 106 referencias nuevas tienen comprobación técnica en `comprobacion-enlaces-0.25.json`: 104 responden y dos referencias de EFE y El País limitan al cliente directo con HTTP 403. Ambas noticias se han localizado en el buscador; el error de acceso directo no se oculta ni se sustituye por una supuesta lectura del fallo original.

La compilación local y la comprobación visual de escritorio y móvil han superado la revisión: orden, filtros, carga progresiva, vínculos compartidos, fuentes y vuelta desde biografías. El último añadido de datos del SMI se comprueba además en el despliegue automático antes de cerrar la publicación.

La ampliación incluye 28 importes anuales del salario mínimo para 1999–2026 contrastados en el artículo 1 original de cada decreto; `salarios-minimos.json` conserva consulta y extractos oficiales. Se distingue mes de publicación y año de efectos, pesetas y euros, cantidad nominal y poder adquisitivo. La colección anual no enumera todas las modificaciones intranuales.
