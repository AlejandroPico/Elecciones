import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import { murcianInstitutions } from "./murcia-model";

const config: RegionalConfig = {
  id: "murcia",
  name: "Región de Murcia",
  chamber: "Asamblea Regional de Murcia",
  board: "Mesa de la Asamblea Regional de Murcia",
  executive: "Consejo de Gobierno de la Región de Murcia",
  ...murcianInstitutions,
  sources: [
    {
      label: "Asamblea · directorio vigente",
      url: "https://www.asambleamurcia.es/diputados?leg=11",
    },
    {
      label: "Asamblea · archivo de las primeras legislaturas",
      url: "https://www.asambleamurcia.es/legacy/es/los-diputados-regionales.html",
    },
    {
      label: "Asamblea · órganos de la Cámara",
      url: "https://www.asambleamurcia.es/arm/organos-x",
    },
    {
      label: "Senado · nombramientos presidenciales en el BOE",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_08",
    },
    {
      label: "CARM · Gobierno y consejerías",
      url: "https://www.carm.es/web/pagina?IDCONTENIDO=1174&IDTIPO=200&RASTRO=c$m59490",
    },
  ],
};

export default function Murcia(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
