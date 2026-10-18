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
