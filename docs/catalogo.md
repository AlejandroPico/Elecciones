# Preguntas, posiciones y fuentes

La versión actual es un banco piloto para comprobar el funcionamiento de la web. No es un instrumento psicométrico validado ni un catálogo de propuestas de las candidaturas de 2026.

## Banco de preguntas

`src/data.ts` contiene 48 preguntas y 8 categorías. Cada tema tiene dos ejes separados y cada pregunta puntúa en uno de ellos. Una respuesta de acuerdo no implica automáticamente estar a la derecha, a la izquierda o en un polo religioso: cada pregunta declara `direction` y `axis`.

La escala es −2, −1, 0, +1, +2. Una pregunta binaria admite −2 y +2. Omitir se guarda como `null` y se excluye de la media. La importancia pesa 1, 2 o 3. El eje es `100 × suma(valor / 2 × dirección × importancia) / suma(importancia)`.

La cobertura de un eje es el número de respuestas válidas frente al total de preguntas de ese eje. El progreso de la encuesta incluye las omisiones explícitas. Un eje sin respuestas se representa sin datos, nunca como una posición neutral. Un punto bidimensional exige datos en ambos ejes. La vista radial resume únicamente el primer eje de cada categoría, con −100 en el centro y +100 en el borde; las 16 dimensiones están disponibles en el detalle.

Antes de incorporar preguntas definitivas:

- Una sola propuesta por pregunta, con contexto claro sobre plazo, territorio o supuesto.
- Evitar términos valorativos, presuposiciones, dobles negaciones y calificativos de partidos.
- Separar opiniones de conocimiento factual; no penalizar «no sé».
- Revisar el equilibrio de los polos y la suficiencia de ítems por eje. El banco piloto no garantiza ese equilibrio.
- Someter el texto y la asignación a ejes a revisión independiente. Publicar cambios y actualizar la versión al modificar texto o puntuación.
- Las preguntas sobre acontecimientos deben tener fecha de corte, contexto contrastado y fuentes primarias. Todavía no se incluyen eventos contemporáneos en el banco piloto.

## Incorporar programas

Primero se conserva el documento original con partido, elección, ámbito territorial, URL, fecha, edición y, cuando proceda, huella del archivo. Después se revisan propuestas concretas con página o sección. Las candidaturas se añadirán por circunscripción a partir de listas oficialmente proclamadas; no se supone que todas concurran en todas las provincias.

Una propuesta ausente o ambigua **se omite** de `positions`; no se convierte en 0. Un 0 significa una posición neutral que tiene fundamento documental. El programa es una fuente de propuestas, no prueba de cumplimiento; una futura capa de votaciones o actuaciones debe diferenciarse de lo prometido.

La importación actual sirve para probar posiciones ya codificadas y revisadas. No interpreta documentos PDF, no publica un catálogo, no guarda el archivo importado entre sesiones y no verifica el contenido remoto de los enlaces. La validación comprueba estructura, versión, preguntas, valores y referencias; la veracidad requiere revisión editorial.

Formato de JSON (ejemplo ficticio; no es una candidatura real y no se carga por defecto):

```json
{
  "version": "es-generales-2026-demo-1",
  "parties": [
    {
      "id": "ejemplo-editorial",
      "name": "Ejemplo de formato",
      "color": "#467C70",
      "positions": {
        "economia-1": {
          "value": 1,
          "source": "https://example.org/programa.pdf",
          "reference": "Página 12, apartado 3. Revisado por dos personas."
        }
      }
    }
  ]
}
```

Máximo 2 MB y 100 candidaturas por archivo. `source` debe ser HTTPS, `reference` debe identificar el pasaje. Los gráficos de partidos usan pesos uniformes para dibujar su perfil documental. La afinidad emplea los pesos que eligió el usuario y se calcula sobre preguntas compartidas: `100 × (1 − media ponderada(|usuario − partido| / 4))`. Se muestran siempre las preguntas comunes y la cobertura; un porcentaje basado en una sola pregunta no resume todo el programa.

## Convocatoria

Referencia localizada el 6 de octubre de 2026: [BOE-A-2026-20742](https://www.boe.es/buscar/doc.php?id=BOE-A-2026-20742&lang=es), con fecha electoral de 29 de noviembre de 2026 verificada en el artículo 2 del documento oficial. Publicación: 6 de octubre de 2026. Esta referencia no acredita candidaturas ni programas todavía no incorporados.
