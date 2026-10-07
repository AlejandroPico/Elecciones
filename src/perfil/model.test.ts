import { describe, expect, it } from "vitest";
import { calculate, parseParties, similarity, type Answers } from "./model";
import { categories, questions, VERSION } from "../../Elecciones";
describe("Modelo de coordenadas", () => {
  it("no atribuye al centro los ejes sin respuestas o con omisiones", () => {
    expect(calculate({}).intervencion.value).toBeNull();
    expect(
      calculate({ "economia-1": { value: null, importance: 3 } }).intervencion
        .value,
    ).toBeNull();
    expect(
      calculate({ "economia-1": { value: 0, importance: 1 } }).intervencion
        .value,
    ).toBe(0);
  });
  it("invierte la dirección y pondera sin salir del intervalo", () => {
    const s = calculate({
      "economia-1": { value: 2, importance: 1 },
      "economia-2": { value: 2, importance: 3 },
    }).intervencion;
    expect(s.value).toBe(-50);
    expect(s.answered).toBe(2);
    expect(s.total).toBe(3);
    const answers: Answers = Object.fromEntries(
      questions.map((q) => [q.id, { value: 2 * q.direction, importance: 3 }]),
    );
    expect(
      Object.values(calculate(answers)).every((s) => s.value === 100),
    ).toBe(true);
  });
  it("asigna cada pregunta a un único eje existente, con identificador único", () => {
    const axes = categories.flatMap((c) => c.axes.map((a) => a.id));
    expect(new Set(questions.map((q) => q.id)).size).toBe(48);
    expect(new Set(axes).size).toBe(16);
    for (const q of questions) {
      expect(
        categories.find((c) => c.id === q.category)?.axes.map((a) => a.id),
      ).toContain(q.axis);
    }
  });
});
const party = {
  id: "prueba",
  name: "Perfil de prueba",
  color: "#123456",
  positions: {
    "economia-1": {
      value: 2,
      source: "https://example.org/programa",
      reference: "Página 8",
    },
  },
};
describe("Comparaciones documentadas", () => {
  it("excluye posiciones desconocidas y expone la cobertura común", () => {
    const s = similarity(
      {
        "economia-1": { value: 2, importance: 1 },
        "economia-2": { value: -2, importance: 3 },
      },
      party,
    );
    expect(s).toEqual({ percent: 100, shared: 1, answered: 2 });
    expect(
      similarity({ "economia-1": { value: -2, importance: 1 } }, party).percent,
    ).toBe(0);
    expect(similarity({}, party).percent).toBeNull();
  });
  it("exige versión, fuentes, referencias y valores válidos", () => {
    expect(parseParties({ version: VERSION, parties: [party] })).toEqual([
      party,
    ]);
    expect(() =>
      parseParties({ version: "vieja", parties: [party] }),
    ).toThrow();
    expect(() =>
      parseParties({ version: VERSION, parties: [party, party] }),
    ).toThrow();
    expect(() =>
      parseParties({
        version: VERSION,
        parties: [
          {
            ...party,
            positions: {
              "economia-1": {
                value: 2,
                source: "javascript:alert(1)",
                reference: "p8",
              },
            },
          },
        ],
      }),
    ).toThrow();
    expect(() =>
      parseParties({
        version: VERSION,
        parties: [
          {
            ...party,
            positions: {
              "sociedad-5": {
                value: 0,
                source: "https://example.org",
                reference: "p8",
              },
            },
          },
        ],
      }),
    ).toThrow();
  });
});
