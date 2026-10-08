import { expect, it } from "vitest";
import { people } from "./datos/catalogo";
import { personActivity } from "./actividad";
import { orderPeople } from "./orden";
import { ownOfficeTerms } from "./relaciones";

it("prioriza actividad documentada en cualquier orden y nunca toma la edad por retirada", () => {
  const base = people.find((p) => p.id === "sanchez")!;
  const active = { ...base, id: "active", name: "Z activo", fullName: "Z activo", activity: { state: "active" as const, checkedAt: "2026-10-08", reason: "Mandato contrastado", sources: [] } };
  const deceased = { ...active, id: "deceased", fullName: "A fallecido", deathYear: 2020 };
  const unknown = { ...active, id: "unknown", activity: undefined, birthYear: 1920, timeline: [] };
  expect(personActivity(deceased)).toBe("historical");
  expect(personActivity(unknown)).toBe("unknown");
  expect(personActivity({ ...unknown, timeline: [{ title: "Senador", period: "2011 — 2015", source: { label: "Senado", url: "https://www.senado.es" } }] })).toBe("unknown");
  for (const order of ["name", "recent", "oldest", "rank"] as const) expect(orderPeople([deceased, unknown, active], order).map((p) => p.id)).toEqual(["active", "unknown", "deceased"]);
});
it("reúne cargos diferentes de una misma persona sin incluir a otros titulares", () => {
  const person = people.find((p) => ownOfficeTerms(p).filter((t) => t.office).length >= 2)!;
  expect(person).toBeTruthy();
  const terms = ownOfficeTerms(person);
  expect(new Set(terms.map((t) => `${t.name}:${t.period}`)).size).toBe(terms.length);
  expect(terms.every((t) => !t.name.includes("Relaciones por cargo"))).toBe(true);
  const guirao = people.find((p) => p.fullName === "José Guirao Cabrera")!;
  expect(ownOfficeTerms(guirao).map((t) => t.period).join(" ")).not.toContain("2023");
});
