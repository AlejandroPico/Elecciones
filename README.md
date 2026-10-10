# Elecciones

Proyecto personal de Alejandro Pico Perez. Versión 0.11.1 · 10 de octubre de 2026.

La Comunitat Valenciana incorpora el Consell y Les Corts desde 1983: catorce etapas presidenciales, once legislaturas y 669 fichas institucionales consultadas. La revisión complementaria fecha las carteras de las doce primeras etapas mediante 95 eventos contrastados del DOGV, incorpora 69 intervalos históricos de la Mesa y recupera 14 de los 18 retratos pendientes. El Consell actual y los 99 diputados vigentes tienen fotografía. Cada mandato, grupo, cargo, comisión y fuente vive en su carpeta correspondiente. Cobertura y límites en [el archivo valenciano](Gobiernos/Autonomías/Comunitat%20Valenciana/README.md).

Madrid incorpora Gobierno y Asamblea desde 1983, con trece legislaturas, catorce etapas del Ejecutivo y las fichas personales enlazadas. Comparte cronología, organigrama y visor parlamentario con Cataluña. Las fuentes históricas que no permiten reconstruir una composición diaria se presentan como archivo nominal, con sus limitaciones documentadas en `Gobiernos/Autonomías/Madrid/README.md`. El menú lateral permite recorrer las autonomías con rueda, tacto y teclado, sin barra visual y con indicación de contenido pendiente.

Cuestionario de 48 preguntas piloto, 8 temas y 16 ejes. Ficha centrada de esquinas rectas, respuestas sin cajetines, importancia y omisión. Cada pregunta permite ampliar su contexto. «Mi perfil» se actualiza con las respuestas. Al responder, una microbarra de tres segundos permite ajustar la importancia antes del avance automático. Cambiar la respuesta o la importancia no reinicia ese plazo; navegar cancela el avance pendiente. La última respuesta abre el perfil.

El favicon abre y cierra la barra lateral manteniendo su imagen. «Cuestionario» despliega «Consultar cuestionario» y «Nueva encuesta». El control inferior de apariencia alterna automático, mañana, tarde y noche con texto e icono. El modo automático usa la hora del sistema. Se respeta la reducción de movimiento.

La barra inferior es fina, con nombre de tema y número de pregunta. El tramo activo muestra una línea continua con crecimiento suave; las preguntas siguen siendo navegables por separado. Los otros temas se compactan conservando sus respuestas: rojo para desacuerdo, verde para acuerdo, gris para neutral y el acento de la apariencia para omisión. El grosor representa la importancia.

**No existe guardado ni exportación de respuestas.** Respuestas, preferencias e importaciones solo viven en memoria; recargar empieza de nuevo. Se eliminan únicamente las dos claves locales de una versión anterior. No hay estadísticas centrales, autenticación ni recogida de respuestas.

## Organización

- `Elecciones/Generales Noviembre 2026/`: cuestionario, contextos, candidaturas y resultado del Congreso usado como referencia.
- `Políticos/<Nombre completo>/`: ficha, datos personales, formación, trayectoria, actuaciones, fuentes y retrato de cada persona.
- `Partidos/<Nombre completo>/`: ficha, historia, dirigentes, programas históricos, fuentes y logotipo.
- `Gobiernos/<legislatura>/`: composiciones y estructura documentada; `Gobiernos/Cargos/<cargo — departamento>/`: fichas de cargos y órganos.
- Cada dominio contiene su código en `interfaz/`. Cuestionario y perfil pertenecen a `Elecciones/interfaz/`; archivo, partidos y gobiernos a sus respectivas carpetas raíz.
- `src/app/`: interfaz común; `src/main.tsx` y `src/vite-env.d.ts`: arranque y tipos del entorno.

El catálogo descubre las carpetas al compilar. La presentación vertical solo muestra apartados con datos. No hay un segundo índice manual de nombres. Se entra directamente a la única convocatoria; el mosaico de elecciones sigue pendiente. Patrones, formatos, fuentes y reglas de migración en [PROTOCOLOS.md](PROTOCOLOS.md).

