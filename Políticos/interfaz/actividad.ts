import type { Person, PoliticalActivity } from "./datos/tipos";

export type ActivityState = PoliticalActivity["state"];
export const activityLabels: Record<ActivityState, string> = {
  active: "Actividad actual documentada",
  unknown: "Actividad por confirmar",
  historical: "Archivo histórico",
};
export const activityRank: Record<ActivityState, number> = { active: 0, unknown: 1, historical: 2 };
export function personActivity(person: Person): ActivityState {
  // El fallecimiento prevalece sobre biografías antiguas que digan «actualidad».
  if (person.deathDate || person.deathYear) return "historical";
  if (person.activity) return person.activity.state;
  // Un mandato cerrado no acredita retirada: puede haber cargos fuera de
  // la cámara o actividad política que todavía no cubre este catálogo.
  return "unknown";
}
