import type { Organization } from "../../Políticos/interfaz/datos/tipos";

export const normalizeParty = (value: string) => value.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
export function electoralResult(party: Organization) {
  return party.electoralResults?.find(result => result.chamber === "congreso" && result.date === "2023-07-23");
}
export function partyDate(party: Organization) {
  return party.founding?.date ?? party.registration?.date;
}
export function compareParties(order: string) {
  return (a: Organization, b: Organization) => {
    const first = electoralResult(a), second = electoralResult(b);
    const names = () => a.fullName.localeCompare(b.fullName, "es");
    if (order === "name") return names();
    if (order === "oldest" || order === "newest") {
      const dateA = partyDate(a), dateB = partyDate(b);
      if (!dateA || !dateB) return Number(!dateA) - Number(!dateB) || names();
      return (order === "oldest" ? 1 : -1) * dateA.localeCompare(dateB) || names();
    }
    const known = Number(!!second) - Number(!!first);
    if (known) return known;
    if (order === "votes") return (second?.votes ?? -1) - (first?.votes ?? -1) || (second?.seats ?? -1) - (first?.seats ?? -1) || names();
    return (second?.seats ?? -1) - (first?.seats ?? -1) || (second?.votes ?? -1) - (first?.votes ?? -1) || Number(!!b.logo) - Number(!!a.logo) || names();
  };
}
