export type Camera = { zoom: number; x: number; y: number };
export const homeCamera: Camera = { zoom: 1, x: 0, y: 0 };
export function constrainCamera(camera: Camera): Camera {
  const zoom = Math.min(4, Math.max(1, camera.zoom));
  return {
    zoom,
    x: Math.min(0, Math.max(1040 * (1 - zoom), camera.x)),
    y: Math.min(0, Math.max(550 * (1 - zoom), camera.y)),
  };
}
export function zoomCamera(
  camera: Camera,
  zoom: number,
  x = 520,
  y = 275,
): Camera {
  const next = Math.min(4, Math.max(1, zoom));
  const ratio = next / camera.zoom;
  return constrainCamera({
    zoom: next,
    x: x - (x - camera.x) * ratio,
    y: y - (y - camera.y) * ratio,
  });
}
export function revealPoint(
  camera: Camera,
  point: { x: number; y: number },
): Camera {
  const x = point.x * camera.zoom + camera.x,
    y = point.y * camera.zoom + camera.y;
  return constrainCamera({
    ...camera,
    x: camera.x + (x < 25 ? 25 - x : x > 1015 ? 1015 - x : 0),
    y: camera.y + (y < 25 ? 25 - y : y > 525 ? 525 - y : 0),
  });
}
