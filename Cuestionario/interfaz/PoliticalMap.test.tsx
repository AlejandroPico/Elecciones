import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
vi.mock("../../Partidos/interfaz/catalogo", () => ({ logos: {} }));
import PoliticalMap from "./PoliticalMap";
import {
  bank,
  coordinatePair,
  documentaryAxis,
  uniqueResponses,
} from "./sesion";

describe("coordenadas personales", () => {
  it("distingue al usuario de los partidos y conserva la pregunta real de cada eje", () => {
    const [a, b] = bank.questions.filter((q) => q.category === "empresa");
    const html = renderToStaticMarkup(
      <PoliticalMap
        answers={{
          [a.id]: { value: -2, importance: 3 },
          [b.id]: { value: 1, importance: 1 },
        }}
        selectedParty="pp"
        selectParty={() => {}}
      />,
    );
    expect(html).toContain("Tus coordenadas");
    expect(html).toContain("Tú · doble aro animado");
    expect(html).toContain("user-position-pulse");
    expect(html).toContain(a.text);
    expect(html).toContain(b.text);
    expect(html).toContain("Por qué PP está aquí");
    expect(html).toContain("Partidos · siglas dentro del punto");
  });
  it("una sola respuesta deja el otro eje pendiente y dibuja una proyección, no un punto en cero", () => {
    const a = bank.questions[0];
    const html = renderToStaticMarkup(
      <PoliticalMap
        answers={{ [a.id]: { value: 2, importance: 2 } }}
        selectedParty="pp"
        selectParty={() => {}}
      />,
    );
    expect(html).toContain("Tú · solo X");
    expect(html).toContain("user-projection");
    expect(html).not.toContain('class="user-position-ring"');
    expect(html).toContain("Y Sin dato");
  });
  it("los signos y ausencias del mapa documental no se infieren de la etiqueta del partido", () => {
    const id = bank.questions[0].id;
    const axis = {
      label: "test",
      indicators: [{ label: "a", questionIds: [id, id], direction: -1 }],
    };
    expect(documentaryAxis("pp", axis).value).toBe(-100);
    expect(documentaryAxis("no-existe", axis).value).toBeNull();
    expect(documentaryAxis("pp", axis).count).toBe(1);
  });
  it("seleccionar propuestas con cobertura común no depende de las respuestas del usuario", () => {
    const qs = bank.questions
      .filter((q) => q.category === "empresa")
      .slice(0, 10);
    const a = Object.fromEntries(
      qs.map((q) => [q.id, { value: 2, importance: 1 as const }]),
    );
    const b = Object.fromEntries(
      qs.map((q) => [q.id, { value: -2, importance: 3 as const }]),
    );
    expect(
      coordinatePair(uniqueResponses(a)).map((e) => e.question.id),
    ).toEqual(coordinatePair(uniqueResponses(b)).map((e) => e.question.id));
  });
});
