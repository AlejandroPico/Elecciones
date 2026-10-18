import { describe, expect, it, vi } from "vitest";
import {
  bank,
  compare,
  sampleCategory,
  secureIndex,
  selectTopics,
  sessionQuestions,
  uniqueResponses,
  userAxis,
  type SessionQuestion,
} from "./sesion";

const q = (
  id: string,
  value: number | null,
  selectionKey = id,
): SessionQuestion => ({
  id,
  category: "test",
  concept: "test",
  text: id,
  selectionKey,
  scope: null,
  positions: {
    p: {
      value,
      basis: "test",
      evidence: [{ proposalId: "e", documentId: "d", pdfPages: [1] }],
    },
  },
});
describe("sesiones por temas", () => {
  it("ofrece los 40 temas completos, diez decisiones distintas por tema y un máximo de 400", () => {
    const ids = bank.categories.map((c) => c.id);
    expect(ids).toHaveLength(40);
    expect(bank.groups.flatMap((g) => g.categoryIds).sort()).toEqual(
      [...ids].sort(),
    );
    const draws = selectTopics({}, ids);
    const questions = sessionQuestions(draws, ids);
    expect(questions).toHaveLength(400);
    expect(new Set(questions.map((q) => q.selectionKey)).size).toBe(400);
    expect(new Set(questions.map((q) => q.id)).size).toBe(400);
    ids.forEach((id) => expect(draws[id]).toHaveLength(10));
  });
  it("conserva el sorteo al retirar, volver a añadir o ampliar temas", () => {
    const first = selectTopics({}, ["empresa"]);
    const random = vi.fn(() => 0);
    const same = selectTopics(first, ["empresa"], random);
    expect(random).not.toHaveBeenCalled();
    const extended = selectTopics(same, ["trabajo"], random);
    expect(extended.empresa).toBe(first.empresa);
    expect(selectTopics(extended, ["empresa"], random).empresa).toEqual(
      first.empresa,
    );
    expect(sessionQuestions(extended, ["empresa"])).toHaveLength(10);
  });
  it("dos órdenes aleatorios diferentes producen muestras distintas sin repetir familias", () => {
    const qs = Array.from({ length: 30 }, (_, i) => ({
      ...q(`q${i}`, 2, `decision-${Math.floor(i / 2)}`),
      category: "test",
    }));
    const a = sampleCategory("test", qs, () => 0);
    const b = sampleCategory("test", qs, (max) => max - 1);
    expect(a).not.toEqual(b);
    expect(a).toHaveLength(10);
    expect(
      new Set(a.map((id) => qs.find((q) => q.id === id)!.selectionKey)).size,
    ).toBe(10);
  });
  it("el sorteo criptográfico rechaza la cola que introduciría sesgo", () => {
    let calls = 0;
    const spy = vi.spyOn(crypto, "getRandomValues").mockImplementation(((
      array: Uint32Array,
    ) => {
      array[0] = calls++ ? 5 : 0xffffffff;
      return array;
    }) as typeof crypto.getRandomValues);
    try {
      expect(secureIndex(10)).toBe(5);
      expect(calls).toBe(2);
    } finally {
      spy.mockRestore();
    }
  });
});
describe("perfil parcial y trazable", () => {
  it("calcula desde la primera respuesta y pondera normal, alta y esencial", () => {
    const qs = [q("a", 2), q("b", -2), q("unknown", null)];
    expect(
      compare({ a: { value: 2, importance: 1 } }, "p", undefined, qs).percent,
    ).toBe(100);
    const result = compare(
      {
        a: { value: 2, importance: 1 },
        b: { value: 2, importance: 3 },
        unknown: { value: 1, importance: 2 },
      },
      "p",
      undefined,
      qs,
    );
    expect(result.percent).toBe(25);
    expect(result.shared).toBe(2);
    expect(result.answered).toBe(3);
    expect(result.weight).toBe(4);
    expect(result.coverage).toBeCloseTo(200 / 3);
    expect(result.distance).toBe(3);
  });
  it("distingue neutral y omisión, y no puntúa posiciones sin evidencia", () => {
    const a = q("a", 2),
      b = q("b", 2);
    b.positions.p.evidence = [];
    const result = compare(
      {
        a: { value: 0, importance: 1 },
        b: { value: 2, importance: 3 },
        skip: { value: null, importance: 3 },
      },
      "p",
      undefined,
      [a, b, q("skip", 2)],
    );
    expect(result.percent).toBe(50);
    expect(result.shared).toBe(1);
    expect(result.answered).toBe(2);
    expect(
      compare({ a: { value: null, importance: 1 } }, "p", undefined, [a])
        .percent,
    ).toBeNull();
    expect(compare({}, "p", undefined, [a]).percent).toBeNull();
  });
  it("no duplica decisiones equivalentes ni respuestas que aparecen en varias rutas", () => {
    const qs = [q("a", 2, "decision"), q("b", 2, "decision")];
    const answers = {
      a: { value: 2, importance: 1 as const },
      b: { value: 2, importance: 3 as const },
    };
    expect(uniqueResponses(answers, qs)).toHaveLength(1);
    expect(compare(answers, "p", undefined, qs).shared).toBe(1);
  });
  it("conserva signos y pesos de los ejes documentados sin colocar ausencias en cero", () => {
    const axis = {
      label: "test",
      indicators: [
        { label: "a", questionIds: [bank.questions[0].id], direction: -1 },
      ],
    };
    expect(userAxis({}, axis).value).toBeNull();
    const result = userAxis(
      { [bank.questions[0].id]: { value: 2, importance: 3 } },
      axis,
    );
    expect(result.value).toBe(-100);
    expect(result.weight).toBe(3);
    expect(result.numerator).toBe(-3);
  });
  it("el filtro de temas solo compara las decisiones del tema indicado", () => {
    const qs = [q("a", 2), { ...q("b", -2), category: "other" }];
    expect(
      compare(
        { a: { value: 2, importance: 1 }, b: { value: 2, importance: 1 } },
        "p",
        "test",
        qs,
      ).percent,
    ).toBe(100);
  });
});
