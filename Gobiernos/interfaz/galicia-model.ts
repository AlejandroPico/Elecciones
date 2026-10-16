import { institutions } from "./norte-model";
import type { CatalanGovernment, CatalanParliament } from "./catalonia-model";

export const galicianInstitutions = institutions(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Galicia/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Galicia/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
);
