# Elecciones

Cuestionario de posiciones políticas por temas. Proyecto personal de Alejandro Pico Perez, creado el 6 de octubre de 2026.

Primera versión: 48 preguntas piloto, 8 temas, 16 ejes, gráficos de coordenadas y vista radial en directo, importancia de las respuestas, revisión, omisiones, progreso local y exportación. Incluye modos mañana, tarde, noche y automático por zona horaria, adaptación a móvil, navegación por teclado y respeto a la preferencia de movimiento reducido.

El banco es una muestra editorial pendiente de revisión. Todavía no se han codificado posiciones de programas reales ni se incluye un catálogo oficial de candidaturas, Google o estadísticas centrales. Se pueden importar posiciones documentadas en JSON para probar las superposiciones y coincidencias. Las ausencias de evidencia no se puntúan como neutralidad.

El archivo político ofrece seis fichas personales iniciales, dos partidos y navegación entre titulares de la Presidencia y Defensa. Incluye fuentes primarias, fotografías con crédito y programas históricos de 2023 para abrir y descargar. Las biografías y esos documentos históricos no acreditan candidaturas de 2026 ni alimentan el cálculo de afinidad.

## Desarrollo

Node.js 22 o superior y pnpm 11.

```sh
pnpm install
pnpm dev
pnpm test
pnpm build
pnpm preview
```

React + TypeScript + Vite. La salida estática queda en `dist/`, con rutas relativas para poder publicarse bajo `/Elecciones/` o en otro directorio. El icono canónico es [`favicon.svg`](favicon.svg) en la **raíz del repositorio**; el proceso de construcción lo copia como `dist/favicon.svg`, disponible en la raíz de la web para el portfolio.

## Publicación

El flujo `.github/workflows/pages.yml` valida y construye en cada cambio de `main`, y después publica en GitHub Pages. En las solicitudes de cambios ejecuta solo la validación. La configuración del repositorio debe tener **Settings → Pages → Source → GitHub Actions**. Si Pages no está habilitado, la validación puede pasar pero el despliegue fallará hasta habilitarlo.

No se deben guardar respuestas de visitantes en Git ni en Actions. La versión actual funciona completamente en el navegador. Véase [propuesta de estadísticas](docs/estadisticas.md) para añadir una API y un almacén de agregados separados.

## Datos y metodología

- [`src/data.ts`](src/data.ts): preguntas, categorías, ejes y metadatos de convocatoria.
- [`src/model.ts`](src/model.ts): puntuación, cobertura, comparación, validación de importaciones y restauración.
- [Guía editorial y formato de posiciones](docs/catalogo.md).
- [Almacenamiento y siguiente fase de estadísticas](docs/estadisticas.md).
- [Archivo de personas, partidos y cargos](docs/archivo-politico.md).

Las pruebas comprueban extremos, ponderación, inversión de dirección, omisiones, cobertura, referencias obligatorias e incompatibilidad de sesiones. Las opiniones políticas se almacenan localmente, sin cuentas; el alojamiento puede registrar datos técnicos de visitas.

El «Acerca de» sigue la estructura de los proyectos TMB y Cosmocronia: autor, versión, fechas, funcionamiento y enlaces.

[Portfolio](https://alejandropico.github.io/Portfolio/) · [Repositorio](https://github.com/AlejandroPico/Elecciones)
