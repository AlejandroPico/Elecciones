import { expect, it } from "vitest";
import { compareParties } from "./orden";
import type { Organization } from "../../Políticos/interfaz/datos/tipos";
function party(id: string, seats?: number, votes?: number): Organization {
  return { id, name: id, fullName: id, folder: id, references: [], documents: [], history: [], leadership: [], electoralResults: seats === undefined ? [] : [{ date: "2023-07-23", election: "2023", chamber: "congreso", seats, votes, candidature: id, source: { label: "BOE", url: "https://www.boe.es/" } }] };
}
it("ordena con datos electorales y distingue un cero acreditado de la ausencia de datos", () => {
  const unknown = party("A desconocido"), small = party("B sin escaños", 0, 100), largest = party("C mayor", 137, 8000000), next = party("D siguiente", 102, 6000000);
  expect([unknown, small, next, largest].sort(compareParties("seats")).map(p => p.id)).toEqual([largest.id, next.id, small.id, unknown.id]);
  expect([party("Más votos", 1, 10000), party("Más escaños", 2, 1000)].sort(compareParties("votes"))[0].id).toBe("Más votos");
});
it("ordena por antigüedad con la fundación documentada y deja fechas desconocidas al final", () => {
  const old = { ...party("Fundado"), founding: { date: "1879-05-02", precision: 11, source: { label: "Fuente", url: "https://example.org" } } }, newParty = { ...party("Inscrito"), registration: { id: "1", name: "Inscrito", date: "2023-01-01", locality: "Madrid", source: "https://example.org", checkedAt: "2026-10-08" } }, unknown = party("Sin fecha");
  expect([unknown, newParty, old].sort(compareParties("oldest")).map(p => p.id)).toEqual([old.id, newParty.id, unknown.id]);
  expect([unknown, old, newParty].sort(compareParties("newest")).map(p => p.id)).toEqual([newParty.id, old.id, unknown.id]);
});
