import { sourceById, type Evidence } from "./sesion";
const documents = import.meta.glob<string>(
  "../../Elecciones/*/programas/**/*.{pdf,txt}",
  { eager: true, query: "?url&no-inline", import: "default" },
);
export default function EvidenceLinks({ evidence }: { evidence: Evidence[] }) {
  return (
    <ul className="response-evidence">
      {evidence.map((e, index) => {
        const source = sourceById.get(e.documentId);
        if (!source) return null;
        const href = documents[`../../${source.file}`];
        const locator = e.pdfPages?.length
          ? `PDF ${e.pdfPages.join(", ")}`
          : `Líneas ${e.textLines?.join(", ")}`;
        return (
          <li key={`${e.proposalId}-${index}`}>
            <a
              href={
                href
                  ? `${href}${e.pdfPages?.length ? `#page=${e.pdfPages[0]}` : ""}`
                  : source.source
              }
              target="_blank"
              rel="noreferrer"
            >
              {source.title} · {locator}
            </a>
            <small>
              {source.kind === "territorial" ? `${source.territory} · ` : ""}
              {source.electionDate?.slice(0, 4) ??
                "Documento general o permanente"}{" "}
              · {e.proposalId}
            </small>
          </li>
        );
      })}
    </ul>
  );
}
