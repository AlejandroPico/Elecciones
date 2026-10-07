import { categories, type Category } from "../..";
import { partyScores, type Party, type Score } from "./model";
type Scores = Record<string, Score>;
export function CoordinateChart({
  category,
  scores,
  parties = [],
  compact = false,
}: {
  category: Category;
  scores: Scores;
  parties?: Party[];
  compact?: boolean;
}) {
  const [x, y] = category.axes;
  const sx = scores[x.id],
    sy = scores[y.id];
  const ready = sx.value !== null && sy.value !== null;
  const pos = (v: number) => 150 + v * 1.05;
  const py = (v: number) => 150 - v * 1.05;
  return (
    <div className={`coordinate-chart ${compact ? "compact" : ""}`}>
      <span className="chart-pole top">{y.high}</span>
      <div className="chart-middle">
        <span className="chart-pole left">{x.low}</span>
        <svg
          viewBox="0 0 300 300"
          role="img"
          aria-label={`Coordenadas de ${category.name}. ${ready ? `${x.name}: ${Math.round(sx.value!)} de 100; ${y.name}: ${Math.round(sy.value!)} de 100.` : "Faltan respuestas en uno o ambos ejes."}`}
        >
          <defs>
            <pattern
              id={`grid-${category.id}`}
              width="30"
              height="30"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 30 0 L 0 0 0 30"
                fill="none"
                className="grid-line"
                strokeWidth=".8"
              />
            </pattern>
          </defs>
          <rect
            x="15"
            y="15"
            width="270"
            height="270"
            fill={`url(#grid-${category.id})`}
            className="chart-border"
          />
          <path d="M15 150H285 M150 15V285" className="axis-line" />
          {[-100, -50, 50, 100].map((v) => (
            <g key={v}>
              <text x={pos(v)} y="164" className="tick" textAnchor="middle">
                {v}
              </text>
              <text x="139" y={py(v) + 3} className="tick" textAnchor="end">
                {v}
              </text>
            </g>
          ))}
          {parties.map((p) => {
            const s = partyScores(p),
              a = s[x.id].value,
              b = s[y.id].value;
            return a !== null && b !== null ? (
              <g key={p.id}>
                <circle
                  cx={pos(a)}
                  cy={py(b)}
                  r="6"
                  fill={p.color}
                  stroke="var(--surface)"
                  strokeWidth="2"
                />
                <title>
                  {p.name}: {Math.round(a)}, {Math.round(b)}
                </title>
              </g>
            ) : null;
          })}
          {ready && (
            <g
              className="user-point"
              style={{
                transform: `translate(${pos(sx.value!)}px, ${py(sy.value!)}px)`,
              }}
            >
              <circle r="17" className="point-halo" />
              <circle r="6" className="point-core" />
              <circle r="2" fill="var(--surface)" />
            </g>
          )}
          {!ready && (
            <g>
              <text x="150" y="187" className="empty-label" textAnchor="middle">
                Sin posición suficiente
              </text>
            </g>
          )}
        </svg>
        <span className="chart-pole right">{x.high}</span>
      </div>
      <span className="chart-pole bottom">{y.low}</span>
    </div>
  );
}
export function RadarChart({
  scores,
  parties = [],
}: {
  scores: Scores;
  parties?: Party[];
}) {
  const selectedAxes = categories.map((c) => c.axes[0]);
  const point = (i: number, radius: number) => {
    const angle = (i * Math.PI) / 4 - Math.PI / 2;
    return [220 + Math.cos(angle) * radius, 190 + Math.sin(angle) * radius];
  };
  const polygon = (radius: number) =>
    selectedAxes.map((_, i) => point(i, radius).join(",")).join(" ");
  const path = (s: Scores) =>
    selectedAxes.every((a) => s[a.id].value !== null)
      ? selectedAxes
          .map((a, i) =>
            point(i, ((s[a.id].value! + 100) / 200) * 125).join(","),
          )
          .join(" ")
      : null;
  const user = path(scores);
  return (
    <svg
      viewBox="0 0 440 380"
      className="radar"
      role="img"
      aria-label="Resumen de ocho dimensiones. El centro corresponde a menos 100 y el borde a más 100. Los ejes sin respuestas no se representan."
    >
      {[0.25, 0.5, 0.75, 1].map((r) => (
        <polygon key={r} points={polygon(125 * r)} className="radar-grid" />
      ))}
      {selectedAxes.map((a, i) => {
        const [x, y] = point(i, 125),
          [lx, ly] = point(i, 157);
        const value = scores[a.id].value;
        return (
          <g key={a.id}>
            <line x1="220" y1="190" x2={x} y2={y} className="grid-line" />
            <text
              x={lx}
              y={ly}
              textAnchor={
                i === 0 || i === 4 ? "middle" : i < 4 ? "start" : "end"
              }
              className="radar-label"
            >
              {a.name.split(" ").map((word, j) => (
                <tspan key={j} x={lx} dy={j ? 13 : 0}>
                  {word}
                </tspan>
              ))}
            </text>
            {value !== null && !user && (
              <circle
                cx={point(i, ((value + 100) / 200) * 125)[0]}
                cy={point(i, ((value + 100) / 200) * 125)[1]}
                r="5"
                className="point-core"
              />
            )}
          </g>
        );
      })}
      {parties.map((p) => {
        const points = path(partyScores(p));
        return points ? (
          <polygon
            key={p.id}
            points={points}
            fill="none"
            stroke={p.color}
            strokeWidth="2"
            strokeDasharray="5 4"
          />
        ) : null;
      })}
      {user && <polygon points={user} className="radar-user" />}
      <text x="220" y="194" textAnchor="middle" className="tick">
        −100
      </text>
    </svg>
  );
}
export function AxisRows({
  category,
  scores,
}: {
  category: Category;
  scores: Scores;
}) {
  return (
    <div className="axis-rows">
      {category.axes.map((axis) => {
        const s = scores[axis.id];
        return (
          <div className="axis-row" key={axis.id}>
            <div className="axis-row-title">
              <span>{axis.name}</span>
              <span>
                {s.value === null
                  ? "Sin datos"
                  : `${s.value > 0 ? "+" : ""}${Math.round(s.value)}`}
              </span>
            </div>
            <div className="axis-track">
              <i />
              {s.value !== null && (
                <b style={{ left: `${(s.value + 100) / 2}%` }} />
              )}
            </div>
            <div className="axis-ends">
              <span>{axis.low}</span>
              <span>{axis.high}</span>
            </div>
            <small>
              {s.answered} de {s.total} preguntas respondidas
            </small>
          </div>
        );
      })}
    </div>
  );
}
