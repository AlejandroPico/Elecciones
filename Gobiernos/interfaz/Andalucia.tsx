import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  andaluciaGovernments,
  andaluciaParliaments,
  andaluciaGovernmentChronology,
  andaluciaParliamentChronology,
} from "./andalucia-model";
const config: RegionalConfig = {
  id: "andalucia",
  name: "Andalucía",
  chamber: "Parlamento de Andalucía",
  board: "Mesa del Parlamento",
  executive: "Consejo de Gobierno",
  governments: andaluciaGovernments,
  parliaments: andaluciaParliaments,
  governmentChronology: andaluciaGovernmentChronology,
  parliamentChronology: andaluciaParliamentChronology,
  governmentNote:
    "Las fuentes distinguen nombramiento, efectos y toma de posesión. Las fechas documentales de las etapas antiguas se explican en las notas de cada registro.",
  sources: [
    {
      label: "Parlamento · archivo de composiciones",
      url: "https://www.parlamentodeandalucia.es/webdinamica/portal-web-parlamento/composicionyfuncionamiento/memoriadecomposiciones.do",
    },
    {
      label: "Parlamento · memorias históricas",
      url: "https://www.parlamentodeandalucia.es/memorias",
    },
    {
      label: "Junta · Consejo de Gobierno",
      url: "https://www.juntadeandalucia.es/organismos/transparencia/transparencia-consejo-gobierno/composicion-funciones.html",
    },
    {
      label: "BOJA · archivo de disposiciones",
      url: "https://www.juntadeandalucia.es/boja/",
    },
  ],
};
export default function Andalucia(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
