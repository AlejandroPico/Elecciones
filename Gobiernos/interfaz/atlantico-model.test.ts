import { expect, it } from "vitest";
import {
  canariasGovernments,
  canariasParliaments,
  canariasGovernmentChronology,
  canariasParliamentChronology,
} from "./canarias-model";
import {
  ceutaGovernments,
  ceutaParliaments,
  ceutaGovernmentChronology,
  ceutaParliamentChronology,
} from "./ceuta-model";
import {
  melillaGovernments,
  melillaParliaments,
  melillaGovernmentChronology,
  melillaParliamentChronology,
} from "./melilla-model";
import {
  archivedGroups,
  catalanMembersAt,
  catalanGroupsAt,
  regionalDates,
} from "./catalonia-model";
import {
  findPerson,
  portraits,
  organizations,
} from "../../Políticos/interfaz/datos/catalogo";
import { ownOfficeTerms } from "../../Políticos/interfaz/relaciones";

it("enlaza las once legislaturas canarias y las ocho de cada ciudad, con todas las presidencias", () => {
  expect(canariasParliaments).toHaveLength(11);
  expect(ceutaParliaments).toHaveLength(8);
  expect(melillaParliaments).toHaveLength(8);
  expect(canariasGovernments).toHaveLength(15);
  expect(ceutaGovernments).toHaveLength(10);
  expect(melillaGovernments).toHaveLength(10);
  for (const p of [
    ...canariasParliaments,
    ...ceutaParliaments,
    ...melillaParliaments,
    ...canariasGovernments,
    ...ceutaGovernments,
    ...melillaGovernments,
  ]) {
    const terms =
      "terms" in p
        ? [...p.terms, ...(p.archiveTerms ?? [])]
        : [...p.records, ...p.board, ...(p.archiveBoard ?? [])];
    for (const t of terms) {
      const person = findPerson(t.person);
      expect(person, t.name).toBeTruthy();
      expect(
        person!.references.some((s) => s.url === t.source),
        t.name,
      ).toBe(true);
      if (t.start && t.end) expect(t.start < t.end, t.name).toBe(true);
      for (const a of person!.affiliations ?? [])
        if (a.organization)
          expect(
            organizations.some(
              (o) =>
                o.id === a.organization ||
                o.legacyIds?.includes(a.organization!),
            ),
            a.name,
          ).toBe(true);
    }
  }
});

it("los registros actuales tienen 70, 25 y 25 personas y no se proyectan sobre 2023", () => {
  for (const [p, count] of [
    [canariasParliaments[0], 70],
    [ceutaParliaments[0], 25],
    [melillaParliaments[0], 25],
  ] as const) {
    expect(p.currentOnly).toBe(true);
    expect(catalanMembersAt(p, p.checkedAt)).toHaveLength(count);
    expect(new Set(p.records.map((t) => t.person)).size).toBe(count);
    expect(
      catalanGroupsAt(p, p.checkedAt).flatMap((g) => g.members),
    ).toHaveLength(count);
    expect(catalanMembersAt(p, "2023-06-01")).toEqual([]);
    expect(p.board).toHaveLength(p.capacity === 70 ? 5 : 3);
  }
});

it("muestra todos los hemiciclos históricos y mantiene los relevos fuera del reparto de electos", () => {
  const counts = [70, 58, 60, 60, 60, 59, 60, 60, 60, 60];
  for (const [index, p] of canariasParliaments.slice(1).entries()) {
    const members = archivedGroups(p).flatMap((g) => g.members);
    expect(members, index.toString()).toHaveLength(counts[index]);
    expect(new Set(members.map((t) => t.person)).size).toBe(members.length);
    expect(p.nominalOnly).toBe(true);
    expect(members.length).toBeLessThanOrEqual(p.capacity!);
  }
  for (const p of [
    ...ceutaParliaments.slice(1),
    ...melillaParliaments.slice(1),
  ]) {
    expect(p.records).toHaveLength(25);
    expect(p.nominalOnly).toBe(true);
    expect(archivedGroups(p).flatMap((g) => g.members)).toHaveLength(25);
    expect(p.records.every((t) => t.start === null && t.end === null)).toBe(
      true,
    );
  }
});

it("conserva una cronología para cada etapa y limita los gabinetes vigentes a la consulta", () => {
  for (const [periods, chronology] of [
    [canariasGovernments, canariasGovernmentChronology],
    [ceutaGovernments, ceutaGovernmentChronology],
    [melillaGovernments, melillaGovernmentChronology],
    [canariasParliaments, canariasParliamentChronology],
    [ceutaParliaments, ceutaParliamentChronology],
    [melillaParliaments, melillaParliamentChronology],
  ] as const) {
    for (const p of periods)
      expect(chronology.some((s) => s.period.id === p.id)).toBe(true);
  }
  for (const [g, count] of [
    [canariasGovernments[0], 13],
    [ceutaGovernments[0], 8],
    [melillaGovernments[0], 9],
  ] as const) {
    expect(g.currentOnly).toBe(true);
    expect(regionalDates(g, g.terms, g.currentOnly)).toEqual([g.checkedAt]);
    expect(g.terms).toHaveLength(count);
    expect(g.terms.every((t) => t.observedAt === g.checkedAt)).toBe(true);
    expect(new Set(g.terms.map((t) => t.person)).size).toBe(count);
  }
});

it("refleja el cese de Hacienda en Melilla y el nombramiento universitario de julio de 2026", () => {
  const g = melillaGovernments[0];
  expect(g.terms.some((t) => t.name.includes("Conesa"))).toBe(false);
  expect(g.terms.some((t) => t.name.includes("Quevedo"))).toBe(false);
  expect(g.terms.find((t) => t.name.includes("Ventura"))?.role).toContain(
    "Medio Ambiente",
  );
  expect(g.terms.find((t) => t.name.includes("Ronda"))?.role).toContain(
    "Seguridad Ciudadana",
  );
  expect(g.terms.find((t) => t.name.includes("Mohatar"))?.level).toBe("vice");
  expect(
    g.terms.some(
      (t) =>
        t.name === "Jesús Manuel Romero Imbroda" &&
        t.role.includes("Universitario"),
    ),
  ).toBe(true);
  expect(
    ceutaGovernments[0].terms.filter((t) => t.level === "vice"),
  ).toHaveLength(2);
  const p = findPerson(g.terms.find((t) => t.name.includes("Romero"))!.person)!;
  expect(ownOfficeTerms(p).some((t) => t.name.includes("Universitario"))).toBe(
    true,
  );
  expect(portraits[p.id]).toBeTruthy();
});
