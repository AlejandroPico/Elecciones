# Archivo de personas, partidos y cargos

El archivo informativo es independiente del cálculo del cuestionario. Tiene seis fichas personales iniciales, dos partidos y dos secuencias recientes de cargos. La selección sirve para establecer el formato y la navegación; no es una relación completa de políticos, partidos, dirigentes ni candidatos de 2026.

## Relaciones y navegación

La siguiente fase deberá presentar jerarquías por gobierno y etapa, con navegación en forma de árbol entre cargos, personas y partidos. Cada ficha se ampliará con estudios documentados, trayectoria política completa y actuaciones. Los éxitos, controversias o escándalos requerirán fuentes, fechas, atribución y estado de cada expediente; no se convertirán valoraciones en hechos. Esta ampliación no está implementada en la versión 0.2, dedicada a rehacer la encuesta y su estructura.

En `Elecciones/Generales Noviembre 2026/archivo-politico.ts` hay entidades con identificadores estables:

- `people`: nombre, vinculación documentada, función, resumen, etapas, fuentes, fotografía y crédito.
- `organizations`: denominación, fundación, documentación, selección histórica y fuentes.
- `offices`: cargo e intervalos de titulares, con enlaces a las fichas.
- `candidacies`: elección, cámara, circunscripción, orden en la lista, suplencia y fuente de proclamación. Vacío hasta incorporar listas oficiales.

La interfaz permite buscar nombres, partidos y cargos; filtrar por vinculación; recorrer una ficha de partido y sus personas; consultar documentos; navegar entre titulares de un cargo; y volver por el historial de fichas. El ejemplo de Defensa comprende Margarita Robles, María Dolores de Cospedal y Pedro Morenés. La Presidencia comprende Sánchez y Rajoy y enlaza la relación oficial más extensa.

Un partido, una coalición electoral, un grupo parlamentario y una afiliación individual no son la misma entidad. Los políticos sin afiliación acreditada no deben recibir la del Gobierno en el que participan. Se debe distinguir militancia, vinculación electoral y cargo público, y fechar cada relación cuando se amplíe el modelo.

## Fuentes y neutralidad editorial

Cada etapa y documento tiene referencias. El catálogo inicial utiliza La Moncloa, BOE, Congreso, Senado y Ministerio de Defensa. Los datos históricos procedentes de páginas de partidos se identifican como información publicada por el propio partido, no como una valoración independiente.

Los PDF de programas del PSOE y PP incorporados son de las generales de julio de 2023, con enlace al original. Se ofrecen para abrir y descargar como documentos históricos. No se usan para puntuar el banco piloto ni se presentan como programas de 2026.

Los resúmenes actuales enumeran cargos, no evalúan logros ni omiten deliberadamente controversias de un supuesto historial completo. La capa de actuaciones necesita una colección separada: fecha, tipo de actuación, órgano, responsabilidad de la persona, disposición o expediente, resultado y fuentes. Debe diferenciar propuesta, voto, norma aprobada, ejecución y resultado. Las valoraciones y alegaciones no se presentarán como hechos sin atribución.

Para completar dirigentes desde la fundación y candidaturas hay que ampliar el catálogo con todas las entradas documentadas, sin limitarlo a partidos grandes o cabezas de lista. Un puesto en una lista no acredita un nombramiento ministerial. Las listas oficiales son territoriales: no existe una única lista nacional del Congreso que permita atribuir el mismo orden a todas las circunscripciones.

## Imágenes

Las fotografías iniciales se conservan en `Elecciones/Generales Noviembre 2026/retratos/` y se sirven localmente, con origen y crédito visibles en cada ficha. La de Morenés es un acto institucional, identificado en el pie. Si falta un retrato o falla la carga, aparece una tarjeta de iniciales indicando que el retrato está pendiente; no se inventa una fotografía.

Fuentes de las imágenes:

- Sánchez: biografía de La Moncloa, Pool Moncloa / Carlos Spottorno de las Morenas.
- Feijóo: ficha del Senado, XIV legislatura; el retrato no acredita su cargo actual.
- Robles: biografía institucional de La Moncloa, 2023.
- Rajoy: archivo de presidentes de La Moncloa.
- Cospedal: ficha del Senado, IX legislatura.
- Morenés: fototeca del Ministerio de Defensa, toma de posesión de 2011; crédito «Ministerio de Defensa de España».

Las fechas y estados abiertos se revisaron el 6 de octubre de 2026. «Actualidad» se refiere a esa fecha de corte, no a una actualización automática. El archivo deberá revisarse tras la elección y cada cambio de Gobierno. El cuestionario no necesita una conexión en directo para mostrar este catálogo.
