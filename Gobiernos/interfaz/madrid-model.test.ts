import { expect, it } from "vitest";
import {
  madridGovernments,
  madridParliaments,
  madridGovernmentChronology,
  madridParliamentChronology,
  madridMembersAt,
  madridGroupsAt,
} from "./madrid-model";
import { catalanTermAt, regionalDates } from "./catalonia-model";
import { findPerson, portraits } from "../../Políticos/interfaz/datos/catalogo";
import audit from "../revisiones/2026-10-09-madrid/informe.json";

it("incorpora las trece legislaturas de Madrid, sin confundir las dos de 2003", () => {
  expect(madridParliaments).toHaveLength(13);
  expect(madridGovernments).toHaveLength(14);
  expect(
    madridParliaments
      .filter((p) => p.start.startsWith("2003"))
      .map((p) => p.label),
  ).toEqual(["Legislatura VII", "Legislatura VI"]);
  expect(audit.assemblyProfiles).toBe(789);
  for (const id of Object.values(audit.identityMapping))
    expect(findPerson(id)).toBeTruthy();
  for (const p of madridParliaments) {
    for (const m of [
      ...p.records,
      ...p.board,
      ...p.groups.flatMap((g) => g.members),
    ]) {
      expect(findPerson(m.person), m.name).toBeTruthy();
      expect(new URL(m.source).protocol).toBe("https:");
    }
    if (!p.nominalOnly)
      for (const d of regionalDates(p, p.records))
        expect(madridMembersAt(p, d).length).toBeLessThanOrEqual(p.capacity!);
  }
});
it("abre cada hemiciclo histórico en una composición documentada y respeta las disoluciones anticipadas", () => {
  for (const p of madridParliaments.filter((p) => !p.nominalOnly)) {
    const snapshots = madridParliamentChronology.filter(
      (s) => s.period.id === p.id,
    );
    expect(snapshots.length, p.label).toBeGreaterThan(0);
    for (const s of snapshots)
      expect(
        madridMembersAt(p, s.date).length,
        `${p.label} ${s.date}`,
      ).toBeGreaterThan(0);
  }
  const xi = madridParliaments.find((p) => p.id === "madrid-asamblea-11")!;
  expect(xi.end).toBe("2021-03-11");
  expect(madridMembersAt(xi, "2021-03-10")).toHaveLength(132);
  expect(madridMembersAt(xi, "2021-03-11")).toHaveLength(0);
  expect(madridParliaments.find((p) => p.id === "madrid-asamblea-6")!.end).toBe(
    "2003-08-28",
  );
});
it("representa los 135 diputados actuales, cuatro grupos y los siete cargos de la Mesa", () => {
  const p = madridParliaments[0],
    members = madridMembersAt(p, p.checkedAt);
  expect(p.nominalOnly).toBe(false);
  expect(members).toHaveLength(135);
  expect(new Set(members.map((m) => m.person)).size).toBe(135);
  const groups = madridGroupsAt(p, p.checkedAt);
  expect(groups).toHaveLength(4);
  expect(groups.reduce((n, g) => n + g.members.length, 0)).toBe(135);
  expect(groups.every((g) => g.name !== "Sin adscripción fechada")).toBe(true);
  expect(p.board.filter((m) => catalanTermAt(m, p.checkedAt))).toHaveLength(7);
});
it("documenta los relevos del Ejecutivo sin perder la presidencia ni convertir el archivo antiguo en un gabinete simultáneo", () => {
  for (const s of madridGovernmentChronology) {
    expect(
      s.period.terms.filter(
        (t) => t.level === "president" && catalanTermAt(t, s.date),
      ),
      `${s.period.label} ${s.date}`,
    ).toHaveLength(1);
  }
  const current = madridGovernments[0];
  const cabinet = (d: string) =>
    current.terms.filter((t) => catalanTermAt(t, d));
  expect(cabinet(current.checkedAt)).toHaveLength(10);
  expect(cabinet("2026-02-15").some((t) => t.name.includes("Viciana"))).toBe(
    true,
  );
  expect(cabinet("2026-02-16").some((t) => t.name.includes("Zarzalejo"))).toBe(
    true,
  );
  expect(cabinet("2026-02-16").some((t) => t.name.includes("Viciana"))).toBe(
    false,
  );
  for (const g of madridGovernments)
    for (const t of [...g.terms, ...(g.archiveTerms ?? [])]) {
      expect(findPerson(t.person), t.name).toBeTruthy();
      expect(
        findPerson(t.person)!.references.some((r) => r.url === t.source),
      ).toBe(true);
    }
  expect(
    madridGovernments
      .at(-1)!
      .archiveTerms!.every((t) => t.start === null && t.end === null),
  ).toBe(true);
  for (const t of cabinet(current.checkedAt))
    expect(portraits[t.person], t.name).toBeTruthy();
});
