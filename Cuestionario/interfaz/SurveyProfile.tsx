import { useState } from "react";
import PoliticalMap from "./PoliticalMap";
import EvidenceLinks from "./EvidenceLinks";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";
import { logos } from "../../Partidos/interfaz/catalogo";
import { colors } from "./model";
import audit from "../auditoria-perfil.json";
import auditReport from "../Revisión del modelo.txt?url&no-inline";
import { bank, compare, uniqueResponses } from "./sesion";

const labels: Record<number, string> = {
  [-2]: "Muy en desacuerdo",
  [-1]: "En desacuerdo",
  0: "Neutral",
  1: "De acuerdo",
  2: "Muy de acuerdo",
};
const rounded = (n: number | null) =>
  n === null
    ? "Sin datos"
    : `${new Intl.NumberFormat("es", { maximumFractionDigits: 1 }).format(n)} %`;

export default function SurveyProfile({
  answers,
  resume,
  topics,
}: {
  answers: Answers;
  resume: (id?: string) => void;
  topics: () => void;
}) {
  const [category, setCategory] = useState("");
  const [requestedParty, setPartyId] = useState<string | null>(null);
  const responded = uniqueResponses(answers);
  const answered = responded.filter((r) => r.answer.value !== null).length;
  const rows = bank.parties.map((p) => ({
    ...p,
    ...compare(answers, p.id, category || undefined),
  }));
  const selected =
    rows.find((p) => p.id === requestedParty) ??
    [...rows].sort(
      (a, b) => b.shared - a.shared || a.name.localeCompare(b.name, "es"),
    )[0];
  const partyId = selected.id;
  const detail = compare(answers, partyId, category || undefined);
  const visibleResponses = responded.filter(
    (r) => !category || r.question.category === category,
  );
  return (
    <section
      className="section-content survey-profile"
      aria-labelledby="profile-title"
    >
      <header className="topic-heading">
        <h1 id="profile-title" className="section-title">
          Mi perfil
        </h1>
        <div>
          <button className="quiet-button" onClick={() => resume()}>
            Reanudar
          </button>
          <button className="quiet-button" onClick={topics}>
            Elegir temas
          </button>
        </div>
      </header>
      <p className="results-summary">
        {answered} {answered === 1 ? "respuesta" : "respuestas"} ·{" "}
        {responded.length - answered}{" "}
        {responded.length - answered === 1 ? "omisión" : "omisiones"}
      </p>
      <p className="profile-limits">
        Perfil parcial y experimental. La coincidencia compara antecedentes de
        distintas fechas y ámbitos; no acredita candidaturas ni programas
        nacionales de 2026. Pocas respuestas o poca cobertura permiten
        conclusiones muy limitadas.
      </p>
      <PoliticalMap
        answers={answers}
        selectedParty={partyId}
        selectParty={setPartyId}
      />
      <details className="result-card model-audit">
        <summary>Estado real de la comparación</summary>
        <p>
          El banco contiene {audit.knownPositions.toLocaleString("es")}{" "}
          posiciones con evidencia de{" "}
          {audit.possiblePositions.toLocaleString("es")} cruces posibles (
          {audit.matrixCoverage.toFixed(1)} %). No es una matriz completa de
          respuestas de todos los partidos.
        </p>
        <p>
          {audit.supportCodes.toLocaleString("es")} códigos son respaldos y{" "}
          {audit.oppositionCodes} son oposiciones. El +2 del banco no significa
          «ideología extrema». Falta contrastar los documentos entre sí y
          asignar el resto de decisiones a ejes explícitos.
        </p>
        <p>
          Hay {audit.mappedQuestions} preguntas asignadas a índices de{" "}
          {audit.questions.toLocaleString("es")} formulaciones. Tener un
          programa descargado no significa que todas sus posturas estén ya
          codificadas.
        </p>
        <a href={auditReport} download="Revisión del modelo.txt">
          Descargar diagnóstico y cobertura por partido
        </a>
      </details>
      <label className="profile-filter">
        Tema
        <select
          aria-label="Tema del perfil"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">Todos los temas respondidos</option>
          {bank.categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.title}
            </option>
          ))}
        </select>
      </label>
      <div className="profile-graphs">
        <section className="result-card affinity-list">
          <h2>Comparar documentos</h2>
          <p className="chart-note">
            Primero se muestra cuántas de tus respuestas se pueden comparar. La
            coincidencia se calcula solo sobre esas decisiones; no es una
            afinidad global ni una probabilidad de voto.
          </p>
          {[...rows]
            .sort((a, b) => a.name.localeCompare(b.name, "es"))
            .map((p) => (
              <button
                key={p.id}
                className={`affinity-row ${partyId === p.id ? "selected" : ""}`}
                aria-pressed={partyId === p.id}
                onClick={() => setPartyId(p.id)}
              >
                {logos[p.id] ? (
                  <img src={logos[p.id]} alt="" />
                ) : (
                  <i style={{ background: colors[p.id] }} />
                )}
                <span>
                  {p.name}
                  <small>
                    {p.shared} de {p.answered} respuestas comparables ·
                    cobertura {rounded(p.coverage)}
                  </small>
                </span>
                <span className="partial-match">
                  {p.percent === null
                    ? "Sin coincidencia calculable"
                    : `Coincidencia parcial: ${rounded(p.percent)}`}
                </span>
              </button>
            ))}
        </section>
      </div>
      <section className="result-card category-affinities">
        <h2>{selected.name} · cobertura por temas</h2>
        <p className="chart-note">
          La barra indica la proporción de respuestas comparables, no cuánto te
          representa el partido.
        </p>
        <div>
          {bank.categories
            .filter((c) =>
              responded.some(
                (r) => r.question.category === c.id && r.answer.value !== null,
              ),
            )
            .map((c) => {
              const match = compare(answers, partyId, c.id);
              return (
                <button key={c.id} onClick={() => setCategory(c.id)}>
                  <span>{c.title}</span>
                  <span className="affinity-bar">
                    <i
                      style={{
                        width: `${match.coverage}%`,
                        background: colors[partyId],
                      }}
                    />
                  </span>
                  <small>
                    {match.shared}/{match.answered} comparables ·{" "}
                    {rounded(match.coverage)}
                  </small>
                </button>
              );
            })}
        </div>
        {!answered && (
          <p>Responde una pregunta para empezar a perfilar tus posiciones.</p>
        )}
      </section>
      <section className="result-card comparison-explanation">
        <h2>Cómo leer la comparación con {selected.name}</h2>
        <p>
          <strong>
            {detail.shared} de {detail.answered} respuestas comparables
          </strong>{" "}
          · cobertura {rounded(detail.coverage)}.
        </p>
        <p>
          {detail.percent === null
            ? "No hay una base común para calcular coincidencia."
            : `En esas ${detail.shared} decisiones, la coincidencia ponderada es ${rounded(detail.percent)}. Las otras ${detail.answered - detail.shared} no se han evaluado: no cuentan como acuerdo, desacuerdo ni neutralidad.`}
        </p>
        {detail.percent !== null &&
          detail.overallRange &&
          detail.unknownWeight > 0 && (
            <p>
              Si se llegaran a documentar todas tus respuestas, el resultado
              global podría estar entre {rounded(detail.overallRange[0])} y{" "}
              {rounded(detail.overallRange[1])}. Son límites matemáticos para
              los datos ausentes, no una estimación ni un intervalo de
              confianza. No se publica un porcentaje global con esa
              incertidumbre.
            </p>
          )}
      </section>
      <details className="result-card response-audit" open>
        <summary>Respuestas y cálculo · {visibleResponses.length}</summary>
        <p>
          Escala −2, −1, 0, +1, +2. Importancia: normal ×1, alta ×2, esencial
          ×3. Omitir excluye la respuesta; neutral sí participa.
        </p>
        <p>
          Coincidencia parcial = 100 × (1 − suma(importancia × |respuesta −
          posición| / 4) / suma(importancias comparables)). Para {selected.name}
          : distancia ponderada {detail.distance.toFixed(2)} / peso{" "}
          {detail.weight} → {rounded(detail.percent)}.
        </p>
        <p>
          Las posiciones son codificaciones editoriales respaldadas por los
          documentos enlazados. Un vacío o una propuesta ambigua se excluyen. La
          coincidencia no es una probabilidad de voto.
        </p>
        {visibleResponses.map(({ question: q, answer: a }) => {
          const p = q.positions[partyId];
          return (
            <details key={q.id} className="response-detail">
              <summary>
                <span>{q.text}</span>
                <small>
                  {a.value === null ? "Omitida" : labels[a.value]} ·{" "}
                  {a.importance === 1
                    ? "Normal"
                    : a.importance === 2
                      ? "Alta"
                      : "Esencial"}
                </small>
              </summary>
              <p>
                {bank.categories.find((c) => c.id === q.category)?.title} ·{" "}
                {q.id}
              </p>
              {q.scope && (
                <p>
                  Ámbito: {q.scope.territory}, programa autonómico{" "}
                  {q.scope.sourceElection}.
                </p>
              )}
              <button className="quiet-button" onClick={() => resume(q.id)}>
                Revisar respuesta
              </button>
              <p>
                {selected.name}:{" "}
                {p?.value == null
                  ? "Sin posición puntuable para esta decisión."
                  : `Posición ${p.value > 0 ? "+" : ""}${p.value}.`}
              </p>
              {p && <p>{p.basis}</p>}
              {a.value !== null &&
                p?.value != null &&
                p.evidence.length > 0 && (
                  <p>
                    Aporta {a.importance} × |{a.value} − ({p.value})| / 4 ={" "}
                    {((a.importance * Math.abs(a.value - p.value)) / 4).toFixed(
                      2,
                    )}{" "}
                    a la distancia; peso {a.importance}.
                  </p>
                )}
              {p && <EvidenceLinks evidence={p.evidence} />}
            </details>
          );
        })}
      </details>
    </section>
  );
}
