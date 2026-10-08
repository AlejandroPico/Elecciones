import { expect, it } from "vitest";
import { people } from "./datos/catalogo";
import { orderPeople, matchesPerson } from "./orden";
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
