import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  aragonGovernments,
  aragonParliaments,
  aragonGovernmentChronology,
  aragonParliamentChronology,
} from "./aragon-model";
const config: RegionalConfig = {
  id: "aragon",
  name: "Aragón",
  chamber: "Cortes de Aragón",
  board: "Mesa de las Cortes",
  executive: "Gobierno de Aragón",
  governments: aragonGovernments,
  parliaments: aragonParliaments,
  governmentChronology: aragonGovernmentChronology,
  parliamentChronology: aragonParliamentChronology,
  sources: [
    {
      label: "Cortes · archivo de legislaturas",
      url: "https://www.cortesaragon.es/Anteriores-legislaturas.2357.0.html?&no_cache=1",
    },
    {
      label: "Cortes · composición vigente",
      url: "https://www.cortesaragon.es/Diputados-y-diputadas.2164.0.html?&no_cache=1",
    },
    {
      label: "Gobierno · composición",
      url: "https://www.aragon.es/transparencia/gobierno",
    },
    {
      label: "Aragón Open Data · organigramas históricos",
      url: "https://opendata.aragon.es/datos/catalogo/dataset/organigrama-del-gobierno-de-aragon",
    },
    {
      label: "Senado · nombramientos presidenciales",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_10",
    },
  ],
};
export default function Aragon(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
