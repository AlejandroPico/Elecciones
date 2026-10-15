# Mapa de presidencias autonómicas

Instantánea nominal del 16 de octubre de 2026. La portada `#/autonomias` colorea las 50 provincias y Ceuta y Melilla por la vinculación partidista de la presidencia de su comunidad o ciudad. No representa diputaciones provinciales, resultados electorales, apoyos de investidura ni el conjunto de partidos del gabinete. Las diecinueve referencias personales y las fuentes del nombramiento y de la vinculación se guardan en `presidencias.json`. El nombre completo y el retrato se enlazan con `Políticos/`, sin duplicar biografías ni imágenes.

La fecha de la ficha flotante se etiqueta **Nombramiento**: corresponde al decreto del mandato actual, no a la primera llegada a la presidencia ni a una fecha de posesión no contrastada. Se comprueba el decreto original porque las etiquetas del dosier del Senado contienen algunas erratas. Los nombramientos de 2026 de Aragón, Andalucía, Extremadura y Castilla y León están incorporados.

## Cartografía y licencia

Los contornos proceden del WFS INSPIRE de unidades administrativas del **Instituto Geográfico Nacional de España**, © IGN, **CC BY 4.0**. El archivo `procedencia-cartografica.json` conserva la consulta, crédito, enlace a licencia, fecha y SHA-256 del original. El servicio devuelve además el código 54, «Territorios no asociados a ninguna provincia»: se conserva como contexto neutro y no se le inventa una presidencia.

`cartografia.json` contiene los trazados derivados para la web. Proyección Lambert conformal cónica esférica, paralelos de 35° y 43°, meridiano de −3,5°. La simplificación conserva una tolerancia visual máxima de 0,075 unidades del viewBox 1100 × 850. Se mantienen islas y huecos; no se sustituyen contornos por polígonos dibujados a mano. Canarias y las dos ciudades utilizan encuadres propios, con Ceuta y Melilla ampliadas y separadores visibles. No comparten escala con el mapa principal.

Portugal, Francia, Andorra y Marruecos proceden de **Natural Earth, Admin 0 1:10m, dominio público**; se muestran recortados y atenuados. La cartografía y ambas licencias se consultan desde «Fuentes» en la propia vista.

Herramientas reproducibles: `Gobiernos/herramientas/preparar-mapa-autonomico.py` y `documentar-presidencias-mapa.py`. Sus descargas originales se conservan en una caché ignorada; la web y las pruebas utilizan solo los datos curados y funcionan sin acceder a esos servicios. Al actualizar, verificar las diecinueve presidencias, sus fotos y decretos y la correspondencia completa de los códigos provinciales. Las áreas transparentes de interacción permanecen inmóviles aunque el contorno visible se eleve: el efecto no debe provocar saltos del puntero. Respetar teclado, tacto y reducción de movimiento.
