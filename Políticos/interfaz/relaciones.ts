import {
  offices,
  findPerson,
  type Person,
  type Reference,
} from "./datos/catalogo";

/** Una sola relación por cargo y periodo propios, nunca la sucesión de terceros. */
export function ownOfficeTerms(person: Person) {
  const terms: {
    office?: string;
    name: string;
    period: string;
    source?: Reference;
  }[] = person.offices.flatMap((id) => {
    const office = offices.find((o) => o.id === id);
    return office
      ? office.members
          .filter((m) => findPerson(m.person)?.id === person.id)
          .map((m) => ({ office: id, name: office.name, period: m.period }))
      : [];
  });
  terms.push(
    ...(person.senateOffices ?? []).map((term) => ({
      name: term.title,
      period: term.period,
      source: term.source,
    })),
  );
  terms.push(
    ...(person.congressOffices ?? []).map((term) => ({
      name: term.title,
      period: term.period,
      source: term.source,
    })),
  );
  return terms
    .filter(
      (term, index, terms) =>
        terms.findIndex(
          (other) => other.name === term.name && other.period === term.period,
        ) === index,
    )
    .sort(
      (a, b) =>
        b.period.localeCompare(a.period) || a.name.localeCompare(b.name, "es"),
    );
}
