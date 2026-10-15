import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  cylGovernments,
  cylParliaments,
  cylGovernmentChronology,
  cylParliamentChronology,
} from "./cyl-model";
const config: RegionalConfig = {
  id: "castilla-y-leon",
  name: "Castilla y León",
  chamber: "Cortes de Castilla y León",
  board: "Mesa de las Cortes",
  executive: "Consejo de Gobierno de la Junta",
  governments: cylGovernments,
  parliaments: cylParliaments,
  governmentChronology: cylGovernmentChronology,
  parliamentChronology: cylParliamentChronology,
  sources: [
    {
      label: "Cortes · composición y archivo",
      url: "https://www.ccyl.es/Organizacion/Procuradores?Legislatura=12",
    },
    {
      label: "Gobierno · composición",
      url: "https://analisis.datosabiertos.jcyl.es/explore/dataset/altos-cargos/",
    },
    {
      label: "Senado · nombramientos presidenciales",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_17",
    },
  ],
};
export default function CastillaLeon(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
