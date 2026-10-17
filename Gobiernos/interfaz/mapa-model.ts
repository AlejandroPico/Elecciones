import geography from "../Autonomías/Mapa/cartografia.json";
import snapshot from "../Autonomías/Mapa/presidencias.json";
import possessions from "../Autonomías/Mapa/posesiones-presidencia.json";
import territories from "../Autonomías/territorios.json";
import history from "../Autonomías/Mapa/historico-presidencias.json";
export { geography };
export const mapParties = {
  pp: { label: "PP", color: "#0875c1" },
  psoe: { label: "PSOE", color: "#df3d4d" },
  psc: { label: "PSC", color: "#df3d4d" },
  pnv: { label: "EAJ-PNV", color: "#248260" },
  cc: { label: "CC", color: "#edc343" },
  ap: { label: "AP", color: "#247ab8" },
  ciu: { label: "CiU", color: "#125b93" },
  jxcat: { label: "JxCat", color: "#28a89c" },
  jxsi: { label: "JxSí", color: "#80a842" },
  erc: { label: "ERC", color: "#e9ad24" },
  cds: { label: "CDS", color: "#489d4b" },
  ucd: { label: "UCD", color: "#82aa46" },
  pdp: { label: "PDP", color: "#3c73a5" },
  par: { label: "PAR", color: "#d7a62e" },
  prc: { label: "PRC", color: "#b5bc40" },
  fac: { label: "FAC", color: "#1c7191" },
  upca: { label: "UPCA", color: "#a47036" },
  upn: { label: "UPN", color: "#234f98" },
  gbai: { label: "Geroa Bai", color: "#cd4f40" },
  pfc: { label: "PFC", color: "#936da1" },
  gil: { label: "GIL", color: "#76aa41" },
  upm: { label: "UPM", color: "#5c7ea3" },
  cpm: { label: "CpM", color: "#50a747" },
  cs: { label: "Cs", color: "#e97721" },
  independent: { label: "Independiente", color: "#8a8d94" },
  unknown: { label: "Sin datos contrastados", color: "var(--line)" },
};
export const presidencies = snapshot.presidencies.map((p) => {
  const tenure = possessions.presidencies.find(
    (t) => t.territory === p.territory && t.person === p.person,
  );
  if (!tenure)
    throw new Error(`Inicio de presidencia sin contrastar: ${p.territory}`);
  return {
    ...p,
    inOfficeSince: tenure.inOfficeSince,
    tenureSource: tenure.source,
    tenureBasis: tenure.basis,
    territoryName: territories.find((t) => t.id === p.territory)!.name,
    color: mapParties[p.party as keyof typeof mapParties].color,
  };
});
export const mapProvinces = geography.provinces.map((p) => ({
  ...p,
  presidency: presidencies.find(
    (president) => president.territory === p.territory,
  )!,
}));
export type MapProvince = (typeof mapProvinces)[number];
/** Una sola silueta animada por autonomía, con sus límites provinciales intactos. */
export const mapAutonomies = presidencies.map((presidency) => ({
  id: presidency.territory,
  provinces: mapProvinces.filter(
    (province) => province.territory === presidency.territory,
  ),
}));
export const mapCheckedAt = snapshot.checkedAt;
export type MapPresidency = (typeof presidencies)[number];
const partyIds: Record<string, keyof typeof mapParties> = {
  PP: "pp",
  PSOE: "psoe",
  PSC: "psc",
  "PSdeG-PSOE": "psoe",
  PNV: "pnv",
  "EAJ-PNV": "pnv",
  CC: "cc",
  AP: "ap",
  CiU: "ciu",
  JxCat: "jxcat",
  JxSÍ: "jxsi",
  ERC: "erc",
  CDS: "cds",
  UCD: "ucd",
  PDP: "pdp",
  PAR: "par",
  PRC: "prc",
  FAC: "fac",
  UPCA: "upca",
  UPN: "upn",
  GBai: "gbai",
  PFC: "pfc",
  GIL: "gil",
  UPM: "upm",
  CpM: "cpm",
  Cs: "cs",
  "Ind.": "independent",
};
export const mapHistory = history.presidencies;
/** Pasos documentados: también se incluyen los finales, para no rellenar lagunas. */
export const mapDates = [
  ...new Set([
    ...mapHistory.flatMap((p) =>
      [p.start, p.end, ...p.partyChanges.map((c) => c.date)].filter(
        (d): d is string => !!d && d <= mapCheckedAt,
      ),
    ),
    mapCheckedAt,
  ]),
].sort();
export function mapDate(selected?: string) {
  const date = selected?.startsWith("map:") ? selected.slice(4) : undefined;
  return date &&
    /^\d{4}-\d{2}-\d{2}$/.test(date) &&
    date >= mapDates[0] &&
    date <= mapCheckedAt
    ? date
    : mapCheckedAt;
}
export function presidenciesAt(date: string): MapPresidency[] {
  if (date === mapCheckedAt) return presidencies;
  return territories.map((territory) => {
    const p = mapHistory
      .filter(
        (p) =>
          p.territory === territory.id &&
          p.start <= date &&
          (!p.end || date < p.end),
      )
      .sort((a, b) => b.start.localeCompare(a.start))[0];
    const change = p?.partyChanges.filter((c) => c.date <= date).at(-1);
    const formation = change?.party ?? p?.party;
    const party = formation ? (partyIds[formation] ?? "unknown") : "unknown";
    const previous =
      p &&
      mapHistory
        .filter(
          (r) =>
            r.territory === p.territory &&
            r.person === p.person &&
            r.start <= p.start,
        )
        .sort((a, b) => b.start.localeCompare(a.start));
    // Conservar solo la cadena continua; un retorno no empieza en el primer mandato.
    let since = p?.start ?? "";
    let sinceSource = p?.source ?? "";
    for (const r of previous ?? [])
      if (r.start < since && r.end === since) {
        since = r.start;
        sinceSource = r.source;
      }
    return {
      territory: territory.id,
      territoryName: territory.name,
      person: p?.person ?? "",
      name: p?.name ?? "Sin presidencia documentada",
      party,
      partyLabel: formation ?? "Vinculación pendiente",
      appointedAt: p?.start ?? "",
      inOfficeSince: since,
      source: p?.source ?? "",
      title: p?.role ?? "",
      dateBasis: p?.dateBasis ?? "",
      tenureSource: sinceSource,
      tenureBasis: p?.dateBasis ?? "",
      partySource: change?.source ?? p?.partySource ?? "",
      checkedAt: history.checkedAt,
      color: mapParties[party].color,
    };
  });
}
export function provincesAt(date: string): MapProvince[] {
  const presidents = presidenciesAt(date);
  return geography.provinces.map((p) => ({
    ...p,
    presidency: presidents.find((r) => r.territory === p.territory)!,
  }));
}
export function autonomiesAt(provinces: MapProvince[]) {
  return territories.map((t) => ({
    id: t.id,
    provinces: provinces.filter((p) => p.territory === t.id),
  }));
}
/** Mantiene la ficha dentro de la pantalla incluso en ciudades e islas. */
export function tooltipPosition(
  x: number,
  y: number,
  width: number,
  height: number,
  viewportWidth: number,
  viewportHeight: number,
) {
  const gap = 16,
    edge = 12;
  const left =
    x + gap + width <= viewportWidth - edge ? x + gap : x - gap - width;
  const top =
    y + gap + height <= viewportHeight - edge ? y + gap : y - gap - height;
  return {
    left: Math.max(edge, Math.min(left, viewportWidth - width - edge)),
    top: Math.max(edge, Math.min(top, viewportHeight - height - edge)),
  };
}
