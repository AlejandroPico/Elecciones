# Ampliaciones de preguntas

Los 5.861 enunciados conservan significado, escala, condiciones y puntuación. La ampliación explica sin mostrar qué partido respalda la respuesta. Su título es la pregunta completa.

- `temas.json`: 40 marcos temáticos con explicación, ejemplo y distinciones.
- `reglas.json`: 155 explicaciones sobre instrumentos concretos (capital riesgo, avales, jornada, aborto, aforamiento, entre otros), con filtros de ámbito y prioridad para evitar confundir términos de distintos sectores.
- `glosario.json`: 159 definiciones explicativas. No es un catálogo de normas vigentes ni asesoramiento personal.
- `excepciones.json`: aclaraciones individuales por ID; contiene los 26 antecedentes ambiguos localizados en expresiones como «esa financiación» o «esos negocios».
- `generadas/<categoría>.json`: ampliaciones de cada pregunta, sin una segunda copia editable del banco. Se cargan al abrir la explicación del tema, no junto al arranque.
- `revision.json`: recuento, uso de perfiles, IDs que utilizan marco temático y límites de la revisión. Este listado permite priorizar explicaciones adicionales para propuestas que necesiten más desarrollo.

Generar con `python Cuestionario/herramientas/generar-explicaciones.py`; comprobar con `--check`. Los controles verifican cobertura exacta de IDs, huella de los enunciados, conservación de números, negaciones y ámbito, referencia al pasaje de origen y ausencia de las antiguas instrucciones genéricas. Las explicaciones combinan contenido redactado con reglas editoriales y el contexto de la propuesta de origen; no deben presentarse como una validación humana independiente de 5.861 textos ni como un instrumento psicométrico validado.

El primer párrafo reformula el enunciado manteniendo condiciones. El marco del documento se limita a la primera propuesta vinculada: no convierte en explicación de la pregunta las pruebas de partidos con posiciones contrarias. Los ejemplos aclaran mecanismos y no inventan compromisos ni resultados garantizados. Las cifras de ejemplo se identifican como tales; un porcentaje no cambia de base, kilómetros no se sustituyen por minutos y una propuesta autonómica conserva su territorio.

En el repaso se consultaron como referencias institucionales la [Guía del Poder Judicial](https://www.poderjudicial.es/cgpj/es/Poder-Judicial/Conoce-el-Poder-Judicial/Guia-del-Poder-Judicial/Guia-del-Poder-Judicial) y las explicaciones de [ACNUR sobre protección](https://www.acnur.org/proteccion) y [personas refugiadas](https://www.acnur.org/es-es/refugiados). Los originales y referencias de cada programa permanecen en el banco documental y en sus carpetas electorales. Estas referencias no se presentan como certificación de todas las definiciones.

Para mejorar un caso concreto, añadir una entrada por ID en `excepciones.json`, sin tocar el archivo generado. Puede incluir `lead`, `paragraphs` o `terms`. Aclarar el antecedente, definir vocabulario y distinguir instrumentos sin expresar superioridad moral de una respuesta. Regenerar y comprobar antes de publicar.

Para las explicaciones monetarias se consultó la [explicación del BCE sobre tipos de interés](https://www.ecb.europa.eu/ecb-and-you/explainers/html/interest-rates-changes.es.html). Se distingue su transmisión al crédito y al ahorro de una modificación de impuestos; no se presenta una propuesta de 2023 como decisión vigente.
