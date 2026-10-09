import { describe, expect, it } from "vitest";
import {
  constrainCamera,
  homeCamera,
  revealPoint,
  zoomCamera,
  wheelCamera,
} from "./hemicycle-camera";

describe("Visor del hemiciclo", () => {
  it("deja desplazar la página al reducir desde el 100 %, pero permite ampliar", () => {
    expect(wheelCamera(homeCamera, 80, 300, 200)).toBeNull();
    expect(wheelCamera(homeCamera, 0, 300, 200)).toBeNull();
    expect(wheelCamera(homeCamera, -80, 300, 200)?.zoom).toBeGreaterThan(1);
  });
  it("la rueda conserva el punto bajo el puntero y respeta los límites", () => {
    const camera = wheelCamera(homeCamera, -100, 300, 200)!;
    expect(300 * camera.zoom + camera.x).toBeCloseTo(300);
    expect(200 * camera.zoom + camera.y).toBeCloseTo(200);
    expect(wheelCamera(zoomCamera(homeCamera, 4), -100, 300, 200)?.zoom).toBe(
      4,
    );
    expect(wheelCamera(zoomCamera(homeCamera, 1.01), 100, 300, 200)).toEqual(
      homeCamera,
    );
  });
  it("amplía alrededor del centro y conserva ese punto", () => {
    const camera = zoomCamera(homeCamera, 2);
    expect(camera).toEqual({ zoom: 2, x: -520, y: -275 });
    expect(520 * camera.zoom + camera.x).toBe(520);
    expect(275 * camera.zoom + camera.y).toBe(275);
    expect(zoomCamera(camera, 1)).toEqual(homeCamera);
  });
  it("impide perder el plano al arrastrar y limita el zoom", () => {
    expect(constrainCamera({ zoom: 2, x: 9000, y: -9000 })).toEqual({
      zoom: 2,
      x: 0,
      y: -550,
    });
    expect(constrainCamera({ zoom: 9, x: -9999, y: -9999 })).toEqual({
      zoom: 4,
      x: -3120,
      y: -1650,
    });
    expect(constrainCamera({ zoom: 0.1, x: 10, y: -10 })).toEqual(homeCamera);
  });
  it("mantiene visible la persona recorrida con el teclado", () => {
    const point = { x: 950, y: 450 };
    const camera = revealPoint(zoomCamera(homeCamera, 4), point);
    expect(point.x * camera.zoom + camera.x).toBeLessThanOrEqual(1015);
    expect(point.y * camera.zoom + camera.y).toBeLessThanOrEqual(525);
    expect(camera.zoom).toBe(4);
  });
});
