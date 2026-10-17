import { expect, it } from "vitest";
import { murcianInstitutions as murcia } from "./murcia-model";
import {
  archivedGroups,
  catalanGroupsAt,
  catalanTermAt,
} from "./catalonia-model";
import {
  findPerson,
  people,
  portraits,
} from "../../Políticos/interfaz/datos/catalogo";
import audit from "../../Políticos/revisiones/2026-10-16-murcia/informe.json";
import conservation from "../revisiones/2026-10-16-murcia/conservacion.json";

it("conserva las identidades previas y enlaza once asambleas y dieciséis gobiernos murcianos", () => {
  expect(audit.baselinePeople).toBe(12291);
  expect(people.length).toBeGreaterThanOrEqual(audit.totalPeople);
  for (const id of conservation.baselineIds)
    expect(findPerson(id), id).toBeTruthy();
  expect(murcia.parliaments).toHaveLength(11);
  expect(murcia.governments).toHaveLength(16);
  expect(murcia.governments.at(-1)!.start).toBe("1982-07-22");
  expect(murcia.governments[0].start).toBe("2023-09-07");
  for (const stage of [...murcia.parliaments, ...murcia.governments]) {
    const rows =
      "records" in stage
        ? [...stage.records, ...stage.board, ...(stage.archiveBoard ?? [])]
        : [...stage.terms, ...(stage.archiveTerms ?? [])];
    for (const row of rows) {
      expect(findPerson(row.person), row.name).toBeTruthy();
      expect(row.source).toMatch(/^https:\/\//);
      expect(row.name).not.toMatch(/Causó Baja|Isabel Alaya|^Víctor Martín$|�/);
    }
  }
});

it("no suma las bajas a los 45 diputados vigentes y contrasta los cambios de grupo de 2026", () => {
  const chamber = murcia.parliaments[0];
  const groups = catalanGroupsAt(chamber, chamber.checkedAt);
  expect(chamber.records).toHaveLength(45);
  expect(new Set(chamber.records.map((r) => r.person)).size).toBe(45);
  expect(groups.map((g) => [g.name, g.members.length])).toEqual([
    ["Popular", 21],
    ["Socialista", 13],
    ["Vox", 7],
    ["Mixto", 4],
  ]);
  const mixed = groups.find((g) => g.name === "Mixto")!;
  expect(
    mixed.members.some((r) => r.name === "José Ángel Antelo Paredes"),
  ).toBe(true);
  expect(mixed.members.some((r) => r.name === "Virginia Martínez García")).toBe(
    true,
  );
  expect(catalanGroupsAt(chamber, chamber.start)).toHaveLength(0);
  expect(chamber.board).toHaveLength(5);
  expect(chamber.board[0].name).toBe("María Visitación Martínez Martínez");
});

it("distingue 43 escaños iniciales, 45 posteriores y las lagunas nominales del archivo", () => {
  for (const chamber of murcia.parliaments.filter((p) => !p.currentOnly)) {
    const seats = archivedGroups(chamber).flatMap((g) => g.members);
    expect(chamber.capacity).toBe(chamber.label === "Legislatura I" ? 43 : 45);
    expect(seats.length).toBeLessThanOrEqual(chamber.capacity!);
    expect(new Set(seats.map((r) => r.person)).size).toBe(seats.length);
    expect(chamber.nominalOnly).toBe(true);
    expect(chamber.archiveBoard!.length).toBeGreaterThanOrEqual(5);
    expect(
      chamber.records.every((r) => r.start === null && r.end === null),
    ).toBe(true);
  }
  const third = murcia.parliaments.find((p) => p.label === "Legislatura III")!;
  expect(archivedGroups(third).flatMap((g) => g.members)).toHaveLength(42);
  expect(third.archivedComposition!.note).toContain("42 de 45");
  const ninth = murcia.parliaments.find((p) => p.label === "Legislatura IX")!;
  expect(archivedGroups(ninth).flatMap((g) => g.members)).toHaveLength(45);
  expect(ninth.source).toContain("/legacy/");
});

it("presenta el gabinete vigente tras mayo de 2026 con retratos y cargos contrastados", () => {
  const government = murcia.governments[0];
  const members = government.terms.filter((r) =>
    r.observedAt
      ? r.observedAt === government.checkedAt
      : catalanTermAt(r, government.checkedAt),
  );
  expect(members).toHaveLength(11);
  expect(members.find((r) => r.role === "Consejera de Salud")!.name).toBe(
    "Isabel Ayala Vigueras",
  );
  expect(members.find((r) => /Portavocía/.test(r.role))!.name).toBe(
    "María Isabel López Aragón",
  );
  expect(members.some((r) => r.name === "Víctor Javier Marín Navarro")).toBe(
    true,
  );
  for (const row of [...murcia.parliaments[0].records, ...members])
    expect(portraits[row.person], row.name).toBeTruthy();
  expect(government.preferredDate).toBe(government.checkedAt);
  const firstCabinet = government.terms.filter((r) =>
    r.observedAt
      ? r.observedAt === "2023-10-19"
      : catalanTermAt(r, "2023-10-19"),
  );
  expect(firstCabinet).toHaveLength(11);
  expect(firstCabinet.some((r) => r.name === "Sara Rubira Martínez")).toBe(
    true,
  );
  expect(
    firstCabinet.some((r) => r.name === "José Manuel Pancorbo de la Torre"),
  ).toBe(true);
  expect(firstCabinet.some((r) => r.name === "Juan José Pedreño Planes")).toBe(
    true,
  );
  for (const row of firstCabinet)
    expect(portraits[row.person], row.name).toBeTruthy();
  expect(audit.portraitErrors).toHaveLength(0);
  for (const old of murcia.governments.slice(1)) {
    expect(old.archiveTerms!.length).toBeGreaterThan(0);
    expect(
      old.archiveTerms!.every((r) => r.start === null && r.end === null),
    ).toBe(true);
  }
});
