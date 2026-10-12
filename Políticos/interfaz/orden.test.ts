import { expect, it } from "vitest";
import { people } from "./datos/catalogo";
import {
  orderPeople,
  matchesPerson,
  randomIndex,
  randomPeopleOrder,
} from "./orden";
it("ordena por actividad documentada y mantiene búsquedas sin tildes por nombre y cargo", () => {
  const sanchez = people.find((p) => p.id === "sanchez")!;
  const suarez = people.find((p) => p.id === "adolfo-suarez-gonzalez")!;
  expect(sanchez).toBeTruthy();
  expect(suarez).toBeTruthy();
  expect(orderPeople([suarez, sanchez], "recent")[0].id).toBe(sanchez.id);
  expect(orderPeople([sanchez, suarez], "oldest")[0].id).toBe(sanchez.id);
  expect(matchesPerson(sanchez, "sanchez")).toBe(true);
  expect(matchesPerson(suarez, "presidente del gobierno")).toBe(true);
});

it("descarta el sobrante del sorteo para evitar sesgo entre índices", () => {
  const draws = [0xffffffff, 5];
  expect(randomIndex(3, () => draws.shift()!)).toBe(2);
  expect(draws).toHaveLength(0);
  expect(() => randomIndex(0)).toThrow(RangeError);
});

it("mezcla sin perder identidades ni modificar el catálogo y conserva el orden al filtrar", () => {
  const originals = people.slice(0, 20);
  const originalIds = originals.map((p) => p.id);
  const ranks = randomPeopleOrder(originals, () => 0);
  expect(new Set(ranks.keys())).toEqual(new Set(originalIds));
  expect(new Set(ranks.values()).size).toBe(originals.length);
  expect(originals.map((p) => p.id)).toEqual(originalIds);
  const all = orderPeople(originals, "random", ranks);
  const subset = originals.filter((_, i) => i % 2 === 0);
  const subsetIds = new Set(subset.map((p) => p.id));
  expect(orderPeople(subset, "random", ranks).map((p) => p.id)).toEqual(
    all.filter((p) => subsetIds.has(p.id)).map((p) => p.id),
  );
  expect(randomPeopleOrder(originals, () => 1)).not.toEqual(ranks);
});

it("mantiene los activos antes que los históricos también en el sorteo", () => {
  const sanchez = people.find((p) => p.id === "sanchez")!;
  const suarez = people.find((p) => p.id === "adolfo-suarez-gonzalez")!;
  const list = [suarez, sanchez];
  expect(
    orderPeople(
      list,
      "random",
      new Map([
        [suarez.id, 0],
        [sanchez.id, 1],
      ]),
    ).map((p) => p.id),
  ).toEqual([sanchez.id, suarez.id]);
});
