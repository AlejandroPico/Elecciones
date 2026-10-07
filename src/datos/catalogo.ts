import type { Person, Organization, Government, Reference } from "./tipos";
export type { Person, Organization, Reference } from "./tipos";
import candidacyData from "../../Elecciones/Generales Noviembre 2026/candidaturas.json";
const personFiles = import.meta.glob<unknown>("../../Políticos/*/*.json", {
  eager: true,
  import: "default",
});
const partyFiles = import.meta.glob<unknown>("../../Partidos/*/*.json", {
  eager: true,
  import: "default",
});
const photos = import.meta.glob<string>(
  "../../Políticos/*/retrato.{jpg,jpeg,png,webp,svg}",
  { eager: true, query: "?url", import: "default" },
);
const marks = import.meta.glob<string>(
  "../../Partidos/*/logotipo.{svg,png,gif,jpg,webp}",
  { eager: true, query: "?url", import: "default" },
);
const governmentFiles = import.meta.glob<Government>(
  "../../Gobiernos/*/composiciones.json",
  { eager: true, import: "default" },
);
function read<T>(
  files: Record<string, unknown>,
  folder: string,
  file: string,
  fallback: T,
): T {
  return (files[`${folder}/${file}`] as T | undefined) ?? fallback;
}
function sections(files: Record<string, unknown>, folder: string) {
  return Object.keys(files)
    .filter((p) => p.startsWith(`${folder}/`))
    .map((p) => p.split("/").at(-1)!);
}
export const governmentCatalog = Object.values(governmentFiles).sort((a, b) =>
  b.cabinets[0].date.localeCompare(a.cabinets[0].date),
);
export const portraits: Record<string, string> = {};
export const people: Person[] = Object.entries(personFiles)
  .filter(([path]) => path.endsWith("/ficha.json"))
  .map(([path, data]) => {
    const folder = path.slice(0, -"/ficha.json".length),
      meta = data as Person;
    const image = read<{ file: string; credit: string; source: string } | null>(
      personFiles,
      folder,
      "retrato.json",
      null,
    );
    if (image && photos[`${folder}/${image.file}`])
      portraits[meta.id] = photos[`${folder}/${image.file}`];
    const personal = read<Partial<Person>>(
      personFiles,
      folder,
      "datos-personales.json",
      {},
    );
    return {
      ...meta,
      ...personal,
      folder,
      sections: sections(personFiles, folder),
      ...(image && portraits[meta.id]
        ? {
            portrait: meta.id,
            photoCredit: image.credit,
            photoSource: image.source,
          }
        : {}),
      education: read<string[]>(personFiles, folder, "formacion.json", []),
      formationSources: read<Reference[]>(
        personFiles,
        folder,
        "fuentes-formacion.json",
        [],
      ),
      timeline: read<Person["timeline"]>(
        personFiles,
        folder,
        "trayectoria.json",
        [],
      ),
      dossier: read<Person["dossier"]>(
        personFiles,
        folder,
        "actuaciones.json",
        [],
      ),
      references: read<Reference[]>(personFiles, folder, "fuentes.json", []),
    };
  })
  .sort((a, b) => a.fullName!.localeCompare(b.fullName!, "es"));
export function findPerson(id: string) {
  return people.find((p) => p.id === id || p.legacyIds?.includes(id));
}
export const logos: Record<string, string> = {};
export const organizations: Organization[] = Object.entries(partyFiles)
  .filter(([path]) => path.endsWith("/ficha.json"))
  .map(([path, data]) => {
    const folder = path.slice(0, -"/ficha.json".length),
      meta = data as Organization;
    const image = read<{ file: string; source: string } | null>(
      partyFiles,
      folder,
      "logotipo.json",
      null,
    );
    if (image) logos[meta.id] = marks[`${folder}/${image.file}`];
    return {
      ...meta,
      folder,
      logo: meta.id,
      logoSource: image?.source,
      references: read<Reference[]>(partyFiles, folder, "fuentes.json", []),
      documents: read<Organization["documents"]>(
        partyFiles,
        folder,
        "programas.json",
        [],
      ),
      history: read<Organization["history"]>(
        partyFiles,
        folder,
        "historia.json",
        [],
      ),
      leadership: read<Organization["leadership"]>(
        partyFiles,
        folder,
        "dirigentes.json",
        [],
      ),
    };
  })
  .sort((a, b) => a.name.localeCompare(b.name, "es"));
function holders(
  predicate: (m: Government["cabinets"][number]["members"][number]) => boolean,
) {
  const records = governmentCatalog
    .flatMap((g) => g.cabinets)
    .sort((a, b) => a.date.localeCompare(b.date));
  const periods: { person: string; start: string; end?: string }[] = [];
  for (const c of records) {
    const member = c.members.find(predicate);
    if (!member || periods.at(-1)?.person === member.person) continue;
    const previous = periods.at(-1);
    if (previous) previous.end = c.date.slice(0, 4);
    periods.push({ person: member.person, start: c.date.slice(0, 4) });
  }
  return periods
    .reverse()
    .map((p) => ({
      person: p.person,
      period: `${p.start}–${p.end ?? "actualidad"}`,
    }));
}
export const offices = [
  {
    id: "presidencia",
    name: "Presidencia del Gobierno",
    description:
      "Titulares desde 1977. Periodos por año derivados de las composiciones archivadas.",
    members: holders((m) => m.level === "president"),
    source: {
      label: "La Moncloa · Gobiernos por legislaturas",
      url: "https://www.lamoncloa.gob.es/gobierno/gobiernosporlegislaturas/Paginas/index.aspx",
    },
  },
  {
    id: "defensa",
    name: "Ministerio de Defensa",
    description:
      "Titulares desde 1977. Periodos por año derivados de las composiciones archivadas.",
    members: holders((m) => /(?:^| y )ministr[oa] de Defensa$/i.test(m.role)),
    source: {
      label: "La Moncloa · Gobiernos por legislaturas",
      url: "https://www.lamoncloa.gob.es/gobierno/gobiernosporlegislaturas/Paginas/index.aspx",
    },
  },
];
export const candidacies = candidacyData;
export const reviewedAt = "7 de octubre de 2026";
