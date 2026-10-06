export type Axis = { id: string; name: string; low: string; high: string };
export type Category = {
  id: string;
  name: string;
  description: string;
  axes: [Axis, Axis];
};
export type Question = {
  id: string;
  category: string;
  text: string;
  context: string;
  axis: string;
  direction: 1 | -1;
  type: "scale" | "binary";
};
export const VERSION = "es-generales-2026-demo-1";
export const election = {
  id: "es-generales-2026",
  name: "Generales de España",
  date: "2026-11-29",
  source: "https://www.boe.es/buscar/doc.php?id=BOE-A-2026-20742&lang=es",
  verification:
    "Convocatoria publicada en el BOE el 6 de octubre de 2026. Artículo 2: elecciones el 29 de noviembre.",
};
export const categories: Category[] = [
  {
    id: "economia",
    name: "Economía",
    description: "Mercados, impuestos y gasto público",
    axes: [
      {
        id: "intervencion",
        name: "Intervención pública",
        low: "Decisión de mercado",
        high: "Intervención pública",
      },
      {
        id: "redistribucion",
        name: "Redistribución fiscal",
        low: "Menor redistribución",
        high: "Mayor redistribución",
      },
    ],
  },
  {
    id: "sociedad",
    name: "Sociedad",
    description: "Derechos y decisiones personales",
    axes: [
      {
        id: "autonomia",
        name: "Autonomía personal",
        low: "Mayor restricción",
        high: "Mayor autonomía",
      },
      {
        id: "pluralismo",
        name: "Pluralismo cultural",
        low: "Modelo común",
        high: "Diversidad de modelos",
      },
    ],
  },
  {
    id: "trabajo",
    name: "Trabajo",
    description: "Empleo y relaciones laborales",
    axes: [
      {
        id: "proteccion",
        name: "Protección laboral",
        low: "Flexibilidad contractual",
        high: "Protección laboral",
      },
      {
        id: "negociacion",
        name: "Negociación colectiva",
        low: "Acuerdos individuales",
        high: "Acuerdos colectivos",
      },
    ],
  },
  {
    id: "servicios",
    name: "Servicios públicos",
    description: "Sanidad, educación y cuidados",
    axes: [
      {
        id: "provision",
        name: "Provisión pública",
        low: "Provisión privada",
        high: "Provisión pública",
      },
      {
        id: "universalidad",
        name: "Acceso universal",
        low: "Ayudas focalizadas",
        high: "Acceso universal",
      },
    ],
  },
  {
    id: "vivienda",
    name: "Vivienda",
    description: "Alquiler y desarrollo urbano",
    axes: [
      {
        id: "regulacion",
        name: "Regulación de vivienda",
        low: "Menor regulación",
        high: "Mayor regulación",
      },
      {
        id: "urbanismo",
        name: "Planificación urbana",
        low: "Expansión urbana",
        high: "Ciudad compacta",
      },
    ],
  },
  {
    id: "medioambiente",
    name: "Medioambiente",
    description: "Energía, clima y territorio",
    axes: [
      {
        id: "transicion",
        name: "Transición ambiental",
        low: "Transición gradual",
        high: "Transición acelerada",
      },
      {
        id: "conservacion",
        name: "Conservación natural",
        low: "Uso productivo",
        high: "Conservación natural",
      },
    ],
  },
  {
    id: "exterior",
    name: "Relaciones exteriores",
    description: "Cooperación y decisiones internacionales",
    axes: [
      {
        id: "integracion",
        name: "Integración internacional",
        low: "Decisión nacional",
        high: "Decisión compartida",
      },
      {
        id: "defensa",
        name: "Capacidad de defensa",
        low: "Menor gasto militar",
        high: "Mayor gasto militar",
      },
    ],
  },
  {
    id: "instituciones",
    name: "Instituciones",
    description: "Representación y organización territorial",
    axes: [
      {
        id: "participacion",
        name: "Participación directa",
        low: "Representación parlamentaria",
        high: "Participación directa",
      },
      {
        id: "descentralizacion",
        name: "Descentralización",
        low: "Competencias estatales",
        high: "Competencias territoriales",
      },
    ],
  },
];
// Banco piloto: estas formulaciones y sus ejes necesitan revisión editorial antes
// de presentarse como un instrumento validado o compararse con programas reales.
const bank: Record<string, [string, string, 1 | -1, string, "binary"?][]> = {
  economia: [
    [
      "intervencion",
      "El Estado debería limitar el precio de bienes básicos en periodos de inflación elevada.",
      1,
      "Piensa en una medida temporal sobre productos de primera necesidad.",
    ],
    [
      "intervencion",
      "Los precios de la electricidad deberían fijarse mediante la competencia entre empresas.",
      -1,
      "La afirmación se refiere a cómo fijar los precios, no a las ayudas a los hogares.",
    ],
    [
      "intervencion",
      "El Estado debería participar en la propiedad de empresas de sectores estratégicos.",
      1,
      "Por ejemplo, energía o infraestructuras; no se plantea la propiedad de todas las empresas.",
    ],
    [
      "redistribucion",
      "Las rentas más altas deberían aportar una proporción mayor de sus ingresos en impuestos.",
      1,
      "Valora la progresividad del impuesto, sin asumir un tipo concreto.",
    ],
    [
      "redistribucion",
      "Las herencias deberían quedar exentas de impuestos con independencia de su importe.",
      -1,
      "La propuesta se refiere al impuesto sobre la herencia, no a otros impuestos.",
    ],
    [
      "redistribucion",
      "El gasto en prestaciones sociales debería aumentar aunque requiera una mayor recaudación.",
      1,
      "Considera conjuntamente el aumento del gasto y su financiación.",
    ],
  ],
  sociedad: [
    [
      "autonomia",
      "La interrupción voluntaria del embarazo debería permitirse por decisión de la mujer durante las primeras 14 semanas.",
      1,
      "La pregunta se limita al plazo indicado; no aborda los supuestos médicos posteriores.",
    ],
    [
      "autonomia",
      "Una persona adulta con una enfermedad incurable debería poder solicitar ayuda médica para morir, con controles legales.",
      1,
      "Se plantea una decisión voluntaria con verificación médica y legal.",
    ],
    [
      "autonomia",
      "El consumo personal de cannabis por adultos debería estar prohibido.",
      -1,
      "La afirmación no se refiere a conducir bajo sus efectos ni al consumo por menores.",
    ],
    [
      "pluralismo",
      "Los centros públicos deberían ofrecer un espacio para la enseñanza de distintas confesiones religiosas.",
      1,
      "Valora la oferta de enseñanza voluntaria, no la obligatoriedad de asistir.",
    ],
    [
      "pluralismo",
      "Las parejas del mismo sexo deberían tener los mismos derechos de adopción que las demás parejas.",
      1,
      "Se mantienen los mismos requisitos de idoneidad para todas las personas solicitantes.",
      "binary",
    ],
    [
      "pluralismo",
      "Las administraciones deberían atender en las lenguas cooficiales del territorio cuando lo solicite la ciudadanía.",
      1,
      "La afirmación se refiere a los territorios donde existe cooficialidad.",
    ],
  ],
  trabajo: [
    [
      "proteccion",
      "La indemnización por despido debería aumentar para los contratos indefinidos.",
      1,
      "Piensa en la regla general, sin fijar un número concreto de días.",
    ],
    [
      "proteccion",
      "Las empresas deberían tener mayor libertad para utilizar contratos temporales.",
      -1,
      "Valora la contratación temporal en general, sin referirse a un sector específico.",
    ],
    [
      "proteccion",
      "La jornada laboral máxima debería reducirse sin disminuir el salario mensual.",
      1,
      "La propuesta mantiene el salario y reduce el límite de horas.",
    ],
    [
      "negociacion",
      "Los convenios sectoriales deberían fijar condiciones mínimas para todas las empresas del sector.",
      1,
      "Se refiere a mínimos negociados colectivamente.",
    ],
    [
      "negociacion",
      "El salario debería pactarse exclusivamente entre cada trabajador y su empresa.",
      -1,
      "Valora el papel del acuerdo individual frente a la negociación colectiva.",
    ],
    [
      "negociacion",
      "Los representantes de los trabajadores deberían participar en las decisiones sobre reorganizaciones de plantilla.",
      1,
      "No se presupone un derecho de veto.",
    ],
  ],
  servicios: [
    [
      "provision",
      "La atención sanitaria financiada por el Estado debería prestarse principalmente en centros de gestión pública.",
      1,
      "Distingue quién financia el servicio de quién lo gestiona.",
    ],
    [
      "provision",
      "Las familias deberían poder utilizar la financiación educativa pública en centros privados de su elección.",
      -1,
      "La propuesta contempla trasladar la financiación al centro elegido.",
    ],
    [
      "provision",
      "La gestión de las residencias financiadas públicamente debería ser principalmente pública.",
      1,
      "Se refiere a la gestión, sin cambiar los criterios de acceso.",
    ],
    [
      "universalidad",
      "La educación de cero a tres años debería ser gratuita para todas las familias.",
      1,
      "Considera una oferta financiada con recursos públicos.",
    ],
    [
      "universalidad",
      "Las ayudas para cuidados de larga duración deberían reservarse a las personas con menos recursos.",
      -1,
      "Se compara el acceso por renta con una prestación universal.",
    ],
    [
      "universalidad",
      "La atención odontológica básica debería incluirse en la cobertura sanitaria pública para toda la población.",
      1,
      "La pregunta no incluye tratamientos exclusivamente estéticos.",
    ],
  ],
  vivienda: [
    [
      "regulacion",
      "En zonas con alta demanda, debería establecerse un límite legal al precio del alquiler.",
      1,
      "Valora la regulación del precio, no otras medidas de vivienda.",
    ],
    [
      "regulacion",
      "Los propietarios deberían poder destinar una vivienda a alquiler turístico sin autorización específica.",
      -1,
      "Se mantienen las obligaciones fiscales y de seguridad generales.",
    ],
    [
      "regulacion",
      "Las viviendas que permanezcan vacías durante largos periodos deberían pagar un recargo fiscal.",
      1,
      "Piensa en vivienda habitable, excluyendo obras y causas justificadas.",
    ],
    [
      "urbanismo",
      "Las ciudades deberían priorizar la construcción en suelo ya urbanizado frente a nuevos desarrollos periféricos.",
      1,
      "La propuesta compara dos formas de ampliar la oferta.",
    ],
    [
      "urbanismo",
      "Debería ampliarse el suelo residencial en la periferia para facilitar la construcción de viviendas.",
      -1,
      "Valora la expansión urbana como política general.",
    ],
    [
      "urbanismo",
      "La planificación urbana debería concentrar vivienda y servicios alrededor del transporte público.",
      1,
      "Se refiere a la distribución de nuevos desarrollos.",
    ],
  ],
  medioambiente: [
    [
      "transicion",
      "El calendario de reducción de emisiones debería acelerarse aunque aumente los costes a corto plazo.",
      1,
      "Considera el ritmo de transición y sus costes.",
    ],
    [
      "transicion",
      "Las restricciones a vehículos contaminantes deberían aplazarse hasta que existan alternativas asequibles para todos los hogares.",
      -1,
      "Valora la condición para aplicar las restricciones.",
    ],
    [
      "transicion",
      "Las subvenciones públicas deberían priorizar las energías renovables frente a los combustibles fósiles.",
      1,
      "La afirmación compara el destino de subvenciones, no la prohibición de tecnologías.",
    ],
    [
      "conservacion",
      "La protección de espacios naturales debería prevalecer sobre nuevos proyectos productivos en esos espacios.",
      1,
      "Se refiere a proyectos que afectan a un espacio protegido.",
    ],
    [
      "conservacion",
      "Debería permitirse ampliar el regadío incluso si reduce el caudal de los ríos.",
      -1,
      "Considera el equilibrio entre producción agrícola y caudal.",
    ],
    [
      "conservacion",
      "La protección de especies amenazadas debería limitar las actividades económicas que comprometan su conservación.",
      1,
      "La limitación se vincula a un impacto demostrado sobre la especie.",
    ],
  ],
  exterior: [
    [
      "integracion",
      "La Unión Europea debería asumir más competencias en política económica.",
      1,
      "Valora el reparto de competencias, no una medida económica particular.",
    ],
    [
      "integracion",
      "España debería decidir su política migratoria sin acuerdos vinculantes con otros países europeos.",
      -1,
      "Se compara la decisión nacional con la decisión compartida.",
    ],
    [
      "integracion",
      "Las decisiones internacionales sobre clima deberían ser vinculantes para los países que las suscriban.",
      1,
      "La obligación se aplicaría a acuerdos aceptados por cada país.",
    ],
    [
      "defensa",
      "España debería aumentar el presupuesto destinado a defensa.",
      1,
      "No se fija un porcentaje ni una operación militar concreta.",
    ],
    [
      "defensa",
      "Parte del presupuesto militar debería trasladarse a cooperación internacional.",
      -1,
      "Valora este cambio de destino del gasto.",
    ],
    [
      "defensa",
      "España debería financiar más capacidades militares comunes con sus aliados.",
      1,
      "Se refiere a capacidades compartidas, no a una intervención concreta.",
    ],
  ],
  instituciones: [
    [
      "participacion",
      "Las decisiones políticas de especial relevancia deberían someterse a referéndum.",
      1,
      "Valora el uso de consultas, respetando las garantías del proceso.",
    ],
    [
      "participacion",
      "Las decisiones legislativas deberían corresponder exclusivamente a los representantes elegidos.",
      -1,
      "La afirmación excluye mecanismos de decisión ciudadana directa.",
    ],
    [
      "participacion",
      "La ciudadanía debería poder impulsar consultas vinculantes reuniendo un número suficiente de firmas.",
      1,
      "No se fija aquí el umbral de firmas.",
    ],
    [
      "descentralizacion",
      "Las comunidades autónomas deberían tener más capacidad para decidir sus impuestos.",
      1,
      "Se refiere al reparto territorial de competencias fiscales.",
    ],
    [
      "descentralizacion",
      "Las competencias educativas deberían concentrarse en el Gobierno central.",
      -1,
      "Valora quién toma las decisiones, no el contenido educativo.",
    ],
    [
      "descentralizacion",
      "Los municipios deberían disponer de mayor autonomía para gestionar sus recursos.",
      1,
      "Considera el nivel municipal dentro de la organización territorial.",
    ],
  ],
};
export const questions: Question[] = categories.flatMap((c) =>
  bank[c.id].map(([axis, text, direction, context, type], i) => ({
    id: `${c.id}-${i + 1}`,
    category: c.id,
    text,
    context,
    axis,
    direction,
    type: type ?? "scale",
  })),
);
