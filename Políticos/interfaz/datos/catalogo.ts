import { offices } from "../../../Gobiernos/interfaz/catalogo";
export {
  offices,
  governmentCatalog,
} from "../../../Gobiernos/interfaz/catalogo";
export { organizations, logos } from "../../../Partidos/interfaz/catalogo";
import type { Person, Reference } from "./tipos";
export type { Person, Organization, Reference } from "./tipos";
import candidacyData from "../../../Elecciones/Generales Noviembre 2026/candidaturas.json";
import personFiles from "virtual:personas-fichas";
import photos from "virtual:personas-retratos";
function read<T>(
  files: Record<string, unknown>,
  folder: string,
  file: string,
  fallback: T,
): T {
  return (files[`${folder}/${file}`] as T | undefined) ?? fallback;
}
const folderSections = new Map<string, string[]>();
for (const path of Object.keys(personFiles)) {
  const end = path.lastIndexOf("/"),
    folder = path.slice(0, end);
  folderSections.set(folder, [
    ...(folderSections.get(folder) ?? []),
    path.slice(end + 1),
  ]);
}
export const portraits: Record<string, string> = {};
export const people: Person[] = Object.entries(personFiles)
  .filter(([path]) => path.endsWith("/ficha.json"))
  .map(([path, data]) => {
    const folder = path.slice(0, -"/ficha.json".length),
      meta = data as Person;
    const image = read<{
      file: string;
      credit: string;
      source: string;
      license?: string;
      licenseUrl?: string;
      date?: string;
    } | null>(personFiles, folder, "retrato.json", null);
    if (image && photos[`${folder}/${image.file}`])
      portraits[meta.id] = photos[`${folder}/${image.file}`];
    const personal = read<Partial<Person>>(
      personFiles,
      folder,
      "datos-personales.json",
      {},
    );
    const senateMandates = read<Person["timeline"]>(
      personFiles,
      folder,
      "mandatos-senado.json",
      [],
    );
    const congressMandates = read<Person["timeline"]>(
      personFiles,
      folder,
      "mandatos-congreso.json",
      [],
    );
    const originalTimeline = read<Person["timeline"]>(
      personFiles,
      folder,
      "trayectoria.json",
      [],
    );
    const catalanMandates = read<Person["timeline"]>(
      personFiles,
      folder,
      "mandatos-catalunya.json",
      [],
    );
    return {
      ...meta,
      ...personal,
      offices: [
        ...new Set([
          ...(meta.offices ?? []),
          ...offices
            .filter((o) =>
              o.members.some(
                (m) =>
                  m.person === meta.id || meta.legacyIds?.includes(m.person),
              ),
            )
            .map((o) => o.id),
        ]),
      ],
      folder,
      sections: folderSections.get(folder) ?? [],
      activity: read<Person["activity"]>(
        personFiles,
        folder,
        "actividad.json",
        undefined,
      ),
      senateOffices: read<Person["senateOffices"]>(
        personFiles,
        folder,
        "cargos-senado.json",
        [],
      ),
      senateMandates,
      congressMandates,
      catalanMandates,
      catalanOffices: read<Person["catalanOffices"]>(
        personFiles,
        folder,
        "cargos-catalunya.json",
        [],
      ),
      catalanGroups: read<Person["catalanGroups"]>(
        personFiles,
        folder,
        "grupos-catalunya.json",
        [],
      ),
      congressOffices: read<Person["congressOffices"]>(
        personFiles,
        folder,
        "cargos-congreso.json",
        [],
      ),
      congressGroups: read<Person["congressGroups"]>(
        personFiles,
        folder,
        "grupos-congreso.json",
        [],
      ),
      ...(image && portraits[meta.id]
        ? {
            portrait: meta.id,
            photoCredit: image.credit,
            photoSource: image.source,
            photoLicense: image.license,
            photoLicenseUrl: image.licenseUrl,
            photoDate: image.date,
          }
        : {}),
      education: read<string[]>(personFiles, folder, "formacion.json", []),
      affiliations: read<NonNullable<Person["affiliations"]>>(
        personFiles,
        folder,
        "afiliaciones.json",
        [],
      ),
      formationSources: read<Reference[]>(
        personFiles,
        folder,
        "fuentes-formacion.json",
        [],
      ),
      timeline: [
        ...originalTimeline.filter(
          (term) =>
            (!senateMandates.length ||
              !(
                term.source.url.includes("senado.es") &&
                /^(Senador|Participación en el Senado|Miembro del Senado)/i.test(
                  term.title,
                )
              )) &&
            (!congressMandates.length ||
              !(
                term.source.url.includes("congreso.es") &&
                /^(Diputad[oa]|Participación en el Congreso|Miembro del Congreso)/i.test(
                  term.title,
                )
              )),
        ),
        ...senateMandates,
        ...congressMandates,
        ...catalanMandates,
      ].sort((a, b) => a.period.localeCompare(b.period)),
      dossier: read<Person["dossier"]>(
        personFiles,
        folder,
        "actuaciones.json",
        [],
      ),
      references: read<Reference[]>(personFiles, folder, "fuentes.json", []),
      institutionalBiography: read<Person["institutionalBiography"]>(
        personFiles,
        folder,
        "biografia-institucional.json",
        [],
      ),
    };
  })
  .sort((a, b) => a.fullName!.localeCompare(b.fullName!, "es"));
const peopleById = new Map(
  people.flatMap((p) =>
    [p.id, ...(p.legacyIds ?? [])].map((id) => [id, p] as const),
  ),
);
export function findPerson(id: string) {
  return peopleById.get(id);
}
export const candidacies = candidacyData;
export const reviewedAt = "8 de octubre de 2026";
