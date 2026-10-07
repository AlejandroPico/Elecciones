import { afterEach, expect, it, vi } from "vitest";
import { createAdvanceClock } from "./avance";
afterEach(() => vi.useRealTimers());
it("avanza una vez a los tres segundos aunque se edite la respuesta o la importancia", () => {
  vi.useFakeTimers();
  const clock = createAdvanceClock(),
    next = vi.fn();
  expect(clock.start(next)).toBe(true);
  vi.advanceTimersByTime(1500);
  expect(clock.start(next)).toBe(false);
  vi.advanceTimersByTime(1499);
  expect(next).not.toHaveBeenCalled();
  vi.advanceTimersByTime(1);
  expect(next).toHaveBeenCalledTimes(1);
});
it("cancela la ficha anterior al navegar y permite un nuevo plazo completo", () => {
  vi.useFakeTimers();
  const clock = createAdvanceClock(),
    previous = vi.fn(),
    next = vi.fn();
  clock.start(previous);
  vi.advanceTimersByTime(2000);
  clock.cancel();
  clock.start(next);
  vi.advanceTimersByTime(2999);
  expect(previous).not.toHaveBeenCalled();
  expect(next).not.toHaveBeenCalled();
  vi.advanceTimersByTime(1);
  expect(next).toHaveBeenCalledTimes(1);
});
