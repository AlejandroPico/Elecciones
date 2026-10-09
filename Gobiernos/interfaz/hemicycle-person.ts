import type { Person } from "../../Políticos/interfaz/datos/tipos";

type Member = { source: string; constituency?: string; formation?: string };

export function memberConstituency(
  member: Member,
  person?: Pick<Person, "senateMandates">,
) {
  if (member.constituency) return member.constituency;
  // La ficha de la misma legislatura acredita también el origen de los senadores.
  const mandate = person?.senateMandates?.find(
    (m) => m.source.url === member.source,
  );
  return mandate?.title
    .split(" · ")
    .slice(2)
    .join(" · ")
    .replace(/^Elect[oa]:\s*/i, "")
    .replace(/\s*\.\s*$/, "")
    .trim();
}

export function memberParty(
  member: Member,
  person: Pick<Person, "affiliations"> | undefined,
  date: string,
) {
  const memberships =
    person?.affiliations?.filter((a) => a.kind === "membership") ?? [];
  const dated = memberships.filter((a) => {
    const period = a.period ?? "";
    if (/última ficha/i.test(period)) return period.includes(date);
    const dates = period.match(/\d{4}-\d{2}-\d{2}/g);
    if (dates?.length)
      return dates[0] <= date && (!dates[1] || date <= dates[1]);
    const years = period.match(/\d{4}/g);
    if (!years || (years.length === 1 && !/desde|actualidad/i.test(period)))
      return false;
    return (
      years[0] <= date.slice(0, 4) &&
      (!years[1] || date.slice(0, 4) <= years[1])
    );
  });
  if (dated.length)
    return {
      label: "Partido",
      name: [...new Set(dated.map((a) => a.name))].join(" · "),
    };
  // Una afiliación sin intervalo no acredita la militancia en una fecha histórica.
  const undated = memberships.filter(
    (a) =>
      !a.period || (/^\d{4}$/.test(a.period) && a.period <= date.slice(0, 4)),
  );
  if (undated.length)
    return {
      label: "Afiliación documentada",
      name: [...new Set(undated.map((a) => a.name))].join(" · "),
    };
  if (member.formation) return { label: "Candidatura", name: member.formation };
  return undefined;
}

export function compactGroupLabel(label: string) {
  const name = label
    .replace(/^GRUPO PARLAMENTARIO\s+/i, "")
    .replace(/\s*\(GP[^)]*\)\s*$/i, "");
  if (/^PLURAL EN EL SENADO/i.test(name)) return "Plural";
  if (/^IZQUIERDA CONFEDERAL/i.test(name)) return "Izquierda Confederal";
  if (/^IZQUIERDAS POR LA INDEPENDENCIA/i.test(name))
    return "Izquierdas por la Independencia";
  return name.replace(/\s+EN EL SENADO/i, "");
}
