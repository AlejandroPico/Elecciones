import { expect, it } from "vitest";
import { people, organizations, offices, candidacies } from "./archive-data";
it("todas las relaciones del archivo tienen destino y las etapas tienen fuente", () => {
  expect(new Set(people.map((p) => p.id)).size).toBe(people.length);
  for (const p of people) {
    if (p.organization)
      expect(organizations.some((o) => o.id === p.organization)).toBe(true);
    for (const id of p.offices)
      expect(offices.some((o) => o.id === id)).toBe(true);
    for (const t of p.timeline)
      expect(new URL(t.source.url).protocol).toBe("https:");
    if (p.portrait) {
      expect(p.photoCredit).toBeTruthy();
      expect(p.photoSource).toBeTruthy();
    }
  }
  for (const o of offices)
    for (const m of o.members)
      expect(
        people.some((p) => p.id === m.person && p.offices.includes(o.id)),
      ).toBe(true);
  for (const o of organizations)
    for (const h of o.history)
      if (h.person) expect(people.some((p) => p.id === h.person)).toBe(true);
});
it("no convierte las biografías ni los documentos históricos en candidaturas de 2026", () => {
  expect(candidacies).toEqual([]);
  for (const o of organizations)
    for (const d of o.documents) {
      expect(d.election).toContain("2023");
      expect(new URL(d.url).protocol).toBe("https:");
    }
});
