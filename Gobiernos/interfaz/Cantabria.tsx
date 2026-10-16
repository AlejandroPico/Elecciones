import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import { cantabrianInstitutions } from "./cantabrico-model";
const config: RegionalConfig = {
  id: "cantabria",
  name: "Cantabria",
  chamber: "Parlamento de Cantabria",
  board: "Mesa del Parlamento de Cantabria",
  executive: "Gobierno de Cantabria",
  ...cantabrianInstitutions,
  sources: [
    {
      label: "Parlamento de Cantabria · legislaturas",
      url: "https://parlamento-cantabria.es/informacion-general/legislaturas",
    },
    {
      label: "Biblioteca del Parlamento · diputados y Mesas por legislaturas",
      url: "https://parlamento-cantabria.es/sites/default/files/5.%20Diputados%20y%20Mesas%20por%20Legislaturas_0.pdf",
    },
    {
      label: "Gobierno de Cantabria · consejerías",
      url: "https://www.cantabria.es/consejerias1",
    },
    {
      label: "Senado · composición del Gobierno de Cantabria",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=aut_composiciongob_06",
    },
    {
      label: "Senado · nombramientos presidenciales",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_06",
    },
  ],
};
export default function Cantabria(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
