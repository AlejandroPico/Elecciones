import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import { balearicInstitutions } from "./extremadura-balears-model";
const config: RegionalConfig = {
  id: "baleares",
  name: "Illes Balears",
  chamber: "Parlament de les Illes Balears",
  board: "Mesa del Parlament de les Illes Balears",
  executive: "Consell de Govern de les Illes Balears",
  ...balearicInstitutions,
  sources: [
    {
      label: "Parlament · legislaturas y archivos nominales",
      url: "https://www.parlamentib.es/PageHandler/Legislatures",
    },
    {
      label: "Parlament · diputados vigentes",
      url: "https://www.parlamentib.es/Representants/Diputats.aspx?criteria=0",
    },
    {
      label: "Parlament · Mesa",
      url: "https://www.parlamentib.es/Representants/Mesa.aspx",
    },
    {
      label: "Govern · composición vigente",
      url: "https://www.caib.es/webgoib/es/govern",
    },
    {
      label: "Senado · nombramientos presidenciales",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_15",
    },
  ],
};
export default function Baleares(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
