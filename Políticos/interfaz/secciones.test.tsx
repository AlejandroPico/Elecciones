import { expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import Archive from "./Archive";
import { people, findPerson } from "./datos/catalogo";
it("sustituye el resumen antiguo del Senado por sus mandatos individuales sin duplicarlo", () => {
  const person = people.find((p) => p.fullName === "Pedro Manuel Rollán Ojeda")!;
  const mandates = person.timeline.filter((t) => /^(Miembro del Senado|Mandato en el Senado)/.test(t.title));
  expect(mandates).toHaveLength(2);
  expect(mandates.every((t) => t.title.startsWith("Mandato en el Senado"))).toBe(true);
});
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
  const relations = html.split("<h3>Relaciones por cargo</h3>")[1]?.split("</article>")[0];
  expect(html.match(/<h3>Relaciones por cargo<\/h3>/g)).toHaveLength(1);
  expect(relations).toContain("2018");
  expect(relations).not.toContain("Ernest Urtasun");
  expect(relations).not.toContain("Máximo Huerta");
});
