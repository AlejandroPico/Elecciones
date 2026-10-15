import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  clmGovernments,
  clmParliaments,
  clmGovernmentChronology,
  clmParliamentChronology,
} from "./clm-model";
const config: RegionalConfig = {
  id: "castilla-la-mancha",
  name: "Castilla-La Mancha",
  chamber: "Cortes de Castilla-La Mancha",
  board: "Mesa de las Cortes",
  executive: "Consejo de Gobierno",
  governments: clmGovernments,
  parliaments: clmParliaments,
  governmentChronology: clmGovernmentChronology,
  parliamentChronology: clmParliamentChronology,
  sources: [
    {
      label: "Cortes · composición y archivo",
      url: "https://www.cortesclm.es/index.php/composicion",
    },
    {
      label: "Gobierno · composición",
      url: "https://castillalamancha.es/gobierno",
    },
    {
      label: "Senado · nombramientos presidenciales",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_11",
    },
  ],
};
export default function CastillaLaMancha(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
