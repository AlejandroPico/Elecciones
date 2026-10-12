# Andalucía

Revisión de 12 de octubre de 2026. Gobierno y Parlamento comparten la presentación,
cronología, navegación y visor de las otras comunidades. Cada cargo enlaza con la
carpeta personal de su titular; las fuentes y los recursos permanecen en el dominio.

## Cobertura

- **16 etapas presidenciales** de la Junta, desde Escuredo en 1982 hasta Moreno III.
  Se incluyen Rodríguez de la Borbolla I–II, Chaves I–VI, Griñán I–II, Díaz I–II y
  Moreno I–III. El periodo preautonómico de 1978–1982 queda fuera de esta incorporación.
- **13 legislaturas**, desde la sesión constitutiva de 21 de junio de 1982 hasta
  la XIII de 11 de junio de 2026. Se consultaron las **1.602 fichas por legislatura**
  del archivo del Parlamento, con 860 identificadores institucionales.
- **894 personas vinculadas** a estas fuentes: 221 fichas anteriores conservadas
  y 673 incorporaciones. Tres personas tienen más de un identificador parlamentario;
  se conserva una sola ficha personal con todas sus referencias.
- **109 diputados vigentes**, con grupos de 53, 28, 15, 8 y 5 miembros, según la
  consulta institucional. Todos tienen retrato, como los 14 miembros del Consejo
  de Gobierno vigente. El Gobierno tiene tres vicepresidencias según el decreto
  de nombramiento de 9 de julio de 2026.
- Mesas, Diputación Permanente, portavocías y **10.403 registros de participación
  en órganos** publicados en las fichas, incluidos los cargos de comisión.
- **655 retratos incorporados**, sin modificar los originales. Se conservan los
  retratos anteriores. Quedan 18 figuras históricas sin retrato contrastado, enumeradas
  en el informe de revisión; la ausencia de fotografía no significa falta de trayectoria.

## Fechas y composición

Las listas históricas contienen todas las personas que participaron durante una
legislatura, incluidas las sustituciones. No publican el intervalo individual del
mandato de diputado. Las legislaturas I–XII ofrecen un **hemiciclo de la composición archivada**,
extraída del listado que la Cámara separa de quienes causaron baja. Las doce
incluyen personas y grupos documentados; la VIII identifica 108 personas de las
109 posiciones y no se inventa el titular restante. La XI conserva las doce
personas cuyo grupo no aparece publicado, sin atribuirles una militancia.

La fuente no fecha esa composición: se identifica como referencia de la
legislatura y no como un Pleno del día del selector. Los 118–139 participantes,
incluidas las sustituciones, permanecen en un listado desplegable. Las sesiones
constitutivas delimitan la biblioteca; no se confunden con las fechas de
disolución ni con el alta personal. Los datos temporales desconocidos siguen
siendo nulos. `archivedComposition` no sustituye los mandatos fechados.

La XIII ofrece el hemiciclo de la **composición consultada el 12 de octubre**. No
se proyecta esa lista hacia fechas anteriores. La distribución de los puntos es
esquemática, no un plano de asientos físicos.

Las Mesas sí publican altas y bajas individuales. Se conserva el relevo del 23
de julio de 2026 de Jesús Ramón Aguirre por Ana Mestre, y los demás cambios. Las
bajas y altas que coinciden en el mismo día se representan con fin exclusivo.
Los representantes de grupos con voz y sin voto se identifican como tales, junto
a los siete cargos electos; no se suman como vicepresidencias o secretarías.

Los nombramientos, ceses, reformas y suplencias del Consejo de Gobierno proceden
del BOJA. Las cláusulas de efectos tienen prioridad sobre la fecha de publicación.
Cuando solo consta la fecha del acto se explica ese criterio: **no se inventa una
toma de posesión**. Las etapas antiguas sin ceremonia contrastada empiezan en la
fecha documental indicada en sus notas. Los intervalos se cierran con el cese
individual o la siguiente composición documentada, manteniendo los gobiernos en
funciones. Las normas consultadas no constituyen una auditoría exhaustiva de todos
los órganos y cargos inferiores de la Junta.

