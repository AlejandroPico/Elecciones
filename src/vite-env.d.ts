/// <reference types="vite/client" />
declare module "virtual:presidencias-retratos" {
  const portraits: Record<
    string,
    { src: string; name: string; credit: string; source: string }
  >;
  export default portraits;
}
declare module "virtual:personas-retratos" {
  const files: Record<string, string>;
  export default files;
}
declare module "virtual:personas-fichas" {
  const files: Record<string, unknown>;
  export default files;
}
declare module "virtual:partidos-fichas" {
  const files: Record<string, unknown>;
  export default files;
}
