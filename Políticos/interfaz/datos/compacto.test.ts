import { expect, it } from "vitest";
import { compactJson, expandJson } from "./compacto";
it("conserva sin pérdida textos, números, arrays, claves especiales y registros repetidos", () => {
  const source = {
    label: "Archivo parlamentario institucional y biografía",
    url: "https://www.cortesaragon.es/ficha-personal/una-referencia-documental-extensa",
    kind: "institutional",
  };
  const value = {
    name: "María José Sáenz de Buruaga Gómez",
    empty: [],
    records: Array.from({ length: 30 }, (_, i) => ({
      n: i - 15,
      source,
      nested: [null, false, ["s", 0], ["o", 2], ["r", 3], ["a"]],
    })),
    special: JSON.parse('{"__proto__":{"source":"conservada"}}'),
  };
  const packed = compactJson(value);
  expect(JSON.stringify(packed).length).toBeLessThan(
    JSON.stringify(value).length,
  );
  expect(expandJson(packed)).toEqual(value);
});
it("reconstruye referencias independientes y no altera el documento original", () => {
  const row = {
    title:
      "Un registro institucional suficientemente extenso para compartir su codificación",
    source: {
      label: "Archivo",
      url: "https://www.cortesaragon.es/una-fuente-publica",
    },
  };
  const value = [{ ...row }, { ...row }],
    before = JSON.stringify(value);
  const result = expandJson<typeof value>(compactJson(value));
  result[0].source.url = "cambiado";
  expect(result[1].source.url).toBe(row.source.url);
  expect(JSON.stringify(value)).toBe(before);
});
