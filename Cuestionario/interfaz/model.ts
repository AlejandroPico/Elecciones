import raw from "../coordenadas.json";
import axes from "../ejes.json";

export type Evidence = {
  proposalId: string;
  documentId: string;
  pdfPages: number[];
  textLines?: number[];
};
export type Position = {
  value: number | null;
  basis: string;
  evidence: Evidence[];
};
export type ResearchQuestion = {
  id: string;
  statement: string;
  category: string;
  positions: Record<string, Position>;
};
export type Indicator = {
  label: string;
  questionIds: string[];
  direction: number;
};
export type Axis = { label: string; indicators: Indicator[] };
export type MapDefinition = {
  id: string;
  title: string;
  categoryIds: string[];
  x: Axis;
  y: Axis;
};
export const corpus = raw;
export const definitions: MapDefinition[] = axes.charts;
export const methodology = axes.method;
export const questions: ResearchQuestion[] = raw.questions;
export const questionById = new Map(questions.map((q) => [q.id, q]));
export const colors: Record<string, string> = {
  pp: "#4394e5",
  psoe: "#ef6468",
  vox: "#84bd55",
  erc: "#d4a732",
  junts: "#39b4af",
  "eh-bildu": "#b88bd8",
  pnv: "#659d77",
  bng: "#cf85b3",
  pacma: "#a3c946",
  "registro-4086": "#9aaec5",
  "registro-6359": "#e88d4f",
  "registro-6040": "#ee465b",
  "registro-7400": "#eed542",
  "registro-7458": "#c2aa80",
  podemos: "#a56be2",
};

export function documentEdition(source: (typeof raw.sources)[number]) {
  return source.kind === "territorial"
    ? `Programa autonómico · ${source.territory} · ${source.electionDate?.slice(0, 4)}`
    : source.kind === "historical"
      ? `Programa ${source.electionDate?.slice(0, 4)}`
      : source.kind === "permanent"
        ? "Programa permanente"
        : "Programa político general";
}

export function evidenceLocator(evidence: Evidence) {
  return evidence.pdfPages.length
    ? `PDF ${evidence.pdfPages.join(", ")}`
    : `Texto · líneas ${(evidence.textLines ?? []).join(", ")}`;
}

/** Repetir una fuente o una variante no aumenta el peso del indicador. */
export function indicatorValue(
  indicator: Indicator,
  party: string,
  bank: ResearchQuestion[] = questions,
) {
  const values = new Set<number>();
  for (const id of new Set(indicator.questionIds)) {
    const pos = bank.find((q) => q.id === id)?.positions[party];
    if (
      pos?.value != null &&
      pos.evidence.length &&
      [-2, 2].includes(pos.value)
    )
      values.add(50 * pos.value * indicator.direction);
  }
  // Una discrepancia de variantes exige revisión; nunca se resuelve por mayoría.
  return values.size === 1 ? [...values][0] : null;
}

export function scoreAxis(
  axis: Axis,
  party: string,
  bank: ResearchQuestion[] = questions,
) {
  const values = axis.indicators.map((i) => indicatorValue(i, party, bank));
  const known = values.filter((v): v is number => v !== null);
  const total = values.length,
    count = known.length;
  const sum = known.reduce((a, b) => a + b, 0);
  return {
    value: count ? sum / count : null,
    count,
    total,
    values,
    interval: total
      ? [
          (sum - (total - count) * 100) / total,
          (sum + (total - count) * 100) / total,
        ]
      : null,
  };
}

export function partyPoint(map: MapDefinition, party: string) {
  const x = scoreAxis(map.x, party),
    y = scoreAxis(map.y, party);
  return { party, x, y, drawable: x.value !== null && y.value !== null };
}

export function markerGroups(points: ReturnType<typeof partyPoint>[]) {
  const groups = new Map<string, typeof points>();
  for (const p of points.filter((p) => p.drawable)) {
    const key = `${p.x.value}:${p.y.value}`;
    groups.set(key, [...(groups.get(key) ?? []), p]);
  }
  return [...groups.values()];
}
