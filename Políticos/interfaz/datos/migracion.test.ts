import { expect, it } from "vitest";
import before from "../../../docs/migracion-2026-10-07.json";
import {
  people,
  organizations,
  governmentCatalog,
  findPerson,
} from "./catalogo";

it("conserva todas las identidades anteriores al separar las carpetas", () => {
  expect(people.flatMap((p) => [p.id, ...(p.legacyIds ?? [])])).toEqual(
    expect.arrayContaining(before.people),
  );
  for (const id of before.people) expect(findPerson(id)).toBeTruthy();
  expect(organizations.map((p) => p.id)).toEqual(
    expect.arrayContaining(before.parties),
  );
  expect(governmentCatalog.flatMap((g) => g.cabinets.map((c) => c.id))).toEqual(
    expect.arrayContaining(before.cabinets),
  );
  for (const p of people) expect(p.folder.split("/").at(-1)).toBe(p.fullName);
});

it("los dirigentes de partidos enlazan una ficha y una fuente sin convertirse en candidaturas", () => {
  for (const party of organizations)
    for (const leader of party.leadership) {
      expect(people.some((p) => p.id === leader.person)).toBe(true);
      expect(new URL(leader.source.url).protocol).toBe("https:");
    }
  expect(
    organizations
      .find((p) => p.id === "pp")
      ?.leadership.some((l) => l.person === "pablo-casado"),
  ).toBe(true);
  expect(
    organizations
      .find((p) => p.id === "psoe")
      ?.leadership.some((l) => l.person === "alfredo-perez-rubalcaba"),
  ).toBe(true);
});
