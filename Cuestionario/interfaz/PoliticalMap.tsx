import { useId, useState } from "react";
import { logos } from "../../Partidos/interfaz/catalogo";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";
import {
  bank,
  coordinatePair,
  documentaryAxis,
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
  cc: "CC",
  podemos: "Pod.",
  psoe: "PSOE",
  pp: "PP",
  vox: "Vox",
  "eh-bildu": "Bildu",
};
export default function PoliticalMap({
  answers,
  selectedParty,
  selectParty,
}: {
  answers: Answers;
  selectedParty: string;
  selectParty: (id: string) => void;
}) {
  const uid = useId().replace(/:/g, "");
  const responded = uniqueResponses(answers).filter(
    (r) => r.answer.value !== null,
  );
  const available = bank.categories.filter((c) =>
    responded.some((r) => r.question.category === c.id),
  );
  const [mode, setMode] = useState<"responses" | "themes">("responses");
  const [category, setCategory] = useState(
    available[0]?.id ?? bank.categories[0].id,
  );
  const [axisIds, setAxisIds] = useState<{ x?: string; y?: string }>({});
  const [mapId, setMapId] = useState(
    () =>
      [...bank.maps].sort(
        (a, b) =>
          userAxis(answers, b.x).contributions.length +
          userAxis(answers, b.y).contributions.length -
          (userAxis(answers, a.x).contributions.length +
            userAxis(answers, a.y).contributions.length),
      )[0].id,
  );
  const entries = responded.filter((r) => r.question.category === category);
  const preferredPair = coordinatePair(entries);
  const first =
    entries.find((r) => r.question.id === axisIds.x) ?? preferredPair[0];
  const second =
    entries.find(
      (r) =>
        r.question.id === axisIds.y && r.question.id !== first?.question.id,
    ) ??
    (preferredPair[1]?.question.id !== first?.question.id
      ? preferredPair[1]
      : undefined) ??
    entries.find((r) => r.question.id !== first?.question.id);
  const map = bank.maps.find((m) => m.id === mapId)!;
  const xUser =
    mode === "themes"
      ? userAxis(answers, map.x).value
      : first
        ? first.answer.value! * 50
        : null;
  const yUser =
    mode === "themes"
      ? userAxis(answers, map.y).value
      : second
        ? second.answer.value! * 50
        : null;
  const xLabel =
    mode === "themes"
      ? map.x.label
      : (first?.question.text ?? "Primera propuesta respondida");
  const yLabel =
    mode === "themes"
      ? map.y.label
      : (second?.question.text ?? "Segunda propuesta pendiente");
  const points = bank.parties.map((p) => {
    const x =
      mode === "themes"
        ? documentaryAxis(p.id, map.x)
        : {
            value:
              first?.question.positions[p.id]?.value == null ||
              !first?.question.positions[p.id]?.evidence.length
                ? null
                : first.question.positions[p.id].value! * 50,
            count:
              first?.question.positions[p.id]?.value == null ||
              !first?.question.positions[p.id]?.evidence.length
                ? 0
                : 1,
            total: 1,
          };
    const y =
      mode === "themes"
        ? documentaryAxis(p.id, map.y)
        : {
            value:
              second?.question.positions[p.id]?.value == null ||
              !second?.question.positions[p.id]?.evidence.length
                ? null
                : second.question.positions[p.id].value! * 50,
            count:
              second?.question.positions[p.id]?.value == null ||
              !second?.question.positions[p.id]?.evidence.length
                ? 0
                : 1,
            total: 1,
          };
    return { ...p, x, y };
  });
  const groups = new Map<string, typeof points>();
  points
    .filter((p) => p.x.value !== null && p.y.value !== null)
    .forEach((p) => {
      const key = `${p.x.value}:${p.y.value}`;
      groups.set(key, [...(groups.get(key) ?? []), p]);
    });
  const selected = points.find((p) => p.id === selectedParty)!;
  const px = (v: number) => 360 + v * 2.6,
    py = (v: number) => 260 - v * 1.9;
  return (
    <section
      className="result-card political-map"
      aria-labelledby={`${uid}-title`}
    >
      <div className="political-map-head">
        <h2 id={`${uid}-title`}>Tus coordenadas</h2>
        <div
          className="segmented"
          role="group"
          aria-label="Tipo de coordenadas"
        >
          <button
            aria-pressed={mode === "responses"}
            onClick={() => setMode("responses")}
          >
            Por propuestas
          </button>
          <button
            aria-pressed={mode === "themes"}
            onClick={() => setMode("themes")}
          >
            Ejes temáticos
          </button>
        </div>
      </div>
      {mode === "responses" ? (
        <div className="political-map-controls">
          <label>
            Tema
            <select
              aria-label="Tema de las coordenadas"
              value={category}
              onChange={(e) => {
                setCategory(e.target.value);
                setAxisIds({});
              }}
            >
              {(available.length ? available : bank.categories).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))}
            </select>
          </label>
          <p>
            Dos propuestas del mismo tema: cada eje muestra tu respuesta y las
            posiciones documentadas de los partidos sobre esa misma propuesta.
            −100 es muy en desacuerdo; +100, muy de acuerdo.
          </p>
        </div>
      ) : (
        <div className="political-map-controls">
          <label>
            Mapa
            <select
              aria-label="Mapa de ejes temáticos"
              value={mapId}
              onChange={(e) => setMapId(e.target.value)}
            >
              {bank.maps.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.title}
                </option>
              ))}
            </select>
          </label>
          <p>
            Índices formados por las propuestas enumeradas en el desglose. Tu
            posición usa tus respuestas ponderadas; cada partido usa sus
            indicadores documentados. Las coberturas pueden ser distintas.
          </p>
        </div>
      )}
      <div className="political-axis-definitions">
        <p>
          <b>X · Horizontal</b>
          {xLabel}
        </p>
        <p>
          <b>Y · Vertical</b>
          {yLabel}
        </p>
      </div>
      <div className="political-map-key">
        <span>
          <i className="user-key" />
          Tú · doble aro animado
        </span>
        <span>
          <i className="party-key" />
          Partidos · siglas dentro del punto
        </span>
      </div>
      <svg
        className="political-map-svg"
        viewBox="0 0 720 540"
        role="img"
        aria-label={`Coordenadas. Eje X: ${xLabel}. Eje Y: ${yLabel}. Tú: X ${number(xUser)}, Y ${number(yUser)}.`}
      >
        {[-100, -50, 0, 50, 100].map((n) => (
          <g key={n}>
            <path
              className="grid-line"
              d={`M100 ${py(n)}H620 M${px(n)} 70V450`}
            />
            <text x={px(n)} y="473" textAnchor="middle">
              {n > 0 ? `+${n}` : n}
            </text>
            <text x="85" y={py(n) + 4} textAnchor="end">
              {n > 0 ? `+${n}` : n}
            </text>
          </g>
        ))}
        <path d="M100 260H620 M360 70V450" className="axis-line" />
        <text x="360" y="510" textAnchor="middle">
          X ·{" "}
          {mode === "responses"
            ? "Acuerdo con la propuesta X"
            : map.x.label.length > 65
              ? map.x.label.slice(0, 62) + "…"
              : map.x.label}
        </text>
        <text x="100" y="35">
          Y ·{" "}
          {mode === "responses"
            ? "Acuerdo con la propuesta Y"
            : map.y.label.length > 65
              ? map.y.label.slice(0, 62) + "…"
              : map.y.label}
        </text>
        {[...groups.values()].map((group) => {
          const active = group.find((p) => p.id === selectedParty) ?? group[0],
            x = px(active.x.value!),
            y = py(active.y.value!);
          return (
            <g
              key={group.map((p) => p.id).join("-")}
              className="political-party-point"
              onClick={() =>
                selectParty(
                  group[
                    (group.findIndex((p) => p.id === selectedParty) + 1) %
                      group.length
                  ].id,
                )
              }
            >
              <circle
                cx={x}
                cy={y}
                r={group.some((p) => p.id === selectedParty) ? 17 : 14}
                fill={colors[active.id]}
                stroke="var(--surface)"
                strokeWidth="2"
              />
              <text
                x={x}
                y={y + 4}
                textAnchor="middle"
                className="party-point-code"
              >
                {group.length > 1
                  ? `${short[active.id] ?? active.name.slice(0, 6)} +${group.length - 1}`
                  : (short[active.id] ?? active.name.slice(0, 6))}
              </text>
              <title>{`${group.map((p) => p.name).join(", ")} · X ${number(active.x.value)} · Y ${number(active.y.value)}`}</title>
            </g>
          );
        })}
        {xUser !== null && yUser !== null ? (
          <g
            className="political-user-point"
            transform={`translate(${px(xUser)},${py(yUser)})`}
          >
            <circle r="25" className="user-position-pulse" />
            <circle r="19" className="user-position-ring" />
            <path d="M-8 0H8 M0-8V8" />
            <text
              x={xUser > 75 ? -32 : 32}
              y={yUser > 75 ? 32 : -28}
              textAnchor={xUser > 75 ? "end" : "start"}
            >
              Tú
            </text>
            <title>{`Tu posición: X ${number(xUser)}, Y ${number(yUser)}`}</title>
          </g>
        ) : xUser !== null ? (
          <g className="political-user-point partial">
            <path d={`M${px(xUser)} 70V450`} className="user-projection" />
            <text
              x={xUser > 75 ? px(xUser) - 12 : px(xUser) + 12}
              y="92"
              textAnchor={xUser > 75 ? "end" : "start"}
            >
              Tú · solo X
            </text>
          </g>
        ) : yUser !== null ? (
          <g className="political-user-point partial">
            <path d={`M100 ${py(yUser)}H620`} className="user-projection" />
            <text x="115" y={py(yUser) - 16}>
              Tú · solo Y
            </text>
          </g>
        ) : (
          <text x="360" y="284" textAnchor="middle">
            Todavía no hay respuestas para estos ejes
          </text>
        )}
      </svg>
      <p className="political-user-summary">
        <strong>Tú</strong> · X: {number(xUser)} · Y: {number(yUser)}
        {(xUser === null || yUser === null) &&
          " · Falta completar un eje; la línea discontinua muestra solo el eje respondido."}
      </p>
      {mode === "responses" && (
        <div className="political-axis-pickers">
          {[
            { key: "x" as const, item: first, label: "X" },
            { key: "y" as const, item: second, label: "Y" },
          ].map(({ key, item, label }) => (
            <label key={key}>
              {label}
              <select
                aria-label={`Propuesta del eje ${label}`}
                value={item?.question.id ?? ""}
                onChange={(e) =>
                  setAxisIds((a) => ({ ...a, [key]: e.target.value }))
                }
              >
                <option value="" disabled>
                  Responde otra propuesta de este tema
                </option>
                {entries
                  .filter(
                    (r) => key === "x" || r.question.id !== first?.question.id,
                  )
                  .map((r) => (
                    <option key={r.question.id} value={r.question.id}>
                      {r.question.text}
                    </option>
                  ))}
              </select>
            </label>
          ))}
        </div>
      )}
      <div className="political-party-legend" aria-label="Partidos del mapa">
        {points.map((p) => (
          <button
            key={p.id}
            aria-pressed={p.id === selectedParty}
            onClick={() => selectParty(p.id)}
            title={`X ${number(p.x.value)}; Y ${number(p.y.value)}`}
          >
            {logos[p.id] && <img src={logos[p.id]} alt="" />}
            <i style={{ background: colors[p.id] }} />
            <span>
              {p.name}
              <small>
                {p.x.value !== null && p.y.value !== null
                  ? `X ${number(p.x.value)} · Y ${number(p.y.value)}`
                  : p.x.value !== null
                    ? `Solo X: ${number(p.x.value)}`
                    : p.y.value !== null
                      ? `Solo Y: ${number(p.y.value)}`
                      : "Sin posición documentada en estos ejes"}
              </small>
            </span>
          </button>
        ))}
      </div>
      <details className="political-position-why" open>
        <summary>
          {selected.x.value !== null && selected.y.value !== null
            ? `Por qué ${selected.name} está aquí`
            : `${selected.name} · datos disponibles`}
        </summary>
        {[
          { key: "x" as const, label: xLabel, entry: first },
          { key: "y" as const, label: yLabel, entry: second },
        ].map(({ key, label, entry }) => (
          <section key={key}>
            <h3>
              {key.toUpperCase()} · {label}
            </h3>
            <p>
              {number(selected[key].value)} · {selected[key].count} de{" "}
              {selected[key].total} indicadores documentados.
            </p>
            {mode === "responses" ? (
              <>
                <p>
                  {entry?.question.positions[selectedParty]?.basis ??
                    "No hay una posición documentada para esta decisión. No se coloca al partido en el centro ni se deduce su postura por su ideología."}
                </p>
                {entry?.question.positions[selectedParty] && (
                  <EvidenceLinks
                    evidence={entry.question.positions[selectedParty].evidence}
                  />
                )}
                {entry && (
                  <p>
                    Respuesta del programa:{" "}
                    {entry.question.positions[selectedParty]?.value ??
                      "sin determinar"}{" "}
                    × 50. Tu respuesta: {entry.answer.value} × 50. La
                    importancia se conserva en el cálculo de afinidad.
                  </p>
                )}
              </>
            ) : (
              <>
                {documentaryAxis(selectedParty, map[key]).contributions.map(
                  (c, i) => (
                    <details key={i}>
                      <summary>
                        {c.indicator.label}: {number(c.value)}
                      </summary>
                      <p>
                        {c.value !== null
                          ? `Posición × 50 × dirección ${c.indicator.direction}`
                          : "Sin evidencia suficiente"}
                      </p>
                      {c.entries.map((e) => (
                        <div key={e.question.id}>
                          <p>{e.question.text}</p>
                          <p>{e.position.basis}</p>
                          <EvidenceLinks evidence={e.position.evidence} />
                        </div>
                      ))}
                    </details>
                  ),
                )}
                <p>
                  Tu eje: media de (respuesta / 2 × dirección), ponderada por
                  importancia 1, 2 o 3. Partido: media de indicadores conocidos,
                  cada uno con peso uno.
                </p>
              </>
            )}
          </section>
        ))}
      </details>
    </section>
  );
}
