import { chronology } from "./government-model";
import { lastDay } from "./calendar";

export type DeputyMandate = {
  person: string;
  name: string;
  code: number;
  start: string | null;
  end: string | null;
  constituency: string;
  formation: string;
  source: string;
};
export type CongressGroup = {
  code: number;
  name: string;
  shortName: string;
  start: string | null;
  source: string;
};
export type CongressMembership = {
  person: string;
  code: number;
  start: string | null;
  end: string | null;
  source: string;
};
export type CongressBoardTerm = {
  person: string;
  name: string;
  role: string;
  start: string | null;
  end: string | null;
  source: string;
};
export type CongressLegislature = {
  id: string;
  number: number;
  label: string;
  start: string;
  end: string;
  checkedAt: string;
  source: string;
  mesaSource: string;
  members: DeputyMandate[];
  groups: CongressGroup[];
  memberships: CongressMembership[];
  board: CongressBoardTerm[];
  incidents: string[];
  physicalSeating: {
    status: "unavailable";
    source: string;
    checkedAt: string;
    reason: string;
  };
};
const files = import.meta.glob<CongressLegislature>(
  "../Congreso/*/composicion.json",
  { eager: true, import: "default" },
);
export const congressLegislatures = Object.values(files).sort(
  (a, b) => b.number - a.number,
);

/** La baja excluye ese día: impide duplicar una sustitución y extender el Pleno disuelto. */
export function congressTermAt(
  term: { start: string | null; end: string | null },
  date: string,
) {
  return !!term.start && term.start <= date && (!term.end || date < term.end);
}
export function congressMembersAt(leg: CongressLegislature, date: string) {
  if (date < leg.start || date >= leg.end) return [];
  const members = new Map<string, DeputyMandate>();
  for (const term of leg.members)
    if (congressTermAt(term, date)) members.set(term.person, term);
  return [...members.values()].sort((a, b) =>
    a.name.localeCompare(b.name, "es"),
  );
}
export function congressGroupsAt(leg: CongressLegislature, date: string) {
  const memberships = new Map<string, CongressMembership>();
  for (const term of [...leg.memberships].sort((a, b) =>
    (a.start ?? "").localeCompare(b.start ?? ""),
  ))
    if (congressTermAt(term, date)) memberships.set(term.person, term);
  const groups = new Map<
    number,
    { group: CongressGroup; members: DeputyMandate[] }
  >();
  for (const member of congressMembersAt(leg, date)) {
    const code = memberships.get(member.person)?.code ?? -1;
    const group = leg.groups.find((g) => g.code === code) ?? {
      code: -1,
      name: "Sin adscripción fechada",
      shortName: "Sin adscripción fechada",
      start: null,
      source: leg.source,
    };
    const entry = groups.get(code) ?? { group, members: [] };
    entry.members.push(member);
    groups.set(code, entry);
  }
  return [...groups.values()].sort(
    (a, b) =>
      b.members.length - a.members.length ||
      a.group.name.localeCompare(b.group.name, "es"),
  );
}
export function congressSnapshots(leg: CongressLegislature) {
  const dates = new Set([leg.start, lastDay(leg.end)]);
  for (const term of [...leg.members, ...leg.memberships, ...leg.board]) {
    for (const date of [term.start, term.end])
      if (date && date >= leg.start && date < leg.end) dates.add(date);
  }
  // Solo fechas exactas del Ejecutivo. Un registro mensual conserva su precisión.
  for (const cabinet of chronology)
    if (
      cabinet.date.length === 10 &&
      cabinet.date >= leg.start &&
      cabinet.date < leg.end
    )
      dates.add(cabinet.date);
  return [...dates]
    .sort()
    .map((date) => ({ id: `${leg.id}-${date}`, date, legislature: leg }));
}
export const congressChronology = congressLegislatures
  .flatMap(congressSnapshots)
  .sort((a, b) => a.date.localeCompare(b.date));
export function congressGovernmentStages(leg: CongressLegislature) {
  return chronology
    .map((cabinet, i) => ({
      ...cabinet,
      until: chronology[i + 1]?.date ?? "9999-12-31",
    }))
    .filter((c) => c.date < leg.end && c.until > leg.start);
}
export function congressStageContains(
  stage: ReturnType<typeof congressGovernmentStages>[number],
  date: string,
) {
  // Los límites mensuales comparan meses, sin atribuir el nombramiento a un día concreto.
  return (
    date.slice(0, stage.date.length) >= stage.date &&
    date.slice(0, stage.until.length) < stage.until
  );
}
export function congressGroupColor(name: string) {
  if (/socialista/i.test(name)) return "#cf5360";
  if (/popular|alianza popular/i.test(name)) return "#579ad0";
  if (/vox/i.test(name)) return "#78a965";
  if (/sumar|podemos|izquierda|comunista/i.test(name)) return "#a282c4";
  if (/vasco|eaj|pnv/i.test(name)) return "#4d9c8b";
  if (/esquerra|republicano/i.test(name)) return "#d5ae56";
  if (/catalán|catalan|junts|converg/i.test(name)) return "#88aaa6";
  if (/centrista|centro|ciudadanos/i.test(name)) return "#d78d4f";
  return "#9199a8";
}
/** Posiciones de un diagrama, nunca números de asiento ni ubicaciones físicas. */
export function congressDiagramPoints(count = 350) {
  const weights = [26, 32, 38, 42, 46, 50, 56, 60];
  const counts = weights.map((w) => Math.floor((count * w) / 350));
  for (let i = 0; counts.reduce((a, b) => a + b, 0) < count; i++)
    counts[7 - (i % 8)]++;
  return counts
    .flatMap((n, row) =>
      Array.from({ length: n }, (_, i) => {
        const radius = 145 + row * 46,
          angle = Math.PI - (Math.PI * i) / Math.max(1, n - 1);
        return {
          x: 520 + Math.cos(angle) * radius,
          y: 495 - Math.sin(angle) * radius,
          angle,
          row,
        };
      }),
    )
    .sort((a, b) => b.angle - a.angle || a.row - b.row);
}
