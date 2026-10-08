import type {
  Organization,
  Reference,
} from "../../Políticos/interfaz/datos/tipos";
import partyFiles from "virtual:partidos-fichas";
const marks = import.meta.glob<string>("../*/logotipo.{svg,png,gif,jpg,webp}", {
  eager: true,
  query: "?url",
  import: "default",
});
function read<T>(
  files: Record<string, unknown>,
  folder: string,
  file: string,
  fallback: T,
): T {
  return (files[`${folder}/${file}`] as T | undefined) ?? fallback;
}
export const logos: Record<string, string> = {};
export const organizations: Organization[] = Object.entries(partyFiles)
  .filter(([path]) => path.endsWith("/ficha.json"))
  .map(([path, data]) => {
    const folder = path.slice(0, -"/ficha.json".length),
      meta = data as Organization;
    const image = read<{
      file: string;
      source: string;
      background?: string;
    } | null>(partyFiles, folder, "logotipo.json", null);
    if (image && marks[`${folder}/${image.file}`])
      logos[meta.id] = marks[`${folder}/${image.file}`];
    return {
      ...meta,
      folder,
      logo: image && logos[meta.id] ? meta.id : undefined,
      logoSource: image?.source,
      logoBackground: image?.background,
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
      electoralResults: read<Organization["electoralResults"]>(partyFiles, folder, "resultados.json", []),
      publicResources: read<Organization["publicResources"]>(partyFiles, folder, "documentacion.json", []),
    };
  })
  .sort((a, b) => a.name.localeCompare(b.name, "es"));
