import { expect, it } from "vitest";
import {
  valenciaGovernments,
  valenciaParliaments,
  valenciaMembersAt,
  valenciaGroupsAt,
  valenciaGovernmentChronology,
  valenciaParliamentChronology,
} from "./valencia-model";
import { catalanTermAt, regionalDates } from "./catalonia-model";
import { findPerson, portraits } from "../../Políticos/interfaz/datos/catalogo";
import audit from "../revisiones/2026-10-09-valencia/informe.json";

it("enlaza las once legislaturas y las catorce etapas valencianas con identidades y fuentes personales", () => {
  expect(valenciaParliaments).toHaveLength(11);
  expect(valenciaGovernments).toHaveLength(14);
  expect(audit.cortsProfiles).toBe(669);
  expect(audit.profileErrors).toHaveLength(0);
  for (const id of Object.values(audit.identityMapping))
    expect(findPerson(id)).toBeTruthy();
  for (const p of valenciaParliaments) {
    expect(p.nominalOnly).toBe(false);
    for (const d of regionalDates(p, p.records))
      expect(
        valenciaMembersAt(p, d).length,
        `${p.label} ${d}`,
      ).toBeLessThanOrEqual(p.capacity!);
    for (const t of [...p.records, ...p.board, ...(p.archiveBoard ?? [])]) {
      expect(findPerson(t.person), t.name).toBeTruthy();
      expect(
        findPerson(t.person)!.references.some((s) => s.url === t.source),
        t.name,
      ).toBe(true);
    }
    expect(
      valenciaParliamentChronology
        .filter((s) => s.period.id === p.id)
        .every((s) => valenciaMembersAt(p, s.date).length > 0),
    ).toBe(true);
  }
  for (const g of valenciaGovernments)
    for (const t of [...g.terms, ...(g.archiveTerms ?? [])]) {
      expect(findPerson(t.person), t.name).toBeTruthy();
      expect(
        findPerson(t.person)!.references.some((s) => s.url === t.source),
        t.name,
      ).toBe(true);
    }
});

it("muestra 99 diputados con retrato, cuatro grupos y la Mesa observada sin retrotraerla", () => {
  const p = valenciaParliaments[0],
    date = p.checkedAt;
  const members = valenciaMembersAt(p, date);
  expect(members).toHaveLength(99);
  expect(new Set(members.map((m) => m.person)).size).toBe(99);
  expect(
    valenciaGroupsAt(p, date)
      .map((g) => g.members.length)
      .sort((a, b) => b - a),
  ).toEqual([40, 31, 15, 13]);
  for (const m of members) expect(portraits[m.person], m.name).toBeTruthy();
  expect(p.board).toHaveLength(5);
  expect(p.board.every((t) => t.observedAt === date && t.start === date)).toBe(
    true,
  );
  expect(p.board.some((t) => catalanTermAt(t, "2024-01-01"))).toBe(false);
  expect(p.archiveBoard!.every((t) => t.start === null && t.end === null)).toBe(
    true,
  );
});

it("corta el Pleno en las disoluciones y diferencia las credenciales de la constitución", () => {
  const first = valenciaParliaments.at(-1)!;
  expect(first.start).toBe("1983-06-07");
  expect(first.end).toBe("1987-05-08");
  expect(valenciaMembersAt(first, first.end!)).toHaveLength(0);
  const ninth = valenciaParliaments.find((p) => p.label === "Legislatura IX")!;
  expect(ninth.end).toBe("2019-03-05");
  expect(valenciaMembersAt(ninth, "2019-03-05")).toHaveLength(0);
  expect(
    valenciaParliaments.find((p) => p.label === "Legislatura V")!.start,
  ).toBe("1999-07-09");
});

it("distingue la toma de posesión presidencial de los efectos de los decretos de consejerías", () => {
  const current = valenciaGovernments[0];
  const at = (d: string) => current.terms.filter((t) => catalanTermAt(t, d));
  expect(current.start).toBe("2025-12-02");
  expect(at("2025-12-02")).toHaveLength(10);
  expect(at("2025-12-03")).toHaveLength(1);
  expect(at("2025-12-04")).toHaveLength(12);
  for (const t of at(current.checkedAt))
    expect(portraits[t.person], t.name).toBeTruthy();
  const mazon = valenciaGovernments[1];
  expect(mazon.start).toBe("2023-07-17");
  expect(
    mazon.terms.filter((t) => catalanTermAt(t, "2023-07-19")),
  ).toHaveLength(1);
  expect(
    mazon.terms.filter((t) => catalanTermAt(t, "2023-07-20")),
  ).toHaveLength(10);
  expect(
    mazon.terms.some(
      (t) => t.name.includes("Barrera") && catalanTermAt(t, "2024-07-11"),
    ),
  ).toBe(false);
  expect(
    mazon.terms.some(
      (t) => t.name.includes("Gan Pampols") && catalanTermAt(t, "2025-11-04"),
    ),
  ).toBe(false);
  expect(
    mazon.terms.some(
      (t) =>
        t.role.includes("Vicepresidente segundo") &&
        t.name.includes("Martínez Mus") &&
        catalanTermAt(t, "2025-11-05"),
    ),
  ).toBe(true);
  expect(valenciaGovernments.find((g) => g.label === "Puig II")!.start).toBe(
    "2019-06-16",
  );
  expect(valenciaGovernments.find((g) => g.label === "Puig I")!.start).toBe(
    "2015-06-28",
  );
  for (const s of valenciaGovernmentChronology) {
    const president = s.period.terms.filter(
      (t) => t.level === "president" && catalanTermAt(t, s.date),
    );
    expect(president, `${s.period.label} ${s.date}`).toHaveLength(
      s.period.label === "Zaplana II" && s.date >= "2002-07-10" ? 0 : 1,
    );
  }
  expect(findPerson("valencia-ximo-puig-ferrer")?.id).toBe("congreso-17-10");
  // Una identidad compartida con el Congreso conserva sus mandatos nacionales,
  // pero el encabezado debe reflejar el cargo valenciano vigente.
  expect(findPerson("congreso-247-14")?.role).toBe(
    "Diputado/a en Les Corts Valencianes",
  );
});
