type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
export type CompactJson = {
  strings: string[];
  shapes: string[][];
  refs: Json[];
  value: Json;
};

/** Codificación sin pérdida: comparte textos, esquemas y registros repetidos.
 * Solo cambia el artefacto de entrega. Los archivos personales siguen siendo
 * el origen y cada referencia se reconstruye como un valor independiente.
 */
export function compactJson(input: unknown): CompactJson {
  const strings = new Map<string, number>(),
    records = new Map<string, number>();
  const keys = new WeakMap<object, string>();
  function count(value: Json) {
    if (typeof value === "string") {
      if (value.length >= 16) strings.set(value, (strings.get(value) ?? 0) + 1);
    } else if (value && typeof value === "object") {
      // No conservar serializaciones de los enormes contenedores del catálogo.
      if (
        (Array.isArray(value) ? value.length : Object.keys(value).length) <= 20
      ) {
        const key = JSON.stringify(value);
        if (key.length >= 100 && key.length <= 3000) {
          keys.set(value, key);
          records.set(key, (records.get(key) ?? 0) + 1);
        }
      }
      for (const child of Object.values(value)) count(child);
    }
  }
  count(input as Json);
  const dictionary = [...strings]
    .filter(([text, n]) => n * (text.length - 10) > text.length + 4)
    .map(([text]) => text);
  const stringIds = new Map(dictionary.map((text, i) => [text, i]));
  const repeated = [...records].filter(([, n]) => n > 1).map(([key]) => key);
  const recordIds = new Map(repeated.map((key, i) => [key, i]));
  const shapes: string[][] = [],
    shapeIds = new Map<string, number>();
  function encode(value: Json, skip?: string): Json {
    if (typeof value === "string") {
      const i = stringIds.get(value);
      return i === undefined ? value : ["s", i];
    }
    if (!value || typeof value !== "object") return value;
    const key = keys.get(value),
      ref = key === undefined ? undefined : recordIds.get(key);
    if (ref !== undefined && key !== skip) return ["r", ref];
    if (Array.isArray(value)) return ["a", ...value.map((v) => encode(v))];
    const fields = Object.keys(value),
      shapeKey = JSON.stringify(fields);
    let shape = shapeIds.get(shapeKey);
    if (shape === undefined) {
      shape = shapes.length;
      shapes.push(fields);
      shapeIds.set(shapeKey, shape);
    }
    return ["o", shape, ...fields.map((field) => encode(value[field]))];
  }
  // JSON.parse crea objetos nuevos: registrar sus claves antes de codificarlos.
  const refs = repeated.map((key) => {
    const value = JSON.parse(key) as Json;
    const register = (v: Json) => {
      if (v && typeof v === "object") {
        const text = JSON.stringify(v);
        if (recordIds.has(text)) keys.set(v, text);
        for (const child of Object.values(v)) register(child);
      }
    };
    register(value);
    return encode(value, key);
  });
  return { strings: dictionary, shapes, refs, value: encode(input as Json) };
}

export function expandJson<T>(data: CompactJson): T {
  function decode(value: Json): Json {
    if (!Array.isArray(value)) return value;
    if (value[0] === "s") return data.strings[value[1] as number];
    if (value[0] === "r") return decode(data.refs[value[1] as number]);
    if (value[0] === "a") return value.slice(1).map(decode);
    if (value[0] === "o")
      return Object.fromEntries(
        data.shapes[value[1] as number].map((key, i) => [
          key,
          decode(value[i + 2]),
        ]),
      );
    throw new Error("Formato de catálogo compacto desconocido");
  }
  return decode(data.value) as T;
}
