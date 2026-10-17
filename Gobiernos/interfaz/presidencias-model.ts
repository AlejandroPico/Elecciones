import eventFile from "../investigacion/presidencias-centrales/eventos.json";
import sourceFile from "../investigacion/presidencias-centrales/fuentes.json";
import stageFile from "../investigacion/presidencias-centrales/etapas.json";
import presentation from "../investigacion/presidencias-centrales/presentacion.json";
import normFile from "../investigacion/presidencias-centrales/normativa.json";
import { governmentCatalog } from "./catalogo";

export type EventKind =
  | "milestone"
  | "balance"
  | "crisis"
  | "scandal"
  | "legislation"
  | "institutional";
export type PresidencyEvent = {
  id: string;
  date: string;
  datePrecision: string;
  stage: string;
  title: string;
  category: string;
  summary: string;
  attribution: string;
  sources: string[];
  pending: string[];
  verification: string;
  reviewedAt: string;
  caseId?: string;
  stageAtMilestone?: string;
  relatedStages?: string[];
  judicialStatus?: string;
  statusAtSource?: string;
  factsPeriod?: string;
  topics?: string[];
  displayStages?: { stage: string; reason: string }[];
  boeId?: string;
};
export const researchDate = eventFile.checkedAt;
const normativeEvents: PresidencyEvent[] = normFile.norms.map((norm) => ({
  id: norm.id.toLowerCase(),
  boeId: norm.id,
  date: norm.date,
  datePrecision: "day",
  stage: norm.stage,
  title: norm.title,
  category: "normativa",
  summary: norm.rank + " · Publicación en el BOE",
  attribution: `Registro del índice del BOE. ${norm.officialTitle} Departamento emisor: ${norm.department}. La fecha es la de publicación; puede diferir de la aprobación y de la entrada en vigor. Las leyes son aprobadas por las Cortes; su inclusión en una presidencia no acredita autoría exclusiva del Ejecutivo.`,
  sources: [norm.id.toLowerCase()],
  pending: [],
  verification: "metadatos-oficiales-boe",
  reviewedAt: normFile.checkedAt,
  topics: norm.topics,
}));
export const events = [
  ...(eventFile.events as PresidencyEvent[]),
  ...normativeEvents,
];
export const sources = Object.fromEntries(
  [
    ...sourceFile.sources,
    ...normFile.norms.map((norm) => ({
      id: norm.id.toLowerCase(),
      title: norm.officialTitle,
      url: `https://www.boe.es/diario_boe/txt.php?id=${norm.id}`,
      supports: "Título, rango y fecha de publicación de la disposición.",
      limits:
        "Entrada documental basada en metadatos oficiales. No es una evaluación de efectos ni una lectura íntegra de los artículos; consultar el texto original para conocer su alcance y vigencia.",
      consultedAt: normFile.checkedAt,
      kind: "primary",
    })),
  ].map((s) => [s.id, s]),
);
export const stages = stageFile.stages;
export const presidencies = presentation.presidencies;
export const kinds: { id: EventKind; label: string }[] = [
  { id: "milestone", label: "Hitos y reformas" },
  { id: "balance", label: "Resultados y costes" },
  { id: "crisis", label: "Crisis y reveses" },
  { id: "scandal", label: "Escándalos" },
  { id: "institutional", label: "Institucional" },
  { id: "legislation", label: "Leyes y medidas" },
];
export const topics = [
  ["vivienda", "Vivienda"],
  ["trabajo", "Trabajo y salarios"],
  ["pensiones-y-proteccion-social", "Pensiones y protección social"],
  ["educacion-y-ciencia", "Educación y ciencia"],
  ["sanidad", "Sanidad"],
  ["economia-y-presupuestos", "Economía y presupuestos"],
  ["energia-y-medio-ambiente", "Energía y medio ambiente"],
  ["justicia-y-derechos", "Justicia y derechos"],
  ["interior-y-seguridad", "Interior y seguridad"],
  ["exterior-y-defensa", "Exterior y defensa"],
  ["territorio-e-instituciones", "Territorio e instituciones"],
  ["infraestructuras-y-sectores", "Infraestructuras y sectores"],
  ["corrupcion-y-crisis-politica", "Corrupción y crisis política"],
  ["otras-materias", "Otras materias"],
] as const;
export function eventTopics(event: PresidencyEvent): readonly string[] {
  if (event.topics?.length) return event.topics;
  if (event.caseId)
    return ["corrupcion-y-crisis-politica", "justicia-y-derechos"];
  const category: Record<string, string> = {
    economico: "economia-y-presupuestos",
    exterior: "exterior-y-defensa",
    social: "pensiones-y-proteccion-social",
    institucional: "territorio-e-instituciones",
  };
  return [category[event.category] ?? "otras-materias"];
}
export const presentationCriteria = presentation;
export function eventKind(event: PresidencyEvent): EventKind {
  if (event.boeId) return "legislation";
  const override = (presentation.eventOverrides as Record<string, EventKind>)[
    event.id
  ];
  if (override) return override;
  if (event.caseId && presentation.scandalCases.includes(event.caseId))
    return "scandal";
  if (event.category === "crisis") return "crisis";
  if (event.category === "corrupcion") return "scandal";
  if (event.category === "economico" || event.category === "social")
    return "balance";
  if (event.category === "normativo" || event.category === "exterior")
    return "milestone";
  return "institutional";
}
export function judicialLabel(event: PresidencyEvent) {
  return event.judicialStatus
    ? ((presentation.judicialLabels as Record<string, string>)[
        event.judicialStatus
      ] ?? "Resolución judicial documentada")
    : undefined;
}
export function researchDateLabel(value: string, compact = false) {
  const [year, month, day] = value.split("-").map(Number);
  return new Intl.DateTimeFormat("es-ES", {
    year: "numeric",
    ...(month
      ? { month: compact ? ("short" as const) : ("long" as const) }
      : {}),
    ...(day ? { day: "numeric" as const } : {}),
    timeZone: "UTC",
  }).format(new Date(Date.UTC(year, (month ?? 1) - 1, day ?? 1)));
}
export function durationLabel(from: string, until: string) {
  const [y, m, d] = from.split("-").map(Number);
  const [ey, em, ed] = until.split("-").map(Number);
  const months = (ey - y) * 12 + em - m - (ed < d ? 1 : 0);
  const years = Math.floor(months / 12),
    rest = months % 12;
  if (years || rest)
    return [
      years ? `${years} ${years === 1 ? "año" : "años"}` : "",
      rest ? `${rest} ${rest === 1 ? "mes" : "meses"}` : "",
    ]
      .filter(Boolean)
      .join(" y ");
  const days = Math.round((Date.parse(until) - Date.parse(from)) / 86400000);
  return `${days} ${days === 1 ? "día" : "días"}`;
}
export function normalizeSearch(value: string) {
  return value
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLocaleLowerCase("es");
}
export function matchesEvent(
  event: PresidencyEvent,
  query: string,
  kind: EventKind | "all",
) {
  if (kind !== "all" && eventKind(event) !== kind) return false;
  const text = normalizeSearch(
    [
      event.title,
      event.summary,
      event.attribution,
      event.factsPeriod,
      event.caseId,
      event.date,
      ...eventTopics(event).map(
        (id) => topics.find((t) => t[0] === id)?.[1] ?? id,
      ),
    ].join(" "),
  );
  return normalizeSearch(query)
    .trim()
    .split(/\s+/)
    .every((word) => text.includes(word));
}
export function stagesFor(person: string) {
  const presidency = presidencies.find((p) => p.person === person);
  return stages
    .filter((stage) => presidency?.stages.includes(stage.id))
    .reverse();
}
export function eventsFor(stageId: string, ascending = false) {
  // Un registro canónico puede mostrarse en varias etapas con su relación expresa.
  return events
    .filter(
      (event) =>
        event.stage === stageId ||
        event.stageAtMilestone === stageId ||
        event.relatedStages?.includes(stageId) ||
        event.displayStages?.some((link) => link.stage === stageId),
    )
    .sort(
      (a, b) =>
        (ascending ? 1 : -1) *
        (a.date.localeCompare(b.date) || a.id.localeCompare(b.id)),
    );
}
export function cabinetFor(stageId: string, person: string) {
  const stage = stages.find((s) => s.id === stageId);
  const government = governmentCatalog.find(
    (g) => g.legislature === stage?.legislature,
  );
  return government?.cabinets.find((c) =>
    c.members.some((m) => m.level === "president" && m.person === person),
  )?.id;
}
export function timelinePosition(from: string, until: string) {
  const first = Date.parse(presidencies[0].from),
    last = Date.parse(researchDate);
  return {
    left: ((Date.parse(from) - first) / (last - first)) * 100,
    width: ((Date.parse(until) - Date.parse(from)) / (last - first)) * 100,
  };
}
