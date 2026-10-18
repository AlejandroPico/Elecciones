import { describe, expect, it } from "vitest";
import {
  corpus,
  definitions,
  documentEdition,
  evidenceLocator,
  indicatorValue,
  markerGroups,
  partyPoint,
  questions,
  scoreAxis,
  type Axis,
  type ResearchQuestion,
} from "./model";

const evidence = { proposalId: "test", documentId: "test", pdfPages: [1] };
const q = (
  id: string,
  value: number | null,
  withEvidence = true,
): ResearchQuestion => ({
  id,
  statement: id,
  category: "test",
  positions: {
    p: { value, basis: "test", evidence: withEvidence ? [evidence] : [] },
  },
});
const axis: Axis = {
  label: "test",
  indicators: [
    { label: "a", direction: 1, questionIds: ["a"] },
    { label: "b", direction: -1, questionIds: ["b"] },
  ],
};

describe("coordenadas documentales", () => {
  it("excluye ausencia y evidencia ambigua, sin colocarlas en el centro", () => {
    const missing = scoreAxis(axis, "p", [q("a", null), q("b", 2, false)]);
    expect(missing.value).toBeNull();
    expect(missing.count).toBe(0);
    expect(missing.interval).toEqual([-100, 100]);
    const partial = scoreAxis(axis, "p", [q("a", 2), q("b", null)]);
    expect(partial.value).toBe(100);
    expect(partial.count).toBe(1);
    expect(partial.interval).toEqual([0, 100]);
  });
  it("aplica signos y media; un cero acreditado difiere de no tener datos", () => {
    const result = scoreAxis(axis, "p", [q("a", 2), q("b", 2)]);
    expect(result.value).toBe(0);
    expect(result.count).toBe(2);
    expect(result.interval).toEqual([0, 0]);
  });
  it("varias fuentes no aumentan el peso y variantes contradictorias requieren revisión", () => {
    const first = q("a", 2);
    first.positions.p.evidence.push(evidence);
    expect(
      indicatorValue(
        { label: "a", direction: 1, questionIds: ["a", "a"] },
        "p",
        [first],
      ),
    ).toBe(100);
    expect(
      indicatorValue(
        { label: "a", direction: 1, questionIds: ["a", "b"] },
        "p",
        [first, q("b", -2)],
      ),
    ).toBeNull();
  });
  it("conserva veintidós organizaciones y distingue las fuentes y sus ediciones", () => {
    expect(corpus.parties.map((p) => p.id)).toEqual([
      "pp",
      "psoe",
      "vox",
      "erc",
      "junts",
      "eh-bildu",
      "pnv",
      "bng",
      "pacma",
      "registro-4086",
      "registro-6359",
      "registro-6040",
      "registro-7400",
      "registro-7458",
      "podemos",
      "registro-6972",
      "registro-6779",
      "registro-6620",
      "registro-7039",
      "coalicion-d21-2026",
      "cc",
      "sumar-coalicion-2023",
    ]);
    expect(corpus.sourceElection).toBeNull();
    expect(corpus.sourceContext).toBe("mixed-editions");
    expect(corpus.sources.filter((s) => s.kind === "historical")).toHaveLength(
      16,
    );
    const podemos = corpus.sources.find((s) => s.organization === "podemos")!;
    expect(podemos.electionDate).toBe("2019-11-10");
    expect(documentEdition(podemos)).toBe("Programa 2019");
    const permanent = corpus.sources.find(
      (s) => s.organization === "registro-4086",
    )!;
    expect(permanent.format).toBe("TXT");
    expect(permanent.pages).toBeNull();
    expect(documentEdition(permanent)).toBe("Programa permanente");
    expect(
      documentEdition(
        corpus.sources.find((s) => s.organization === "registro-6359")!,
      ),
    ).toBe("Programa político general");
    expect(
      evidenceLocator({
        proposalId: "test",
        documentId: permanent.id,
        pdfPages: [],
        textLines: [6],
      }),
    ).toBe("Texto · líneas 6");
    // Evaluar una rebaja del IVA o condicionar un gravamen no acredita aprobarlos.
    const iva = questions.find((q) => q.id === "q-pnv23-g0016-05")!;
    expect(iva.positions.pnv.value).toBeNull();
    expect(iva.positions.pnv.evidence.length).toBeGreaterThan(0);
    expect(corpus.categories.reduce((n, c) => n + c.questions, 0)).toBe(
      corpus.counts.questions,
    );
    for (const question of questions)
      for (const [party, position] of Object.entries(question.positions)) {
        if (position.value !== null)
          expect(position.evidence.length).toBeGreaterThan(0);
        for (const ev of position.evidence) {
          const source = corpus.sources.find((s) => s.id === ev.documentId)!;
          expect(source.organization).toBe(party);
          expect(
            ev.pdfPages.every(
              (p) => p > 0 && source.pages !== null && p <= source.pages,
            ),
          ).toBe(true);
        }
      }
  });
  it("no desplaza puntos coincidentes y solo dibuja cuando se conocen ambos ejes", () => {
    for (const map of definitions) {
      const points = corpus.parties.map((p) => partyPoint(map, p.id));
      const groups = markerGroups(points);
      expect(groups.flat().length).toBe(
        points.filter((p) => p.drawable).length,
      );
      for (const group of groups)
        for (const point of group) {
          expect(point.x.value).toBe(group[0].x.value);
          expect(point.y.value).toBe(group[0].y.value);
        }
      for (const point of points)
        for (const axis of [point.x, point.y])
          if (axis.value !== null) {
            expect(axis.value).toBeGreaterThanOrEqual(-100);
            expect(axis.value).toBeLessThanOrEqual(100);
            expect(axis.interval![0]).toBeLessThanOrEqual(axis.value);
            expect(axis.interval![1]).toBeGreaterThanOrEqual(axis.value);
          }
    }
  });
  it("no inventa coordenadas sectoriales para el programa de artículo único", () => {
    for (const map of definitions) {
      const point = partyPoint(map, "registro-4086");
      expect(point.drawable).toBe(false);
      expect(point.x.value).toBeNull();
      expect(point.y.value).toBeNull();
    }
  });
  it("no convierte el contrato autonómico de SALF en posiciones nacionales", () => {
    const source = corpus.sources.find(
      (s) => s.organization === "registro-7458",
    )!;
    expect(documentEdition(source)).toBe(
      "Programa autonómico · Castilla y León · 2026",
    );
    expect(source.electionDate).toBe("2026-03-15");
    for (const question of questions) {
      expect(question.positions["registro-7458"].value).toBeNull();
      expect(question.positions["registro-7458"].evidence).toEqual([]);
    }
    for (const map of definitions)
      expect(partyPoint(map, "registro-7458").drawable).toBe(false);
  });
  it("separa Drago autonómico de los ejes nacionales y admite varias fuentes por partido", () => {
    const drago = corpus.sources.find(
      (s) => s.organization === "registro-7039",
    )!;
    expect(documentEdition(drago)).toBe(
      "Programa autonómico · Canarias · 2023",
    );
    expect(drago.format).toBe("TXT");
    expect(drago.pages).toBeNull();
    expect(
      corpus.sources.filter((s) => s.organization === "coalicion-d21-2026"),
    ).toHaveLength(2);
    expect(corpus.sources).toHaveLength(23);
    for (const question of questions) {
      expect(question.positions["registro-7039"].value).toBeNull();
      expect(question.positions["registro-7039"].evidence).toEqual([]);
    }
    for (const map of definitions)
      expect(partyPoint(map, "registro-7039").drawable).toBe(false);
  });
  it("identifica el programa común de Sumar sin atribuirlo al Frente Amplio ni a cada integrante", () => {
    const source = corpus.sources.find(
      (s) => s.organization === "sumar-coalicion-2023",
    )!;
    expect(source.electionDate).toBe("2023-07-23");
    expect(source.pages).toBe(182);
    expect(corpus.parties.some((p) => p.id === "sumar")).toBe(false);
    expect(
      corpus.parties.some((p) => p.id === "coalicion-frente-amplio-2026"),
    ).toBe(false);
    const tax = questions.find((q) => q.id === "q-pp23-042-a")!;
    expect(tax.positions["sumar-coalicion-2023"].value).toBe(2);
    expect(
      tax.positions["sumar-coalicion-2023"].evidence.every(
        (e) => e.documentId === source.id,
      ),
    ).toBe(true);
  });
});
