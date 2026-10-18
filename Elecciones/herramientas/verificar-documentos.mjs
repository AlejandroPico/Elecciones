/** Verificación local: no altera originales ni depende de la disponibilidad de la red. */
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { resolve, sep } from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
const manifest = JSON.parse(
  await readFile(
    resolve(root, "Generales Noviembre 2026/programas.json"),
    "utf8",
  ),
);
const ids = new Set();
for (const document of manifest) {
  if (ids.has(document.id)) throw new Error(`ID duplicado: ${document.id}`);
  ids.add(document.id);
  const target = resolve(root, document.file);
  if (!target.startsWith(root.endsWith(sep) ? root : root + sep))
    throw new Error(`Ruta fuera de Elecciones: ${document.file}`);
  const bytes = await readFile(target);
  const hash = createHash("sha256").update(bytes).digest("hex");
  if (hash !== document.sha256 || bytes.length !== document.bytes)
    throw new Error(`Original alterado: ${document.id}`);
  if (document.htmlCapture) {
    const capturePath = resolve(root, document.htmlCapture.file);
    if (!capturePath.startsWith(root.endsWith(sep) ? root : root + sep))
      throw new Error(`Captura fuera de Elecciones: ${document.id}`);
    const capture = await readFile(capturePath);
    if (
      capture.length !== document.htmlCapture.bytes ||
      createHash("sha256").update(capture).digest("hex") !==
        document.htmlCapture.sha256
    )
      throw new Error(`Captura HTML alterada: ${document.id}`);
  }
  if (document.format === "PDF" && bytes.subarray(0, 5).toString() !== "%PDF-")
    throw new Error(`PDF inválido: ${document.id}`);
  if (document.kind === "historical") {
    const election = new Date(`${document.electionDate}T00:00:00Z`);
    const months = [
      "Enero",
      "Febrero",
      "Marzo",
      "Abril",
      "Mayo",
      "Junio",
      "Julio",
      "Agosto",
      "Septiembre",
      "Octubre",
      "Noviembre",
      "Diciembre",
    ];
    if (
      !/^\d{4}-\d{2}-\d{2}$/.test(document.electionDate ?? "") ||
      Number.isNaN(election.getTime()) ||
      election.toISOString().slice(0, 10) !== document.electionDate ||
      document.electionDate >= document.retrievedAt ||
      !document.file.startsWith(
        `Generales ${months[election.getUTCMonth()]} ${election.getUTCFullYear()}/programas/`,
      )
    )
      throw new Error(`Antecedente fuera de su elección: ${document.id}`);
  }
  if (document.scoringEligible && document.analysis !== "reviewed")
    throw new Error(
      `Análisis pendiente utilizado como posición: ${document.id}`,
    );
}
console.log(
  `${manifest.length} documentos: rutas, formatos, tamaño e integridad correctos.`,
);
