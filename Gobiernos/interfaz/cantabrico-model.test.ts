import { expect, it } from "vitest";
import {
  asturianInstitutions as asturias,
  cantabrianInstitutions as cantabria,
} from "./cantabrico-model";
import { archivedGroups, catalanGroupsAt } from "./catalonia-model";
import {
  findPerson,
  people,
  portraits,
} from "../../Políticos/interfaz/datos/catalogo";
import conservation from "../revisiones/2026-10-16-cantabrico/conservacion.json";
import audit from "../../Políticos/revisiones/2026-10-16-cantabrico/informe.json";

it("conserva las identidades previas y resuelve gobiernos, Mesas y mandatos de ambas regiones", () => {
  expect(people.length).toBeGreaterThanOrEqual(audit.totalPeople);
  for (const id of conservation.baselineIds)
    expect(findPerson(id), id).toBeTruthy();
  expect(asturias.governments).toHaveLength(13);
  expect(cantabria.governments).toHaveLength(13);
  expect(asturias.parliaments).toHaveLength(12);
  expect(cantabria.parliaments).toHaveLength(11);
  for (const institutions of [asturias, cantabria]) {
    for (const period of [
      ...institutions.governments,
      ...institutions.parliaments,
    ]) {
      const records =
        "records" in period
          ? [...period.records, ...period.board, ...(period.archiveBoard ?? [])]
          : [...period.terms, ...(period.archiveTerms ?? [])];
      expect(records.length, period.id).toBeGreaterThan(0);
      for (const row of records) {
        expect(findPerson(row.person), row.name).toBeTruthy();
        expect(row.source).toMatch(/^https:\/\//);
        expect(row.name).not.toMatch(/Legislatura|�/);
        if (row.start && row.end)
          expect(row.start <= row.end, row.name).toBe(true);
      }
    }
  }
});

it("reproduce 45 escaños asturianos y 35 o 39 cántabros sin inventar fechas individuales", () => {
  for (const institutions of [asturias, cantabria]) {
    for (const period of institutions.parliaments) {
      const members = period.currentOnly
        ? catalanGroupsAt(period, period.checkedAt).flatMap((g) => g.members)
        : archivedGroups(period).flatMap((g) => g.members);
      expect(members, period.id).toHaveLength(period.capacity!);
      expect(new Set(members.map((r) => r.person)).size, period.id).toBe(
        period.capacity,
      );
      if (!period.currentOnly) {
        expect(period.nominalOnly).toBe(true);
        expect(period.groups).toHaveLength(0);
        expect(
          period.records.every((r) => r.start === null && r.end === null),
        ).toBe(true);
        expect(period.archiveBoard!.length).toBeGreaterThanOrEqual(5);
      }
    }
  }
  expect(asturias.parliaments.every((p) => p.capacity === 45)).toBe(true);
  expect(
    cantabria.parliaments.find((p) => p.label === "Legislatura VIII")!.capacity,
  ).toBe(39);
  expect(cantabria.parliaments[0].capacity).toBe(35);
});

it("limita las composiciones vigentes a la consulta y ofrece retrato de sus integrantes", () => {
  for (const [institutions, ministers, deputies] of [
    [asturias, 11, 45],
    [cantabria, 10, 35],
  ] as const) {
    const government = institutions.governments[0];
    const chamber = institutions.parliaments[0];
    expect(government.currentOnly).toBe(true);
    expect(chamber.currentOnly).toBe(true);
    expect(government.terms).toHaveLength(ministers);
    expect(chamber.records).toHaveLength(deputies);
    expect(chamber.board).toHaveLength(5);
    for (const row of [
      ...government.terms,
      ...chamber.records,
      ...chamber.board,
    ]) {
      expect(row.observedAt).toBe("2026-10-16");
      expect(portraits[row.person], row.name).toBeTruthy();
    }
  }
  expect(
    cantabria.parliaments[0].records.some(
      (r) => r.name === "Ana Obregón Abascal",
    ),
  ).toBe(true);
  expect(
    cantabria.parliaments[0].records.find(
      (r) => r.name === "Cristóbal Palacio Ruiz",
    )?.formationLabel,
  ).toBe("Diputado no adscrito");
  expect(
    asturias.governments[0].terms.some(
      (r) => r.name === "Gimena Llamedo González",
    ),
  ).toBe(true);
});

it("separa homónimos y conserva los alias de identidades consolidadas", () => {
  const former = people.find((p) => p.fullName === "José García González")!;
  const current = people.find(
    (p) => p.fullName === "José Ramón García González",
  )!;
  expect(former).toBeTruthy();
  expect(current).toBeTruthy();
  expect(former.id).not.toBe(current.id);
  expect(findPerson("asturias-sergio-marques")?.fullName).toBe(
    "Sergio Marqués Fernández",
  );
  expect(
    people.filter((p) => /Sergio Marqués/.test(p.fullName ?? p.name)),
  ).toHaveLength(1);
  expect(people.some((p) => p.fullName === "XI Legislatura")).toBe(false);
  expect(audit.portraitErrors).toHaveLength(0);
});
