import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Plugin } from "vite";

/** Lee las fichas originales al compilar, sin mantener un índice duplicado. */
export function partyCatalogPlugin(): Plugin {
  const publicId = "virtual:partidos-fichas",
    resolvedId = "\0" + publicId;
  let projectRoot = "", watching = false;
  return {
    name: "elecciones-partidos",
    configResolved(config) {
      projectRoot = config.root;
      watching = config.command === "serve" && config.mode !== "test";
    },
    resolveId(id) {
      if (id === publicId) return resolvedId;
    },
    async load(id) {
      if (id !== resolvedId) return;
      const directory = join(projectRoot, "Partidos");
      const folders = (await readdir(directory, { withFileTypes: true }))
        .filter((d) => d.isDirectory() && !["interfaz", "herramientas", "revisiones"].includes(d.name))
        .sort((a, b) => a.name.localeCompare(b.name, "es"));
      const files: Record<string, unknown> = {};
      for (let offset = 0; offset < folders.length; offset += 64) {
        await Promise.all(
          folders.slice(offset, offset + 64).map(async (folder) => {
            const path = join(directory, folder.name);
            for (const name of (await readdir(path)).filter((n) =>
              ["ficha.json", "fuentes.json", "historia.json", "dirigentes.json", "programas.json", "logotipo.json", "resultados.json", "documentacion.json"].includes(n),
            )) {
              const file = join(path, name);
              files[`../${folder.name}/${name}`] = JSON.parse(
                await readFile(file, "utf8"),
              );
              if (watching) this.addWatchFile(file);
            }
          }),
        );
      }
      return `export default ${JSON.stringify(files)};`;
    },
    handleHotUpdate(context) {
      if (
        !context.file.startsWith(join(projectRoot, "Partidos")) ||
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
