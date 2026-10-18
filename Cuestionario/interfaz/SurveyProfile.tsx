import { useState } from "react";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";
import { logos } from "../../Partidos/interfaz/catalogo";
import { colors } from "./model";
import {
  bank,
  compare,
  sourceById,
  uniqueResponses,
  userAxis,
  type Evidence,
} from "./sesion";

const documents = import.meta.glob<string>(
  "../../Elecciones/*/programas/**/*.{pdf,txt}",
  { eager: true, query: "?url&no-inline", import: "default" },
);
const labels: Record<number, string> = {
  [-2]: "Muy en desacuerdo",
  [-1]: "En desacuerdo",
  0: "Neutral",
  1: "De acuerdo",
  2: "Muy de acuerdo",
};
const rounded = (n: number | null) =>
  n === null ? "Sin datos" : `${Math.round(n)} %`;

function EvidenceLinks({ evidence }: { evidence: Evidence[] }) {
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
  const [mapId, setMapId] = useState(bank.maps[0].id);
  const [hover, setHover] = useState<string | null>(null);
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
  const chart = bank.maps.find((m) => m.id === mapId)!;
  const x = userAxis(answers, chart.x),
    y = userAxis(answers, chart.y);
  const visibleResponses = responded.filter(
    (r) => !category || r.question.category === category,
  );
  const groupedPoints = new Map<string, typeof rows>();
  for (const p of rows.filter((p) => p.percent !== null)) {
    const key = `${p.percent}:${p.coverage}`;
    groupedPoints.set(key, [...(groupedPoints.get(key) ?? []), p]);
  }
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
        <section className="result-card affinity-map">
          <h2>Mapa de afinidad documental</h2>
          <p className="chart-note">
            Horizontal: coincidencia. Vertical: proporción de tus respuestas con
            posición documentada. Cada punto es una comparación distinta; una
            cobertura baja no permite ordenar preferencias.
          </p>
          <svg
            viewBox="0 0 580 350"
            role="img"
            aria-label="Mapa de coincidencia de 0 a 100 por ciento y cobertura de 0 a 100 por ciento"
          >
            {[0, 25, 50, 75, 100].map((n) => (
              <g key={n}>
                <path
                  d={`M55 ${290 - n * 2.4}H545 M${55 + n * 4.9} 50V290`}
                  className="grid-line"
                />
                <text x={55 + n * 4.9} y="312" textAnchor="middle">
                  {n}
                </text>
                <text x="43" y={294 - n * 2.4} textAnchor="end">
                  {n}
                </text>
              </g>
            ))}
            <text x="300" y="340" textAnchor="middle">
              Coincidencia (%)
            </text>
            <text x="55" y="25">
              Cobertura (%)
            </text>
            {[...groupedPoints.values()].flatMap((group) =>
              group.map((p, i) => {
                const columns = Math.min(4, group.length);
                const spanX = (columns - 1) * 20;
                const spanY = (Math.ceil(group.length / columns) - 1) * 20;
                const anchorX = Math.max(
                  65,
                  Math.min(535 - spanX, 55 + p.percent! * 4.9 - spanX / 2),
                );
                const anchorY = Math.max(
                  60,
                  Math.min(280 - spanY, 290 - p.coverage * 2.4 - spanY / 2),
                );
                const cx = anchorX + (i % columns) * 20;
                const cy = anchorY + Math.floor(i / columns) * 20;
                return (
                  <g
                    key={p.id}
                    className="affinity-marker"
                    tabIndex={0}
                    role="button"
                    aria-label={`${p.name}: ${rounded(p.percent)} de coincidencia, ${p.shared} de ${p.answered} respuestas con evidencia`}
                    onMouseEnter={() => setHover(p.id)}
                    onMouseLeave={() => setHover(null)}
                    onFocus={() => setHover(p.id)}
                    onBlur={() => setHover(null)}
                    onClick={() => setPartyId(p.id)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        setPartyId(p.id);
                      }
                    }}
                  >
                    <line
                      x1={55 + p.percent! * 4.9}
                      y1={290 - p.coverage * 2.4}
                      x2={cx}
                      y2={cy}
                      stroke={colors[p.id]}
                    />
                    <circle
                      cx={cx}
                      cy={cy}
                      r={p.id === partyId ? 10 : 7}
                      fill={colors[p.id]}
                      stroke="var(--surface)"
                      strokeWidth="2"
                    />
                    <title>
                      {p.name} · {rounded(p.percent)} · cobertura{" "}
                      {Math.round(p.coverage)} %
                    </title>
                  </g>
                );
              }),
            )}
            {!rows.some((p) => p.percent !== null) && (
              <text x="300" y="175" textAnchor="middle">
                Sin respuestas comparables todavía
              </text>
            )}
          </svg>
          <p className="affinity-caption" aria-live="polite">
            {(() => {
              const p = rows.find((p) => p.id === hover) ?? selected;
              return `${p.name} · ${rounded(p.percent)} · ${p.shared} de ${p.answered} respuestas con evidencia`;
            })()}
          </p>
          <p className="chart-note">
            Los puntos coincidentes se separan ligeramente para poder
            seleccionarlos; la línea conserva la coordenada exacta.
          </p>
        </section>
        <section className="result-card affinity-list">
          <h2>Comparar documentos</h2>
          <p className="chart-note">
            Orden alfabético, sin clasificación automática entre muestras de
            cobertura distinta.
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
                    {p.shared} / {p.answered} con evidencia
                  </small>
                </span>
                <strong>{rounded(p.percent)}</strong>
              </button>
            ))}
        </section>
      </div>
      <section className="result-card category-affinities">
        <h2>{selected.name} · por temas</h2>
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
                        width: `${match.percent ?? 0}%`,
                        background: colors[partyId],
                      }}
                    />
                  </span>
                  <small>
                    {rounded(match.percent)} · {match.shared}/{match.answered}
                  </small>
                </button>
              );
            })}
        </div>
        {!answered && (
          <p>Responde una pregunta para empezar a perfilar tus posiciones.</p>
        )}
      </section>
      <details className="result-card documented-dimensions">
        <summary>Coordenadas temáticas con dirección documentada</summary>
        <p className="chart-note">
          Se conservan los indicadores y signos del análisis. Las preguntas sin
          un eje definido intervienen en la afinidad y en el resumen de
          respuestas, sin recibir una etiqueta ideológica inventada.
        </p>
        <select
          aria-label="Mapa temático"
          value={mapId}
          onChange={(e) => setMapId(e.target.value)}
        >
          {bank.maps.map((m) => (
            <option key={m.id} value={m.id}>
              {m.title}
            </option>
          ))}
        </select>
        <svg
          viewBox="0 0 400 310"
          role="img"
          aria-label={`Coordenadas de ${chart.title}: ${x.value === null ? "eje X sin respuestas" : `X ${Math.round(x.value)}`}, ${y.value === null ? "eje Y sin respuestas" : `Y ${Math.round(y.value)}`}`}
        >
          <path d="M40 145H360 M200 25V265" className="axis-line" />
          <rect
            x="40"
            y="25"
            width="320"
            height="240"
            fill="none"
            className="grid-line"
          />
          {x.value !== null && y.value !== null ? (
            <circle
              cx={200 + x.value * 1.6}
              cy={145 - y.value * 1.2}
              r="7"
              fill="var(--accent)"
            />
          ) : (
            <text x="200" y="290" textAnchor="middle">
              Faltan respuestas en uno o ambos ejes
            </text>
          )}
          <text x="40" y="280">
            −100
          </text>
          <text x="325" y="280">
            +100
          </text>
        </svg>
        {[
          { axis: chart.x, score: x },
          { axis: chart.y, score: y },
        ].map(({ axis, score }, i) => (
          <details key={i}>
            <summary>
              {i ? "Y" : "X"}: {axis.label} ·{" "}
              {score.value === null ? "Sin datos" : Math.round(score.value)} ·{" "}
              {score.contributions.length} respuestas
            </summary>
            <p>
              100 × suma(respuesta / 2 × dirección × importancia) /
              suma(importancias). Numerador {score.numerator.toFixed(2)}; peso{" "}
              {score.weight}.
            </p>
            {score.contributions.map((c) => (
              <p key={c.question.id}>
                {c.question.text} · {c.answer.value} / 2 × {c.direction} ×{" "}
                {c.answer.importance} = {c.numerator.toFixed(2)}
              </p>
            ))}
          </details>
        ))}
      </details>
      <details className="result-card response-audit" open>
        <summary>Respuestas y cálculo · {visibleResponses.length}</summary>
        <p>
          Escala −2, −1, 0, +1, +2. Importancia: normal ×1, alta ×2, esencial
          ×3. Omitir excluye la respuesta; neutral sí participa.
        </p>
        <p>
          Coincidencia = 100 × (1 − suma(importancia × |respuesta − posición| /
          4) / suma(importancias comparables)). Para {selected.name}: distancia
          ponderada {detail.distance.toFixed(2)} / peso {detail.weight} →{" "}
          {rounded(detail.percent)}.
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
