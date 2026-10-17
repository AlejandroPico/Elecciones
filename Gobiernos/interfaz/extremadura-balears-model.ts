import { institutions } from "./norte-model";
import type { CatalanGovernment, CatalanParliament } from "./catalonia-model";

export const extremaduranInstitutions = institutions(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Extremadura/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Extremadura/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
);
export const balearicInstitutions = institutions(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Illes Balears/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Illes Balears/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
);
