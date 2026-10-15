import geography from "../Autonomías/Mapa/cartografia.json";
import snapshot from "../Autonomías/Mapa/presidencias.json";
import territories from "../Autonomías/territorios.json";
export { geography };
export const mapParties = {
  pp: { label: "PP", color: "#0875c1" },
  psoe: { label: "PSOE", color: "#df3d4d" },
  psc: { label: "PSC", color: "#df3d4d" },
  pnv: { label: "EAJ-PNV", color: "#248260" },
  cc: { label: "CC", color: "#edc343" },
};
export const presidencies = snapshot.presidencies.map((p) => ({
  ...p,
  territoryName: territories.find((t) => t.id === p.territory)!.name,
  color: mapParties[p.party as keyof typeof mapParties].color,
}));
export const mapProvinces = geography.provinces.map((p) => ({
  ...p,
  presidency: presidencies.find(
    (president) => president.territory === p.territory,
  )!,
}));
export type MapProvince = (typeof mapProvinces)[number];
export const mapCheckedAt = snapshot.checkedAt;
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