La primera revisión individual de 8 de octubre de 2026 repasa las 276 fichas existentes, reúne nueve duplicados y añade 33 dirigentes nacionales y autonómicos: 300 personas con retrato local identificado, 295 fechas de nacimiento completas y formación documentada en 292 fichas. Conserva todas las identidades anteriores mediante alias y todos sus recursos gráficos; el informe está en `Políticos/revisiones/2026-10-08/`. Cada carpeta contiene sus fuentes y `revision.json`, con correcciones y datos pendientes. Wikipedia complementa las fuentes institucionales con atribución expresa. No se inventan fechas completas, títulos académicos ni militancia; los historiales mantienen distinta cobertura y no constituyen un censo exhaustivo de España.

La ampliación parlamentaria incorpora las 3.023 identidades del archivo del Congreso y las 2.521 del Senado desde 1977. Tras reunir personas que aparecen en ambas cámaras, el catálogo contiene **5.114 personas y 5.108 retratos**. Las seis ausencias quedan identificadas en `Políticos/revisiones/2026-10-08-parlamento/informe.json`. Cada mandato del Congreso conserva alta, baja, circunscripción y candidatura. En el Senado se distinguen fechas personales del mandato y límites generales de la legislatura; no se sustituyen unas por otras. Se conservan las 300 fichas anteriores, los IDs alternativos y sus recursos. Las discrepancias biográficas se explican junto al dato y sus fuentes. La formación electoral acredita candidatura, no militancia actual.

«Archivo político» combina búsqueda, vinculación acreditada y orden por nombre, actividad más reciente, actividad más antigua o rango de cargo. La búsqueda incluye nombres habituales y todos los cargos documentados. El filtro consulta cambios de partido y federaciones regionales; las fichas diferencian militancia, colaboración electoral e independencia documentada. Las tarjetas compactas muestran el nombre bajo el retrato y despliegan partido y cargos al pasar el ratón o enfocarlas con teclado. Carga más fichas al acercarse al final, sin botón adicional. La antigüedad procede de la actividad documentada, no de la edad.

