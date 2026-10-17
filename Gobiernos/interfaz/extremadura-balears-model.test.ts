import { expect, it } from "vitest";
import {
  extremaduranInstitutions as extremadura,
  balearicInstitutions as baleares,
} from "./extremadura-balears-model";
import {
  archivedGroups,
  catalanGroupsAt,
  catalanTermAt,
} from "./catalonia-model";
import {
  people,
  findPerson,
  portraits,
} from "../../Políticos/interfaz/datos/catalogo";
import audit from "../../Políticos/revisiones/2026-10-16-extremadura-balears/informe.json";
import conservation from "../revisiones/2026-10-16-extremadura-balears/conservacion.json";

it("conserva las identidades previas y enlaza todos los gobiernos y legislaturas de las dos comunidades", () => {
  expect(audit.baselinePeople).toBe(12641);
  expect(people).toHaveLength(audit.totalPeople);
  for (const id of conservation.baselineIds)
    expect(findPerson(id), id).toBeTruthy();
  expect(extremadura.governments).toHaveLength(12);
  expect(extremadura.parliaments).toHaveLength(12);
  expect(baleares.governments).toHaveLength(13);
  expect(baleares.parliaments).toHaveLength(11);
  for (const region of [extremadura, baleares]) {
    for (const stage of [...region.governments, ...region.parliaments]) {
      const rows =
        "records" in stage
          ? [...stage.records, ...stage.board, ...(stage.archiveBoard ?? [])]
          : [...stage.terms, ...(stage.archiveTerms ?? [])];
      for (const row of rows) {
        expect(findPerson(row.person), row.name).toBeTruthy();
        expect(row.source).toMatch(/^https:\/\//);
        expect(row.name).not.toMatch(
          /Junta de Extremadura|Legislatura|Parlament de|Esquerra Unida de Mallorca|�/,
        );
      }
    }
  }
});

it("separa los 65 diputados actuales extremeños de sus bajas y de las composiciones anteriores", () => {
  const stage = extremadura.parliaments[0];
  expect(stage.label).toBe("Legislatura XII");
  expect(stage.start).toBe("2026-01-20");
  expect(stage.records).toHaveLength(65);
  expect(new Set(stage.records.map((p) => p.person)).size).toBe(65);
  expect(
    catalanGroupsAt(stage, stage.checkedAt)
      .map((g) => g.members.length)
      .sort((a, b) => a - b),
  ).toEqual([7, 11, 18, 29]);
  expect(catalanGroupsAt(stage, stage.start)).toHaveLength(0);
  expect(stage.board).toHaveLength(6);
  expect(stage.board[0].role).toMatch(/^Presidente/);
  for (const row of stage.records)
    expect(portraits[row.person], row.name).toBeTruthy();
});

it("respeta los 54 escaños iniciales baleares, los 59 posteriores y los cambios de grupo actuales", () => {
  expect(baleares.parliaments.at(-1)!.capacity).toBe(54);
  const stage = baleares.parliaments[0];
  expect(stage.records).toHaveLength(59);
  expect(new Set(stage.records.map((p) => p.person)).size).toBe(59);
  expect(
    catalanGroupsAt(stage, stage.checkedAt)
      .map((g) => g.members.length)
      .sort((a, b) => a - b),
  ).toEqual([3, 4, 4, 5, 18, 25]);
  expect(stage.board).toHaveLength(5);
  expect(stage.board[0].role).toMatch(/^President/);
  const mixed = stage.groups.find((g) => g.name === "Mixt")!;
  expect(
    mixed.members.every(
      (p) => p.formation && p.formationLabel === "Candidatura documentada",
    ),
  ).toBe(true);
  expect(mixed.members.some((p) => p.formation === "MÉS PER MENORCA")).toBe(
    true,
  );

  const fourth = baleares.parliaments.find(
    (p) => p.label === "Legislatura IV",
  )!;
  const names = archivedGroups(fourth)
    .flatMap((g) => g.members)
    .map((p) => findPerson(p.person)!);
  const ferra = names.find((p) => p.fullName === "Damià Ferrà Pons i Pons")!;
  const pons = names.find((p) => p.fullName === "Damià Pons i Pons")!;
  expect(ferra).toBeTruthy();
  expect(pons).toBeTruthy();
  expect(ferra.id).not.toBe(pons.id);

  for (const row of stage.records)
    expect(portraits[row.person], row.name).toBeTruthy();
  for (const stage of baleares.parliaments.slice(1))
    expect(archivedGroups(stage).flatMap((g) => g.members)).toHaveLength(
      stage.capacity!,
    );
});

it("no asigna por conjetura los escaños pendientes del archivo electoral y evita duplicar integrantes de las Mesas", () => {
  for (const region of [extremadura, baleares])
    for (const stage of region.parliaments.slice(1)) {
      const members = archivedGroups(stage).flatMap((g) => g.members);
      expect(members).toHaveLength(stage.capacity!);
      expect(members.length).toBeLessThanOrEqual(stage.capacity!);
      expect(new Set(members.map((p) => p.person)).size).toBe(members.length);
      expect(stage.nominalOnly).toBe(true);
      expect(stage.archiveBoard!.length).toBeGreaterThanOrEqual(5);
    }
});

it("muestra los gabinetes vigentes con retratos y conserva los cuadros históricos como documentación sin fechas inventadas", () => {
  for (const region of [extremadura, baleares]) {
    const stage = region.governments[0];
    const members = stage.terms.filter((row) =>
      row.observedAt
        ? row.observedAt === stage.checkedAt
        : catalanTermAt(row, stage.checkedAt),
    );
    expect(members).toHaveLength(12);
    expect(members.filter((row) => row.level === "vice")).toHaveLength(2);
    for (const member of members)
      expect(portraits[member.person], member.name).toBeTruthy();
    for (const old of region.governments.slice(1)) {
      expect(old.archiveTerms!.length).toBeGreaterThan(5);
      expect(
        old.archiveTerms!.every(
          (row) => row.start === null && row.end === null,
        ),
      ).toBe(true);
    }
  }
  const current = new Set(
    [extremadura, baleares].flatMap((region) => [
      ...region.parliaments[0].records.map((row) => row.person),
      ...region.governments[0].terms.map((row) => row.person),
    ]),
  );
  for (const error of audit.portraitErrors) {
    expect(current.has(error.person), error.person).toBe(false);
    expect(audit.missingPortraits).toContain(error.person);
    expect(error.resource).toMatch(/^https:\/\//);
  }
});
