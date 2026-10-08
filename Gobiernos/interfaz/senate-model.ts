import type { Reference } from "../../Políticos/interfaz/datos/tipos";
export type SenateTerm = {
  person: string; name: string; role: string; organ: string;
  start: string | null; end: string | null; source: string;
};
export type SenatorMandate = {
  person: string; name: string; start: string | null; end: string | null;
  group: string; source: string;
};
export type SenateLegislature = {
  id: string; number: number; label: string; start: string; end: string;
  source: string; mesaSource: string; checkedAt: string;
  terms: SenateTerm[]; senators: SenatorMandate[];
  finalBoard: SenateTerm[]; incidents: string[];
};
const files = import.meta.glob<SenateLegislature>("../Senado/*/composicion.json", { eager: true, import: "default" });
export const senateLegislatures = Object.values(files).sort((a, b) => b.start.localeCompare(a.start));
export function nextDay(date: string) {
  const d = new Date(date + "T12:00:00Z"); d.setUTCDate(d.getUTCDate() + 1);
  return d.toISOString().slice(0, 10);
}
export function lastDay(date: string) {
  const d = new Date(date + "T12:00:00Z"); d.setUTCDate(d.getUTCDate() - 1);
  return d.toISOString().slice(0, 10);
}
export function termAt(term: { start: string | null; end: string | null }, date: string) {
  // La fecha de baja publicada es inclusiva. No inventar un alta desconocida.
  return !!term.start && term.start <= date && (!term.end || term.end >= date);
}
export function senateSnapshots(legislature: SenateLegislature) {
  const dates = new Set([legislature.start, lastDay(legislature.end)]);
  for (const term of [...legislature.terms, ...legislature.senators]) {
    if (term.start && term.start >= legislature.start && term.start < legislature.end) dates.add(term.start);
    if (term.end && nextDay(term.end) >= legislature.start && nextDay(term.end) < legislature.end) dates.add(nextDay(term.end));
  }
  return [...dates].sort().map((date) => ({
    id: `${legislature.id}-${date}`, date, legislature,
    members: legislature.terms.filter((term) => termAt(term, date)),
  }));
}
export const senateChronology = senateLegislatures.flatMap(senateSnapshots).sort((a, b) => a.date.localeCompare(b.date));
export function senatorGroups(legislature: SenateLegislature, date: string) {
  const groups = new Map<string, SenatorMandate[]>();
  const members = new Map<string, SenatorMandate>();
  for (const mandate of legislature.senators) if (termAt(mandate, date)) members.set(mandate.person, mandate);
  for (const member of members.values()) {
    const group = member.group || "Grupo no publicado";
    groups.set(group, [...(groups.get(group) ?? []), member]);
  }
  return [...groups].map(([name, members]) => ({ name, members })).sort((a, b) => b.members.length - a.members.length || a.name.localeCompare(b.name, "es"));
}
export function senateSources(legislature: SenateLegislature): Reference[] {
  return [{ label: "Senado · composición de la Mesa", url: legislature.mesaSource }, { label: "Senado · senadores de esta legislatura", url: legislature.source }];
}
