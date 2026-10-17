# Presidencias centrales: investigación de hitos, crisis y responsabilidades

Documento interno de trabajo. Abierto el **17 de octubre de 2026**, antes de iniciar la recopilación de fuentes de esta fase. La versión 0.24 presenta una selección de sus hechos y conserva sus límites de investigación.

## Encargo y alcance

Preparar una cronología extensa de las administraciones centrales de España, organizada por legislaturas y etapas presidenciales. La futura pantalla de «Gobiernos centrales» utilizará este material una vez revisado. Esta fase se dedica a la investigación y a su trazabilidad; la presentación web es el último paso.

El recorrido principal empieza en la legislatura constituyente de 1977 y llega hasta la fecha de corte de la revisión. La presidencia de Carlos Arias Navarro desde la muerte de Franco y el primer Gobierno de Adolfo Suárez se incorporarán como contexto de la transición, sin inventarles una legislatura democrática. Una legislatura puede contener más de una presidencia y una presidencia puede continuar en funciones tras su final parlamentario.

La unidad de investigación es un **hecho fechado**, no una calificación global de un presidente. Se recogerán reformas, decisiones, resultados verificables, crisis, conflictos institucionales, corrupción y resoluciones judiciales. El mismo criterio de selección y exigencia documental se aplica a todas las administraciones.

## Criterios editoriales y de atribución

1. Separar la fecha del hecho, su publicación, su descubrimiento y la resolución judicial. Un proceso conocido en una presidencia puede referirse a hechos de otra.
2. Distinguir decisión del Gobierno, aprobación parlamentaria, decisión judicial, actuación de una comunidad autónoma y circunstancia externa. Identificar autor y ámbito de responsabilidad; no atribuir automáticamente todo lo ocurrido al presidente.
3. Una ley aprobada es un hito normativo verificable. Su valoración como beneficio exige un resultado y un criterio explícitos; las controversias o efectos adversos se documentan aparte. No contar toda reforma como un «éxito».
4. Distinguir denuncia, investigación, acusación, apertura de juicio, condena recurrible, condena firme, absolución, archivo, indulto y anulación. Registrar persona, órgano, delito si consta, fecha y estado de actualización. La responsabilidad penal es individual; no se transmite por parentesco, amistad, cargo o pertenencia a un partido.
5. Separar financiación de partidos, contratación pública, enriquecimiento individual, responsabilidad contable, responsabilidad administrativa y responsabilidad política. No etiquetar toda crisis como corrupción.
6. Incluir respuestas documentadas y resoluciones posteriores que modifiquen un caso. Una imputación inicial no permanece como estado vigente si hubo archivo, absolución o anulación.
7. No fijar una cuota de entradas favorables o adversas ni una conclusión cromática anticipada. En la futura web, distinguir clase de evento y estado procesal; los colores no acreditan culpabilidad ni convierten una opinión en un resultado.
8. Evitar duplicaciones: un caso tendrá un identificador estable y varios hitos relacionados, diferenciando el desarrollo del caso de la suma de casos distintos.
9. Priorizar fuentes primarias concretas: BOE, Congreso, Senado, tribunales, organismos de fiscalización y estadísticas oficiales. Las memorias gubernamentales acreditan decisiones y declaraciones, pero no bastan para evaluar su éxito. Usar hemeroteca identificada para contexto, cronología contemporánea y contradicciones que la documentación oficial no resuelva.
10. No equiparar número de entradas con gravedad, volumen de corrupción o calidad de una presidencia. El archivo reflejará cobertura documental, duración de etapas y límites de investigación.

## Registro mínimo por hecho

- ID estable; título factual; fecha o intervalo y precisión real.
- Legislatura o legislaturas; administración de los hechos y administración en la que se conocen o resuelven.
- Tipo: institucional, normativo, económico, social, exterior, seguridad, crisis, corrupción o resolución judicial.
- Resumen verificable; alcance, protagonistas y nivel de atribución.
- Resultado acreditado y controversia, si se conocen; no completar campos con opiniones de relleno.
- Estado procesal y fecha de revisión cuando corresponda.
- Fuentes concretas con URL, organismo, fecha y afirmación respaldada.
- Relación con otros eventos y pendientes de contraste.

