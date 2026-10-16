import RegionalInstitution, {
  type RegionalConfig,
} from "./RegionalInstitution";
import { galicianInstitutions } from "./galicia-model";
const config: RegionalConfig = {
  id: "galicia",
  name: "Galicia",
  chamber: "Parlamento de Galicia",
  board: "Mesa del Parlamento de Galicia",
  executive: "Consello de la Xunta de Galicia",
  ...galicianInstitutions,
  sources: [
    {
      label: "Parlamento de Galicia · legislaturas anteriores",
      url: "https://www.parlamentodegalicia.es/Composicion/Composicionsanteriores",
    },
    {
      label: "Parlamento de Galicia · Pleno vigente",
      url: "https://www.parlamentodegalicia.es/Composicion/Organos/1200003",
    },
    {
      label: "Parlamento de Galicia · Mesa vigente",
      url: "https://www.parlamentodegalicia.es/Composicion/Organos/1200001/mesa-do-parlamento",
    },
    {
      label: "Xunta · composición del Gobierno",
      url: "https://transparencia.xunta.gal/es/tema/transparencia-institucional/goberno-e-altos-cargos/composicion-do-goberno",
    },
    {
      label: "Senado · nombramientos de las presidencias de Galicia",
      url: "https://www.senado.es/web/conocersenado/biblioteca/dossieresareastematicas/detalle/index.html?id=presidentes_gobiernos_03",
    },
    {
      label: "DOG · proclamación electoral de 2012",
      url: "https://www.xunta.gal/dog/Publicados/2012/20121107/AnuncioG2453-061112-1_gl.pdf",
    },
  ],
};
export default function Galicia(
  props: Omit<Parameters<typeof RegionalInstitution>[0], "config">,
) {
  return <RegionalInstitution {...props} config={config} />;
}
