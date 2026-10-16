import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import { asturianInstitutions } from "./cantabrico-model";
const config: RegionalConfig = {
  id: "asturias",
  name: "Asturias",
  chamber: "Junta General del Principado de Asturias",
  board: "Mesa de la Junta General",
  executive: "Consejo de Gobierno del Principado de Asturias",
  ...asturianInstitutions,
  sources: [
    {
      label: "Junta General · diputados y diputadas",
      url: "https://www.jgpa.es/diputados-y-diputadas",
    },
    { label: "Junta General · Mesa", url: "https://www.jgpa.es/mesa" },
    {
      label: "Junta General · resultados electorales",
      url: "https://www.jgpa.es/resultados-electorales",
    },
    {
      label: "Principado de Asturias · equipo de Gobierno",
      url: "https://transparencia.asturias.es/gobierno/equipo-gobierno",
    },
    {
      label: "Senado · nombramientos presidenciales",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_05",
    },
  ],
};
export default function Asturias(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