## Organización del expediente

- `investigacion.md`: encargo, reglas, cobertura y decisiones de método.
- `cronologia.md`: dossier legible, con hechos y referencias enlazadas.
- `etapas.json`: índice de presidencias y legislaturas, incluidos relevos e interinidades; sus rótulos anuales todavía no son intervalos jurídicos diarios.
- `eventos.json`: hechos, atribución, expedientes relacionados, resoluciones posteriores y pendientes por entrada.
- `fuentes.json`: registro de fuentes consultadas y alcance de cada una.
- `pendientes.md`: preguntas abiertas, lagunas, contradicciones y trabajo por completar.
- `comprobacion-enlaces.json`: comprobación técnica de las referencias; disponibilidad de una página no acredita la veracidad de todas sus afirmaciones.

La cronología se genera con `Gobiernos/herramientas/redactar-investigacion-presidencias.py`. Su opción `--check` valida los registros y detecta un dossier desactualizado. No consulta fuentes ni emite una evaluación histórica: la lectura y el contraste siguen siendo necesarios. `stage` identifica la administración de origen; `relatedStages` conserva alcance compartido y `stageAtMilestone` identifica la etapa de una resolución posterior. `date` es la fecha del hito descrito, no necesariamente la del hecho originario; `factsPeriod` lo distingue cuando está acreditado.

Estos archivos pertenecen a `Gobiernos/`. Las biografías y retratos siguen en `Políticos/`; las referencias personales utilizan sus IDs existentes. No mezclar este expediente con datos electorales o con el mapa autonómico.

## Presentación autorizada · versión 0.24

Tras la entrega de la primera investigación, el usuario autorizó expresamente construir el histórico político de gobiernos. La web presenta los 80 hechos conservando atribución, fechas de resolución posteriores, fuentes y pendientes; no declara concluido el barrido histórico. `presentacion.json` documenta las siete identidades, carpetas personales, fechas y criterio de duración, clasificación visual y etiquetas judiciales legibles. El código de presentación vive en `Gobiernos/interfaz/`. La franja temporal mide duración, no cantidad de escándalos ni un saldo político; las biografías no se duplican.

Para la duración se consulta la relación cronológica de Presidencia. En Sánchez se utiliza el Real Decreto 354/2018, firmado el 1 de junio y publicado el 2: la discrepancia con la tabla se conserva expresamente. El extremo abierto termina en el corte documental del 17 de octubre de 2026, sin presentarlo como cese. Los periodos anuales por legislatura siguen siendo rótulos de contexto, no duraciones calculadas.

## Plan de revisión

1. Contrastar los límites de legislaturas y etapas presidenciales y crear el índice de cobertura.
2. Recorrer las etapas desde la transición: elaborar una primera cronología documentada de reformas, resultados, crisis y casos.
3. Desarrollar cada caso en hitos procesales y actualizar las resoluciones posteriores. Revisar especialmente los expedientes abiertos próximos a la fecha de corte.
4. Hacer una segunda pasada por años y por temas para localizar omisiones. Un barrido por años no acredita una revisión semanal exhaustiva.
5. Revisar atribución, precisión de fechas, proporcionalidad descriptiva, fuentes y ausencia de duplicados.
6. Tras la autorización de presentación, publicar la selección documentada con sus límites y mantener su ampliación ligada a la revisión del expediente. No convertir la primera pantalla en una declaración de exhaustividad.

## Estado de la primera entrega · 17 de octubre de 2026

El documento de criterios se creó antes de recopilar fuentes. La primera pasada incorpora **80 hechos y 79 referencias**, con un índice de **21 etapas**, desde el contexto de Arias Navarro hasta la legislatura XV. Se han contrastado hechos base, normas y resoluciones seleccionadas; no se ha realizado todavía un barrido semanal ni una revisión exhaustiva de todos los años o de cada expediente judicial.

