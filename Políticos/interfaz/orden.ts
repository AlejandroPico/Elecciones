import { governmentCatalog, type Person } from "./datos/catalogo";
export type Order = "name" | "recent" | "oldest" | "rank";
function normalize(s: string) {
  return s
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}
const activity = new Map<
  string,
  { first: number; last: number; rank: number; roles: string[] }
>();
for (const g of governmentCatalog)
  for (const c of g.cabinets)
    for (const m of c.members) {
      const year = Number(c.date.slice(0, 4));
      const rank =
        m.level === "president"
          ? 1
          : m.level === "vicepresident"
            ? 2
            : m.level === "minister"
              ? 3
              : 4;
      const previous = activity.get(m.person);
      activity.set(m.person, {
        first: Math.min(previous?.first ?? year, year),
        last: Math.max(previous?.last ?? year, year),
        rank: Math.min(previous?.rank ?? rank, rank),
        roles: [...new Set([...(previous?.roles ?? []), m.role])],
      });
    }
export function activityOf(p: Person) {
  const records = [p.id, ...(p.legacyIds ?? [])]
    .map((id) => activity.get(id))
    .filter((record): record is NonNullable<typeof record> => !!record);
  const documented = records.length
    ? {
        first: Math.min(...records.map((r) => r.first)),
        last: Math.max(...records.map((r) => r.last)),
        rank: Math.min(...records.map((r) => r.rank)),
        roles: [...new Set(records.flatMap((r) => r.roles))],
      }
    : undefined;
  const years = p.timeline.flatMap((t) =>
    [...t.period.matchAll(/\b(?:19|20)\d{2}\b/g)].map((m) => Number(m[0])),
  );
  const current = p.timeline.some((t) => /actualidad|presente/i.test(t.period));
  const first = Math.min(documented?.first ?? Infinity, ...years);
  const last = Math.max(
    documented?.last ?? -Infinity,
    ...years,
    ...(current ? [new Date().getFullYear()] : []),
  );
  return {
    first,
    last,
    rank:
      documented?.rank ??
      (/presiden(?:te|ta) (?:del congreso|del senado|de la junta|de la general|de la regi|del principado)|lehendakari/i.test(
        p.role,
      )
        ? 3
        : 5),
    roles: [
      ...new Set([
        ...(documented?.roles ?? []),
        ...p.timeline.map((t) => t.title),
        p.role,
      ]),
    ],
  };
}
export function orderPeople(list: Person[], order: Order) {
  return [...list].sort((a, b) => {
    const x = activityOf(a),
      y = activityOf(b);
    let comparison = 0;
    if (order === "recent") comparison = y.last - x.last;
    if (order === "oldest") comparison = x.first - y.first;
    if (order === "rank") comparison = x.rank - y.rank || y.last - x.last;
    return (
      (Number.isNaN(comparison) ? 0 : comparison) ||
      (a.fullName ?? a.name).localeCompare(b.fullName ?? b.name, "es")
    );
  });
}
export function matchesPerson(p: Person, query: string, partyName = "") {
  return normalize(
    [
      p.name,
      p.fullName,
      ...(p.knownAs ?? []),
      p.role,
      p.relation,
      partyName,
      ...(p.affiliations ?? []).map((a) => `${a.name} ${a.period ?? ""}`),
      ...activityOf(p).roles,
    ].join(" "),
  ).includes(normalize(query).trim());
}
