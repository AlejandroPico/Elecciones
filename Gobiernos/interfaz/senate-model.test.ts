import { expect, it } from "vitest";
import { senateLegislatures, senateChronology, senateSnapshots, termAt, senatorGroups } from "./senate-model";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";

it("conserva todas las legislaturas desde 1977 con personas y fuentes individuales", () => {
  expect(senateLegislatures.map((l) => l.number)).toEqual(Array.from({length: 16}, (_, i) => 15 - i));
  expect(senateLegislatures.at(-1)!.start).toBe("1977-07-13");
  const ids = new Set<string>();
  for (const leg of senateLegislatures) {
    expect(leg.senators.length).toBeGreaterThan(100);
    expect(senateSnapshots(leg).every((s) => s.date >= leg.start && s.date < leg.end)).toBe(true);
    if (leg.number !== 11) expect(leg.incidents, leg.label).toEqual([]);
    for (const term of leg.terms) {
      if (term.start && term.end) expect(term.start <= term.end, `${leg.label}: ${term.name}`).toBe(true);
    }
    for (const member of [...leg.senators, ...leg.terms]) {
      expect(findPerson(member.person), `${leg.label}: ${member.name}`).toBeTruthy();
      expect(new URL(member.source).hostname).toBe("www.senado.es");
    }
    leg.senators.forEach((s) => ids.add(s.person));
  }
  expect(ids.size).toBeGreaterThan(2400);
  expect(senateLegislatures.find((leg) => leg.number === 11)!.incidents).toHaveLength(3);
});
it("respeta altas y bajas inclusive y sitúa los relevos en su fecha individual", () => {
  expect(termAt({start: "2021-07-12", end: "2023-05-30"}, "2021-07-11")).toBe(false);
  expect(termAt({start: "2021-07-12", end: "2023-05-30"}, "2023-05-30")).toBe(true);
  expect(termAt({start: null, end: "2023-05-30"}, "2020-01-01")).toBe(false);
  const leg = senateLegislatures.find((l) => l.number === 14)!;
  const llop = leg.terms.find((t) => /Llop/.test(t.name) && /^PRESIDENTA$/i.test(t.role) && /MESA DEL SENADO/.test(t.organ))!;
  const gil = leg.terms.find((t) => /Ander Gil/.test(t.name) && /^PRESIDENTE$/i.test(t.role) && /MESA DEL SENADO/.test(t.organ))!;
  expect(llop).toBeTruthy(); expect(gil).toBeTruthy();
  const before = senateSnapshots(leg).find((s) => s.date === llop.start)!;
  expect(before.members.some((t) => t.person === llop.person && /^PRESIDENTA$/i.test(t.role))).toBe(true);
  const after = senateSnapshots(leg).find((s) => s.date === gil.start)!;
  expect(after.members.some((t) => t.person === gil.person && /^PRESIDENTE$/i.test(t.role))).toBe(true);
  expect(after.members.some((t) => t.person === llop.person && /^PRESIDENTA$/i.test(t.role))).toBe(false);
});
it("la última Mesa tiene siete miembros y el Pleno no cuenta dos veces a la misma persona", () => {
  const latest = senateChronology.at(-1)!;
  expect(latest.legislature.number).toBe(15);
  expect(latest.members.filter((m) => /MESA DEL SENADO/i.test(m.organ))).toHaveLength(7);
  const groups = senatorGroups(latest.legislature, latest.date);
  const members = groups.flatMap((g) => g.members);
  expect(new Set(members.map((m) => m.person)).size).toBe(members.length);
  expect(members.length).toBeGreaterThan(250);
  expect(members.length).toBeLessThan(300);
  expect(latest.members.filter((m) => /^PORTAVOZ$/i.test(m.role)).every((m) => /^GRUPO PARLAMENTARIO/i.test(m.organ))).toBe(true);
});
