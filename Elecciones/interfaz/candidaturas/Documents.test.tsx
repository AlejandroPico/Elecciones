import { expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import ElectionDocuments from "./Documents";
import { documentsFor, documentUrl } from "./catalogo";

it("muestra el documento autonómico analizado de SALF sin confundirlo con su programa nacional", () => {
  const html = renderToStaticMarkup(
    <ElectionDocuments organization="registro-7458" />,
  );
  const document = documentsFor("registro-7458")[0];
  expect(document.kind).toBe("territorial");
  expect(html).toContain(
    "Generales del 29N: programa nacional todavía no localizado.",
  );
  expect(html).toContain(
    "Documento autonómico disponible · PDF · análisis incorporado",
  );
  // The download must be visible before expanding the documentary details.
  const firstDetails = html.indexOf('class="document-record"');
  const visibleLink = html.indexOf(`href="${documentUrl(document)}"`);
  expect(visibleLink).toBeGreaterThan(-1);
  expect(visibleLink).toBeLessThan(firstDetails);
});

it("permite descargar el antecedente de Podemos de 2019 sin presentarlo como programa de 2026 o de 2023", () => {
  const html = renderToStaticMarkup(
    <ElectionDocuments organization="podemos" />,
  );
  const document = documentsFor("podemos")[0];
  expect(document.electionDate).toBe("2019-11-10");
  expect(html).toContain(
    "Antecedente nacional de 2019 disponible · PDF · análisis incorporado",
  );
  expect(html).not.toContain("Antecedente de 2023");
  expect(html).toContain(
    "Programa específico de las generales del 29N pendiente",
  );
  expect(html.indexOf(`href="${documentUrl(document)}"`)).toBeLessThan(
    html.indexOf('class="document-record"'),
  );
  expect(html).toContain("Archivo de prensa utilizado");
});
