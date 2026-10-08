import { expect, it } from "vitest";
import { autonomyEntry, readAutonomyEntry, territories } from "./Autonomies";
import { routeHash, parseRoute } from "../../src/app/navigation";
it("ofrece las 17 comunidades y las dos ciudades, con dos secciones navegables", () => {
  expect(territories).toHaveLength(19);
  expect(territories.filter((t) => t.kind === "comunidad")).toHaveLength(17);
  expect(
    territories.filter((t) => t.kind === "ciudad").map((t) => t.name),
  ).toEqual(["Ceuta", "Melilla"]);
  expect(new Set(territories.map((t) => t.id)).size).toBe(19);
  for (const territory of territories)
    for (const section of ["government", "parliament"] as const) {
      const id = autonomyEntry(territory.id, section);
      expect(readAutonomyEntry(id)).toEqual({ territory, section });
      const route = {
        view: "autonomies",
        entry: { kind: "autonomy", id },
      } as const;
      expect(parseRoute(routeHash(route))).toEqual(route);
    }
  expect(readAutonomyEntry("cataluna:inventado")).toBeUndefined();
  expect(
    readAutonomyEntry("cataluna:parliament:catalunya-parlament-15-2026-10-08")
      ?.snapshot,
  ).toBe("catalunya-parlament-15-2026-10-08");
});
