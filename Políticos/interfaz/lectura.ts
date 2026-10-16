import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Plugin } from "vite";
import { compactJson } from "./datos/compacto";

/** Cada carpeta es la ficha original; los informes de revisión quedan fuera de la web. */
export function personCatalogPlugin(): Plugin {
  const publicId = "virtual:personas-fichas",
    resolvedId = "\0" + publicId;
  const photosId = "virtual:personas-retratos";
  const previewId = "virtual:presidencias-retratos";
  let root = "",
    testing = false,
    watching = false;
  let prepared: string | undefined;
  const allowed = new Set([
    "ficha.json",
    "datos-personales.json",
    "retrato.json",
    "formacion.json",
    "afiliaciones.json",
    "fuentes-formacion.json",
    "trayectoria.json",
    "actuaciones.json",
    "fuentes.json",
    "biografia-institucional.json",
    "actividad.json",
    "cargos-senado.json",
    "mandatos-senado.json",
    "mandatos-congreso.json",
    "cargos-congreso.json",
    "grupos-congreso.json",
    "mandatos-catalunya.json",
    "cargos-catalunya.json",
    "grupos-catalunya.json",
    "mandatos-madrid.json",
    "cargos-madrid.json",
    "grupos-madrid.json",
    "comisiones-madrid.json",
    "mandatos-valencia.json",
    "cargos-valencia.json",
    "grupos-valencia.json",
    "comisiones-valencia.json",
    "mandatos-andalucia.json",
    "cargos-andalucia.json",
    "grupos-andalucia.json",
    "comisiones-andalucia.json",
    "mandatos-autonomias.json",
    "cargos-autonomias.json",
    "grupos-autonomias.json",
  ]);
  async function collect(watch?: (file: string) => void) {
    const directory = join(root, "Políticos");
    const folders = (await readdir(directory, { withFileTypes: true })).filter(
      (d) =>
        d.isDirectory() &&
        !["interfaz", "herramientas", "revisiones"].includes(d.name),
    );
    const files: Record<string, unknown> = {};
    for (let offset = 0; offset < folders.length; offset += 64)
      await Promise.all(
        folders.slice(offset, offset + 64).map(async (folder) => {
          const path = join(directory, folder.name);
          for (const name of (await readdir(path)).filter((n) =>
            allowed.has(n),
          )) {
            const file = join(path, name);
            files[`../../${folder.name}/${name}`] = JSON.parse(
              await readFile(file, "utf8"),
            );
            watch?.(file);
          }
        }),
      );
    const original = JSON.stringify(files),
      packed = JSON.stringify(compactJson(files));
    console.info(
      `Catálogo personal: ${(original.length / 1e6).toFixed(1)} MB → ${(packed.length / 1e6).toFixed(1)} MB de datos compactos, sin pérdida.`,
    );
    return `import {expandJson} from '/Políticos/interfaz/datos/compacto.ts'; export default expandJson(JSON.parse(${JSON.stringify(packed)}));`;
  }
  return {
    name: "elecciones-personas",
    async configResolved(config) {
      root = config.root;
      testing = config.mode === "test";
      watching = config.command === "serve" && !testing;
      // Preparar las fichas antes de iniciar los trabajadores evita que una
      // lectura lenta de OneDrive consuma su plazo de comunicación.
      if (testing) prepared = await collect();
    },
    resolveId(id) {
      if (id === publicId) return resolvedId;
      if (id === photosId) return "\0" + photosId;
      if (id === previewId) return "\0" + previewId;
    },
    async load(id) {
      if (id === "\0" + previewId) {
        const snapshotFile = join(
          root,
          "Gobiernos",
          "Autonomías",
          "Mapa",
          "presidencias.json",
        );
        const snapshot = JSON.parse(await readFile(snapshotFile, "utf8")) as {
          presidencies: { person: string; name: string }[];
        };
        const imports: string[] = [],
          entries: string[] = [];
        if (watching) this.addWatchFile(snapshotFile);
        for (const [i, p] of snapshot.presidencies.entries()) {
          const folder = join(root, "Políticos", p.name),
            metaFile = join(folder, "ficha.json"),
            photoFile = join(folder, "retrato.json");
          const meta = JSON.parse(await readFile(metaFile, "utf8")),
            photo = JSON.parse(await readFile(photoFile, "utf8"));
          if (meta.id !== p.person)
            throw new Error(
              `Identidad del mapa sin correspondencia: ${p.name}`,
            );
          if (watching) {
            this.addWatchFile(metaFile);
            this.addWatchFile(photoFile);
          }
          imports.push(
            `import image${i} from ${JSON.stringify(`/Políticos/${p.name}/${photo.file}?url&no-inline`)};`,
          );
          entries.push(
            `${JSON.stringify(p.person)}:{src:image${i},name:${JSON.stringify(p.name)},credit:${JSON.stringify(photo.credit)},source:${JSON.stringify(photo.source)}}`,
          );
        }
        return imports.join("\n") + `\nexport default {${entries.join(",")}};`;
      }
      if (id === "\0" + photosId) {
        if (!testing)
          return `export default Object.fromEntries(Object.entries(import.meta.glob('/Políticos/*/retrato*.{jpg,jpeg,png,webp,svg,gif}', {eager:true,query:'?url',import:'default'})).map(([path,url]) => ['../../'+path.slice('/Políticos/'.length),url]));`;
        const photos: Record<string, string> = {};
        // Las pruebas de datos comprueban el recurso real sin ejecutar un módulo
        // de JavaScript por cada una de las miles de imágenes.
        const folders = (
          await readdir(join(root, "Políticos"), { withFileTypes: true })
        ).filter(
          (d) =>
            d.isDirectory() &&
            !["interfaz", "herramientas", "revisiones"].includes(d.name),
        );
        for (let offset = 0; offset < folders.length; offset += 64)
          await Promise.all(
            folders.slice(offset, offset + 64).map(async (folder) => {
              for (const file of await readdir(
                join(root, "Políticos", folder.name),
              ))
                if (/^retrato[^/\\]*\.(jpg|jpeg|png|webp|svg|gif)$/.test(file))
                  photos[`../../${folder.name}/${file}`] = join(
                    root,
                    "Políticos",
                    folder.name,
                    file,
                  );
            }),
          );
        return `export default ${JSON.stringify(photos)};`;
      }
      if (id !== resolvedId) return;
      return (
        prepared ??
        collect(watching ? (file) => this.addWatchFile(file) : undefined)
      );
    },
    handleHotUpdate(context) {
      if (
        !context.file.startsWith(join(root, "Políticos")) ||
        !context.file.endsWith(".json")
      )
        return;
      const module = context.server.moduleGraph.getModuleById(resolvedId);
      if (module) {
        context.server.moduleGraph.invalidateModule(module);
        context.server.ws.send({ type: "full-reload" });
      }
    },
  };
}
