import { expect, it } from "vitest";
import {
  clmGovernments,
  clmParliaments,
  clmGovernmentChronology,
  clmParliamentChronology,
} from "./clm-model";
import {
  cylGovernments,
  cylParliaments,
  cylGovernmentChronology,
  cylParliamentChronology,
} from "./cyl-model";
import { archivedGroups, regionalDates } from "./catalonia-model";
import { findPerson, portraits } from "../../Políticos/interfaz/datos/catalogo";
import conservation from "../revisiones/2026-10-15-castillas/conservacion.json";

it("conserva todos los IDs del archivo previo al incorporar las dos comunidades", () => {
  for (const id of conservation.baselineIds)
    expect(findPerson(id), id).toBeTruthy();
});

it("incorpora las once y doce legislaturas y todos los nombramientos presidenciales, con enlaces personales", () => {
  expect(clmParliaments).toHaveLength(11);
  expect(cylParliaments).toHaveLength(12);
  expect(clmGovernments).toHaveLength(12);
  expect(cylGovernments).toHaveLength(15);
  const periods = [
    ...clmParliaments,
    ...cylParliaments,
    ...clmGovernments,
    ...cylGovernments,
  ];
  expect(new Set(periods.map((p) => p.id)).size).toBe(periods.length);
  for (const p of periods) {
    const records =
      "records" in p
        ? [...p.records, ...p.board, ...(p.archiveBoard ?? [])]
        : [...p.terms, ...(p.archiveTerms ?? [])];
    for (const record of records) {
      expect(findPerson(record.person), record.name).toBeTruthy();
      // Algunos decretos históricos publican su enlace original por HTTP.
      // Se conserva la referencia efectiva, sin inventar una URL equivalente.
      expect(record.source).toMatch(/^https?:\/\//);
    }
  }
});

it("representa personas únicas en los plenos actuales y las composiciones archivadas de ambas Castillas", () => {
  for (const [periods, count] of [
    [clmParliaments, 33],
    [cylParliaments, 82],
  ] as const) {
    const current = periods[0];
    expect(current.currentOnly).toBe(true);
    expect(current.records).toHaveLength(count);
    expect(new Set(current.records.map((p) => p.person)).size).toBe(count);
    for (const person of current.records)
      expect(
        portraits[findPerson(person.person)!.id],
        person.name,
      ).toBeTruthy();
    for (const p of periods.slice(1)) {
      expect(p.nominalOnly).toBe(true);
      const members = archivedGroups(p).flatMap((g) => g.members);
      expect(new Set(members.map((m) => m.person)).size).toBe(members.length);
      expect(members.length).toBeGreaterThan(0);
      expect(members.length).toBeLessThanOrEqual(p.capacity!);
    }
  }
  for (const p of cylParliaments.slice(1))
    expect(archivedGroups(p).flatMap((g) => g.members)).toHaveLength(
      p.capacity!,
    );
  expect(
    clmParliaments.find((p) => p.label === "Legislatura IX")!.records.length,
  ).toBeGreaterThan(33);
  expect(
    archivedGroups(
      clmParliaments.find((p) => p.label === "Legislatura IX")!,
    ).flatMap((g) => g.members),
  ).toHaveLength(30);
});

it("limita los gobiernos vigentes a su consulta, reúne las competencias y conserva gabinetes históricos", () => {
  for (const [periods, count] of [
    [clmGovernments, 13],
    [cylGovernments, 12],
  ] as const) {
    const g = periods[0];
    expect(g.currentOnly).toBe(true);
    expect(regionalDates(g, g.terms, g.currentOnly)).toEqual([g.checkedAt]);
    expect(g.terms).toHaveLength(count);
    expect(new Set(g.terms.map((t) => t.person)).size).toBe(count);
    for (const t of g.terms)
      expect(portraits[findPerson(t.person)!.id], t.name).toBeTruthy();
    for (const p of periods.slice(1))
      expect(p.archiveTerms?.length, p.label).toBeGreaterThan(0);
  }
  const pollan = cylGovernments[0].terms.find((t) =>
    t.name.includes("Pollán"),
  )!;
  expect(pollan.level).toBe("vice");
  expect(pollan.role).toContain("Desregulación");
});

it("conserva todas las etapas en ambas cronologías y los IDs anteriores al completar nombres", () => {
  for (const [periods, chronology] of [
    [clmGovernments, clmGovernmentChronology],
    [cylGovernments, cylGovernmentChronology],
    [clmParliaments, clmParliamentChronology],
    [cylParliaments, cylParliamentChronology],
  ] as const)
    for (const p of periods)
      expect(chronology.some((s) => s.period.id === p.id)).toBe(true);
  expect(findPerson("congreso-107-13")?.fullName).toBe(
    "Blanca Pilar Fernández Morena",
  );
  expect(findPerson("clm-blanca-pilar-fernandez-morena")?.id).toBe(
    "congreso-107-13",
  );
  expect(findPerson("clm-ma-mercedes-gomez-rodriguez")?.fullName).toBe(
    "María Mercedes Gómez Rodríguez",
  );
  expect(findPerson("cyl-jose-constantino-nalda")?.id).toBe("senado-10906");
  expect(findPerson("cyl-milagros-marcos")?.id).toBe("congreso-320-15");
});
