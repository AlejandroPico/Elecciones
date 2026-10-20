import { describe, expect, it } from "vitest";
import {
  bank,
  documentaryAxis,
  sampleCategory,
  userAxis,
  questionById,
} from "./sesion";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";

describe("simulaciones del cuestionario", () => {
  it("recorre los 40 temas y 12 patrones sin convertir ausencias en centro ni salir de escala", () => {
    let seed = 20261020;
    const next = (max: number) => {
      seed = (1664525 * seed + 1013904223) >>> 0;
      return seed % max;
    };
    for (const category of bank.categories) {
      const ids = sampleCategory(category.id, bank.questions, next);
      for (let pattern = 0; pattern < 12; pattern++) {
        const a: Answers = Object.fromEntries(
          ids.map((id, i) => [
            id,
            {
              value:
                pattern === 0
                  ? 0
                  : pattern === 1
                    ? null
                    : ((i + pattern) % 5) - 2,
              importance: (((i + pattern) % 3) + 1) as 1 | 2 | 3,
            },
          ]),
        );
        const inverted: Answers = Object.fromEntries(
          Object.entries(a).map(([id, r]) => [
            id,
            { ...r, value: r.value === null ? null : -r.value },
          ]),
        );
        for (const map of bank.maps)
          for (const axis of [map.x, map.y]) {
            const score = userAxis(a, axis),
              opposite = userAxis(inverted, axis);
            expect(opposite.count).toBe(score.count);
            if (score.value !== null) {
              expect(Number.isFinite(score.value)).toBe(true);
              expect(Math.abs(score.value)).toBeLessThanOrEqual(100);
              expect(opposite.value).toBeCloseTo(-score.value, 10);
            } else expect(score.count).toBe(0);
          }
      }
    }
  });
  it("produce un abanico de valores intermedios sin añadir ruido ni alterar las respuestas", () => {
    const axis = bank.maps.find((m) => m.id === "control-gobierno")!.x;
    const ids: string[] = [],
      seen = new Set<string>();
    for (const i of axis.indicators) {
      const q = questionById.get(i.questionIds[0])!;
      if (!seen.has(q.selectionKey)) {
        ids.push(q.id);
        seen.add(q.selectionKey);
      }
      if (ids.length === 10) break;
    }
    const values = new Set<number>();
    let seed = 17;
    for (let run = 0; run < 100; run++) {
      const a: Answers = {};
      for (const id of ids) {
        seed = (1664525 * seed + 1013904223) >>> 0;
        const value = (seed % 5) - 2;
        seed = (1664525 * seed + 1013904223) >>> 0;
        a[id] = { value, importance: ((seed % 3) + 1) as 1 | 2 | 3 };
      }
      const first = userAxis(a, axis).value!;
      expect(userAxis(a, axis).value).toBe(first);
      values.add(first);
    }
    expect(values.size).toBeGreaterThan(50);
    expect([...values].some((n) => Math.abs(n % 50) > 1e-8)).toBe(true);
  });
  it("las variantes de un indicador no multiplican el peso de un documento", () => {
    const qs = bank.questions
      .filter((q) => !q.scope && q.positions.pp?.value === 2)
      .slice(0, 4);
    const single = {
      label: "test",
      indicators: [{ label: "one", questionIds: [qs[0].id], direction: 1 }],
    };
    const variants = {
      label: "test",
      indicators: [
        {
          label: "one",
          questionIds: qs.flatMap((q) => [q.id, q.id]),
          direction: 1,
        },
      ],
    };
    expect(documentaryAxis("pp", single).count).toBe(1);
    expect(documentaryAxis("pp", variants).count).toBe(1);
    expect(documentaryAxis("pp", single).value).toBe(
      documentaryAxis("pp", variants).value,
    );
  });
});
