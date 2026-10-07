# Elecciones

Proyecto personal de Alejandro Pico Perez. Primera convocatoria: generales de noviembre de 2026. Versión 0.3.0, actualizada el 7 de octubre de 2026.

Cuestionario de 48 preguntas piloto, 8 temas y 16 ejes. Ficha centrada de esquinas rectas, respuestas sin cajetines, importancia y omisión. Cada pregunta abre una explicación de su alcance y consideraciones en ambos sentidos. La barra inferior permite navegar, expande el tema activo y compacta los demás con transiciones suaves. Al completar un tema avanza al siguiente pendiente. Los gráficos se consultan en «Mi perfil» y usan las mismas respuestas.

Barra lateral contraíble, también en escritorio. Un único icono cambia entre automático, mañana, tarde y noche. El modo automático usa la hora del sistema; el nocturno combina azul marino y acentos cálidos. Se respeta la preferencia de reducir movimiento.

**No existe guardado ni exportación de respuestas.** Respuestas, preferencias e importaciones solo viven en memoria. Recargar empieza de nuevo. Se eliminan únicamente las dos claves locales de la versión antigua. No hay estadísticas centrales, autenticación ni recogida de respuestas.

## Contenido por convocatoria

Toda la información de la convocatoria reside en `Elecciones/Generales Noviembre 2026/`: cuestionario, contextos, partidos, biografías, actuaciones, gobiernos, estructura ampliada, Congreso, logotipos y retratos. La interfaz y el cálculo común residen en `src/`. Se entra directamente a la única convocatoria. Los nombres y la estructura de futuras carpetas se definen en [PROTOCOLOS.md](PROTOCOLOS.md).

«Programas y partidos» ofrece 15 organizaciones con recursos gráficos oficiales y enlaces internos y externos. Es un directorio: no acredita candidaturas de 2026. Solo los programas históricos del PSOE y PP de 2023 están enlazados; no alimentan la puntuación. Las listas proclamadas y posiciones documentadas de 2026 siguen pendientes.

«Archivo político» incorpora las 23 biografías del gabinete actual, formación y retratos individuales institucionales; los presidentes desde 1977 y los titulares de los gabinetes históricos tienen fichas con distinta cobertura. Las fichas incompletas lo indican. El nacimiento se muestra con la precisión de su fuente; no se inventan días para calcular una edad exacta. Hay una selección inicial de actuaciones y controversias documentadas, que distingue decisiones políticas y judiciales. No es un historial exhaustivo.

«Gobiernos» ofrece una biblioteca por legislaturas y una cronología interactiva de 72 composiciones del archivo de La Moncloa, desde julio de 1977. Permite desplazar y reproducir los cambios, abrir fichas desde el organigrama y recorrer titulares de Presidencia y Defensa. No equivale a un registro diario: los registros antiguos que solo precisan el mes se identifican así. El segundo y tercer nivel incluyen una instantánea de tres órganos de Defensa, consultada el 7 de octubre de 2026; los demás departamentos y periodos están pendientes.

El hemiciclo muestra los 350 escaños por candidatura en la elección de 2023, con fuente JEC/BOE. Es una distribución esquemática del resultado electoral, no de grupos posteriores ni de asientos físicos. Otras legislaturas quedan pendientes.

## Desarrollo y publicación

Node.js 22 o superior y pnpm 11.

```sh
pnpm install
pnpm dev
pnpm test
pnpm build
pnpm preview
```

React, TypeScript y Vite. GitHub Actions comprueba, construye y publica main en [la web](https://alejandropico.github.io/Elecciones/). Rutas relativas compatibles con /Elecciones/. Archivo y gobiernos se cargan al abrir sus secciones. El icono canónico es favicon.svg en la raíz del repositorio y se copia a la raíz de la web al construir.

Las pruebas cubren puntuación, importancia, omisiones, cobertura, importaciones, navegación por temas, referencias cruzadas, contexto de cada pregunta, relevo de marzo de 2026 y suma de escaños. La comprobación visual incluye escritorio y móvil, barra lateral, temas, contexto, fichas y organigramas.

- [Catálogo y posiciones documentadas](docs/catalogo.md).
- [Estadísticas: propuesta para una fase futura](docs/estadisticas.md).
- [Archivo político y cobertura](docs/archivo-politico.md).

[Portfolio](https://alejandropico.github.io/Portfolio/) · [Repositorio](https://github.com/AlejandroPico/Elecciones)