«Partidos» reúne las 4.027 inscripciones que devuelve el [Registro de Partidos Políticos del Ministerio del Interior](https://servicio.mir.es/nfrontal/webpartido_politico.html) con fecha hasta el 7 de octubre de 2026, incluidas organizaciones regionales y municipales. Cada ficha conserva identidad registral, localidad y fuente. Inscripción no equivale a actividad actual ni a candidatura. Hay 260 logotipos documentados, 172 webs y 517 enlaces a documentación pública: programas, estatutos, historia, transparencia y organización. Se contrastan 484 identidades con fuentes adicionales y se descartan 22 coincidencias homónimas. Búsqueda, filtro territorial, cobertura y orden por escaños, votos, nombre o antigüedad. El orden inicial usa el resultado oficial del Congreso de 2023, conservando separadas las coaliciones y sus integrantes; los resultados desconocidos no se interpretan como cero. Fundación e inscripción son fechas distintas. Carga progresiva. Los recursos desconocidos permanecen pendientes, con identificación textual; no se inventan marcas ni se enlazan dominios antiguos reconvertidos. Las candidaturas confirmadas se presentan primero y el resto en «Otros partidos»; actualmente no se ha incorporado ninguna proclamación oficial de 2026.

Se conservan las presidencias de AP/PP desde 1979 y secretarías generales y gestoras del PSOE desde 1974, enlazadas a personas. Estas selecciones no reúnen todos los dirigentes desde la fundación ni todas las sustituciones temporales. Los programas están fechados por convocatoria y no alimentan la puntuación. Los de 2023 no se presentan como programas de 2026.

«Gobiernos» ofrece 16 legislaturas y 72 composiciones desde julio de 1977, con cronología interactiva, organigrama y fichas vinculadas. La precisión antigua puede ser mensual; no equivale a un registro diario. El segundo y tercer nivel incluyen una instantánea de tres órganos de Defensa consultada el 7 de octubre de 2026. Los demás departamentos siguen pendientes. El Congreso tiene ahora una sección propia, con mandatos individuales y adscripciones fechadas desde 1977.

«Cargos e historia» tiene su propia entrada y 251 fichas de cargos y órganos: Gobierno, Cortes, secretarías de Estado, subsecretarías, secretarías generales, direcciones generales y otras instituciones. Las sucesiones ministeriales se derivan de las composiciones conservadas; los cargos sin historia indican que su ficha está pendiente. La estructura de órganos ministeriales usa el [Real Decreto 1009/2023](https://www.boe.es/buscar/act.php?id=BOE-A-2023-24842), actualizado el 29 de julio de 2026. Esa norma acredita órganos, no inventa biografías ni históricos de titulares.

Atrás y Adelante del navegador recorren secciones, fichas de personas, partidos, cargos y composiciones de gobierno. Cada ficha tiene una dirección propia que permite recargarla o compartirla. Al volver al directorio se mantienen los filtros y la carga progresiva. La ficha personal solo reúne sus propios cargos y periodos; el historial completo de titulares pertenece a «Cargos e historia».

## Desarrollo y publicación

Node.js 22 o superior y pnpm 11.

```sh
pnpm install
pnpm dev
pnpm test
pnpm build
pnpm preview
```

React, TypeScript y Vite. GitHub Actions valida y publica main en [la web](https://alejandropico.github.io/Elecciones/). Partidos, archivo y gobiernos se cargan al abrir sus secciones. Rutas relativas compatibles con `/Elecciones/`. `favicon.svg` es el icono canónico en la raíz del repositorio y se copia a la raíz del sitio al construir.

Las pruebas cubren cálculo, importancia, omisiones, importaciones, navegación, avance de tres segundos, contexto, ordenación, identidad registral, relaciones, conservación de identidades, apartados ausentes, cumpleaños, relevos y suma de escaños. La revisión visual verifica escritorio, teclado, carga progresiva, recursos gráficos y ausencia de desbordamientos móviles.

- [Preguntas, posiciones y fuentes](docs/catalogo.md).
- [Estadísticas para una fase futura](docs/estadisticas.md).
- [Archivo político y cobertura](docs/archivo-politico.md).

[Portfolio](https://alejandropico.github.io/Portfolio/) · [Repositorio](https://github.com/AlejandroPico/Elecciones)

## Actividad y Senado

Personas y partidos priorizan actividad documentada, después los casos por confirmar y finalmente el archivo histórico. La prioridad se conserva con cualquier orden secundario y con los filtros. No se utiliza la edad, la ausencia de fotografía ni la inscripción registral para inferir retirada o actividad. Una disolución de las Cámaras no convierte automáticamente a sus integrantes en retirados. Los criterios contrastados se conservan en `actividad.json` junto a cada ficha, con fuentes y fecha; las biografías explican su alcance.

«Gobiernos centrales» despliega «Gobierno», «Congreso» y «Senado». El Senado ofrece las 16 legislaturas desde 1977, con Presidencia, vicepresidencias, secretarías de la Mesa, portavoces de grupos, presidencias de comisión y mandatos individuales. Las composiciones se guardan en `Gobiernos/Senado/<legislatura>/`, sus herramientas en `Gobiernos/herramientas/` y sus informes en `Gobiernos/revisiones/`. `mandatos-senado.json` y `cargos-senado.json` pertenecen a la carpeta de cada persona. El historial del navegador conserva el punto elegido.

La cronología utiliza altas y bajas individuales, con baja inclusiva. No inventa fechas de cargo. El Pleno agrupa la última adscripción publicada para cada mandato; no reconstruye traslados internos sin fechas. La XV legislatura se representa antes de su disolución. Todos los cargos propios de una persona se reúnen en un único apartado de relaciones, incluidos los cargos del Senado.


## Congreso y menú autonómico · 0.8

El Congreso reúne 6.323 mandatos de las 16 legislaturas desde la Constituyente, 125 grupos parlamentarios y 6.547 adscripciones fechadas. Cada posición del hemiciclo identifica al diputado, grupo, circunscripción y periodo, con enlace a su ficha y a la fuente oficial. Incluye búsqueda, filtro de grupo, legislatura, etapa del Ejecutivo, cronología y reproducción. El último Pleno documentado es el del 5 de octubre de 2026; no se confunde con la Diputación Permanente tras la disolución.

La distribución es **esquemática**, no un plano de asientos físicos. El plano público del Congreso muestra actualmente el aviso de disolución y no aporta matrices históricas de ubicaciones. No se inventan números de asiento. Las fechas individuales pueden dejar posiciones sin mandato acreditado; se indican expresamente. La III legislatura contiene coincidencias temporales de hasta 352 mandatos en la fuente: se conservan y señalan, sin recortar personas para forzar una suma. Las fechas de pertenencia a un grupo no acreditan militancia en un partido.

`Gobiernos/Congreso/<ordinal> Legislatura/` contiene composiciones y fuentes. La carpeta Constituyente se llama `Legislatura Constituyente`. En cada carpeta de `Políticos/` están `mandatos-congreso.json`, `grupos-congreso.json` y, cuando corresponde, `cargos-congreso.json`. Se contrastaron quince mandatos con variantes de nombre y fechas de nacimiento coincidentes en dos fichas oficiales; la revisión se conserva en `Gobiernos/revisiones/2026-10-08-congreso/`. Los cargos de la Mesa se integran en la única sección personal «Relaciones por cargo».

«Gobiernos autonómicos» ofrece las 17 comunidades y Ceuta y Melilla, con Gobierno y Parlamento (Asamblea en las ciudades). Cataluña, Madrid y la Comunitat Valenciana tienen contenido documentado; los demás territorios conservan sus rutas pendientes. «Cargos e historia» conserva su entrada independiente. El historial permite volver desde una ficha al punto parlamentario que se estaba consultando.

## Hemiciclos y Cataluña · 0.9

Congreso, Senado y Parlament comparten un visor de ancho completo: seleccionar una persona no desplaza el diagrama. Debajo se reúnen los filtros compactos y una ficha breve sin scroll interno. Tiene zoom de 100 a 400 % con rueda centrada en el puntero (reducir desde el 100 % desplaza la página), arrastre, recorrido con teclado, búsqueda y selección simultánea de grupos. El contador muestra las coincidencias sobre el total documentado. La Mesa queda bajo el hemiciclo. Gobierno, Congreso y Senado mantienen el selector horizontal de legislaturas en ambas vistas, sin un segundo desplegable de legislatura.

El archivo de Cataluña consulta las **1.073 fichas individuales** disponibles en el Parlament e incorpora **14 registros de legislaturas** desde 1980 y **15 etapas del Govern** desde el gobierno provisional de 1977. El Parlament publica un registro conjunto de XIII y XIV: se conserva esa cobertura, sin dividirla por conjetura. Cada periodo guarda mandatos, Mesa, grupos o competencias y sus fuentes en `Gobiernos/Autonomías/Cataluña/`. El Govern procede del dossier institucional DT02, con nombramientos y ceses documentados, incluidas las sustituciones y el relevo de Derechos Sociales de julio de 2026. Los límites de cuadro sin cese individual se identifican expresamente. Los cambios de 2017–2018 distinguen nombramiento y toma de posesión.

La XV legislatura catalana se muestra como registro nominal vigente consultado el **8 de octubre de 2026**, con 135 personas. No se atribuye esa lista a fechas anteriores sin registros fechados. Los históricos conservan altas, bajas y cambios de adscripción publicados; un grupo parlamentario no acredita militancia. Los nuevos datos personales, retratos y cargos propios viven en cada carpeta de `Políticos/`; se conservan identidades anteriores y se contrastan variantes nominales. Los retratos de Commons incluyen autor y licencia. La revisión de cobertura y las ausencias se conservan en `Gobiernos/revisiones/2026-10-08-catalunya/informe.json`.
