import { expect, it } from "vitest";
import audit from "../revisiones/2026-10-08-parlamento/informe.json";
import { people, portraits, findPerson } from "./datos/catalogo";
import { matchesAffiliation } from "./vinculaciones";

it("incluye cada identidad del Congreso y Senado desde 1977 con su fuente individual", () => {
  expect(audit.records).toHaveLength(5544);
  expect(audit.records.filter((r) => r.chamber === "congreso")).toHaveLength(3023);
  expect(audit.records.filter((r) => r.chamber === "senado")).toHaveLength(2521);
  expect(new Set(audit.records.map((r) => `${r.chamber}:${r.key}`)).size).toBe(5544);
  expect(people).toHaveLength(audit.uniquePeople);
  for (const r of audit.records) {
    const person = findPerson(r.id);
    expect(person, r.name).toBeTruthy();
    expect(person!.references.some((s) => s.url === r.source), r.name).toBe(true);
    expect(r.sourceError, r.name).toBeFalsy();
  }
  expect(people.filter((p) => matchesAffiliation(p, "pp")).length).toBeGreaterThan(500);
  expect(people.filter((p) => matchesAffiliation(p, "psoe")).length).toBeGreaterThan(1000);
});

it("los retratos corresponden a recursos documentados y las ausencias quedan identificadas", () => {
  const available = people.filter((p) => portraits[p.id]);
  expect(available.length).toBe(audit.portraitPeople);
  expect(available.length / people.length).toBeGreaterThan(.99);
  for (const p of available) {
    expect(p.photoCredit, p.name).toBeTruthy();
    expect(new URL(p.photoSource!).protocol, p.name).toBe("https:");
  }
  expect(people.filter((p) => !portraits[p.id]).map((p) => p.id).sort()).toEqual(audit.missingPortraits.map((p) => p.id).sort());
});

it("reúne identidades de ambas cámaras y explica las discrepancias sin inventar precisión", () => {
  expect(findPerson("congreso-304-15")?.id).toBe("aitor-esteban");
  expect(findPerson("senado-10262")?.id).toBe("congreso-182-6");
  expect(findPerson("agustin-rodriguez-sahagun")?.birthDate).toBe("1932-04-27");
  const valdivielso = people.find((p) => p.fullName === "Santiago López Valdivielso")!;
  expect(valdivielso.birthDate).toBe("1950-02-07");
  expect(valdivielso.deathDate).toBe("2024-01-09");
  expect(valdivielso.birthNote).toContain("Congreso");
});
