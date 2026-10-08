import { expect, it } from "vitest";
import {
  congressLegislatures,
  congressChronology,
  congressSnapshots,
  congressMembersAt,
  congressGroupsAt,
  congressTermAt,
  congressDiagramPoints,
  congressGovernmentStages,
  congressStageContains,
} from "./congress-model";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";
import { ownOfficeTerms } from "../../Políticos/interfaz/relaciones";
import audit from "../revisiones/2026-10-08-congreso/informe.json";
import identityReview from "../revisiones/2026-10-08-congreso/identidades.json";

it("conserva los 6323 mandatos y las 16 legislaturas con identidades y fuentes verificables", () => {
  expect(congressLegislatures.map((l) => l.number)).toEqual(
    Array.from({ length: 16 }, (_, i) => 15 - i),
  );
  expect(
    congressLegislatures.reduce((sum, l) => sum + l.members.length, 0),
  ).toBe(6323);
  expect(audit.unmatched).toEqual([]);
  expect(
    congressLegislatures.reduce((sum, l) => sum + l.groups.length, 0),
  ).toBe(125);
  for (const leg of congressLegislatures) {
    expect(
      congressSnapshots(leg).every(
        (s) => s.date >= leg.start && s.date < leg.end,
      ),
    ).toBe(true);
    for (const member of [...leg.members, ...leg.board]) {
      expect(
        findPerson(member.person),
        `${leg.label}: ${member.name}`,
      ).toBeTruthy();
      expect(new URL(member.source).hostname).toBe("www.congreso.es");
    }
    // Nunca presentar una posición inventada como asiento físico oficial.
    expect(leg.physicalSeating.status).toBe("unavailable");
    expect(leg.physicalSeating.source).toBe(
      "https://www.congreso.es/hemiciclo",
    );
  }
  for (const record of identityReview.records)
    expect(
      findPerson(record.person)?.congressMandates?.some(
        (m) => m.source.url === record.sources[0],
      ),
      record.name,
    ).toBe(true);
});
it("respeta sustituciones y la disolución sin duplicar personas ni extender el Pleno", () => {
  expect(
    congressTermAt({ start: "2024-01-01", end: "2024-02-01" }, "2024-02-01"),
  ).toBe(false);
  expect(congressTermAt({ start: "2024-02-01", end: null }, "2024-02-01")).toBe(
    true,
  );
  expect(congressTermAt({ start: null, end: null }, "2024-02-01")).toBe(false);
  const latest = congressChronology.at(-1)!;
  expect(latest.date).toBe("2026-10-05");
  expect(latest.legislature.number).toBe(15);
  const groups = congressGroupsAt(latest.legislature, latest.date);
  const members = groups.flatMap((g) => g.members);
  expect(members).toHaveLength(350);
  expect(new Set(members.map((m) => m.person)).size).toBe(350);
  expect(congressMembersAt(latest.legislature, "2026-10-06")).toEqual([]);
  expect(congressDiagramPoints()).toHaveLength(350);
  // Las anomalías históricas se conservan, nunca se recortan para forzar 350.
  const third = congressLegislatures.find((l) => l.number === 3)!;
  expect(congressMembersAt(third, "1986-10-03")).toHaveLength(352);
  expect(congressDiagramPoints(352)).toHaveLength(352);
});
it("utiliza adscripciones fechadas y refleja traslados de grupo de la misma persona", () => {
  const leg = congressLegislatures[0];
  const changed = leg.memberships.find(
    (m) =>
      m.start &&
      m.start > "2023-09-01" &&
      leg.memberships.some(
        (old) =>
          old.person === m.person && old.code !== m.code && old.end === m.start,
      ),
  );
  expect(changed).toBeTruthy();
  const after = congressGroupsAt(leg, changed!.start!).find((g) =>
    g.members.some((m) => m.person === changed!.person),
  );
  expect(after?.group.code).toBe(changed!.code);
  expect(
    congressGroupsAt(leg, leg.start).flatMap((g) => g.members).length,
  ).toBe(congressMembersAt(leg, leg.start).length);
  expect(congressSnapshots(leg).some((s) => s.date === changed!.start)).toBe(
    true,
  );
});
it("filtra por etapas del Ejecutivo conservando la precisión mensual", () => {
  const stage = congressGovernmentStages(congressLegislatures[0]).find(
    (s) => s.date === "2023-11-21",
  )!;
  expect(stage).toBeTruthy();
  expect(congressStageContains(stage, "2023-11-20")).toBe(false);
  expect(congressStageContains(stage, "2023-11-21")).toBe(true);
  const monthly = congressLegislatures
    .flatMap(congressGovernmentStages)
    .find((s) => s.date.length === 7)!;
  expect(monthly).toBeTruthy();
  expect(congressStageContains(monthly, `${monthly.date}-15`)).toBe(true);
});
it("reúne los cargos de la Mesa en la única relación propia y conserva la trayectoria", () => {
  const term = congressLegislatures[0].board.find(
    (m) => m.role === "Presidenta",
  )!;
  const person = findPerson(term.person)!;
  expect(person.congressOffices?.length).toBeGreaterThan(0);
  const own = ownOfficeTerms(person);
  expect(own.some((t) => /Mesa del Congreso/.test(t.name))).toBe(true);
  expect(new Set(own.map((t) => `${t.name}|${t.period}`)).size).toBe(
    own.length,
  );
});
