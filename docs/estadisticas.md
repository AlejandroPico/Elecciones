# Almacenamiento y estadísticas

## Lo que funciona en esta edición

La encuesta guarda respuestas y preferencias en `localStorage` del navegador, con versión del cuestionario. Funciona sin cuentas y sin base de datos. No hay cookies de seguimiento, envío de respuestas, servicio de estadísticas ni inicio de sesión de Google. Las fuentes tipográficas se sirven junto a la web, sin conexiones a Google Fonts.

El guardado puede fallar si el navegador bloquea el almacenamiento o no queda espacio; la encuesta sigue funcionando en memoria y avisa de la limitación. El perfil se puede exportar por decisión del usuario. Las importaciones de posiciones de partidos son temporales en memoria. Reiniciar borra las respuestas actuales y conserva preferencias.

[GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) sirve archivos estáticos y no proporciona un servidor de aplicación ni una base de datos para respuestas. Actions construye y publica la web, pero no sustituye a una API de recogida. No debemos escribir las respuestas en el repositorio: sería público, tendría historial y no es un almacén adecuado para esta información.

## Propuesta para la siguiente fase

Mantener la web en Pages y conectar una API separada con una base de datos. Una opción compatible es [Supabase](https://supabase.com/docs/guides/database/overview): dispone de PostgreSQL y servicios de autenticación y funciones. No se ha creado ni conectado ninguna cuenta en esta edición.

Flujo propuesto:

1. El usuario termina la encuesta y ve sus resultados sin enviar nada.
2. Se ofrece participación voluntaria en estadísticas, con explicación del contenido enviado. Rechazarla no impide usar la web.
3. Se envían la versión del cuestionario y las respuestas elegidas a un endpoint protegido. No se envían nombre, correo, ubicación precisa ni credenciales.
4. La API valida los identificadores y rangos, limita abusos y acumula recuentos por pregunta y respuesta en una transacción. No conserva el vector individual tras agregarlo.
5. Un panel restringido consulta totales, distribución de respuestas y omisiones. No se expone una tabla de perfiles públicos.

Tabla conceptual para los recuentos: `answer_counts(election_id, questionnaire_version, question_id, answer_code, count)`. Para promedios de ejes puede mantenerse `axis_totals(..., axis_id, sum, count)`; no mezclaremos versiones ni escalas incompatibles. Los grupos de resultados públicos necesitarían un umbral mínimo y evitar filtros que permitan aislar a una persona.

El endpoint debe impedir escrituras directas a tablas desde el cliente. Credenciales de administración solo en el servidor, permisos mínimos, control de origen, límites de tamaño y frecuencia, y acceso interno autenticado. Los registros de red del proveedor pueden incluir IP aunque nuestra tabla no la almacene; hay que configurar y describir la retención real. No se puede prometer anonimato absoluto ni una persona = una respuesta sin introducir mecanismos adicionales. La deduplicación debe acordarse antes de implementar la recogida.

Google puede añadirse para acceso opcional o sincronización, pero devuelve información de identidad. Eso exige explicar el tratamiento de esos datos y separar la cuenta de los agregados. Para esta fase no aporta nada al guardado local y se mantiene fuera del flujo.

Las estadísticas de visitantes son una muestra autoseleccionada. No equivalen a un sondeo representativo de la población o a una estimación de resultados electorales.
