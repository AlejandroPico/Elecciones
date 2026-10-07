import { expect, it } from "vitest";
import { offices, governmentCatalog } from "./catalogo";
it("distingue Cultura de Agricultura y un ministerio de una vicepresidencia con responsabilidad sobre el área", () => {
  const recent = governmentCatalog[0].cabinets.at(-1)!;
  const culture = recent.members.find((m) =>
    /ministr[oa] de Cultura$/i.test(m.role),
  )!;
  expect(culture).toBeTruthy();
  expect(offices.find((o) => o.id === "cultura")!.members[0].person).toBe(
    culture.person,
  );
  const first = governmentCatalog.at(-1)!.cabinets[0];
  const defense = first.members.find((m) =>
    /ministr[oa] de Defensa$/i.test(m.role),
  )!;
  expect(offices.find((o) => o.id === "defensa")!.members.at(-1)!.person).toBe(
    defense.person,
  );
});
it("los cargos pendientes tienen una fuente institucional y no inventan titulares", () => {
  for (const o of offices.filter((o) => o.pending)) {
    expect(o.members).toEqual([]);
    expect(new URL(o.source.url).protocol).toBe("https:");
  }
  expect(offices.some((o) => o.id === "congreso")).toBe(true);
  expect(offices.some((o) => o.id === "portavoces-senado")).toBe(true);
  expect(new Set(offices.map((o) => o.id)).size).toBe(offices.length);
  const structure = offices.filter((o) => o.id.startsWith("boe-1009-2023-"));
  expect(structure).toHaveLength(192);
  for (const office of structure) {
    expect(office.department).toBeTruthy();
    expect(office.pending).toBe(true);
    expect(office.source.url).toContain("BOE-A-2023-24842");
  }
});
