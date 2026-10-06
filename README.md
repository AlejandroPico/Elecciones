# Elecciones

Proyecto personal de Alejandro Pico Perez. Primera convocatoria: generales de noviembre de 2026. Versión 0.2.0, actualizada el 7 de octubre de 2026.

Interfaz con barra lateral, ficha centrada de esquinas rectas y navegación inferior por preguntas y temas. El tema activo expande sus segmentos; los demás se compactan. Al resolver la última pregunta pendiente de un tema se expande el siguiente con preguntas pendientes. Las flechas y segmentos permiten recorrer las preguntas sin controles de navegación dentro de la ficha. Gráfica desplegable a la derecha; mapa de dos ejes y vista radial. La importancia y las omisiones se conservan durante la visita.

**No existe guardado ni exportación de respuestas.** Respuestas, preferencias e importaciones solo viven en memoria. Recargar empieza de nuevo. Al abrir la edición se eliminan las dos claves locales de la versión anterior, sin acceder a otros datos del navegador. No hay estadísticas centrales ni Google. El modo automático usa la hora del sistema; la apariencia se cambia con iconos, sin selector de ciudades.

## Contenido por convocatoria

```
Elecciones/
  index.ts
  Generales Noviembre 2026/
    cuestionario.ts
    archivo-politico.ts
    retratos/
    README.md
src/                         # interfaz y cálculo compartidos
```

Los 48 enunciados piloto, 8 temas, 16 ejes, metadatos y fichas están dentro de la carpeta de la elección. No se muestra mosaico: se entra directamente a la única convocatoria. Las futuras autonómicas o generales tendrán sus propias carpetas y datos.

El archivo político sigue siendo un catálogo parcial de seis personas, dos partidos y dos secuencias de cargos. Su ampliación a jerarquías, gobiernos, estudios y actuaciones queda para otra fase, con fuentes documentadas. Los PDF enlazados son programas históricos de 2023; no acreditan candidaturas de 2026 ni generan puntuaciones. No se han incorporado posiciones electorales reales.

## Desarrollo y publicación

Node.js 22 o superior y pnpm 11.

```sh
pnpm install
pnpm dev
pnpm test
pnpm build
pnpm preview
```

React, TypeScript y Vite. GitHub Actions comprueba, construye y publica los cambios de `main` en [la web](https://alejandropico.github.io/Elecciones/). La salida usa rutas relativas para `/Elecciones/`. El icono canónico es `favicon.svg` en la raíz del repositorio y se copia a la raíz de la web al construir.

Las pruebas cubren puntuación, ponderación, omisiones, cobertura, validación de posiciones, referencias del archivo y navegación con temas de distinto tamaño. La comprobación visual incluye escritorio, móvil, cambio de tema y pérdida de respuestas tras recargar.

- [Catálogo y posiciones documentadas](docs/catalogo.md).
- [Estadísticas: propuesta para una fase futura](docs/estadisticas.md).
- [Archivo político](docs/archivo-politico.md).

[Portfolio](https://alejandropico.github.io/Portfolio/) · [Repositorio](https://github.com/AlejandroPico/Elecciones)
