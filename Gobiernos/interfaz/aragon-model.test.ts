import { expect, it } from "vitest";
import {
  aragonGovernments,
  aragonParliaments,
  aragonGovernmentChronology,
  aragonParliamentChronology,
} from "./aragon-model";
import { archivedGroups, regionalDates } from "./catalonia-model";
import { findPerson, portraits } from "../../Políticos/interfaz/datos/catalogo";
import conservation from "../revisiones/2026-10-16-aragon/conservacion.json";
import audit from "../revisiones/2026-10-16-aragon/informe.json";

it("conserva el catálogo anterior y enlaza todas las etapas aragonesas con personas reales", () => {
  for (const id of conservation.baselineIds)
    expect(findPerson(id), id).toBeTruthy();
  expect(aragonGovernments).toHaveLength(14);
  expect(aragonParliaments).toHaveLength(12);
  expect(audit.profileErrors).toHaveLength(0);
  for (const p of [...aragonGovernments, ...aragonParliaments]) {
    const records =
      "records" in p
        ? [...p.records, ...p.board, ...(p.archiveBoard ?? [])]
        : [...p.terms, ...(p.archiveTerms ?? [])];
    for (const r of records) {
      expect(findPerson(r.person), r.name).toBeTruthy();
      expect(r.name).not.toMatch(/[�Ãã]/);
      expect(r.source).toMatch(/^https:\/\//);
    }
  }
});
it("distingue los 66 escaños de la primera legislatura de los 67 siguientes y conserva los relevos aparte", () => {
  for (const p of aragonParliaments) {
    const capacity = p.label === "Legislatura I" ? 66 : 67;
    expect(p.capacity).toBe(capacity);
    const members = p.currentOnly
      ? p.groups.flatMap((g) => g.members)
      : archivedGroups(p).flatMap((g) => g.members);
    expect(members).toHaveLength(capacity);
    expect(new Set(members.map((m) => m.person)).size).toBe(capacity);
    expect(p.records.length).toBeGreaterThanOrEqual(capacity);
    if (p.currentOnly)
      for (const m of members)
        expect(portraits[findPerson(m.person)!.id], m.name).toBeTruthy();
  }
  expect(aragonParliaments[0].start).toBe("2026-03-03");
  expect(aragonParliaments[0].end).toBeNull();
  expect(aragonParliaments[0].board).toHaveLength(5);
  expect(aragonParliaments.at(-1)!.records.length).toBeGreaterThan(66);
});
it("limita el Gobierno actual a su consulta, conserva la interinidad y los gabinetes archivados", () => {
  const current = aragonGovernments[0];
  expect(current.start).toBe("2026-04-29");
  expect(current.currentOnly).toBe(true);
  expect(regionalDates(current, current.terms, current.currentOnly)).toEqual([
    current.checkedAt,
  ]);
  expect(current.terms).toHaveLength(10);
  expect(new Set(current.terms.map((t) => t.person)).size).toBe(10);
  for (const t of current.terms)
    expect(portraits[findPerson(t.person)!.id], t.name).toBeTruthy();
  expect(current.terms.filter((t) => t.level === "vice")).toHaveLength(2);
  expect(
    aragonGovernments.find((p) => p.label.includes("interino"))?.terms[0].name,
  ).toBe("Ramón Tejedor Sanz");
  for (const surname of [
    "Aliaga López",
    "Boné Pueyo",
    "Almunia Badía",
    "Ferrer Górriz",
  ]) {
    const records = [
      ...aragonGovernments.flatMap((g) => [
        ...g.terms,
        ...(g.archiveTerms ?? []),
      ]),
      ...aragonParliaments.flatMap((p) => p.records),
    ].filter((r) => r.name.endsWith(surname));
    expect(records.length).toBeGreaterThan(1);
    expect(new Set(records.map((r) => r.person)).size, surname).toBe(1);
  }
  for (const p of aragonGovernments.slice(1))
    expect(p.archiveTerms?.length, p.name).toBeGreaterThan(0);
  for (const p of aragonGovernments)
    expect(aragonGovernmentChronology.some((s) => s.period.id === p.id)).toBe(
      true,
    );
  for (const p of aragonParliaments)
    expect(aragonParliamentChronology.some((s) => s.period.id === p.id)).toBe(
      true,
    );
});
