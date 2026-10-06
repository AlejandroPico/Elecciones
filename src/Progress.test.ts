import { expect, it } from "vitest";
import { categories, questions } from "../Elecciones";
import { progressGroups } from "./Progress";
it("una omisión resuelve la navegación sin confundirse con una respuesta neutral", () => {
  const groups = progressGroups(
    {
      "economia-1": { value: null, importance: 3 },
      "economia-2": { value: 0, importance: 1 },
    },
    2,
  );
  expect(groups[0].completed).toBe(2);
  expect(groups[0].items.map((item) => item.state)).toEqual([
    "skipped",
    "answered",
    "pending",
    "pending",
    "pending",
    "pending",
  ]);
  expect(
    groups.filter((group) => group.active).map((group) => group.category.id),
  ).toEqual(["economia"]);
});
it("la navegación conserva el índice global con temas de tamaños diferentes", () => {
  const bank = [
    ...questions.filter((q) => q.category === "economia").slice(0, 2),
    ...questions.filter((q) => q.category === "sociedad").slice(0, 5),
  ];
  const groups = progressGroups({}, 4, categories.slice(0, 2), bank);
  expect(groups.map((g) => g.items.length)).toEqual([2, 5]);
  expect(groups[1].items.map((item) => item.index)).toEqual([2, 3, 4, 5, 6]);
  expect(groups.map((g) => g.active)).toEqual([false, true]);
});
