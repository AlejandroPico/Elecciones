import { useState } from "react";
import { ArrowUpRight, Download } from "lucide-react";
import { organizations } from "../../../Partidos/interfaz/catalogo";
import { PartyLogo } from "../../../Partidos/interfaz/Logotipo";
import { normalizeParty } from "../../../Partidos/interfaz/orden";
import {
  documentUrl,
  documentsFor,
  electionResearch,
  matchesScope,
  participationLabels,
} from "./catalogo";
import "./candidaturas.css";

export default function ElectionDirectory({
  openParty,
  query,
}: {
  openParty: (id: string) => void;
  query: string;
}) {
  const [chamber, setChamber] = useState("all");
  const [province, setProvince] = useState("all");
  const [showAgreements, setShowAgreements] = useState(false);
  const entries = electionResearch.entries.filter(
    (entry) => entry.status !== "not-running",
  );
  const options = [
    ...new Set(
      entries.flatMap((entry) =>
        entry.scope.flatMap((scope) => scope.provinces),
      ),
    ),
  ].sort((a, b) => a.localeCompare(b, "es"));
  const filtered = entries.filter(
    (entry) =>
      normalizeParty(
        `${entry.name} ${organizations.find((party) => party.id === entry.organization)?.fullName ?? ""} ${entry.candidates.map((candidate) => candidate.name).join(" ")}`,
      ).includes(normalizeParty(query).trim()) &&
      matchesScope(entry, chamber, province) &&
      (showAgreements || entry.status !== "agreement"),
  );
  return (
    <section
      className="election-directory"
      aria-label="Investigación de candidaturas"
    >
      <div className="election-directory-heading">
        <h2>Generales · 29 de noviembre de 2026</h2>
        <a
          href={electionResearch.officialSource}
          target="_blank"
          rel="noreferrer"
        >
          JEC
          <ArrowUpRight size={13} />
        </a>
      </div>
      <p className="election-status-note">
        Anuncios y acuerdos · listas todavía sin proclamar. Las papeletas
        definitivas varían por circunscripción y cámara.
      </p>
      <div className="election-directory-filters">
        <select
          aria-label="Cámara de la candidatura"
          value={chamber}
          onChange={(event) => setChamber(event.target.value)}
        >
          <option value="all">Congreso y Senado</option>
          <option value="congreso">Congreso</option>
          <option value="senado">Senado</option>
        </select>
        <select
          aria-label="Circunscripción anunciada"
          value={province}
          onChange={(event) => setProvince(event.target.value)}
        >
          <option value="all">Todos los ámbitos anunciados</option>
          {options.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
        <label>
          <input
            type="checkbox"
            checked={showAgreements}
            onChange={(event) => setShowAgreements(event.target.checked)}
          />
          Incluir acuerdos territoriales
        </label>
      </div>
      {province !== "all" && (
        <p className="small-note">
          Se muestran menciones expresas a esta circunscripción; los anuncios
          sin reparto provincial siguen pendientes de cotejo. Este filtro no
          certifica las papeletas disponibles.
        </p>
      )}
      <div className="election-cards">
        {filtered.map((entry) => {
          const party = organizations.find(
            (organization) => organization.id === entry.organization,
          );
          if (!party) return null;
          const documents = documentsFor(entry.organization);
          const general = documents.find(
            (document) => document.kind !== "historical",
          );
          const historical = documents.find(
            (document) => document.kind === "historical",
          );
          return (
            <article key={entry.id}>
              <button
                className={`election-card-brand ${party.logoBackground === "light" ? "on-light" : party.logoBackground === "dark" || ["pp", "eh-bildu", "bng", "pacma"].includes(party.id) ? "on-dark" : ""}`}
                onClick={() => openParty(party.id)}
                aria-label={`Ficha de ${entry.name}`}
              >
                <PartyLogo party={party} />
              </button>
              {(entry.status === "agreement" ||
                entry.id === "cc-primero-canarias") && (
                <span className="election-mark-caption">
                  Marca de {party.name}
                </span>
              )}
              <h3>
                <button onClick={() => openParty(party.id)}>
                  {entry.name}
                </button>
              </h3>
              <p className="election-card-status">
                {participationLabels[entry.status]}
              </p>
              <p className="election-card-candidate">
                {entry.candidates.length
                  ? entry.candidates
                      .map((candidate) => candidate.name)
                      .join(" · ")
                  : "Cabeceras pendientes de incorporar"}
              </p>
              <p className="election-card-scope">
                {entry.scope
                  .map(
                    (scope) =>
                      `${scope.chamber === "unknown" ? "Cámara por cotejar" : scope.chamber === "congreso" ? "Congreso" : "Senado"} · ${scope.territory}`,
                  )
                  .join(" / ")}
              </p>
              <div className="election-card-links">
                <button onClick={() => openParty(party.id)}>
                  Ficha y fuentes
                </button>
                {party.website && (
                  <a
                    href={party.website}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={`Web oficial de ${entry.name}`}
                  >
                    <ArrowUpRight size={14} />
                  </a>
                )}
              </div>
              {general ? (
                <>
                  <a
                    className="election-card-download"
                    href={documentUrl(general)}
                    download
                  >
                    <Download size={13} />
                    {general.kind === "permanent"
                      ? "Propuesta permanente"
                      : general.kind === "territorial"
                        ? `Autonómicas · ${"territory" in general ? general.territory : ""} ${general.electionDate?.slice(0, 4) ?? ""}`
                        : "Documento general"}{" "}
                    · {general.format}
                  </a>
                  {general.kind === "territorial" && (
                    <span className="election-program-pending">
                      Programa nacional todavía no localizado
                    </span>
                  )}
                </>
              ) : historical ? (
                <a
                  className="election-card-download"
                  href={documentUrl(historical)}
                  download
                >
                  <Download size={13} />
                  Antecedente {historical.electionDate?.slice(0, 4)} ·{" "}
                  {historical.format}
                </a>
              ) : (
                <span className="election-program-pending">
                  Programa por incorporar
                </span>
              )}
            </article>
          );
        })}
      </div>
      {!filtered.length && (
        <p className="small-note">
          No hay anuncios incorporados que coincidan con estos filtros.
        </p>
      )}
      <details className="election-coverage">
        <summary>Calendario y alcance de la revisión</summary>
        <p>{electionResearch.coverage}</p>
        <ul>
          {electionResearch.nextSteps.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ul>
        <p>
          Una coalición constituida no es una lista proclamada. Las agrupaciones
          y partidos sin representación también pueden concurrir; su presencia
          depende de los requisitos y de las listas oficiales. El directorio
          inferior incluye organizaciones sin candidatura acreditada.
        </p>
        {electionResearch.entries
          .filter((entry) => entry.status === "not-running")
          .map((entry) => (
            <p key={entry.id}>
              <strong>{entry.name}</strong>: {entry.note}{" "}
              <a href={entry.sources[0].url} target="_blank" rel="noreferrer">
                Fuente
                <ArrowUpRight size={12} />
              </a>
            </p>
          ))}
        <a
          href={electionResearch.officialSource}
          target="_blank"
          rel="noreferrer"
        >
          Candidaturas · JEC
          <ArrowUpRight size={13} />
        </a>
      </details>
    </section>
  );
}
