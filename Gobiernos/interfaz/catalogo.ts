import type {
  Government,
  Reference,
} from "../../Políticos/interfaz/datos/tipos";
const governmentFiles = import.meta.glob<Government>(
  "../*/composiciones.json",
  { eager: true, import: "default" },
);
export const governmentCatalog = Object.values(governmentFiles).sort((a, b) =>
  b.cabinets[0].date.localeCompare(a.cabinets[0].date),
);
export type Office = {
  id: string;
  name: string;
  group: string;
  department?: string;
  description: string;
  pattern?: string;
  level?: string;
  pending?: boolean;
  source: Reference;
  members: { person: string; period: string }[];
};
const files = import.meta.glob<Office>("../Cargos/*/ficha.json", {
  eager: true,
  import: "default",
});
function holders(office: Office) {
  if (office.pending) return [];
  const records = governmentCatalog
    .flatMap((g) => g.cabinets)
    .sort((a, b) => a.date.localeCompare(b.date));
  const pattern = office.pattern ? new RegExp(office.pattern, "i") : null;
  const periods: { person: string; start: string; end?: string }[] = [];
  let active: (typeof periods)[number] | undefined;
  for (const c of records) {
    const ministerial =
      office.name.startsWith("Ministerios") || office.id === "sin-cartera";
    const member = c.members.find(
      (m) =>
        (!office.level || m.level === office.level) &&
        (!ministerial || /ministr[oa]\b/i.test(m.role)) &&
        (!pattern || pattern.test(m.role)),
    );
    if (active?.person === member?.person) continue;
    if (active) active.end = c.date.slice(0, 4);
    active = member
      ? { person: member.person, start: c.date.slice(0, 4) }
      : undefined;
    if (active) periods.push(active);
  }
  return periods
    .reverse()
    .map((p) => ({
      person: p.person,
      period: `${p.start}–${p.end ?? "última composición"}`,
    }));
}
export const offices: Office[] = Object.values(files).map((o) => ({
  ...o,
  members: holders(o),
}));
