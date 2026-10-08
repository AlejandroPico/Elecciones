import type { Person, Organization } from "./datos/tipos";
function normalize(value: string) {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();
}
export function affiliationKey(
  affiliation: NonNullable<Person["affiliations"]>[number],
) {
  return affiliation.organization ?? `historico:${normalize(affiliation.name)}`;
}
export function matchesAffiliation(person: Person, filter: string) {
  if (filter === "all") return true;
  if (filter === "independent")
    return person.affiliationStatus === "independent";
  if (filter === "pending") return person.affiliationStatus === "pending";
  return (
    person.organization === filter ||
    person.affiliations?.some((a) => affiliationKey(a) === filter) === true
  );
}
export function affiliationOptions(
  people: Person[],
  organizations: Organization[],
) {
  const values = new Map<string, string>();
  for (const person of people) {
    if (person.organization) {
      const party = organizations.find((o) => o.id === person.organization);
      if (party) values.set(party.id, party.name);
    }
    for (const affiliation of person.affiliations ?? []) {
      if (affiliation.kind === "independent") continue;
      const party = organizations.find(
        (o) => o.id === affiliation.organization,
      );
      values.set(affiliationKey(affiliation), party?.name ?? affiliation.name);
    }
  }
  return [...values]
    .map(([value, label]) => ({ value, label }))
    .sort((a, b) => a.label.localeCompare(b.label, "es"));
}
export function affiliationLabel(
  person: Person,
  organizations: Organization[],
) {
  const affiliations = person.affiliations ?? [];
  const names = [
    ...new Set(
      affiliations
        .filter((a) => a.kind !== "independent")
        .map((a) => {
          const name =
            organizations.find((o) => o.id === a.organization)?.name ?? a.name;
          return a.kind === "association" ? `Vinculación con ${name}` : name;
        }),
    ),
  ];
  if (person.affiliationStatus === "independent")
    return "Independiente" + (names.length ? ` · ${names.join(" · ")}` : "");
  if (names.length) return names.join(" · ");
  return (
    organizations.find((o) => o.id === person.organization)?.name ??
    "Vinculación pendiente"
  );
}
