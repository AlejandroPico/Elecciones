import { expect, it } from "vitest";
import { riojanInstitutions as rioja } from "./rioja-model";
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
import audit from "../../Políticos/revisiones/2026-10-16-rioja/informe.json";
import conservation from "../revisiones/2026-10-16-rioja/conservacion.json";

it("conserva las fichas anteriores y enlaza once parlamentos y catorce gobiernos riojanos", () => {
  expect(audit.baselinePeople).toBe(12061);
  expect(people).toHaveLength(audit.totalPeople);
  for (const id of conservation.baselineIds)
    expect(findPerson(id), id).toBeTruthy();
  expect(rioja.parliaments).toHaveLength(11);
  expect(rioja.governments).toHaveLength(14);
  expect(rioja.governments.at(-1)!.start).toBe("1982-08-26");
  expect(rioja.governments[0].start).toBe("2023-06-28");
  for (const stage of [...rioja.parliaments, ...rioja.governments]) {
    const rows =
      "records" in stage
        ? [...stage.records, ...stage.board, ...(stage.archiveBoard ?? [])]
        : stage.terms;
    for (const row of rows) {
      expect(findPerson(row.person), row.name).toBeTruthy();
      expect(row.source).toMatch(/^https:\/\//);
      expect(row.name).not.toMatch(/Cuervas|Garíca|Begoña Arregui Martínez|�/);
      if (row.start && row.end)
        expect(row.start < row.end, row.name).toBe(true);
    }
  }
});

it("distingue los 35 escaños de 1983 de los 33 posteriores sin sumar relevos", () => {
  for (const stage of rioja.parliaments) {
    const rows = stage.currentOnly
      ? catalanGroupsAt(stage, stage.checkedAt).flatMap((g) => g.members)
      : archivedGroups(stage).flatMap((g) => g.members);
    expect(rows, stage.label).toHaveLength(stage.capacity!);
    expect(new Set(rows.map((r) => r.person)).size, stage.label).toBe(
      stage.capacity,
    );
    expect(stage.capacity).toBe(stage.label === "Legislatura I" ? 35 : 33);
    const ids = new Set(stage.records.map((r) => r.person));
    for (const row of [...stage.board, ...(stage.archiveBoard ?? [])])
      expect(ids.has(row.person), row.name).toBe(true);
    if (!stage.currentOnly) {
      expect(stage.nominalOnly).toBe(true);
      expect(
        stage.records.every((r) => r.start === null && r.end === null),
      ).toBe(true);
      expect(stage.archiveBoard!.length).toBeGreaterThanOrEqual(5);
    }
  }
  const second = rioja.parliaments.find((p) => p.label === "Legislatura II")!;
  expect(second.start).toBe("1987-07-06");
  expect(
    second.archiveBoard!.some((m) => /Fernández Ilarraza/.test(m.name)),
  ).toBe(true);
  expect(second.archiveBoard!.some((m) => /Virosta/.test(m.name))).toBe(true);
  const third = rioja.parliaments.find((p) => p.label === "Legislatura III")!;
  expect(
    third.archiveBoard!.find((m) => /Virosta/.test(m.name))!.source,
  ).toContain("bopr-3-17c");
});

it("verifica el directorio vigente, su Mesa, sus retratos y las adscripciones documentadas", () => {
  const chamber = rioja.parliaments[0];
  const executive = rioja.governments[0];
  const cabinet = executive.terms.filter((r) =>
    r.observedAt
      ? r.observedAt === executive.checkedAt
      : catalanTermAt(r, executive.checkedAt),
  );
  expect(chamber.records).toHaveLength(33);
  expect(chamber.board).toHaveLength(5);
  expect(cabinet).toHaveLength(8);
  expect(chamber.board[0].name).toBe("Marta Fernández Cornago");
  for (const row of [...chamber.records, ...cabinet])
    expect(portraits[row.person], row.name).toBeTruthy();
  expect(
    catalanGroupsAt(chamber, chamber.checkedAt)
      .map((g) => g.members.length)
      .sort((a, b) => a - b),
  ).toEqual([2, 2, 12, 17]);
  expect(catalanGroupsAt(chamber, chamber.start)).toHaveLength(0);
  const president = cabinet.find((r) => r.level === "president")!;
  expect(findPerson(president.person)!.birthDate).toBe("1972-01-23");
  expect(audit.portraitErrors).toHaveLength(0);
});

it("conserva las fechas individuales y corrige la errata mensual con el nombramiento acreditado", () => {
  expect(
    rioja.governments
      .at(-1)!
      .terms.some(
        (r) =>
          r.role ===
          "Consejero de Administración Territorial, Urbanismo, Vivienda y Medio Ambiente",
      ),
  ).toBe(true);
  const andreu = rioja.governments.find((p) => p.start === "2019-08-28")!;
  const hita = andreu.terms.find((r) => r.name === "Eva Hita Lorite")!;
  expect(hita.start).toBe("2019-08-29");
  expect(hita.source).toContain("BOE-A-2020-1767");
  expect(
    andreu.terms.some((r) => r.start === "2022-01-11" && /Somalo/.test(r.name)),
  ).toBe(true);
  for (const period of rioja.governments) {
    if (period.preferredDate)
      expect(
        rioja.governmentChronology.some(
          (s) => s.period.id === period.id && s.date === period.preferredDate,
        ),
      ).toBe(true);
  }
});
