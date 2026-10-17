import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import { extremaduranInstitutions } from "./extremadura-balears-model";
const config: RegionalConfig = {
  id: "extremadura",
  name: "Extremadura",
  chamber: "Asamblea de Extremadura",
  board: "Mesa de la Asamblea de Extremadura",
  executive: "Consejo de Gobierno de la Junta de Extremadura",
  ...extremaduranInstitutions,
  sources: [
    {
      label: "Asamblea · legislaturas y directorios históricos",
      url: "https://www.asambleaex.es/legislaturas",
    },
    {
      label: "Asamblea · composición vigente",
      url: "https://www.asambleaex.es/dipslegis-12",
    },
    {
      label: "Asamblea · Mesa",
      url: "https://www.asambleaex.es/dipsorgano-3-12",
    },
    {
      label: "Junta de Extremadura · Gobierno",
      url: "https://www.juntaex.es/es/lajunta",
    },
    {
      label: "Senado · cronología de las legislaturas",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=CRONOL_LEGISL_EXTREMADURA&lang=gl_ES",
    },
  ],
};
export default function Extremadura(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
