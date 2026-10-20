import { useState } from "react";
import PoliticalMap from "./PoliticalMap";
import { corpus, documentEdition } from "./model";
import { bank } from "./sesion";
import indices from "../indices-perfil.json";
import audit from "../auditoria-perfil.json";
import notebook from "../Resumen Preguntas.txt?url&no-inline";
import report from "../Revisión del modelo.txt?url&no-inline";
import "./coordinates.css";
import "./survey.css";

const documents = import.meta.glob<string>(
  "../../Elecciones/*/programas/**/*.{pdf,txt}",
  { eager: true, query: "?url&no-inline", import: "default" },
);
export default function Coordinates() {
  const [party, setParty] = useState("pp");
  return (
    <div className="section-content documentary-page">
      <header className="documentary-heading">
        <h1 className="section-title">Coordenadas políticas</h1>
        <a href={notebook} download="Resumen Preguntas.txt">
          Resumen de preguntas
        </a>
      </header>
      <p className="coordinate-coverage">
        El banco no permite todavía un mapa completo del espectro político: hay{" "}
        {audit.knownPositions.toLocaleString("es")} posiciones con evidencia de{" "}
        {audit.possiblePositions.toLocaleString("es")} cruces posibles. Los
        siguientes índices usan solo sus decisiones enumeradas y son los mismos
        que aparecen en Mi perfil.
      </p>
      <PoliticalMap
        answers={{}}
        selectedParty={party}
        selectParty={setParty}
        showUser={false}
      />
      <details className="documentary-method">
        <summary>Cómo se calculan y qué falta</summary>
        <ol>
          {indices.method.map((text) => (
            <li key={text}>{text}</li>
          ))}
        </ol>
        <a href={report} download="Revisión del modelo.txt">
          Diagnóstico y cobertura por partido
        </a>
      </details>
      <details className="documentary-method">
        <summary>Programas y procedencia</summary>
        <div className="documentary-sources">
          {corpus.sources.map((s) => (
            <section key={s.id}>
              <h3>{bank.parties.find((p) => p.id === s.organization)?.name}</h3>
              <p>
                {documentEdition(s)} ·{" "}
                {s.format === "PDF"
                  ? `${s.pages} páginas`
                  : "transcripción HTML · TXT"}
              </p>
              <a href={documents[`../../${s.file}`]} download>
                Descargar original conservado
              </a>
              <a href={s.source} target="_blank" rel="noreferrer">
                Referencia original
              </a>
              <small>SHA-256: {s.sha256}</small>
            </section>
          ))}
        </div>
      </details>
    </div>
  );
}
