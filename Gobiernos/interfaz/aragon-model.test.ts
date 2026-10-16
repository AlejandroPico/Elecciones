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
import portraitReview from "../Autonomías/Aragón/fuentes/revision-retratos-pendientes.json";
import completedPortraits from "../Autonomías/Aragón/fuentes/retratos-complementados.json";

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
  const firstBoard = aragonParliaments.at(-1)!.archiveBoard!;
  expect(firstBoard).toHaveLength(5);
  expect(new Set(firstBoard.map((m) => m.person)).size).toBe(5);
  expect(
    firstBoard.find((m) => m.role.startsWith("Vicepresidenta"))!.name,
  ).toBe("María Soledad Navarro Pratsavall");
  for (const m of firstBoard) {
    expect(m.start).toBeNull();
    expect(m.end).toBeNull();
  }
});
it("registra todos los retratos revisados y distingue ausencias de homónimos", () => {
  expect(portraitReview.cases).toHaveLength(41);
  expect(portraitReview.remaining).toBe(23);
  expect(completedPortraits.portraits).toHaveLength(18);
  for (const p of completedPortraits.portraits)
    expect(portraits[p.id], p.name).toBeTruthy();
  expect(
    portraitReview.cases
      .flatMap((p) => p.articleChecks)
      .filter((p) => p.result.startsWith("descartado")),
  ).toHaveLength(2);
  expect(audit.supplementaryReview.inconsistentIntervals).toHaveLength(3);
  for (const p of aragonGovernments)
    for (const t of p.archiveTerms ?? []) {
      const dates = t.period?.match(
        /(\d{4}-\d{2}-\d{2}) — (\d{4}-\d{2}-\d{2})/,
      );
      if (dates) expect(dates[1] < dates[2], t.name).toBe(true);
    }
  const council = findPerson("jorge-azcon")!.timeline!.filter(
    (t) => t.title === "Concejal del Ayuntamiento de Zaragoza",
  );
  expect(council.map((t) => t.period)).toEqual(["2000 – 2007", "2011 – 2023"]);
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
