import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  catalanGovernments,
  catalanParliaments,
  catalanGovernmentChronology,
  catalanParliamentChronology,
} from "./catalonia-model";
const config: RegionalConfig = {
  id: "cataluna",
  name: "Cataluña",
  chamber: "Parlament de Catalunya",
  board: "Mesa del Parlament",
  executive: "Consell Executiu",
  governments: catalanGovernments,
  parliaments: catalanParliaments,
  governmentChronology: catalanGovernmentChronology,
  parliamentChronology: catalanParliamentChronology,
  sources: [
    {
      label: "Parlament · archivo de legislaturas",
      url: "https://www.parlament.cat/web/composicio/legislatures-anteriors/index.html",
    },
    {
      label: "Parlament · dossier histórico de gobiernos",
      url: "https://www.parlament.cat/web/documentacio/recursos-documentals/dossiers-tematics/sumari/index.html?p_id=DOSSIER_TEMATIC_02",
    },
  ],
  governmentNote:
    "Las medidas del artículo 155 se aplicaron tras el cese de octubre de 2017. El gabinete de Torra fue nombrado el 29 de mayo de 2018 y tomó posesión el 2 de junio; el cuadro distingue el nombramiento de la restitución efectiva.",
};
export default function Catalonia(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
