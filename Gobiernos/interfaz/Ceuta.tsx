import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  ceutaGovernments,
  ceutaParliaments,
  ceutaGovernmentChronology,
  ceutaParliamentChronology,
} from "./ceuta-model";
const config: RegionalConfig = {
  id: "ceuta",
  name: "Ceuta",
  chamber: "Asamblea de Ceuta",
  board: "Mesa de la Asamblea",
  executive: "Consejo de Gobierno",
  governments: ceutaGovernments,
  parliaments: ceutaParliaments,
  governmentChronology: ceutaGovernmentChronology,
  parliamentChronology: ceutaParliamentChronology,
  sources: [
    {
      label: "Ciudad · Asamblea",
      url: "https://www.ceuta.es/gobiernodeceuta/index.php/el-gobierno/la-asamblea",
    },
    {
      label: "Ciudad · equipo de gobierno",
      url: "https://www.ceuta.es/gobiernodeceuta/index.php/el-gobierno/el-equipo",
    },
    {
      label: "BOCCE · archivo de boletines",
      url: "https://www.ceuta.es/ceuta/component/jdownloads/category/3-bocce",
    },
    {
      label: "Interior · resultados electorales",
      url: "https://infoelectoral.interior.gob.es/",
    },
  ],
};
export default function Ceuta(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
