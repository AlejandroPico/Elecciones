import { expect, it } from "vitest";
import {
  andaluciaGovernments,
  andaluciaParliaments,
  andaluciaMembersAt,
  andaluciaGroupsAt,
  andaluciaGovernmentChronology,
  andaluciaParliamentChronology,
} from "./andalucia-model";
import { catalanTermAt, regionalDates } from "./catalonia-model";
import { findPerson, portraits } from "../../Políticos/interfaz/datos/catalogo";
import { ownOfficeTerms } from "../../Políticos/interfaz/relaciones";
import audit from "../revisiones/2026-10-12-andalucia/informe.json";

it("conserva las 1.602 fichas institucionales y enlaza las trece legislaturas y dieciséis etapas", () => {
  expect(audit.parliamentProfiles).toBe(1602);
  expect(audit.parliamentIdentities).toBe(860);
  expect(audit.profileErrors).toHaveLength(0);
  expect(andaluciaParliaments).toHaveLength(13);
  expect(andaluciaGovernments).toHaveLength(16);
  for (const id of Object.values(audit.identityMapping))
    expect(findPerson(id)).toBeTruthy();
  for (const p of [...andaluciaGovernments, ...andaluciaParliaments]) {
    const terms = "terms" in p ? p.terms : [...p.records, ...p.board];
    for (const t of terms) {
      const person = findPerson(t.person);
      expect(person, t.name).toBeTruthy();
      expect(
        person!.references.some((s) => s.url === t.source),
        t.name,
      ).toBe(true);
      if (t.start && t.end) expect(t.start < t.end, t.name).toBe(true);
    }
  }
});

it("ofrece los 109 diputados vigentes con retrato y los cinco grupos publicados", () => {
  const p = andaluciaParliaments[0];
  expect(p.currentOnly).toBe(true);
  expect(p.nominalOnly).toBe(false);
  expect(andaluciaMembersAt(p, p.checkedAt)).toHaveLength(109);
  expect(new Set(p.records.map((t) => t.person)).size).toBe(109);
  expect(
    andaluciaGroupsAt(p, p.checkedAt).map((g) => g.members.length),
  ).toEqual([53, 28, 15, 8, 5]);
  for (const t of p.records) expect(portraits[t.person], t.name).toBeTruthy();
  expect(andaluciaMembersAt(p, "2026-07-01")).toHaveLength(0);
  expect(audit.currentMissingPortraits).toHaveLength(0);
});

it("no convierte los registros históricos de sustituciones en plenos de más de 109 escaños", () => {
  for (const p of andaluciaParliaments.slice(1)) {
    expect(p.nominalOnly).toBe(true);
    expect(p.currentOnly).toBe(false);
    expect(p.records.length).toBeGreaterThan(109);
    expect(p.records.every((t) => t.start === null && t.end === null)).toBe(
      true,
    );
    for (const d of regionalDates(p, p.records))
      expect(andaluciaMembersAt(p, d)).toHaveLength(0);
    expect(
      andaluciaParliamentChronology.some((s) => s.period.id === p.id),
    ).toBe(true);
  }
});

it("recoge el relevo de julio en la Mesa y distingue los representantes con voz de los siete cargos electos", () => {
  const p = andaluciaParliaments[0];
  const at = (d: string) => p.board.filter((t) => catalanTermAt(t, d));
  expect(
    at("2026-07-22").find((t) => t.role.startsWith("Presidente"))?.name,
  ).toContain("Aguirre");
  expect(
    at("2026-07-23").find((t) => t.role.startsWith("Presidenta"))?.name,
  ).toContain("Mestre");
  expect(
    at(p.checkedAt).filter((t) => !t.role.startsWith("Representante")),
  ).toHaveLength(7);
  expect(
    at(p.checkedAt).filter((t) => t.role.startsWith("Representante")),
  ).toHaveLength(2);
  expect(at(p.checkedAt).some((t) => t.name.includes("Aguirre"))).toBe(false);
  expect(p.archiveBoard!.length).toBeGreaterThan(at(p.checkedAt).length);
});

it("representa la Junta vigente con catorce personas y las tres vicepresidencias del decreto", () => {
  const g = andaluciaGovernments[0];
  const terms = g.terms.filter((t) => catalanTermAt(t, g.checkedAt));
  expect(g.start).toBe("2026-07-05");
  expect(terms).toHaveLength(14);
  expect(new Set(terms.map((t) => t.person)).size).toBe(14);
  expect(terms.filter((t) => t.level === "vice").map((t) => t.name)).toEqual([
    "Antonio Sanz Cabello",
    "Manuel Gavira Florentino",
    "Carolina España Reina",
  ]);
  for (const t of terms) expect(portraits[t.person], t.name).toBeTruthy();
  expect(andaluciaGovernmentChronology.some((s) => s.period.id === g.id)).toBe(
    true,
  );
});

it("respeta el fallecimiento de Gómez Villamandos y la suplencia educativa publicada en junio", () => {
  const g = andaluciaGovernments.find((g) => g.label === "Moreno II")!;
  const before = g.terms.filter((t) => catalanTermAt(t, "2026-06-02"));
  const after = g.terms.filter((t) => catalanTermAt(t, "2026-06-03"));
  expect(before.some((t) => t.name.includes("Gómez Villamandos"))).toBe(true);
  expect(after.some((t) => t.name.includes("Gómez Villamandos"))).toBe(false);
  expect(after.find((t) => t.name.includes("Castillo Mena"))?.role).toContain(
    "temporalmente Universidad",
  );
  expect(findPerson("andalucia-jose-carlos-gomez-villamandos")?.deathDate).toBe(
    "2026-06-02",
  );
});

it("une los cargos propios y conserva los ceses y las suplencias sin repetir predecesores", () => {
  const g = andaluciaGovernments.find(
    (g) => g.label === "Rodríguez de la Borbolla II",
  )!;
  expect(
    g.terms
      .filter((t) => catalanTermAt(t, "1987-02-03"))
      .some((t) => t.name.includes("Salinas")),
  ).toBe(false);
  const person = findPerson("congreso-304-8")!;
  expect(person).toBeTruthy();
  expect(
    ownOfficeTerms(person).some((t) =>
      t.name.includes("Presidencia de la Junta"),
    ),
  ).toBe(true);
});
