import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
vi.mock("../../Partidos/interfaz/catalogo", () => ({ logos: {} }));
import PoliticalMap from "./PoliticalMap";
import { bank, documentaryAxis, questionById, userAxis } from "./sesion";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";

const map = bank.maps.find((m) => m.id === "control-gobierno")!;
function responses() {
  const answers: Answers = {},
    seen = new Set<string>();
  const values = { x: [2, 1, 0, -1, 0], y: [-2, 1, 0, 2, -1] };
  const weights = { x: [3, 2, 2, 1, 2], y: [1, 3, 1, 1, 1] };
  for (const key of ["x", "y"] as const) {
    let index = 0;
    for (const i of map[key].indicators) {
      const q = questionById.get(i.questionIds[0])!;
      if (seen.has(q.selectionKey)) continue;
      seen.add(q.selectionKey);
      answers[q.id] = {
        value: values[key][index],
        importance: weights[key][index] as 1 | 2 | 3,
      };
      if (++index === 5) break;
    }
  }
  return answers;
}
describe("índices fijos: regresión de los errores observados", () => {
  it("agrega las diez respuestas y obtiene 35 y 14,2857, sin saltos de 50", () => {
    const answers = responses();
    expect(Object.keys(answers)).toHaveLength(10);
    expect(userAxis(answers, map.x).value).toBeCloseTo(35, 10);
    expect(userAxis(answers, map.y).value).toBeCloseTo(100 / 7, 10);
    expect(userAxis(answers, map.x).count).toBe(5);
    const html = renderToStaticMarkup(
      <PoliticalMap
        answers={answers}
        selectedParty="pp"
        selectParty={() => {}}
      />,
    );
    expect(html).toContain("Tus índices por temas");
    expect(html).toContain("user-position-pulse");
    expect(html).toContain("Tú: X +35, Y +14,3");
    expect(html).not.toContain("Propuesta del eje");
    expect(html).not.toContain("Por propuestas");
  });
  it("Control del Gobierno usa la evidencia de varios documentos y no solo PACMA", () => {
    const parties = bank.parties.filter(
      (p) =>
        documentaryAxis(p.id, map.x).value !== null &&
        documentaryAxis(p.id, map.y).value !== null,
    );
    expect(parties.length).toBeGreaterThanOrEqual(9);
    for (const id of [
      "pp",
      "psoe",
      "vox",
      "pnv",
      "pacma",
      "podemos",
      "coalicion-d21-2026",
      "sumar-coalicion-2023",
    ])
      expect(parties.map((p) => p.id)).toContain(id);
    // None of these functions accepts user answers: the party basis remains fixed.
    const before = parties.map((p) => [
      p.id,
      documentaryAxis(p.id, map.x).value,
      documentaryAxis(p.id, map.y).value,
    ]);
    userAxis(responses(), map.x);
    expect(
      parties.map((p) => [
        p.id,
        documentaryAxis(p.id, map.x).value,
        documentaryAxis(p.id, map.y).value,
      ]),
    ).toEqual(before);
  });
  it("una sola respuesta conserva la proyección parcial y no inventa el segundo eje", () => {
    const id = map.x.indicators[0].questionIds[0];
    const html = renderToStaticMarkup(
      <PoliticalMap
        answers={{ [id]: { value: 2, importance: 1 } }}
        selectedParty="pp"
        selectParty={() => {}}
      />,
    );
    expect(html).toContain("Tú · solo X");
    expect(html).toContain("user-projection");
    expect(html).not.toContain('class="user-position-ring"');
    expect(html).toContain("Base escasa");
  });
  it("expone respuestas sin asignación en lugar de fabricarles coordenadas", () => {
    const mapped = new Set(
      bank.maps.flatMap((m) =>
        [m.x, m.y].flatMap((a) => a.indicators.flatMap((i) => i.questionIds)),
      ),
    );
    const q = bank.questions.find((q) => !mapped.has(q.id))!;
    const html = renderToStaticMarkup(
      <PoliticalMap
        answers={{ [q.id]: { value: 1, importance: 1 } }}
        selectedParty="pp"
        selectParty={() => {}}
      />,
    );
    expect(html).toContain("todavía no tiene un eje revisado");
    expect(html).toContain("Sin respuestas asignadas a estos ejes");
  });
  it("la vista documental y la personal comparten la misma base y la documental no dibuja un usuario", () => {
    const html = renderToStaticMarkup(
      <PoliticalMap
        answers={{}}
        selectedParty="pp"
        selectParty={() => {}}
        showUser={false}
      />,
    );
    expect(html).toContain("Índices documentales por temas");
    expect(html).not.toContain("user-position-ring");
    expect(documentaryAxis("no-existe", map.x).value).toBeNull();
  });
});
