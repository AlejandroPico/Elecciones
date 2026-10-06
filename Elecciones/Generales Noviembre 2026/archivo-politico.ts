import sanchezPortrait from "./retratos/sanchez.jpg";
import feijooPortrait from "./retratos/feijoo.jpg";
import roblesPortrait from "./retratos/robles.jpg";
import rajoyPortrait from "./retratos/rajoy.jpg";
import cospedalPortrait from "./retratos/cospedal.jpg";
import morenesPortrait from "./retratos/morenes.jpg";
export const portraits: Record<string, string> = {
  "sanchez.jpg": sanchezPortrait,
  "feijoo.jpg": feijooPortrait,
  "robles.jpg": roblesPortrait,
  "rajoy.jpg": rajoyPortrait,
  "cospedal.jpg": cospedalPortrait,
  "morenes.jpg": morenesPortrait,
};
export type Reference = { label: string; url: string };
export type Person = {
  id: string;
  name: string;
  initials: string;
  organization: string | null;
  relation: string;
  role: string;
  portrait?: string;
  photoCredit?: string;
  photoSource?: string;
  summary: string;
  timeline: { period: string; title: string; source: Reference }[];
  offices: string[];
  references: Reference[];
};
export type Organization = {
  id: string;
  name: string;
  fullName: string;
  foundation: string;
  summary: string;
  references: Reference[];
  documents: { title: string; election: string; url: string }[];
  history: { period: string; title: string; person?: string }[];
};
export const reviewedAt = "6 de octubre de 2026";
const moncloa = (slug: string) => `https://www.lamoncloa.gob.es/${slug}`;
const sanchezBio = {
  label: "La Moncloa · Biografía de Pedro Sánchez",
  url: moncloa("presidente/biografia/Paginas/index.aspx"),
};
const rajoyBio = {
  label: "La Moncloa · Archivo de Mariano Rajoy",
  url: moncloa("presidente/presidentes/paginas/marianorajoy_bio.aspx"),
};
const roblesBio = {
  label: "La Moncloa · Biografía de Margarita Robles",
  url: moncloa(
    "gobierno/paginas/biografias-xv-legislatura/ministra-margarita-robles.aspx",
  ),
};
const cospedalRef = {
  label: "Defensa · Toma de posesión, 4 de noviembre de 2016",
  url: "https://www.defensa.gob.es/gabinete/notasPrensa/2016/11/DGC-161104-toma-posesion-ministra.html",
};
const morenesRef = {
  label: "Defensa · Toma de posesión, diciembre de 2011",
  url: "https://www.defensa.gob.es/gabinete/multimedia/fototeca/2011/12/DGC_111222_Toma_Posesion_02.html",
};
const ppHistory = {
  label: "PP · Historia publicada por el partido",
  url: "https://www.pp.es/historia/",
};
const psoeHistory = {
  label: "PSOE · Historia publicada por el partido",
  url: "https://www.psoe.es/conocenos/historia/",
};
export const people: Person[] = [
  {
    id: "sanchez",
    name: "Pedro Sánchez",
    initials: "PS",
    organization: "psoe",
    relation: "PSOE",
    role: "Presidente del Gobierno desde 2018",
    portrait: "sanchez.jpg",
    photoCredit: "Pool Moncloa · Carlos Spottorno de las Morenas",
    photoSource: sanchezBio.url,
    summary:
      "Economista y secretario general del PSOE. Llegó a la Presidencia del Gobierno en junio de 2018, tras una moción de censura. Su trayectoria anterior incluye el Congreso de los Diputados y el Ayuntamiento de Madrid.",
    timeline: [
      {
        period: "2018–actualidad",
        title: "Presidencia del Gobierno de España",
        source: sanchezBio,
      },
      {
        period: "2014–2016",
        title: "Secretaría general del PSOE y liderazgo de la oposición",
        source: sanchezBio,
      },
      {
        period: "Etapa anterior",
        title: "Diputado por Madrid y concejal del Ayuntamiento de Madrid",
        source: sanchezBio,
      },
    ],
    offices: ["presidencia"],
    references: [
      sanchezBio,
      {
        label: "BOE · Nombramiento de 2018",
        url: "https://boe.es/diario_boe/txt.php?id=BOE-A-2018-7400",
      },
    ],
  },
  {
    id: "feijoo",
    name: "Alberto Núñez Feijóo",
    initials: "AF",
    organization: "pp",
    relation: "Partido Popular",
    role: "Presidente del Partido Popular desde 2022",
    portrait: "feijoo.jpg",
    photoCredit: "Senado de España · fotografía de la XIV legislatura",
    photoSource:
      "https://www.senado.es/web/composicionorganizacion/senadores/composicionsenado/fichasenador/index.html?id1=19746&lang=es_ES&legis=14",
    summary:
      "Presidente del Partido Popular desde 2022. La ficha de la XV legislatura del Congreso lo registra como diputado por Madrid. El retrato procede de su etapa en el Senado.",
    timeline: [
      {
        period: "Desde 2023",
        title: "Diputado por Madrid en la XV legislatura",
        source: {
          label: "Congreso · Ficha de la XV legislatura",
          url: "https://www.congreso.es/es/busqueda-de-diputados?codParlamentario=346&idLegislatura=XV&mostrarFicha=true",
        },
      },
      {
        period: "Desde 2022",
        title: "Presidencia del Partido Popular",
        source: ppHistory,
      },
    ],
    offices: [],
    references: [
      ppHistory,
      {
        label: "Congreso · Actividad y ficha parlamentaria",
        url: "https://www.congreso.es/es/busqueda-de-diputados?codParlamentario=346&idLegislatura=XV&mostrarFicha=true",
      },
    ],
  },
  {
    id: "robles",
    name: "Margarita Robles",
    initials: "MR",
    organization: null,
    relation: "Gobierno de España",
    role: "Ministra de Defensa desde 2018",
    portrait: "robles.jpg",
    photoCredit: "Pool Moncloa · retrato institucional de 2023",
    photoSource: roblesBio.url,
    summary:
      "Jurista y ministra de Defensa desde junio de 2018. Antes de su etapa ministerial desarrolló su carrera en la judicatura, incluido el Tribunal Supremo. La ficha distingue el cargo público de la afiliación a un partido.",
    timeline: [
      {
        period: "2018–actualidad",
        title: "Ministerio de Defensa",
        source: roblesBio,
      },
      {
        period: "2004",
        title: "Nombramiento como magistrada del Tribunal Supremo",
        source: {
          label: "La Moncloa · Biografías del Gobierno de 2018",
          url: moncloa(
            "gobierno/Documents/06062018_Biografi%CC%81asGabinete2.pdf",
          ),
        },
      },
    ],
    offices: ["defensa"],
    references: [
      roblesBio,
      {
        label: "Ministerio de Defensa · Organigrama",
        url: "https://www.defensa.gob.es/ministerio/organigrama/ministra/index.html",
      },
    ],
  },
  {
    id: "rajoy",
    name: "Mariano Rajoy",
    initials: "MR",
    organization: "pp",
    relation: "Partido Popular",
    role: "Presidente del Gobierno · 2011–2018",
    portrait: "rajoy.jpg",
    photoCredit: "La Moncloa · archivo de presidentes",
    photoSource: moncloa("presidente/presidentes/Paginas/index.aspx"),
    summary:
      "Registrador de la propiedad y expresidente del Gobierno. Presidió el Ejecutivo entre diciembre de 2011 y junio de 2018. Con anterioridad fue ministro y vicepresidente del Gobierno, y presidente del Partido Popular.",
    timeline: [
      {
        period: "2011–2018",
        title: "Presidencia del Gobierno de España",
        source: rajoyBio,
      },
      {
        period: "2004",
        title: "Elegido presidente del Partido Popular",
        source: rajoyBio,
      },
      {
        period: "1996–2003",
        title: "Cargos ministeriales y vicepresidencia del Gobierno",
        source: rajoyBio,
      },
    ],
    offices: ["presidencia"],
    references: [rajoyBio, ppHistory],
  },
  {
    id: "cospedal",
    name: "María Dolores de Cospedal",
    initials: "MC",
    organization: "pp",
    relation: "Partido Popular",
    role: "Ministra de Defensa · 2016–2018",
    portrait: "cospedal.jpg",
    photoCredit: "Senado de España · fotografía de la IX legislatura",
    photoSource:
      "https://www.senado.es/web/composicionorganizacion/senadores/composicionsenado/fichasenador/index.html?id1=13305&legis=9",
    summary:
      "Ocupó el Ministerio de Defensa durante el segundo Gobierno de Mariano Rajoy. La secuencia de titulares permite pasar de su ficha a la de su antecesor, Pedro Morenés, y a la de su sucesora, Margarita Robles.",
    timeline: [
      {
        period: "2016–2018",
        title: "Ministerio de Defensa; toma de posesión en noviembre de 2016",
        source: cospedalRef,
      },
    ],
    offices: ["defensa"],
    references: [cospedalRef, roblesBio],
  },
  {
    id: "morenes",
    name: "Pedro Morenés",
    initials: "PM",
    organization: null,
    relation: "Gobierno de Mariano Rajoy",
    role: "Ministro de Defensa · 2011–2016",
    portrait: "morenes.jpg",
    photoCredit:
      "Ministerio de Defensa de España · acto de toma de posesión, 2011",
    photoSource: morenesRef.url,
    summary:
      "Ministro de Defensa en el primer Gobierno de Mariano Rajoy. Tomó posesión en diciembre de 2011 y fue sucedido por María Dolores de Cospedal en noviembre de 2016. La imagen muestra el acto institucional de toma de posesión.",
    timeline: [
      {
        period: "2011–2016",
        title: "Ministerio de Defensa",
        source: morenesRef,
      },
    ],
    offices: ["defensa"],
    references: [morenesRef, cospedalRef],
  },
];
export const organizations: Organization[] = [
  {
    id: "psoe",
    name: "PSOE",
    fullName: "Partido Socialista Obrero Español",
    foundation: "2 de mayo de 1879",
    summary:
      "Partido fundado en Madrid en 1879. Esta ficha reúne referencias a su historia, documentación electoral y personas incorporadas al archivo. Los textos del propio partido se identifican como tales.",
    references: [
      psoeHistory,
      {
        label: "PSOE · Archivo de programas electorales",
        url: "https://www.psoe.es/transparencia/informacion-politica-organizativa/programa/",
      },
    ],
    documents: [
      {
        title: "Programa de elecciones generales · 2023",
        election: "23 de julio de 2023 · documento histórico",
        url: "https://www.psoe.es/media-content/2023/07/PROGRAMA_ELECTORAL-GENERALES-2023.pdf",
      },
    ],
    history: [
      {
        period: "1879",
        title: "Fundación en Madrid, impulsada por Pablo Iglesias Posse",
      },
      {
        period: "2014–2016",
        title: "Pedro Sánchez · secretaría general",
        person: "sanchez",
      },
      {
        period: "Desde 2018",
        title: "Pedro Sánchez · Presidencia del Gobierno",
        person: "sanchez",
      },
    ],
  },
  {
    id: "pp",
    name: "PP",
    fullName: "Partido Popular",
    foundation: "1989 · refundación de Alianza Popular",
    summary:
      "El Partido Popular se constituyó con esa denominación en 1989 tras la refundación de Alianza Popular. La ficha enlaza su archivo de programas y una selección de personas y etapas verificadas.",
    references: [
      ppHistory,
      {
        label: "PP · Archivo de programas electorales",
        url: "https://www.pp.es/categoria/programa-electoral/",
      },
    ],
    documents: [
      {
        title: "Programa de elecciones generales · 2023",
        election: "23 de julio de 2023 · documento histórico",
        url: "https://www.pp.es/wp-content/uploads/2023/07/programa_electoral_pp_23j_feijoo_2023.pdf",
      },
    ],
    history: [
      {
        period: "1989",
        title: "Refundación de Alianza Popular como Partido Popular",
      },
      {
        period: "2004",
        title: "Mariano Rajoy · elegido presidente del partido",
        person: "rajoy",
      },
      {
        period: "2011–2018",
        title: "Mariano Rajoy · Presidencia del Gobierno",
        person: "rajoy",
      },
      {
        period: "Desde 2022",
        title: "Alberto Núñez Feijóo · Presidencia del partido",
        person: "feijoo",
      },
    ],
  },
];
export const offices = [
  {
    id: "presidencia",
    name: "Presidencia del Gobierno",
    description:
      "Secuencia reciente de titulares. No incluye todavía todos los presidentes del archivo histórico.",
    members: [
      { person: "sanchez", period: "2018–actualidad" },
      { person: "rajoy", period: "2011–2018" },
    ],
    source: {
      label: "La Moncloa · Relación cronológica completa",
      url: moncloa("presidente/presidentes-desde-1823/Paginas/index.aspx"),
    },
  },
  {
    id: "defensa",
    name: "Ministerio de Defensa",
    description:
      "Secuencia reciente de titulares. Los periodos se muestran por año; las fuentes detallan los nombramientos.",
    members: [
      { person: "robles", period: "2018–actualidad" },
      { person: "cospedal", period: "2016–2018" },
      { person: "morenes", period: "2011–2016" },
    ],
    source: {
      label: "Ministerio de Defensa · Organigrama y archivo",
      url: "https://www.defensa.gob.es/ministerio/organigrama/ministra/index.html",
    },
  },
];
export type Candidacy = {
  personId: string;
  organizationId: string;
  electionId: string;
  chamber: "congreso" | "senado";
  district: string;
  position: number;
  substitute: boolean;
  proclamationSource: string;
};
// Las fichas biográficas no acreditan candidatura. Se incorporará cada fila desde
// una proclamación oficial y no desde la jerarquía del partido o un cargo previo.
export const candidacies: Candidacy[] = [];
