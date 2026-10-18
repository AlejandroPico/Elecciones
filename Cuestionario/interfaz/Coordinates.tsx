import { useState } from "react";
import { ArrowDownToLine, ChevronDown } from "lucide-react";
import {
  colors,
  corpus,
  definitions,
  documentEdition,
  evidenceLocator,
  indicatorValue,
  markerGroups,
  methodology,
  partyPoint,
  questionById,
  scoreAxis,
  type Axis,
} from "./model";
import notebook from "../Resumen Preguntas.txt?url&no-inline";
import categoryReport from "../Resumen Categorías.txt?url&no-inline";
import selectionPlan from "../Plan de selección.txt?url&no-inline";
import "./coordinates.css";

const documents = import.meta.glob<string>(
  "../../Elecciones/*/programas/**/*.{pdf,txt}",
  {
    eager: true,
    query: "?url&no-inline",
    import: "default",
  },
);
const number = (value: number | null) =>
  value === null
    ? "Sin datos"
    : new Intl.NumberFormat("es", {
        maximumFractionDigits: 1,
        signDisplay: "exceptZero",
      }).format(value);
const sx = (n: number) => 70 + (n + 100) * 2.2;
const sy = (n: number) => 350 - (n + 100) * 1.5;

function AxisEvidence({
  axis,
  party,
  letter,
}: {
  axis: Axis;
  party: string;
  letter: string;
}) {
  const result = scoreAxis(axis, party);
  return (
    <section className="documentary-axis">
      <h3>
        <span>{letter}</span>
        {axis.label}
      </h3>
      <p className="documentary-formula">
        {result.count
          ? `${result.values
              .filter((v) => v !== null)
              .map((v) => `(${number(v)})`)
              .join(" + ")} ÷ ${result.count} = ${number(result.value)}`
          : "Sin evidencia suficiente para calcular este eje."}
      </p>
      {axis.indicators.map((indicator, i) => {
        const value = indicatorValue(indicator, party);
        return (
          <details key={i} className="documentary-indicator">
            <summary>
              <span>{indicator.label}</span>
              <strong>{number(value)}</strong>
              <ChevronDown size={13} />
            </summary>
            <div>
              {indicator.direction === -1 && (
                <p>
                  Signo invertido: rechazar este enunciado aumenta el valor del
                  eje.
                </p>
              )}
              {indicator.questionIds.map((id) => {
                const q = questionById.get(id)!;
                const pos = q.positions[party];
                return (
                  <div key={id} className="documentary-reference">
                    <p>{q.statement}</p>
                    <small>
                      {pos.value === null
                        ? "Sin posición determinada"
                        : pos.value === 2
                          ? "Respaldo documental · +2"
                          : "Oposición documental · −2"}
                    </small>
                    {pos.evidence.length ? (
                      <>
                        <p className="documentary-basis">{pos.basis}</p>
                        {pos.evidence.map((ev) => {
                          const source = corpus.sources.find(
                            (s) => s.id === ev.documentId,
                          )!;
                          const href = documents[`../../${source.file}`];
                          return (
                            <a
                              key={ev.proposalId}
                              href={
                                ev.pdfPages.length
                                  ? `${href}#page=${ev.pdfPages[0]}`
                                  : href
                              }
                              target="_blank"
                              rel="noreferrer"
                            >
                              {documentEdition(source)} · {evidenceLocator(ev)}{" "}
                              <span className="sr-only">· {source.title}</span>
                            </a>
                          );
                        })}
                      </>
                    ) : (
                      <p className="documentary-basis">
                        No se ha vinculado una propuesta a esta decisión exacta.
                        No significa neutralidad ni oposición.
                      </p>
                    )}
                    <code>{id}</code>
                  </div>
                );
              })}
            </div>
          </details>
        );
      })}
    </section>
  );
}

