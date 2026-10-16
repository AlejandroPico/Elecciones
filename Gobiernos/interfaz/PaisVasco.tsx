import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import { basqueInstitutions } from "./norte-model";
const config: RegionalConfig = {
  id: "pais-vasco",
  name: "País Vasco",
  chamber: "Parlamento Vasco",
  board: "Mesa del Parlamento Vasco",
  executive: "Gobierno Vasco",
  ...basqueInstitutions,
  sources: [
    {
      label: "Parlamento Vasco · miembros y legislaturas",
      url: "https://www.legebiltzarra.eus/comparla/c_comparla_alf_ACT.html",
    },
    {
      label: "Gobierno Vasco · Consejo de Gobierno",
      url: "https://www.euskadi.eus/miembros-del-consejo-de-gobierno/web01-s1ezaleh/es/",
    },
    {
      label: "Gobierno Vasco · equipos históricos",
      url: "https://www.euskadi.eus/equipo-de-gobierno-de-la-legislatura-4/web01-s1ezaleh/es/",
    },
    {
      label: "Senado · nombramientos presidenciales",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_01",
    },
  ],
};
export default function PaisVasco(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
