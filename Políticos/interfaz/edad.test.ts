import { expect, it } from "vitest";
import { ageAt } from "./edad";
it("calcula la edad al cumplir años según la fecha local", () => {
  expect(ageAt("1956-11-10", new Date(2026, 10, 9, 23, 59))).toBe(69);
  expect(ageAt("1956-11-10", new Date(2026, 10, 10))).toBe(70);
  expect(ageAt("2000-02-29", new Date(2024, 1, 28))).toBe(23);
  expect(ageAt("2000-02-29", new Date(2024, 1, 29))).toBe(24);
});