export default function Coordinates() {
  const [mapId, setMapId] = useState(definitions[0].id);
  const [party, setParty] = useState("pp");
  const [visible, setVisible] = useState(
    () => new Set(corpus.parties.map((p) => p.id)),
  );
  const map = definitions.find((c) => c.id === mapId)!;
  const points = corpus.parties.map((p) => partyPoint(map, p.id));
  const current = points.find((p) => p.party === party)!;
  const label = corpus.parties.find((p) => p.id === party)!.name;
  const groups = markerGroups(points.filter((p) => visible.has(p.party)));
  function toggle(id: string) {
    setVisible((old) => {
      const next = new Set(old);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }
  return (
    <div className="section-content documentary-page">
      <header className="documentary-heading">
        <div>
          <h1 className="section-title">Coordenadas políticas</h1>
          <p>
            Antecedentes y programas generales <span>·</span> Borrador
            documental
          </p>
        </div>
        <a
          className="documentary-download"
          href={notebook}
          download="Resumen Preguntas.txt"
        >
          <ArrowDownToLine size={15} />
          Resumen de preguntas
        </a>
      </header>
      <div className="documentary-tabs" aria-label="Tema del gráfico">
        {definitions.map((c) => (
          <button
            key={c.id}
            aria-pressed={mapId === c.id}
            onClick={() => setMapId(c.id)}
          >
            {c.title}
          </button>
        ))}
      </div>
      <div className="documentary-map-heading">
        <h2>{map.title}</h2>
        <p>Media de decisiones documentadas · escala de −100 a +100</p>
      </div>
      <div className="documentary-layout">
        <div className="documentary-plot">
          <p className="documentary-axis-caption">
            <b>Y</b> {map.y.label}
          </p>
          <svg
            key={map.id}
            viewBox="0 0 580 410"
            role="group"
            aria-label={`Mapa documental de ${map.title}. X: ${map.x.label}. Y: ${map.y.label}. Las coordenadas y coberturas se muestran también en la lista de partidos.`}
          >
            <rect
              x="70"
              y="50"
              width="440"
              height="300"
              className="documentary-field"
            />
            {[-100, -50, 0, 50, 100].map((n) => (
              <g key={n}>
                <line
                  x1={sx(n)}
                  y1="50"
                  x2={sx(n)}
                  y2="350"
                  className={n === 0 ? "documentary-zero" : "documentary-grid"}
                />
                <line
                  x1="70"
                  y1={sy(n)}
                  x2="510"
                  y2={sy(n)}
                  className={n === 0 ? "documentary-zero" : "documentary-grid"}
                />
                <text x={sx(n)} y="377" textAnchor="middle">
                  {number(n)}
                </text>
                <text x="52" y={sy(n) + 4} textAnchor="end">
                  {number(n)}
                </text>
              </g>
            ))}
            {current.drawable &&
              visible.has(party) &&
              current.x.interval &&
              current.y.interval && (
                <rect
                  className="documentary-missing-range"
                  x={sx(current.x.interval[0])}
                  y={sy(current.y.interval[1])}
                  width={sx(current.x.interval[1]) - sx(current.x.interval[0])}
                  height={sy(current.y.interval[0]) - sy(current.y.interval[1])}
                  style={{ stroke: colors[party] }}
                >
                  <title>
                    Intervalo posible al completar indicadores sin datos. No es
                    confianza estadística.
                  </title>
                </rect>
              )}
            {groups.map((group) => {
              const chosen = group.find((p) => p.party === party) ?? group[0];
              const names = group
                .map((p) => corpus.parties.find((x) => x.id === p.party)!.name)
                .join(", ");
              const desc = `${names}. X ${number(chosen.x.value)}; Y ${number(chosen.y.value)}. ${group.length > 1 ? "Posiciones coincidentes." : ""}`;
              const select = () =>
                setParty(
                  group[
                    (group.findIndex((p) => p.party === party) + 1) %
                      group.length
                  ].party,
                );
              return (
                <g
                  key={`${chosen.x.value}:${chosen.y.value}`}
                  transform={`translate(${sx(chosen.x.value!)},${sy(chosen.y.value!)})`}
                  role="button"
                  tabIndex={0}
                  aria-label={desc}
                  onClick={select}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      select();
                    }
                  }}
                  className="documentary-marker"
                >
                  <title>{desc}</title>
                  {group.some((p) => p.party === party) && (
                    <circle r="17" className="documentary-selection" />
                  )}
                  <circle r="11" fill={colors[chosen.party]} />
                  {group.length > 1 && (
                    <text
                      y="4"
                      textAnchor="middle"
                      className="documentary-cluster"
                    >
                      {group.length}
                    </text>
                  )}
                </g>
              );
            })}
            {!groups.length && (
              <text x="290" y="192" textAnchor="middle">
                Sin puntos con datos en ambos ejes
              </text>
            )}
          </svg>
          <p className="documentary-axis-caption documentary-x">
            <b>X</b> {map.x.label}
          </p>
          <p className="documentary-map-note">
            Los valores aplican los signos publicados en cada indicador. El cero
            exige datos; una ausencia queda sin posición. Los números agrupan
            partidos coincidentes, sin implicar programas equivalentes.
          </p>
        </div>
        <div
          className="documentary-parties"
          aria-label="Posiciones y cobertura por partido"
        >
          <div className="documentary-party-columns">
            <span>Partido</span>
            <span>X · cobertura</span>
            <span>Y · cobertura</span>
          </div>
          {points.map((point) => {
            const p = corpus.parties.find((p) => p.id === point.party)!;
            return (
              <div
                key={p.id}
                className={`documentary-party ${party === p.id ? "selected" : ""}`}
              >
                <button
                  className="documentary-visibility"
                  onClick={() => toggle(p.id)}
                  aria-label={`${visible.has(p.id) ? "Ocultar" : "Mostrar"} ${p.name} en el mapa`}
                  aria-pressed={visible.has(p.id)}
                >
                  <span
                    style={{
                      background: visible.has(p.id)
                        ? colors[p.id]
                        : "transparent",
                      borderColor: colors[p.id],
                    }}
                  />
                </button>
                <button
                  className="documentary-party-select"
                  onClick={() => setParty(p.id)}
                  aria-pressed={party === p.id}
                >
                  <strong>{p.name}</strong>
                  <span>
                    {number(point.x.value)}
                    <small>
                      {point.x.count}/{point.x.total}
                    </small>
                  </span>
                  <span>
                    {number(point.y.value)}
                    <small>
                      {point.y.count}/{point.y.total}
                    </small>
                  </span>
                </button>
              </div>
            );
          })}
          <p className="documentary-map-note">
            Cobertura: indicadores con evidencia / indicadores del eje. La
            cobertura desigual impide interpretar estos puntos como un ranking
            comparable.
          </p>
        </div>
      </div>
      <section
        className="documentary-audit"
        aria-label={`Cálculo y fuentes de ${label}`}
      >
        <header>
          <h2>
            <i style={{ background: colors[party] }} />
            {label}
          </h2>
          <p>
            {current.drawable
              ? `Cobertura del punto: ${current.x.count}/${current.x.total} en X · ${current.y.count}/${current.y.total} en Y`
              : "Sin punto: falta evidencia en al menos un eje"}
          </p>
        </header>
        <div className="documentary-audit-grid">
          <AxisEvidence
            key={`${map.id}-${party}-x`}
            axis={map.x}
            party={party}
            letter="X"
          />
          <AxisEvidence
            key={`${map.id}-${party}-y`}
            axis={map.y}
            party={party}
            letter="Y"
          />
        </div>
        <p className="documentary-map-note">
          Intervalo al completar datos ausentes: X{" "}
          {current.x.count && current.x.interval
            ? current.x.interval.map(number).join(" a ")
            : "sin datos"}{" "}
          · Y{" "}
          {current.y.count && current.y.interval
            ? current.y.interval.map(number).join(" a ")
            : "sin datos"}
          . Se dibuja para el partido seleccionado. No expresa probabilidad.
        </p>
      </section>
      <details className="documentary-method">
        <summary>
          Cómo se calcula
          <ChevronDown size={15} />
        </summary>
        <ol>
          {methodology.map((s) => (
            <li key={s}>{s}</li>
          ))}
        </ol>
        <p>
          La selección actual utiliza {corpus.questions.length} formulaciones.
          No equivale al catálogo completo.
        </p>
        <a href={selectionPlan} download="Plan de selección.txt">
          Plan de agrupación y selección
        </a>
      </details>
      <details className="documentary-method">
        <summary>
          Categorías del borrador <span>{corpus.counts.categories}</span>
          <ChevronDown size={15} />
        </summary>
        <p>
          {corpus.counts.questions.toLocaleString("es")} formulaciones ·{" "}
          {corpus.counts.concepts} conceptos ·{" "}
          {corpus.counts.proposalGroups.toLocaleString("es")} grupos de
          propuestas
        </p>
        <div className="documentary-categories">
          {corpus.categories.map((c) => (
            <div key={c.id}>
              <span>{c.title}</span>
              <strong>{c.questions}</strong>
            </div>
          ))}
        </div>
        <a href={categoryReport} download="Resumen Categorías.txt">
          Descargar recuento por categoría
        </a>
      </details>
      <details className="documentary-method">
        <summary>
          Programas y procedencia
          <ChevronDown size={15} />
        </summary>
        <div className="documentary-sources">
          {corpus.sources.map((s) => (
            <section key={s.id}>
              <h3>
                {corpus.parties.find((p) => p.id === s.organization)!.name}
              </h3>
              <p>
                {documentEdition(s)} ·{" "}
                {s.format === "PDF"
                  ? `${s.pages} páginas`
                  : "transcripción HTML · TXT"}{" "}
                ·{" "}
                {s.sourceKind === "mirror"
                  ? "copia de archivo de prensa"
                  : "descarga oficial"}
              </p>
              <a href={documents[`../../${s.file}`]} download>
                Descargar {s.format} conservado
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
