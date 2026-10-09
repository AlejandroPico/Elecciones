import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import {
  madridGovernments,
  madridParliaments,
  madridGovernmentChronology,
  madridParliamentChronology,
} from "./madrid-model";
const config: RegionalConfig = {
  id: "madrid",
  name: "Madrid",
  chamber: "Asamblea de Madrid",
  board: "Mesa de la Asamblea",
  executive: "Consejo de Gobierno",
  governments: madridGovernments,
  parliaments: madridParliaments,
  governmentChronology: madridGovernmentChronology,
  parliamentChronology: madridParliamentChronology,
  sources: [
    {
      label: "Asamblea · archivo histórico",
      url: "https://www.asambleamadrid.es/la-asamblea/historia",
    },
    {
      label: "Asamblea · datos abiertos",
      url: "https://ctyp.asambleamadrid.es/web/guest/servicios/datos-abiertos",
    },
    {
      label: "Comunidad de Madrid · equipo de Gobierno",
      url: "https://www.comunidad.madrid/gobierno/equipo-gobierno",
    },
    {
      label: "Comunidad de Madrid · estructura institucional",
      url: "https://www.comunidad.madrid/transparencia/organizacion-recursos/organizacion",
    },
  ],
};
export default function Madrid(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
