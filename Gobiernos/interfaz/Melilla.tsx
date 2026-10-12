import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  melillaGovernments,
  melillaParliaments,
  melillaGovernmentChronology,
  melillaParliamentChronology,
} from "./melilla-model";
const config: RegionalConfig = {
  id: "melilla",
  name: "Melilla",
  chamber: "Asamblea de Melilla",
  board: "Mesa de la Asamblea",
  executive: "Consejo de Gobierno",
  governments: melillaGovernments,
  parliaments: melillaParliaments,
  governmentChronology: melillaGovernmentChronology,
  parliamentChronology: melillaParliamentChronology,
  sources: [
    {
      label: "Ciudad · Asamblea",
      url: "https://sede.melilla.es/sta/CarpetaPublic/doEvent?APP_CODE=STA&PAGE_CODE=PTS2_MIEMBROS",
    },
    {
      label: "Ciudad · Consejo de Gobierno",
      url: "https://www.melilla.es/melillaportal/contenedor.jsp?codMenu=253&codMenuPN=600&seccion=distribuidor_menus.jsp",
    },
    {
      label: "BOME · archivo de nombramientos",
      url: "https://bomemelilla.es/",
    },
    {
      label: "Interior · resultados electorales",
      url: "https://infoelectoral.interior.gob.es/",
    },
  ],
};
export default function Melilla(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
