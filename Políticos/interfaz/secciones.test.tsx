import { expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import Archive from "./Archive";
import { people, findPerson } from "./datos/catalogo";
it("oculta los apartados para los que una carpeta no contiene datos", () => {
  const sparse = people.find(
    (p) => !p.education?.length && !p.dossier?.length,
  )!;
  expect(sparse).toBeTruthy();
  const html = renderToStaticMarkup(
    <Archive initialRoute={{ kind: "person", id: sparse.id }} />,
  );
  expect(html).not.toContain("<h3>Formación</h3>");
  expect(html).not.toContain("<h3>Actuaciones y controversias</h3>");
  if (!sparse.sections.includes("datos-personales.json"))
    expect(html).not.toContain("<h3>Datos personales</h3>");
  expect(html).toContain(sparse.name);
});
it("las relaciones de una persona muestran sus periodos, sin listar los demás titulares", () => {
  const person = findPerson("jose-guirao")!;
  const html = renderToStaticMarkup(<Archive initialRoute={{ kind: "person", id: person.id }} />);
  const relations = html.split("RELACIONES POR CARGO")[1]?.split("</article>")[0];
  expect(relations).toContain("2018");
  expect(relations).not.toContain("Ernest Urtasun");
  expect(relations).not.toContain("Máximo Huerta");
});
