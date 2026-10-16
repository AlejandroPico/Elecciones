import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import { navarreInstitutions } from "./norte-model";
const config: RegionalConfig = {
  id: "navarra",
  name: "Navarra",
  chamber: "Parlamento de Navarra",
  board: "Mesa del Parlamento de Navarra",
  executive: "Gobierno de Navarra",
  ...navarreInstitutions,
  sources: [
    {
      label: "Parlamento de Navarra · parlamentarias y parlamentarios",
      url: "https://parlamentodenavarra.es/composicion-organos/parlamentarios-forales",
    },
    {
      label: "Parlamento de Navarra · boletines oficiales",
      url: "https://parlamentodenavarra.es/es/publicaciones/boletin-parlamento",
    },
    {
      label: "Gobierno de Navarra · composición",
      url: "https://gobiernoabierto.navarra.es/es/transparencia/gobierno",
    },
    {
      label: "Gobierno de Navarra · gobiernos anteriores",
      url: "https://www.navarra.es/es/gobierno-de-navarra/gobiernos-anteriores",
    },
    {
      label: "Senado · nombramientos presidenciales",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_13",
    },
  ],
};
export default function Navarra(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
