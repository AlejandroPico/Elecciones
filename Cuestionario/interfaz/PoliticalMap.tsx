import { useId, useState } from "react";
import { logos } from "../../Partidos/interfaz/catalogo";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";
import {
  bank,
  documentaryAxis,
  representedResponses,
  uniqueResponses,
  userAxis,
} from "./sesion";
import { colors } from "./model";
import EvidenceLinks from "./EvidenceLinks";

const number = (v: number | null) =>
  v === null
    ? "Sin dato"
    : new Intl.NumberFormat("es", {
        maximumFractionDigits: 1,
        signDisplay: "exceptZero",
      }).format(v);
const short: Record<string, string> = {
  "registro-4086": "EB",
  "registro-6359": "FO",
  "registro-6040": "PCTE",
  "registro-7400": "IE",
  "registro-7458": "SALF",
  "registro-6972": "SY",
  "registro-6779": "TE",
  "registro-6620": "AA",
  "registro-7039": "Drago",
  "coalicion-d21-2026": "D21",
  "sumar-coalicion-2023": "Sumar",
  podemos: "Pod.",
  "eh-bildu": "Bildu",
  pp: "PP",
  psoe: "PSOE",
  vox: "Vox",
  cc: "CC",
};
export default function PoliticalMap({
  answers,
  selectedParty,
  selectParty,
  showUser = true,
}: {
  answers: Answers;
  selectedParty: string;
  selectParty: (id: string) => void;
  showUser?: boolean;
}) {
  const uid = useId().replace(/:/g, "");
  const [requestedMap, setMap] = useState<string | null>(null);
  const responded = uniqueResponses(answers).filter(
    (r) => r.answer.value !== null,
  );
  const map =
    bank.maps.find((m) => m.id === requestedMap) ??
    [...bank.maps].sort(
      (a, b) =>
        userAxis(answers, b.x).count +
        userAxis(answers, b.y).count -
        userAxis(answers, a.x).count -
        userAxis(answers, a.y).count,
    )[0];
  const user = { x: userAxis(answers, map.x), y: userAxis(answers, map.y) };
  const represented = representedResponses(answers).length;
  const points = bank.parties.map((p) => ({
    ...p,
    x: documentaryAxis(p.id, map.x),
    y: documentaryAxis(p.id, map.y),
  }));
  const groups = new Map<string, typeof points>();
  points
    .filter((p) => p.x.value !== null && p.y.value !== null)
    .forEach((p) => {
      const k = `${p.x.value}:${p.y.value}`;
      groups.set(k, [...(groups.get(k) ?? []), p]);
    });
  const selected = points.find((p) => p.id === selectedParty) ?? points[0];
  const px = (v: number) => 360 + v * 2.6,
    py = (v: number) => 260 - v * 1.9;
  const ids = new Set(
    [map.x, map.y].flatMap((a) => a.indicators.flatMap((i) => i.questionIds)),
  );
  const inCategory = responded.filter((r) =>
    map.categoryIds.includes(r.question.category),
  );
  const inMap = inCategory.filter(
    (r) => ids.has(r.question.id) && !r.question.scope,
  );
  const drawable = points.filter(
    (p) => p.x.value !== null && p.y.value !== null,
  );
  return (
    <section
      className="result-card political-map"
      aria-labelledby={`${uid}-title`}
    >
      <div className="political-map-head">
        <h2 id={`${uid}-title`}>
          {showUser
            ? "Tus índices por temas"
            : "Índices documentales por temas"}
        </h2>
      </div>
      <div className="political-map-controls">
        <label>
          Tema
          <select
            aria-label="Tema de los índices"
            value={map.id}
            onChange={(e) => setMap(e.target.value)}
          >
            {bank.maps.map((m) => (
              <option key={m.id} value={m.id}>
                {m.title}
              </option>
            ))}
          </select>
        </label>
        <p>
          Medias de varios indicadores fijos. Los partidos usan sus documentos
          vinculados a esos indicadores; su posición no cambia cuando cambia tu
          sorteo.
        </p>
      </div>
      {showUser && (
        <p className="coordinate-coverage" role="status">
          <strong>
            {represented} de {responded.length} respuestas tienen asignación a
            estos mapas.
          </strong>{" "}
          {represented < responded.length
            ? "El resto todavía no tiene un eje revisado y queda fuera de las coordenadas. Este banco aún no permite representar tu espectro político completo."
            : "La asignación de ejes es editorial y parcial; no es un test ideológico validado."}
          {inCategory.length > inMap.length && (
            <>
              {" "}
              En este tema se utilizan {inMap.length} de {inCategory.length}{" "}
              respuestas.
            </>
          )}
        </p>
      )}
      <div className="political-axis-definitions">
        <p>
          <b>X · Horizontal</b>
          {map.x.label}
        </p>
        <p>
          <b>Y · Vertical</b>
          {map.y.label}
        </p>
      </div>
      <p className="chart-note">
        Se promedian respuestas con el signo definido en cada indicador; los
        enunciados de sentido contrario se invierten. Un 0 es una media
        intermedia, no falta de opinión. Un +100 no significa ideología extrema.
        Con pocos indicadores, el índice es provisional.
      </p>
      <div className="political-map-key">
        {showUser && (
          <span>
            <i className="user-key" />
            Tú · doble aro animado
          </span>
        )}
        <span>
          <i className="party-key" />
          Documentos · siglas dentro del punto
        </span>
      </div>
      <svg
        className="political-map-svg"
        viewBox="0 0 720 540"
        role="group"
        aria-label={`${map.title}. X: ${map.x.label}. Y: ${map.y.label}.${showUser ? ` Tú: X ${number(user.x.value)}, Y ${number(user.y.value)}.` : ""}`}
      >
        {[-100, -50, 0, 50, 100].map((n) => (
          <g key={n}>
            <path
              className="grid-line"
              d={`M100 ${py(n)}H620 M${px(n)} 70V450`}
            />
            <text x={px(n)} y="473" textAnchor="middle">
              {number(n)}
            </text>
            <text x="85" y={py(n) + 4} textAnchor="end">
              {number(n)}
            </text>
          </g>
        ))}
        <path d="M100 260H620 M360 70V450" className="axis-line" />
        <text x="360" y="510" textAnchor="middle">
          X · Media de indicadores del eje horizontal
        </text>
        <text x="100" y="35">
          Y · Media de indicadores del eje vertical
        </text>
        {[...groups.values()].map((group) => {
          const p = group.find((p) => p.id === selectedParty) ?? group[0];
          const choose = () =>
            selectParty(
              group[
                (group.findIndex((p) => p.id === selectedParty) + 1) %
                  group.length
              ].id,
            );
          return (
            <g
              key={`${p.x.value}:${p.y.value}`}
              className="political-party-point"
              role="button"
              tabIndex={0}
              aria-label={`${group.map((p) => p.name).join(", ")}. X ${number(p.x.value)}, Y ${number(p.y.value)}`}
              onClick={choose}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  choose();
                }
              }}
            >
              <circle
                cx={px(p.x.value!)}
                cy={py(p.y.value!)}
                r={group.some((p) => p.id === selectedParty) ? 17 : 14}
                fill={colors[p.id]}
                stroke="var(--surface)"
                strokeWidth="2"
              />
              <text
                x={px(p.x.value!)}
                y={py(p.y.value!) + 4}
                textAnchor="middle"
                className="party-point-code"
              >
                {short[p.id] ?? p.name.slice(0, 6)}
                {group.length > 1 ? ` +${group.length - 1}` : ""}
              </text>
              <title>{`${group.map((p) => p.name).join(", ")} · X ${number(p.x.value)} · Y ${number(p.y.value)}. Pulsa para recorrer los documentos coincidentes.`}</title>
            </g>
          );
        })}
        {(selected.x.value === null) !== (selected.y.value === null) && (
          <g
            className="party-partial-projection"
            style={{ stroke: colors[selected.id] }}
          >
            <path
              d={
                selected.x.value !== null
                  ? `M${px(selected.x.value)} 70V450`
                  : `M100 ${py(selected.y.value!)}H620`
              }
            />
            <title>{`${selected.name}: solo hay base para un eje; no se inventa el otro.`}</title>
          </g>
        )}
        {showUser &&
          (user.x.value !== null && user.y.value !== null ? (
            <g
              className="political-user-point"
              transform={`translate(${px(user.x.value)},${py(user.y.value)})`}
            >
              <circle r="25" className="user-position-pulse" />
              <circle r="19" className="user-position-ring" />
              {!points.some(
                (p) => p.x.value === user.x.value && p.y.value === user.y.value,
              ) && <path d="M-8 0H8 M0-8V8" />}
              <text
                x={user.x.value > 75 ? -32 : 32}
                y={user.y.value > 75 ? 32 : -28}
                textAnchor={user.x.value > 75 ? "end" : "start"}
              >
                Tú
              </text>
              <title>{`Tu índice: X ${number(user.x.value)}, Y ${number(user.y.value)}`}</title>
            </g>
          ) : user.x.value !== null || user.y.value !== null ? (
            <g className="political-user-point partial">
              <path
                className="user-projection"
                d={
                  user.x.value !== null
                    ? `M${px(user.x.value)} 70V450`
                    : `M100 ${py(user.y.value!)}H620`
                }
              />
              <text x="115" y="92">
                Tú · solo {user.x.value !== null ? "X" : "Y"}
              </text>
            </g>
          ) : (
            <text x="360" y="284" textAnchor="middle">
              Sin respuestas asignadas a estos ejes
            </text>
          ))}
      </svg>
      {showUser && (
        <p className="political-user-summary">
          <strong>Tú</strong> · X {number(user.x.value)} ({user.x.count}{" "}
          indicadores) · Y {number(user.y.value)} ({user.y.count} indicadores).
          Media ponderada por importancia, sin redondear a saltos de 50.
          {(user.x.count < 2 || user.y.count < 2) &&
            " Base escasa: falta más de una decisión en algún eje."}
        </p>
      )}
      {groups.size === 1 && drawable.length > 1 && (
        <p className="coordinate-coverage">
          Los {drawable.length} documentos situables coinciden en los
          indicadores conocidos. Eso no demuestra que sus programas sean
          equivalentes; faltan comparaciones para diferenciarlos. No se
          desplazan los puntos para aparentar diferencias.
        </p>
      )}
      <div className="political-party-legend" aria-label="Documentos del mapa">
        {points.map((p) => {
          const extracted = bank.questions.filter(
            (q) =>
              map.categoryIds.includes(q.category) &&
              q.positions[p.id]?.value != null &&
              q.positions[p.id]?.evidence.length,
          ).length;
          return (
            <button
              key={p.id}
              aria-pressed={p.id === selectedParty}
              onClick={() => selectParty(p.id)}
            >
              {logos[p.id] && <img src={logos[p.id]} alt="" />}
              <i style={{ background: colors[p.id] }} />
              <span>
                {p.name}
                <small>
                  X {number(p.x.value)} · {p.x.count}/{p.x.total} · Y{" "}
                  {number(p.y.value)} · {p.y.count}/{p.y.total}
                </small>
                {(p.x.value === null || p.y.value === null) && (
                  <small>
                    {extracted
                      ? `${extracted} formulaciones extraídas en el tema; asignación al eje incompleta.`
                      : "Sin formulaciones puntuables extraídas en este tema. No acredita ausencia de postura."}
                  </small>
                )}
              </span>
            </button>
          );
        })}
      </div>
      <details className="political-position-why" open>
        <summary>Por qué {selected.name} aparece así</summary>
        <p>
          Se promedian indicadores con evidencia del documento, no se asigna una
          ideología por el nombre del partido. El código +2 del banco significa
          respaldo de una propuesta, no grado de radicalidad. Las fuentes
          regionales se mantienen fuera de estos índices nacionales.
        </p>
        {(["x", "y"] as const).map((key) => {
          const result = selected[key],
            personal = user[key];
          return (
            <section key={key}>
              <h3>
                {key.toUpperCase()} · {map[key].label}
              </h3>
              <p>
                Documento: {number(result.value)} · {result.count} de{" "}
                {result.total} indicadores conocidos.{" "}
                {result.count
                  ? `Suma de valores ${number(result.value! * result.count)} ÷ ${result.count}.`
                  : "Falta vincular evidencia: no se introduce un cero."}
              </p>
              {showUser && (
                <p>
                  Tú:{" "}
                  {personal.count
                    ? `${number(100 * personal.numerator)} ÷ peso ${personal.weight.toFixed(2)} = ${number(personal.value)}.`
                    : "Sin respuestas asignadas."}{" "}
                  Cada respuesta mantiene su signo e importancia 1, 2 o 3.
                </p>
              )}
              {result.contributions.map((c, i) => (
                <details key={i}>
                  <summary>
                    {c.indicator.label}: {number(c.value)}
                  </summary>
                  <p>
                    Dirección {c.indicator.direction === 1 ? "+1" : "−1"}; valor
                    = posición × 50 × dirección.{" "}
                    {c.value === null &&
                      "Sin posición puntuable, con discrepancia o sin evidencia nacional."}
                  </p>
                  {c.entries.map((e) => (
                    <div key={e.question.id}>
                      <p>{e.question.text}</p>
                      <p>{e.position.basis}</p>
                      <EvidenceLinks evidence={e.position.evidence} />
                    </div>
                  ))}
                  {showUser &&
                    personal.indicators[i]?.entries.map((e) => (
                      <p key={e.question.id}>
                        Tu respuesta {e.answer.value}, importancia{" "}
                        {e.answer.importance}; aportación firmada{" "}
                        {number(50 * e.answer.value! * e.direction)}.
                      </p>
                    ))}
                </details>
              ))}
            </section>
          );
        })}
      </details>
    </section>
  );
}
