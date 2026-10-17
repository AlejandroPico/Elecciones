import type { CatalanGovernment, CatalanParliament } from "./catalonia-model";

type Step = {
  id: string;
  date: string;
  period: CatalanGovernment | CatalanParliament;
};
type Period = Pick<CatalanParliament, "id" | "label" | "start">;

/** El ordinal pertenece a la cámara, nunca al número de mandatos del presidente. */
export function legislatureLabel(label: string) {
  return (
    label.match(/\b[IVXLCDM]+(?:[–-][IVXLCDM]+)?\b/)?.[0].replace("-", "–") ??
    (label.startsWith("Parlamento Foral") ? "Foral" : "Provisional")
  );
}

export function legislatureAt(periods: Period[], date: string) {
  return [...periods]
    .sort((a, b) => b.start.localeCompare(a.start))
    .find((p) => p.start <= date);
}

/** Añade los límites parlamentarios sin inventar gabinetes de una instantánea. */
export function legislatureChronology(
  chronology: Step[],
  governments: CatalanGovernment[],
  parliaments: CatalanParliament[],
): Step[] {
  const steps = [...chronology];
  for (const p of parliaments) {
    const government = [...governments]
      .sort((a, b) => b.start.localeCompare(a.start))
      .find((g) => g.start <= p.start && (!g.end || p.start < g.end));
    if (!government || government.currentOnly || p.start > government.checkedAt)
      continue;
    const id = `${government.id}-${p.start}`;
    if (!steps.some((s) => s.id === id))
      steps.push({ id, date: p.start, period: government });
  }
  return steps.sort((a, b) => a.date.localeCompare(b.date));
}

export function legislatureLibrary(
  chronology: Step[],
  parliaments: CatalanParliament[],
) {
  const entries = new Map<
    string,
    { id: string; label: string; start: string; steps: Step[] }
  >();
  for (const step of chronology) {
    const p = legislatureAt(parliaments, step.date);
    const id = p?.id ?? "provisional";
    if (!entries.has(id))
      entries.set(id, {
        id,
        label: p ? legislatureLabel(p.label) : "Provisional",
        start: p?.start ?? step.date,
        steps: [],
      });
    entries.get(id)!.steps.push(step);
  }
  return [...entries.values()].sort((a, b) => b.start.localeCompare(a.start));
}

/** Las rutas históricas del mapa seleccionan una composición conservada del gobierno. */
export function regionalPosition(chronology: Step[], selected?: string) {
  const exact = chronology.findIndex((s) => s.id === selected);
  if (exact >= 0) return exact;
  if (selected?.startsWith("at-")) {
    const date = selected.slice(3);
    const period = [...chronology]
      .sort((a, b) => b.period.start.localeCompare(a.period.start))
      .find(
        (s) => s.period.start <= date && (!s.period.end || date < s.period.end),
      )?.period;
    if (period) {
      const steps = chronology.filter((s) => s.period.id === period.id);
      const step = steps.filter((s) => s.date <= date).at(-1) ?? steps[0];
      if (step) return chronology.findIndex((s) => s.id === step.id);
    }
  }
  return Math.max(0, chronology.length - 1);
}
