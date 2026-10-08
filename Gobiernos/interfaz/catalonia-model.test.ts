import { expect, it } from "vitest";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";
import {
  catalanGovernments,
  catalanParliaments,
  catalanGroupsAt,
  catalanMembersAt,
  catalanTermAt,
  regionalDates,
} from "./catalonia-model";
import audit from "../revisiones/2026-10-08-catalunya/informe.json";
it("conserva todas las fichas catalanas consultadas y los cuadros de las etapas de gobierno", () => {
  expect(catalanGovernments).toHaveLength(15);
  expect(catalanParliaments).toHaveLength(14);
  expect(audit.profileRecords).toBe(1073);
  expect(audit.officialProfileErrors).toEqual([]);
  for (const record of audit.identities)
    expect(
      findPerson(record.person)?.references.some(
        (s) => s.url === record.source,
      ),
      record.key,
    ).toBe(true);
  for (const government of catalanGovernments)
    for (const term of government.terms) {
      expect(findPerson(term.person), term.name).toBeTruthy();
      expect(new URL(term.source).protocol).toBe("https:");
    }
});
it("acredita 135 personas en el registro vigente sin trasladarlo a 2024", () => {
  const current = catalanParliaments[0];
  expect(catalanMembersAt(current, current.checkedAt)).toHaveLength(135);
  expect(
    new Set(catalanMembersAt(current, current.checkedAt).map((m) => m.person))
      .size,
  ).toBe(135);
  expect(
    catalanGroupsAt(current, current.checkedAt).reduce(
      (n, g) => n + g.members.length,
      0,
    ),
  ).toBe(135);
  expect(catalanMembersAt(current, "2024-06-10")).toEqual([]);
  expect(regionalDates(current, current.records, true)).toEqual([
    current.checkedAt,
  ]);
  const first = catalanParliaments.at(-1)!;
  expect(catalanMembersAt(first, first.start)).toHaveLength(135);
  expect(catalanMembersAt(first, first.end!)).toEqual([]);
});
it("respeta el relevo de julio de 2026 y diferencia la suplencia de una presidencia", () => {
  const current = catalanGovernments[0];
  const rights = (date: string) =>
    current.terms.filter(
      (t) => t.role.includes("Drets Socials") && catalanTermAt(t, date),
    );
  expect(rights("2026-07-19").map((t) => t.name)).toEqual([
    "Mónica Martínez Bravo",
  ]);
  expect(rights("2026-07-20").map((t) => t.name)).toEqual([
    "Raúl Moreno Montaña",
  ]);
  const torra = catalanGovernments.find((g) => g.label === "XII")!;
  expect(
    torra.terms
      .filter((t) => t.level === "president" && catalanTermAt(t, "2020-10-01"))
      .map((t) => t.role),
  ).toEqual(["Vicepresidencia en sustitución de la presidencia"]);
  expect(
    catalanGovernments
      .find((g) => g.label === "III")!
      .terms.find((t) => t.role.includes("Medi Ambient"))?.start,
  ).toBe("1991-04-04");
});
