import { PartyLogo } from "./Logotipo";
import { useState } from "react";
import { ArrowUpRight, Search } from "lucide-react";
import { election, candidacies } from "../../Elecciones";
import { organizations } from "./catalogo";
import type { Organization } from "../../Políticos/interfaz/datos/tipos";
import { useInfiniteList } from "../../src/app/useInfiniteList";
function Tile({
  party,
  openParty,
}: {
  party: Organization;
  openParty: (id: string) => void;
}) {
  return (
    <article
      className={`logo-tile ${party.logoBackground === "dark" || ["pp", "eh-bildu", "bng", "pacma"].includes(party.id) ? "logo-on-dark" : ""}`}
    >
      <button
        className="logo-open"
        aria-label={`Ficha de ${party.name}`}
        title={party.fullName}
        onClick={() => openParty(party.id)}
      >
        <PartyLogo party={party} />
      </button>
      {party.website && (
        <a
          className="official-link"
          href={party.website}
          aria-label={`Web oficial de ${party.name}`}
          title={`Web oficial de ${party.name}`}
          target="_blank"
          rel="noreferrer"
        >
          <ArrowUpRight size={15} />
        </a>
      )}
    </article>
  );
}
export default function Programs({
  openParty,
}: {
  openParty: (id: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [province, setProvince] = useState("all");
  const confirmedIds = new Set(
    (candidacies as { organization: string }[]).map((c) => c.organization),
  );
  const normal = (s: string) =>
    s
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  const provinceOf = (p: Organization) =>
    p.registration?.locality.match(/\(([^()]+)\)$/)?.[1];
  const filtered = organizations.filter(
    (p) =>
      normal(
        `${p.name} ${p.fullName} ${p.registration?.locality ?? ""}`,
      ).includes(normal(query).trim()) &&
      (province === "all" || provinceOf(p) === province),
  );
  const confirmed = filtered.filter((p) => confirmedIds.has(p.id));
  const others = filtered
    .filter((p) => !confirmedIds.has(p.id))
    .sort(
      (a, b) =>
        Number(!!b.logo) - Number(!!a.logo) ||
        a.fullName.localeCompare(b.fullName, "es"),
    );
  const { visibleCount, sentinel } = useInfiniteList(
    others.length,
    `${query}|${province}`,
    60,
  );
  return (
    <>
      <div className="programs-head">
        <h2>Candidaturas de esta elección</h2>
        <a href={election.source} target="_blank" rel="noreferrer">
          Convocatoria · BOE <ArrowUpRight size={14} />
        </a>
      </div>
      {confirmed.length ? (
        <div className="logo-grid">
          {confirmed.map((p) => (
            <Tile key={p.id} party={p} openParty={openParty} />
          ))}
        </div>
      ) : (
        <p className="party-directory-note">
          Pendientes de incorporar las listas proclamadas.
        </p>
      )}
      <div className="programs-head other-parties-head">
        <h2>Otros partidos</h2>
        <a
          href="https://servicio.mir.es/nfrontal/webpartido_politico.html"
          target="_blank"
          rel="noreferrer"
        >
          Registro del Interior <ArrowUpRight size={14} />
        </a>
      </div>
      <div className="party-controls">
        <label className="archive-search">
          <Search size={16} />
          <input
            type="search"
            aria-label="Buscar partido"
            placeholder="Buscar partido o localidad"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <select
          aria-label="Filtrar partidos por provincia de inscripción"
          value={province}
          onChange={(e) => setProvince(e.target.value)}
        >
          <option value="all">Todas las provincias</option>
          {[...new Set(organizations.map(provinceOf).filter(Boolean))]
            .sort((a, b) => a!.localeCompare(b!, "es"))
            .map((p) => (
              <option key={p}>{p}</option>
            ))}
        </select>
      </div>
      <p className="party-directory-note">
        La inscripción no acredita actividad actual ni candidatura. Web y
        logotipo se muestran cuando están documentados.
      </p>
      <div className="logo-grid">
        {others.slice(0, visibleCount).map((p) => (
          <Tile key={p.id} party={p} openParty={openParty} />
        ))}
      </div>
      {!others.length && (
        <p className="archive-empty">
          No hay partidos que coincidan con esta búsqueda.
        </p>
      )}
      <div ref={sentinel} className="infinite-sentinel" aria-hidden="true" />
    </>
  );
}