Se documentan, entre otras, las suplencias tras la salida de IU en enero de 2015,
Agricultura en mayo de 2024, Salud en octubre de 2025 y Universidad en junio de
2026 tras el fallecimiento de José Carlos Gómez Villamandos. Las correcciones de
denominación de las consejerías de 2022 se conservan con sus fuentes.

## Identidad, biografía y retratos

El archivo individual del Parlamento tiene prioridad para enlazar identidades.
No se fusionan personas por parecido de apellidos. Las variantes abreviadas de
los decretos se contrastan expresamente y se registran en `identidades.json`.
Las erratas «Griñón», «Luis Pizarro Fernández» y «Jesús Ramón García Muñoz» se
contrastan con las fichas individuales y los actos posteriores; no generan nuevos
titulares ficticios. Las grafías de la fuente original permanecen en el corpus.

La memoria institucional del XXV aniversario aporta datos biográficos breves de
439 personas, con página de procedencia. Se extraen hechos y títulos académicos,
sin reproducir el relato completo ni consultar declaraciones patrimoniales. Nueve
fechas de nacimiento discrepan con fichas anteriores: se conservan los datos
previos y las discrepancias se enumeran, sin resolverlas por conjetura.

Una adscripción parlamentaria no acredita militancia. Las vinculaciones partidarias
solo se completan cuando una biografía o ficha individual las publica expresamente.
El fin de un mandato no implica jubilación. La actividad vigente se acredita con
la composición consultada; el fallecimiento prevalece sobre una biografía antigua.

Los retratos parlamentarios se asocian a un nombre e identificador explícitos.
Para las figuras históricas se prefiere el recurso de la legislatura más antigua
disponible; para los cargos vigentes, el retrato institucional actual. Los recursos
complementarios de Commons conservan autor, licencia y enlace. Victoria Cruz se
identifica mediante el retrato publicado por el PSOE de Almería; Lina Gálvez utiliza
su ficha oficial del Parlamento Europeo.

## Organización y mantenimiento

- `Gobierno/<año> <etapa>/composicion.json`: Consejo de Gobierno, cargos y fuentes.
- `Parlamento/<año> Legislatura <romano>/composicion.json`: participantes, Mesa y grupos.
- `fuentes/`: corpus jurídico, transcripciones, biografías breves y correspondencias.
- `Políticos/<nombre completo>/`: ficha, fuentes, datos personales y retrato originales;
  `mandatos-andalucia.json`, `grupos-andalucia.json`, `cargos-andalucia.json` y
  `comisiones-andalucia.json` contienen exclusivamente la trayectoria propia.
- `Gobiernos/herramientas/`: consulta, transcripción e incorporación.
  `documentar-hemiciclos-andalucia.py` reproduce las composiciones archivadas
  a partir de los originales, respetando el epígrafe de bajas. Los documentos
  descargados se guardan en la caché ignorada de `test-results/andalucia/`.
- `Gobiernos/revisiones/2026-10-12-andalucia/informe.json`: conservación de identidades,
  cobertura, discrepancias y retratos pendientes. No forma parte del catálogo web.

Antes de regenerar, consultar los originales y revisar las transcripciones y las
variantes de identidad. No eliminar fuentes, alias, retratos ni secciones de una
ficha anterior. Verificar las referencias cruzadas, las bajas de la Mesa, las
suplencias y la cobertura del hemiciclo antes de publicar.

## Fuentes principales

- [Archivo de composiciones del Parlamento](https://www.parlamentodeandalucia.es/webdinamica/portal-web-parlamento/composicionyfuncionamiento/memoriadecomposiciones.do).
- [Fichas de diputados vigentes](https://www.parlamentodeandalucia.es/webdinamica/portal-web-parlamento/composicionyfuncionamiento/diputadosysenadores.do).
- [Memorias institucionales](https://www.parlamentodeandalucia.es/memorias).
- [Cronología parlamentaria del Senado](https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=CRONOL_LEGISL_ANDALUCIA).
- [Consejo de Gobierno de la Junta](https://www.juntadeandalucia.es/organismos/transparencia/transparencia-consejo-gobierno/composicion-funciones.html).
- [Archivo del BOJA](https://www.juntadeandalucia.es/boja/).
