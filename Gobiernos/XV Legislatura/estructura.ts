// Instantánea de órganos consultada en las fichas oficiales. No inferir su
// permanencia en todo el intervalo de un gabinete ni en gobiernos anteriores.
export const structureSnapshot = {
  observedAt: "2026-10-07",
  department: "robles",
  nodes: [
    {person:"valcarce",name:"María Amparo Valcarce García",role:"Secretaría de Estado de Defensa",parent:"robles",level:2,source:"https://www.defensa.gob.es/ministerio/organigrama/sedef/index.html"},
    {person:"mateos",name:"Adoración Mateos Tejada",role:"Subsecretaría de Defensa",parent:"robles",level:2,source:"https://www.defensa.gob.es/ministerio/organigrama/subdef/index.html"},
    {person:"sanchez-martinez",name:"José Luís Sánchez Martínez",role:"Dirección General de Asuntos Económicos",parent:"valcarce",level:3,source:"https://www.defensa.gob.es/ministerio/organigrama/sedef/digeneco/index.html"},
  ],
};
