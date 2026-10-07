import { offices } from "../../../Gobiernos/interfaz/catalogo";
export {
  offices,
  governmentCatalog,
} from "../../../Gobiernos/interfaz/catalogo";
export { organizations, logos } from "../../../Partidos/interfaz/catalogo";
import type { Person, Reference } from "./tipos";
export type { Person, Organization, Reference } from "./tipos";
import candidacyData from "../../../Elecciones/Generales Noviembre 2026/candidaturas.json";
const personFiles = import.meta.glob<unknown>("../../*/*.json", {
  eager: true,
  import: "default",
});
const photos = import.meta.glob<string>(
  "../../*/retrato.{jpg,jpeg,png,webp,svg}",
  { eager: true, query: "?url", import: "default" },
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
      offices: [
        ...new Set([
          ...(meta.offices ?? []),
          ...offices
            .filter((o) => o.members.some((m) => m.person === meta.id))
            .map((o) => o.id),
        ]),
      ],
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
export const candidacies = candidacyData;
export const reviewedAt = "7 de octubre de 2026";
