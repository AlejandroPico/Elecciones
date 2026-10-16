import { expect, it } from "vitest";
import {
  basqueInstitutions as basque,
  navarreInstitutions as navarre,
} from "./norte-model";
import {
  archivedGroups,
  catalanGroupsAt,
  regionalDates,
} from "./catalonia-model";
import {
  findPerson,
  people,
  portraits,
} from "../../Políticos/interfaz/datos/catalogo";
import conservation from "../revisiones/2026-10-16-norte/conservacion.json";
import audit from "../../Políticos/revisiones/2026-10-16-norte/informe.json";
import overlaps from "../Autonomías/País Vasco/fuentes/solapamientos-cronologicos.json";

it("conserva todas las identidades previas y resuelve cada cargo de ambas comunidades", () => {
  for (const id of conservation.baselineIds)
    expect(findPerson(id), id).toBeTruthy();
  expect(people.length).toBeGreaterThanOrEqual(
    conservation.baselineIds.length + audit.newPeople.length,
  );
  expect(basque.governments).toHaveLength(14);
  expect(navarre.governments).toHaveLength(15);
  expect(basque.parliaments).toHaveLength(13);
  expect(navarre.parliaments).toHaveLength(12);
  for (const institutions of [basque, navarre]) {
    for (const period of [
      ...institutions.governments,
      ...institutions.parliaments,
    ]) {
      const records =
        "records" in period
          ? [...period.records, ...period.board, ...(period.archiveBoard ?? [])]
          : [...period.terms, ...(period.archiveTerms ?? [])];
      expect(records.length, period.label).toBeGreaterThan(0);
      for (const row of records) {
        expect(findPerson(row.person), row.name).toBeTruthy();
        expect(row.source).toMatch(/^https:\/\//);
        expect(row.name).not.toMatch(/�|Sustituido|^de Goicoechea$|^y Lazkano/);
        if (row.start && row.end)
          expect(row.start <= row.end, row.name).toBe(true);
      }
    }
  }
});

it("reproduce el aforo vasco de 60 y 75 sin ofrecer los solapamientos erróneos del origen", () => {
  expect(basque.parliaments.at(-1)!.capacity).toBe(60);
  for (const period of basque.parliaments) {
    const capacity = period.label === "Legislatura I" ? 60 : 75;
    expect(period.capacity).toBe(capacity);
    expect(period.board.length).toBeGreaterThanOrEqual(5);
    const preferred = catalanGroupsAt(period, period.preferredDate!).flatMap(
      (g) => g.members,
    );
    expect(preferred).toHaveLength(capacity);
    expect(
      preferred.every((r) => !!r.constituency),
      period.label,
    ).toBe(true);
    for (const snapshot of basque.parliamentChronology.filter(
      (s) => s.period.id === period.id,
    ))
      expect(
        catalanGroupsAt(period, snapshot.date).flatMap((g) => g.members).length,
      ).toBeLessThanOrEqual(capacity);
  }
  expect(overlaps.records.length).toBeGreaterThan(0);
  for (const row of overlaps.records)
    expect(
      basque.parliamentChronology.some(
        (s) =>
          s.period.id === `pais-vasco-parlamento-${row.legislature}` &&
          s.date === row.date,
      ),
    ).toBe(false);
  const current = catalanGroupsAt(
    basque.parliaments[0],
    basque.parliaments[0].checkedAt,
  ).flatMap((g) => g.members);
  expect(current).toHaveLength(75);
  for (const row of current)
    expect(portraits[row.person], row.name).toBeTruthy();
});

it("distingue las relaciones nominales navarras del Pleno vigente y de sus relevos", () => {
  for (const period of navarre.parliaments) {
    const capacity = period.label.startsWith("Parlamento Foral") ? 70 : 50;
    expect(period.capacity).toBe(capacity);
    const members = period.currentOnly
      ? catalanGroupsAt(period, period.checkedAt).flatMap((g) => g.members)
      : archivedGroups(period).flatMap((g) => g.members);
    expect(members).toHaveLength(capacity);
    expect(new Set(members.map((r) => r.person)).size).toBe(capacity);
    if (!period.currentOnly) {
      expect(period.nominalOnly).toBe(true);
      expect(
        period.records.every((r) => r.start === null && r.end === null),
      ).toBe(true);
      expect(period.archiveBoard!.length).toBeGreaterThanOrEqual(5);
    } else {
      expect(regionalDates(period, period.records, true)).toEqual([
        period.checkedAt,
      ]);
      expect(period.board).toHaveLength(5);
      for (const row of members)
        expect(portraits[row.person], row.name).toBeTruthy();
    }
  }
  expect(navarre.parliaments.at(-1)!.start).toBe("1979-04-23");
  expect(navarre.parliaments[0].start).toBe("2023-06-16");
});

it("limita los gabinetes vigentes a la consulta y reúne competencias por persona", () => {
  for (const [institutions, count] of [
    [basque, 16],
    [navarre, 14],
  ] as const) {
    const current = institutions.governments[0];
    expect(current.currentOnly).toBe(true);
    expect(current.terms).toHaveLength(count);
    expect(new Set(current.terms.map((r) => r.person)).size).toBe(count);
    expect(current.terms.filter((r) => r.level === "president")).toHaveLength(
      1,
    );
    expect(regionalDates(current, current.terms, true)).toEqual([
      current.checkedAt,
    ]);
    for (const row of current.terms)
      expect(portraits[row.person], row.name).toBeTruthy();
    for (const period of institutions.governments.filter(
      (g) => !g.currentOnly,
    )) {
      expect(period.archiveTerms!.length, period.label).toBeGreaterThan(0);
      expect(new Set(period.archiveTerms!.map((r) => r.person)).size).toBe(
        period.archiveTerms!.length,
      );
      expect(
        period.archiveTerms!.every((r) => r.start === null && r.end === null),
      ).toBe(true);
    }
  }
  const bix = people.find((p) => p.fullName === "Bixen Itxaso González");
  const denis = people.find((p) => p.fullName === "Denis Itxaso González");
  expect(bix).toBeTruthy();
  expect(denis).toBeTruthy();
  expect(bix!.id).not.toBe(denis!.id);
  const historic = navarre.governments.flatMap((p) => p.archiveTerms ?? []);
  expect(
    historic.some((p) => p.name === "Pedro Sánchez de Muniáin Corera"),
  ).toBe(true);
  expect(historic.some((p) => p.name === "Jesús Pejenaute Grávalos")).toBe(
    true,
  );
  expect(
    people.some(
      (p) =>
        p.fullName === "Jesús Pejenaute Garde" ||
        p.fullName === "Pedro Sánchez de Muniáin Lacasia",
    ),
  ).toBe(false);
});
