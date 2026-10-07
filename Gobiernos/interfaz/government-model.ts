import { governmentCatalog } from "./catalogo";
export const governments = governmentCatalog;
export const chronology = governments
  .flatMap((g) => g.cabinets.map((c) => ({ ...c, government: g })))
  .sort((a, b) => a.date.localeCompare(b.date));
export function dateLabel(date: string) {
  return new Intl.DateTimeFormat("es-ES", {
    year: "numeric",
    month: "long",
    ...(date.length === 10 ? { day: "numeric" as const } : {}),
  }).format(
    new Date(date.length === 7 ? `${date}-01T12:00:00` : `${date}T12:00:00`),
  );
}
export function snapshotAt(date: string) {
  // Los registros mensuales no se convierten en nombramientos de día 1.
  return chronology.filter((c) => c.date <= date).at(-1);
}
