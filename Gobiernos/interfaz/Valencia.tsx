import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  valenciaGovernments,
  valenciaParliaments,
  valenciaGovernmentChronology,
  valenciaParliamentChronology,
} from "./valencia-model";
const config: RegionalConfig = {
  id: "valencia",
  name: "Comunitat Valenciana",
  chamber: "Les Corts Valencianes",
  board: "Mesa de Les Corts",
  executive: "Consell de la Generalitat",
  governments: valenciaGovernments,
  parliaments: valenciaParliaments,
  governmentChronology: valenciaGovernmentChronology,
  parliamentChronology: valenciaParliamentChronology,
  sources: [
    {
      label: "Les Corts · diputados y diputadas",
      url: "https://www.cortsvalencianes.es/es/composicion/diputados",
    },
    {
      label: "Les Corts · archivo histórico de retratos y cargos",
      url: "https://www.cortsvalencianes.es/sites/default/files/publication_book/doc/Semblants_0.pdf.pdf",
    },
    {
      label: "Generalitat · Consell",
      url: "https://www.gva.es/es/web/generalitat/el-consell",
    },
    {
      label: "DOGV · nombramientos del Consell",
      url: "https://dogv.gva.es/datos/2025/12/03/pdf/2025_49244_es.pdf",
    },
  ],
};
export default function Valencia(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
