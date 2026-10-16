import { institutions } from "./norte-model";
import type { CatalanGovernment, CatalanParliament } from "./catalonia-model";

export const murcianInstitutions = institutions(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Región de Murcia/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Región de Murcia/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
);
