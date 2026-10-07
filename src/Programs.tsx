import { ArrowUpRight } from "lucide-react";
import { election } from "../Elecciones";
import parties from "../Elecciones/Generales Noviembre 2026/partidos.json";
const assets = import.meta.glob<string>("../Elecciones/Generales Noviembre 2026/logotipos/*", { eager: true, query: "?url", import: "default" });
export default function Programs({ openParty }: { openParty: (id: string) => void }) {
  return <>
    <div className="programs-head"><p>Directorio de partidos · candidaturas de 2026 pendientes de incorporar</p><a href={election.source} target="_blank" rel="noreferrer">Convocatoria · BOE <ArrowUpRight size={15}/></a></div>
    <div className="logo-grid">
      {parties.map(p => <article className={`logo-tile ${["pp","eh-bildu","bng","pacma"].includes(p.id) ? "logo-on-dark" : ""}`} key={p.id}>
        <button className="logo-open" aria-label={`Ficha de ${p.name}`} title={p.fullName} onClick={() => openParty(p.id)}><img src={assets[`../Elecciones/Generales Noviembre 2026/logotipos/${p.logo}`]} alt={p.name}/></button>
        <a className="official-link" href={p.website} aria-label={`Web oficial de ${p.name}`} title={`Web oficial de ${p.name}`} target="_blank" rel="noreferrer"><ArrowUpRight size={17}/></a>
      </article>)}
    </div>
  </>;
}
