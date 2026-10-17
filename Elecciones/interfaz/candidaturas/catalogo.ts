import participation from "../../Generales Noviembre 2026/participacion.json";
import documents from "../../Generales Noviembre 2026/programas.json";

export type ElectionDocument = (typeof documents)[number];
export type Participation = (typeof participation.entries)[number];
export const electionResearch = participation;
export const electoralDocuments = documents;
export const participationLabels: Record<string, string> = {
  announced: "Participación anunciada",
  preparing: "Preparación de candidatura",
  "registered-coalition": "Coalición constituida · JEC",
  agreement: "Acuerdo territorial o de cámara",
  "not-running": "No concurre · anuncio documentado",
};
const files = import.meta.glob<string>("../../*/programas/**/*.{pdf,txt}", {
  eager: true,
  query: "?url&no-inline",
  import: "default",
});
export function documentUrl(document: ElectionDocument) {
  return files[`../../${document.file}`];
}
export function documentsFor(organization: string) {
  return electoralDocuments.filter(
    (document) => document.organization === organization,
  );
}
export function participationFor(organization: string) {
  return electionResearch.entries.filter(
    (entry) =>
      entry.organization === organization ||
      ("members" in entry && entry.members?.includes(organization)),
  );
}
export function matchesScope(
  entry: Participation,
  chamber: string,
  province: string,
) {
  return entry.scope.some(
    (scope) =>
      (chamber === "all" || scope.chamber === chamber) &&
      (province === "all" || scope.provinces.includes(province)),
  );
}
