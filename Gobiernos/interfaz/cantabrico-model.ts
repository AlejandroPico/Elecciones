import { institutions } from "./norte-model";
import type { CatalanGovernment, CatalanParliament } from "./catalonia-model";

export const asturianInstitutions = institutions(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Asturias/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Asturias/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
);
export const cantabrianInstitutions = institutions(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Cantabria/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Cantabria/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
);
