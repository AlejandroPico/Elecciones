import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import { riojanInstitutions } from "./rioja-model";

const config: RegionalConfig = {
  id: "la-rioja",
  name: "La Rioja",
  chamber: "Parlamento de La Rioja",
  board: "Mesa del Parlamento de La Rioja",
  executive: "Consejo de Gobierno de La Rioja",
  ...riojanInstitutions,
  sources: [
    {
      label: "Parlamento · legislaturas anteriores",
      url: "https://www.parlamento-larioja.org/conoce-el-parlamento/legislaturas-anteriores",
    },
    {
      label: "Parlamento · directorio vigente",
      url: "https://www.parlamento-larioja.org/composicion-y-organos/diputados",
    },
    {
      label: "Parlamento · Mesa vigente",
      url: "https://www.parlamento-larioja.org/composicion-y-organos/legislatura-11/organos/mesa",
    },
    {
      label: "Gobierno de La Rioja · composición",
      url: "https://web.larioja.org/consejo-de-gobierno",
    },
    {
      label: "Transparencia · gobiernos anteriores y fechas de consejerías",
      url: "https://web.larioja.org/portal-transparencia/56-gobierno/consejo-de-gobierno/174-gobiernos-anteriores",
    },
  ],
};

export default function LaRioja(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
