import { ArrowUpRight, Download, FileText } from "lucide-react";
import {
  documentUrl,
  documentsFor,
  participationFor,
  participationLabels,
} from "./catalogo";
import "./candidaturas.css";
import research from "../../../Cuestionario/cobertura.json";

export default function ElectionDocuments({
  organization,
}: {
  organization: string;
}) {
  const documents = documentsFor(organization);
  const territorialDocuments = documents.filter(
    (document) => document.kind === "territorial",
  );
  const availableDocuments = documents.filter(
    (document) =>
      document.kind === "territorial" ||
      document.kind === "historical" ||
      document.analysis === "editorial-draft",
  );
  const entries = participationFor(organization);
  if (!documents.length && !entries.length) return null;
  return (
    <section className="election-documents">
      {!!entries.length && (
        <>
          <h3>Generales · 29 de noviembre de 2026</h3>
          {entries.map((entry) => (
            <details key={entry.id} className="participation-detail">
              <summary>
                {entry.name} · {participationLabels[entry.status]}
              </summary>
              {entry.scope.map((scope, index) => (
                <p key={index}>
                  {scope.chamber === "unknown"
                    ? "Cámara por cotejar"
                    : scope.chamber === "congreso"
                      ? "Congreso"
                      : "Senado"}{" "}
                  · {scope.territory}
                </p>
              ))}
              {entry.candidates.map((candidate) => (
                <p key={`${candidate.name}-${candidate.role}`}>
                  <strong>{candidate.name}</strong> · {candidate.role}{" "}
                  <a
                    href={candidate.source.url}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={`Fuente de candidatura de ${candidate.name}`}
                  >
                    <ArrowUpRight size={12} />
                  </a>
                </p>
              ))}
              {entry.note && <p>{entry.note}</p>}
              {entry.sources.map((source) => (
                <a
                  className="document-link"
                  href={source.url}
                  key={source.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {source.label}
                  <ArrowUpRight size={13} />
                </a>
              ))}
            </details>
          ))}
          <p className="small-note">
            {territorialDocuments.length
              ? "Generales del 29N: programa nacional todavía no localizado."
              : "Programa específico de las generales del 29N pendiente de incorporar y analizar."}
          </p>
          {availableDocuments.map((document) => (
            <a
              key={document.id}
              className="document-link"
              href={documentUrl(document)}
              download
            >
              <Download size={16} />
              <span>
                {document.title}
                <small>
                  {document.kind === "territorial"
                    ? "Documento autonómico disponible"
                    : document.kind === "historical"
                      ? `Antecedente nacional de ${document.electionDate?.slice(0, 4)} disponible`
                      : "Documento político disponible"}{" "}
                  · {document.format}
                  {research.sourceDocumentIds.includes(document.id)
                    ? " · análisis incorporado"
                    : " · análisis pendiente"}
                </small>
              </span>
            </a>
          ))}
        </>
      )}
      {!!documents.length && (
        <>
          <h3>Documentos descargables</h3>
          {documents.map((document) => (
            <details key={document.id} className="document-record">
              <summary>
                <FileText size={17} />
                <span>
                  {document.title}
                  <small>
                    {document.kind === "historical"
                      ? `Antecedente de ${document.electionDate?.slice(0, 4)}`
                      : document.kind === "territorial"
                        ? `Programa autonómico · ${"territory" in document ? document.territory : ""}`
                        : document.kind === "permanent"
                          ? "Programa permanente"
                          : "Documento político general"}{" "}
                    · {document.format}
                    {document.pages ? ` · ${document.pages} páginas` : ""}
                  </small>
                </span>
              </summary>
              <p>{document.note}</p>
              <a
                className="document-link"
                href={documentUrl(document)}
                download
              >
                <Download size={16} />
                Descargar copia local · {document.format}
              </a>
              <a
                className="document-link"
                href={document.source}
                target="_blank"
                rel="noreferrer"
              >
                Procedencia original
                <ArrowUpRight size={14} />
              </a>
              {document.sourceKind === "mirror" && (
                <a
                  className="document-link"
                  href={document.downloadedFrom}
                  target="_blank"
                  rel="noreferrer"
                >
                  Archivo de prensa utilizado
                  <ArrowUpRight size={14} />
                </a>
              )}
              <dl className="document-provenance">
                <div>
                  <dt>Consulta</dt>
                  <dd>{document.retrievedAt}</dd>
                </div>
                <div>
                  <dt>Integridad · SHA-256</dt>
                  <dd>
                    <code>{document.sha256}</code>
                  </dd>
                </div>
                <div>
                  <dt>Análisis</dt>
                  <dd>
                    {research.sourceDocumentIds.includes(document.id) ? (
                      <a href="#/coordenadas-politicas">
                        Borrador documental · propuestas y fuentes
                      </a>
                    ) : (
                      "Pendiente · no se utiliza para calcular afinidades"
                    )}
                  </dd>
                </div>
              </dl>
            </details>
          ))}
        </>
      )}
    </section>
  );
}
