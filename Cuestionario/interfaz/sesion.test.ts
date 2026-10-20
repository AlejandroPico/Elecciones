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
  documentaryAxis,
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
  it("un 92 % con dos de treinta no se convierte en afinidad global", () => {
    const qs = Array.from({ length: 30 }, (_, i) =>
      q(`p${i}`, i < 2 ? 2 : null),
    );
    const answers = Object.fromEntries(
      qs.map((q, i) => [
        q.id,
        { value: i === 1 ? 1 : 2, importance: (i === 0 ? 2 : 1) as 1 | 2 | 3 },
      ]),
    );
    const result = compare(answers, "p", undefined, qs);
    expect(result.shared).toBe(2);
    expect(result.answered).toBe(30);
    expect(result.percent).toBeCloseTo(91.6666667);
    expect(result.coverage).toBeCloseTo(100 / 15);
    expect(result.totalWeight).toBe(31);
    expect(result.unknownWeight).toBe(28);
    expect(result.overallRange![0]).toBeCloseTo((100 * 2.75) / 31);
    expect(result.overallRange![1]).toBeCloseTo((100 * 30.75) / 31);
    expect(result.overallRange![1] - result.overallRange![0]).toBeGreaterThan(
      90,
    );
  });
  it("los límites se cierran con cobertura completa; neutral no equivale a ausencia", () => {
    const qs = [q("a", 2), q("b", -2)];
    const result = compare(
      { a: { value: 0, importance: 1 }, b: { value: -1, importance: 2 } },
      "p",
      undefined,
      qs,
    );
    expect(result.overallRange![0]).toBeCloseTo(result.percent!);
    expect(result.overallRange![1]).toBeCloseTo(result.percent!);
    expect(result.unknownWeight).toBe(0);
    const unknown = compare(
      { a: { value: 2, importance: 1 } },
      "missing",
      undefined,
      qs,
    );
    expect(unknown.percent).toBeNull();
    expect(unknown.overallRange).toEqual([0, 100]);
  });
  it("una ambigüedad y una contradicción no se resuelven por mayoría de variantes", () => {
    const axis = {
      label: "test",
      indicators: [{ label: "a", questionIds: ["a", "b"], direction: 1 }],
    };
    expect(
      documentaryAxis("p", axis, [q("a", 2), q("b", null)]).value,
    ).toBeNull();
    expect(
      documentaryAxis("p", axis, [q("a", 2), q("b", -2)]).value,
    ).toBeNull();
    expect(documentaryAxis("p", axis, [q("a", 2), q("b", 2)]).value).toBe(100);
  });
  it("un programa autonómico no se proyecta a un índice nacional", () => {
    const territorial = {
      ...q("regional", 2),
      scope: { territory: "Castilla y León", sourceElection: "2026" },
    };
    const axis = {
      label: "test",
      indicators: [{ label: "r", questionIds: ["regional"], direction: 1 }],
    };
    const a = { regional: { value: 2, importance: 1 as const } };
    expect(userAxis(a, axis, [territorial]).value).toBeNull();
    expect(documentaryAxis("p", axis, [territorial]).value).toBeNull();
    expect(compare(a, "p", undefined, [territorial]).percent).toBe(100);
  });
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
