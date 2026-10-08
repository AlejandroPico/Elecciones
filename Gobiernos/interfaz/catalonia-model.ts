import { lastDay } from "./calendar";
import type { HemicycleGroup, HemicycleMember } from "./Hemicycle";
export type CatalanTerm = HemicycleMember & {
  role: string;
  level?: "president" | "vice" | "minister";
  endBasis?: string;
};
export type CatalanGovernment = {
  id: string;
  label: string;
  start: string;
  end: string | null;
  checkedAt: string;
  name: string;
  source: string;
  terms: CatalanTerm[];
  incidents: string[];
};
export type CatalanParliament = {
  id: string;
  label: string;
  start: string;
  end: string | null;
  checkedAt: string;
  source: string;
  currentOnly: boolean;
  note: string;
  records: CatalanTerm[];
  board: CatalanTerm[];
  groups: { name: string; source: string; members: CatalanTerm[] }[];
};
export const catalanGovernments = Object.values(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Cataluña/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const catalanParliaments = Object.values(
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Cataluña/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
// Las instantáneas se cortan antes de la disolución; el Pleno no es la Diputación Permanente.
export function catalanTermAt(
  term: { start: string | null; end: string | null },
  date: string,
) {
  return !!term.start && term.start <= date && (!term.end || date < term.end);
}
export function regionalDates(
  period: { start: string; end: string | null; checkedAt: string },
  terms: { start: string | null; end: string | null }[],
  currentOnly = false,
) {
  if (currentOnly) return [period.checkedAt];
  const until = period.end ? lastDay(period.end) : period.checkedAt;
  return [
    ...new Set([
      period.start,
      until,
      ...terms.flatMap((t) =>
        [t.start, t.end].filter(
          (d): d is string => !!d && d >= period.start && d <= until,
        ),
      ),
    ]),
  ].sort();
}
export const catalanGovernmentChronology = catalanGovernments
  .flatMap((period) =>
    regionalDates(period, period.terms).map((date) => ({
      id: `${period.id}-${date}`,
      date,
      period,
    })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
export const catalanParliamentChronology = catalanParliaments
  .flatMap((period) =>
    regionalDates(
      period,
      [...period.records, ...period.groups.flatMap((g) => g.members)],
      period.currentOnly,
    ).map((date) => ({ id: `${period.id}-${date}`, date, period })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
export function catalanMembersAt(period: CatalanParliament, date: string) {
  if (period.currentOnly)
    return date === period.checkedAt ? period.records : [];
  if (date < period.start || (period.end && date >= period.end)) return [];
  return [
    ...new Map(
      period.records
        .filter((m) => catalanTermAt(m, date))
        .map((m) => [m.person, m]),
    ).values(),
  ];
}
export function catalanGroupsAt(
  period: CatalanParliament,
  date: string,
): HemicycleGroup[] {
  const groups = new Map<string, HemicycleGroup>();
  for (const member of catalanMembersAt(period, date)) {
    const applicable = period.groups
      .flatMap((g) =>
        g.members
          .filter(
            (m) =>
              m.person === member.person &&
              (period.currentOnly || catalanTermAt(m, date)),
          )
          .map((m) => ({ g, m })),
      )
      .sort((a, b) => (b.m.start ?? "").localeCompare(a.m.start ?? ""));
    const group = applicable[0]?.g;
    const name = group?.name ?? "Sin adscripción fechada";
    if (!groups.has(name))
      groups.set(name, {
        id: name,
        name,
        label: name.replace(/^Grup (?:Parlamentari |parlamentari )?/, ""),
        source: group?.source ?? period.source,
        members: [],
      });
    groups.get(name)!.members.push(member);
  }
  return [...groups.values()]
    .map((g) => ({
      ...g,
      members: g.members.sort((a, b) => a.name.localeCompare(b.name, "es")),
    }))
    .sort(
      (a, b) =>
        b.members.length - a.members.length ||
        a.name.localeCompare(b.name, "es"),
    );
}