La cobertura incluye transición constitucional, adhesión europea y OTAN, reformas sociales y económicas, conflictos laborales, GAL, Filesa, Roldán, Gürtel, Prestige, Yak-42, Irak, 11M, asistencia bancaria, conflicto catalán, pandemia, libertad sexual, amnistía, DANA, apagón y piezas de los casos Kitchen y Koldo. **Incluir un caso no significa haber agotado su investigación.** Los límites y siguientes documentos están anotados en cada entrada y en `pendientes.md`.

Se distinguen sentencias y hechos de distintas administraciones, amparos que modifican condenas, responsabilidad civil y penal, fases de instrucción y condenas. Las novedades de mascarillas de junio y octubre de 2026 se conservan como información de agencia identificada, pendiente de incorporar los originales judiciales; la pieza de obras no hereda su resultado. La evaluación del IMV se separa de la ley que lo creó. La resolución constitucional de la amnistía se registra con sus estimaciones parciales y condiciones, no con una etiqueta absoluta.

**Investigación en curso.** Los campos `consultedAt` y `reviewedAt` fechan la consulta, no garantizan que una resolución antigua sea el estado vigente del proceso. `statusAtSource` fija la fecha real del estado documentado. Siguen pendientes profundización anual, resultados comparables, originales judiciales pendientes y actualización de causas abiertas. La presentación inicial incluye estos límites y no modifica las biografías ni los datos electorales.


## Segunda ampliación · versión 0.25

El encargo posterior exige mayor profundidad, orden inverso dentro de cada legislatura y visibilidad compartida de acontecimientos que afecten a varias presidencias. Se incorporan **200 acontecimientos desarrollados** y un catálogo separado de **3.085 disposiciones estatales**. Son niveles documentales distintos: el segundo recupera metadatos de la base general de legislación del BOE, incluidas normas derogadas, sin pretender haber evaluado sus efectos ni leído íntegramente cada artículo.

Los cinco índices de rango consultados devuelven 3.983 resultados, 3.118 documentos únicos después de reunir los solapamientos. Se excluyen normas anteriores al intervalo y las ya desarrolladas con referencia BOE o ELI. Las referencias permiten acceder al texto oficial original; no se reutiliza una versión consolidada de 2026 como si fuera la de aprobación. El índice abarca publicaciones del 20 de noviembre de 1975 al 17 de octubre de 2026.

`catalogos-boe.json` conserva el inventario recibido, consultas y huellas; `normativa.json`, registros publicados y exclusiones; `revision-normativa.json`, cobertura por años y etapas. `cobertura-semanal.json` divide todo el intervalo en **2.657 semanas** y registra qué entradas existen y qué revisión periodística falta. **No se ha realizado una lectura semanal exhaustiva de cincuenta años de hemeroteca.** El incremento cuantitativo no equivale a multiplicar treinta veces la profundidad del análisis de crisis o corrupción.

Cada hito editorial conserva un único ID. `displayStages` permite mostrarlo en otra etapa con una explicación específica; `relatedStages` y `stageAtMilestone` también permiten consulta compartida. Esta visibilidad no multiplica expedientes ni atribuye al presidente de la resolución los hechos del anterior. Las actividades de un expresidente posteriores a su mandato se indican expresamente, como en Plus Ultra.

La revisión añade fases de Bárcenas y Gürtel, Ibercorp, Roldán, CESID, Gescartera, conflictos laborales, crisis financieras, emergencias y relaciones exteriores. En las causas actuales se registran imputaciones, declaraciones, decisiones cautelares, aperturas de juicio, condenas recurribles, absoluciones parciales y defensas. Salazar se trata como crisis por denuncias de acoso, sin convertir una inadmisión procesal en un enjuiciamiento de los testimonios. Los acontecimientos no se clasifican por una cuota favorable o desfavorable.
