import { describe, expect, it } from "vitest";
import { parseRoute, routeHash, type Route } from "./navigation";
describe("direcciones de secciones y fichas", () => {
  it("permite reconstruir todos los pasos y sus identificadores al retroceder o recargar", () => {
    const routes: Route[] = [
      { view: "governments" },
      { view: "governments", entry: { kind: "government", id: "VII-2003-09" } },
      { view: "senate", entry: { kind: "senate", id: "senado-14-2021-07-12" } },
      { view: "archive", entry: { kind: "person", id: "pedro-sánchez/2026" } },
      { view: "programs", entry: { kind: "party", id: "psoe" } },
      { view: "offices", entry: { kind: "office", id: "defensa" } },
    ];
    expect(routes.map(routeHash).map(parseRoute)).toEqual(routes);
    expect([...routes].reverse().map(routeHash).map(parseRoute)).toEqual([...routes].reverse());
  });
  it("descarta fichas de otra sección y direcciones mal formadas", () => {
    expect(parseRoute("#/partidos/person/psoe")).toEqual({ view: "programs" });
    expect(parseRoute("#/archivo/person/%XX")).toEqual({ view: "archive" });
    expect(parseRoute("#desconocida")).toEqual({ view: "survey" });
  });
});
