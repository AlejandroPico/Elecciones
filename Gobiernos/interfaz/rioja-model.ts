import { institutions } from "./norte-model";
import type { CatalanGovernment, CatalanParliament } from "./catalonia-model";

export const riojanInstitutions = institutions(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/La Rioja/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
  import.meta.glob<CatalanParliament>(
    "../Autonomías/La Rioja/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
);
