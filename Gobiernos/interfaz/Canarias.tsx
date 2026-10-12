import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  canariasGovernments,
  canariasParliaments,
  canariasGovernmentChronology,
  canariasParliamentChronology,
} from "./canarias-model";
const config: RegionalConfig = {
  id: "canarias",
  name: "Canarias",
  chamber: "Parlamento de Canarias",
  board: "Mesa del Parlamento",
  executive: "Consejo de Gobierno",
  governments: canariasGovernments,
  parliaments: canariasParliaments,
  governmentChronology: canariasGovernmentChronology,
  parliamentChronology: canariasParliamentChronology,
  sources: [
    {
      label: "Parlamento · composición y archivo",
      url: "https://www.parcan.es/composicion/",
    },
    {
      label: "Instituto Canario de Igualdad · cuadros históricos",
      url: "https://www.gobiernodecanarias.org/icigualdad/comunicacion/estadisticas/participacion/",
    },
    {
      label: "Gobierno · altos cargos",
      url: "https://www.gobiernodecanarias.org/organigrama/",
    },
    {
      label: "Boletín Oficial de Canarias",
      url: "https://www.gobiernodecanarias.org/boc/",
    },
  ],
};
export default function Canarias(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
