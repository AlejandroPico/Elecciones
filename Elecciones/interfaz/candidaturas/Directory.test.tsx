import { expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import ElectionDirectory from "./Directory";
import ElectionDocuments from "./Documents";
import { documentUrl, documentsFor } from "./catalogo";

it("encuentra el Frente Amplio al buscar Sumar y ofrece la ficha del integrante", () => {
  const html = renderToStaticMarkup(
    <ElectionDirectory query="sumar" openParty={() => {}} />,
  );
  expect(html).toContain("Frente Amplio");
  expect(html).toContain('aria-label="Ficha de Movimiento Sumar"');
  expect(html).toContain(
    'aria-label="Organizaciones vinculadas a Frente Amplio"',
  );
  expect(html).not.toContain("No hay anuncios incorporados");
});

it("ofrece el programa común de 2023 desde la ficha actual sin atribuirlo a 2026", () => {
  const html = renderToStaticMarkup(<ElectionDocuments organization="sumar" />);
  const source = documentsFor("sumar")[0];
  expect(html).toContain("coalición Sumar · generales 23J 2023");
  expect(html).toContain(
    "Antecedente nacional de 2023 disponible · PDF · análisis incorporado",
  );
  expect(html.indexOf(`href="${documentUrl(source)}"`)).toBeLessThan(
    html.indexOf('class="document-record"'),
  );
  expect(html).toContain("programa propio a cada integrante");
  expect(html).toContain(
    "Programa específico de las generales del 29N pendiente",
  );
});
