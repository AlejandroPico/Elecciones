# Elecciones

Proyecto personal de Alejandro Pico Perez. Versión 0.5.0 · 7 de octubre de 2026.

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

La migración conserva los 275 identificadores anteriores, sus trayectorias y referencias. Doce identificadores duplicados se unifican mediante alias históricos. El catálogo ampliado reúne 276 personas, 64 retratos institucionales y 150 fechas de nacimiento completas. Se corrigieron nombres contaminados por notas del documento original. Wikipedia complementa datos biográficos ausentes con atribución expresa. Las fichas mantienen distinta cobertura y no son historiales exhaustivos.

«Archivo político» combina búsqueda, vinculación acreditada y orden por nombre, actividad más reciente, actividad más antigua o rango de cargo. Las tarjetas compactas muestran el nombre bajo el retrato y despliegan partido y cargos al pasar el ratón o enfocarlas con teclado. Carga más fichas al acercarse al final, sin botón adicional. La antigüedad procede de la actividad documentada, no de la edad.

«Partidos» reúne las 4.027 inscripciones que devuelve el [Registro de Partidos Políticos del Ministerio del Interior](https://servicio.mir.es/nfrontal/webpartido_politico.html) con fecha hasta el 7 de octubre de 2026, incluidas organizaciones regionales y municipales. Cada ficha conserva identidad registral, localidad y fuente. Inscripción no equivale a actividad actual ni a candidatura. Hay 45 logotipos contrastados, webs cuando han podido verificarse, búsqueda, filtro territorial y carga progresiva. Los recursos desconocidos permanecen pendientes, con identificación textual; no se inventan marcas ni se enlazan dominios antiguos reconvertidos. Las candidaturas confirmadas se presentan primero y el resto en «Otros partidos»; actualmente no se ha incorporado ninguna proclamación oficial de 2026.

Se conservan las presidencias de AP/PP desde 1979 y secretarías generales y gestoras del PSOE desde 1974, enlazadas a personas. Estas selecciones no reúnen todos los dirigentes desde la fundación ni todas las sustituciones temporales. Los programas enlazados de PSOE y PP son de 2023 y no alimentan la puntuación.

«Gobiernos» ofrece 16 legislaturas y 72 composiciones desde julio de 1977, con cronología interactiva, organigrama y fichas vinculadas. La precisión antigua puede ser mensual; no equivale a un registro diario. El segundo y tercer nivel incluyen una instantánea de tres órganos de Defensa consultada el 7 de octubre de 2026. Los demás departamentos siguen pendientes. El hemiciclo muestra los 350 escaños por candidatura en 2023, con fuente JEC/BOE; no representa grupos posteriores ni asientos físicos.

«Cargos e historia» tiene su propia entrada y 251 fichas de cargos y órganos: Gobierno, Cortes, secretarías de Estado, subsecretarías, secretarías generales, direcciones generales y otras instituciones. Las sucesiones ministeriales se derivan de las composiciones conservadas; los cargos sin historia indican que su ficha está pendiente. La estructura de órganos ministeriales usa el [Real Decreto 1009/2023](https://www.boe.es/buscar/act.php?id=BOE-A-2023-24842), actualizado el 29 de julio de 2026. Esa norma acredita órganos, no inventa biografías ni históricos de titulares.

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
