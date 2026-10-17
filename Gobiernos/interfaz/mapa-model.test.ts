import { expect, it } from "vitest";
import {
  geography,
  mapAutonomies,
  mapProvinces,
  presidencies,
  tooltipPosition,
  presidenciesAt,
  provincesAt,
  autonomiesAt,
  mapDates,
  mapDate,
  mapHistory,
} from "./mapa-model";
import territories from "../Autonomías/territorios.json";
import { findPerson, portraits } from "../../Políticos/interfaz/datos/catalogo";
import { parseRoute, routeHash } from "../../src/app/navigation";

it("representa las 50 provincias y las dos ciudades, con todas las presidencias y sus fuentes", () => {
  expect(mapProvinces).toHaveLength(52);
  expect(new Set(mapProvinces.map((p) => p.id)).size).toBe(52);
  expect(presidencies).toHaveLength(19);
  expect(mapAutonomies).toHaveLength(19);
  expect(
    mapAutonomies
      .flatMap((a) => a.provinces)
      .map((p) => p.id)
      .sort(),
  ).toEqual(mapProvinces.map((p) => p.id).sort());
  expect(
    mapAutonomies.find((a) => a.id === "andalucia")!.provinces,
  ).toHaveLength(8);
  expect(
    mapAutonomies.find((a) => a.id === "canarias")!.provinces,
  ).toHaveLength(2);
  for (const autonomy of mapAutonomies)
    expect(autonomy.provinces.every((p) => p.territory === autonomy.id)).toBe(
      true,
    );
  expect(presidencies.map((p) => p.territory).sort()).toEqual(
    territories.map((t) => t.id).sort(),
  );
  for (const p of presidencies) {
    expect(findPerson(p.person)?.fullName, p.territory).toBe(p.name);
    expect(portraits[findPerson(p.person)!.id], p.name).toBeTruthy();
    expect(p.source).toMatch(/^https:\/\/www.boe.es\//);
    expect(p.partySource).toMatch(/^https:\/\//);
    expect(p.appointedAt).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(p.dateBasis).toContain("no equivale a toma de posesión");
    expect(p.inOfficeSince).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(p.inOfficeSince <= p.checkedAt).toBe(true);
    expect(p.tenureSource).toMatch(/^https:\/\//);
  }
  expect(mapProvinces.find((p) => p.id === "50")!.presidency.name).toBe(
    "Jorge Antonio Azcón Navarro",
  );
  expect(mapProvinces.find((p) => p.id === "08")!.presidency.party).toBe("psc");
  expect(mapProvinces.find((p) => p.id === "48")!.presidency.party).toBe("pnv");
});
it("distingue mandatos consecutivos, retornos y posesión de nombramiento", () => {
  const since = (id: string) =>
    presidencies.find((p) => p.territory === id)!.inOfficeSince;
  expect(since("aragon")).toBe("2023-08-11");
  expect(since("galicia")).toBe("2022-05-14");
  expect(since("canarias")).toBe("2023-07-14");
  expect(since("melilla")).toBe("2023-07-08");
  expect(since("ceuta")).toBe("2001-02-08");
});
it("recorre presidencias históricas sin proyectar titulares ni partidos actuales", () => {
  const president = (territory: string, date: string) =>
    presidenciesAt(date).find((p) => p.territory === territory)!;
  expect(president("aragon", "1988-01-01").party).toBe("par");
  expect(president("aragon", "1994-01-01").party).toBe("psoe");
  expect(president("baleares", "1995-08-01").name).toBe(
    "Cristòfol Soler i Cladera",
  );
  expect(president("baleares", "1996-07-01").person).toBe(
    "jaime-matas-i-palou",
  );
  expect(president("cataluna", "2020-09-27").person).toBe("quim-torra");
  expect(president("cataluna", "2020-10-01").person).toBe("pere-aragones");
  expect(president("cataluna", "2020-10-01").party).toBe("erc");
  expect(president("cataluna", "2017-11-01").person).toBe("");
  expect(president("madrid", "2019-05-01").person).toBe("senado-19063");
  expect(president("ceuta", "1990-01-01").person).toBe("");
  expect(president("melilla", "2001-01-01").party).toBe("upm");
  expect(president("melilla", "2020-01-01").party).toBe("cs");
  expect(president("melilla", "2022-01-01").party).toBe("independent");
  expect(president("melilla", "2024-01-01").inOfficeSince).toBe("2023-07-07");
  for (const date of ["1977-12-05", "1983-08-01", "1995-08-01", "2019-08-01"]) {
    const provinces = provincesAt(date);
    expect(provinces).toHaveLength(52);
    for (const autonomy of autonomiesAt(provinces))
      expect(
        new Set(
          autonomy.provinces.map(
            (p) => `${p.presidency.person}:${p.presidency.color}`,
          ),
        ).size,
      ).toBe(1);
  }
});
it("conserva fuentes, límites y enlaces fechados de todo el índice histórico", () => {
  expect(mapHistory).toHaveLength(263);
  expect(mapDates[0]).toBe("1977-12-05");
  expect(new Set(mapDates).size).toBe(mapDates.length);
  expect(mapDates).toEqual([...mapDates].sort());
  for (const p of mapHistory) {
    expect(findPerson(p.person)?.fullName).toBe(p.name);
    expect(p.source).toMatch(/^https?:\/\//);
    if (p.party) expect(p.partySource).toMatch(/^https?:\/\//);
    expect(p.end === null || p.end > p.start).toBe(true);
  }
  expect(mapDate("map:1996-07-01")).toBe("1996-07-01");
  expect(mapDate("map:2027-01-01")).toBe(mapDates.at(-1));
  const route = {
    view: "autonomies",
    entry: { kind: "autonomy", id: "map:1996-07-01" },
  } as const;
  expect(parseRoute(routeHash(route))).toEqual(route);
});
it("conserva límites detallados e inserciones separadas para Canarias y las ciudades", () => {
  expect(
    geography.provinces.reduce(
      (n, p) => n + (p.path.match(/L/g)?.length ?? 0),
      0,
    ),
  ).toBeGreaterThan(30000);
  for (const p of mapProvinces) {
    expect(p.path).toMatch(/^M/);
    expect(p.path).not.toMatch(/NaN|Infinity/);
    expect(p.presidency.territory).toBe(p.territory);
  }
  expect(
    mapProvinces
      .filter((p) => p.panel === "canarias")
      .map((p) => p.id)
      .sort(),
  ).toEqual(["35", "38"]);
  expect(mapProvinces.find((p) => p.id === "51")!.panel).toBe("ceuta");
  expect(mapProvinces.find((p) => p.id === "52")!.panel).toBe("melilla");
  expect(new Set(geography.neighbours.map((p) => p.name))).toEqual(
    new Set(["Portugal", "France", "Andorra", "Morocco"]),
  );
  const centre = (code: string) => {
    const points = [
      ...mapProvinces
        .find((p) => p.id === code)!
        .path.matchAll(/(-?\d+\.\d+),(-?\d+\.\d+)/g),
    ];
    const xs = points.map((p) => Number(p[1])),
      ys = points.map((p) => Number(p[2]));
    return {
      x: (Math.min(...xs) + Math.max(...xs)) / 2,
      y: (Math.min(...ys) + Math.max(...ys)) / 2,
    };
  };
  // Comprobación geográfica independiente de la fórmula de proyección: norte
  // arriba y levante a la derecha en las coordenadas de pantalla.
  expect(centre("15").y).toBeLessThan(centre("41").y);
  expect(centre("08").y).toBeLessThan(centre("46").y);
  expect(centre("15").x).toBeLessThan(centre("08").x);
});
it("mantiene las fichas dentro de pantalla y las rutas de gobierno autonómico al volver al mapa", () => {
  for (const [w, h, width, height] of [
    [1280, 900, 370, 150],
    [390, 844, 366, 150],
  ])
    for (const [x, y] of [
      [0, 0],
      [w, h],
      [w / 2, h / 2],
    ]) {
      const p = tooltipPosition(x, y, width, height, w, h);
      expect(p.left).toBeGreaterThanOrEqual(12);
      expect(p.top).toBeGreaterThanOrEqual(12);
      expect(p.left + width).toBeLessThanOrEqual(w - 12);
      expect(p.top + height).toBeLessThanOrEqual(h - 12);
    }
  const overview = { view: "autonomies" } as const;
  expect(parseRoute(routeHash(overview))).toEqual(overview);
  for (const autonomy of mapAutonomies) {
    const government = {
      view: "autonomies",
      entry: { kind: "autonomy", id: `${autonomy.id}:government` },
    } as const;
    expect(parseRoute(routeHash(government))).toEqual(government);
  }
});
