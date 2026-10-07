import { expect, it } from "vitest";
import { questions } from "../../../Elecciones";
import { contexts } from "../../../Elecciones/Generales Noviembre 2026/contextos";
import {
  chronology,
  governments,
  snapshotAt,
} from "../../../Gobiernos/interfaz/government-model";
import { people, portraits, organizations } from "./catalogo";
import { structureSnapshot } from "../../../Gobiernos/XV Legislatura/estructura";
const parties = organizations;
import { congress } from "../../../Elecciones/Generales Noviembre 2026/congreso";
it("toda pregunta tiene una explicación de alcance y dos consideraciones", () => {
  expect(Object.keys(contexts).sort()).toEqual(
    questions.map((q) => q.id).sort(),
  );
  for (const q of questions) {
    expect(contexts[q.id].scope.length).toBeGreaterThan(140);
    expect(contexts[q.id].considerations).toHaveLength(2);
  }
});
it("el relevo de marzo de 2026 cambia Hacienda y Vicepresidencia Primera el día documentado", () => {
  const before = snapshotAt("2026-03-26")!,
    after = snapshotAt("2026-03-27")!;
  expect(
    before.members.some((m) => m.person === "maria-jesus-montero-cuadrado"),
  ).toBe(true);
  expect(
    after.members.some((m) => m.person === "maria-jesus-montero-cuadrado"),
  ).toBe(false);
  expect(after.members.find((m) => m.person === "cuerpo")?.level).toBe(
    "vicepresident",
  );
  expect(after.members.some((m) => m.person === "espana")).toBe(true);
  expect(after.members).toHaveLength(23);
});
it("todos los gabinetes y órganos tienen fichas y niveles independientes", () => {
  expect(governments).toHaveLength(16);
  expect(governments.at(-1)?.cabinets[0].date).toBe("1977-07");
  expect(new Set(chronology.map((c) => c.id)).size).toBe(chronology.length);
  for (const g of governments) {
    expect(new URL(g.source).protocol).toBe("https:");
    for (const c of g.cabinets) {
      expect(c.members.filter((m) => m.level === "president")).toHaveLength(1);
      expect(c.members.length).toBeGreaterThan(10);
      for (const m of c.members)
        expect(people.some((p) => p.id === m.person)).toBe(true);
    }
  }
  for (const n of structureSnapshot.nodes) {
    expect(people.some((p) => p.id === n.person)).toBe(true);
    expect(people.some((p) => p.id === n.parent)).toBe(true);
  }
});
it("los nombres y retratos no se asignan a una persona por un apellido compartido", () => {
  const normal = (s: string) =>
    s
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/-/g, " ")
      .toLowerCase()
      .split(/\s+/)
      .slice(0, 2)
      .join(" ");
  for (const p of people) {
    if (p.fullName) expect(normal(p.fullName)).toBe(normal(p.name));
    if (p.portrait) expect(portraits[p.portrait]).toBeTruthy();
  }
  const felipe = people.find((p) => p.id === "felipe-gonzalez-marquez")!;
  expect(felipe.birthYear).toBe(1942);
  expect(people.find((p) => p.id === "manuel-chaves-gonzalez")?.birthYear).toBe(
    1945,
  );
});
it("el mosaico enlaza fichas reales y el Congreso suma 350 sin mezclar PSOE y PSC", () => {
  for (const p of parties) {
    expect(organizations.some((o) => o.id === p.id)).toBe(true);
    if (p.logo) expect(new URL(p.logoSource!).protocol).toBe("https:");
  }
  expect(congress.parties.reduce((sum, p) => sum + p.seats, 0)).toBe(
    congress.total,
  );
  expect(congress.parties.find((p) => p.name === "PSOE")?.seats).toBe(102);
  expect(congress.parties.find((p) => p.name === "PSC-PSOE")?.seats).toBe(19);
});
