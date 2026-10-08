import { useEffect, useRef, useState } from "react";
import { ChevronLeft, ChevronRight, Pause, Play, Search } from "lucide-react";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";
import { Portrait } from "../../Políticos/interfaz/Retrato";
import Sources from "../../src/app/Sources";
import { dateLabel, snapshotAt } from "./government-model";
import {
  congressChronology,
  congressLegislatures,
  congressGroupsAt,
  congressGovernmentStages,
  congressStageContains,
  congressTermAt,
  congressDiagramPoints,
  congressGroupColor,
  type CongressLegislature,
  type DeputyMandate,
  type CongressGroup,
} from "./congress-model";
import "./congress.css";

type NamedPosition = { member: DeputyMandate; group: CongressGroup };
function CongressHemicycle({
  legislature,
  date,
  openPerson,
}: {
  legislature: CongressLegislature;
  date: string;
  openPerson: (id: string) => void;
}) {
  const groups = congressGroupsAt(legislature, date);
  const positions: NamedPosition[] = groups.flatMap((g) =>
    g.members.map((member) => ({ member, group: g.group })),
  );
  const total = positions.length;
  const [query, setQuery] = useState("");
  const [groupFilter, setGroupFilter] = useState<number | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [focusIndex, setFocusIndex] = useState(0);
  const refs = useRef<(SVGGElement | null)[]>([]);
  const selected = positions.find((p) => p.member.person === selectedId);
  const person = selected && findPerson(selected.member.person);
  const normalize = (value: string) =>
    value
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase("es");
  const matches = (p: NamedPosition) =>
    (groupFilter === null || p.group.code === groupFilter) &&
    normalize(`${p.member.name} ${p.member.constituency}`).includes(
      normalize(query),
    );
  const found = positions.filter(matches);
  const points = congressDiagramPoints(Math.max(350, total));
  const tabIndex = positions[focusIndex] ? focusIndex : 0;
  useEffect(() => {
    setSelectedId(null);
    setGroupFilter(null);
    setFocusIndex(0);
  }, [date, legislature.id]);
  return (
    <section
      className="congress-hemicycle"
      aria-labelledby="congress-hemicycle-title"
    >
      <div className="congress-graph-heading">
        <h2 id="congress-hemicycle-title">Hemiciclo</h2>
        <span>
          {total} mandatos documentados · {legislature.label}
        </span>
      </div>
      <div className="congress-search">
        <label>
          <Search size={15} />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar diputado o circunscripción"
            aria-label="Buscar diputado en el hemiciclo"
          />
        </label>
        <select
          value={groupFilter ?? "all"}
          onChange={(e) =>
            setGroupFilter(
              e.target.value === "all" ? null : Number(e.target.value),
            )
          }
          aria-label="Filtrar grupo parlamentario del Congreso"
        >
          <option value="all">Todos los grupos</option>
          {groups.map((g) => (
            <option key={g.group.code} value={g.group.code}>
              {g.group.shortName} · {g.members.length}
            </option>
          ))}
        </select>
      </div>
      <div className="congress-diagram-layout">
        <svg
          className="congress-diagram"
          viewBox="0 0 1040 550"
          role="group"
          aria-label={`Hemiciclo esquemático del Congreso. ${total} diputados. Las flechas recorren los mandatos y Enter abre la ficha.`}
        >
          {points.map((point, index) => {
            const item = positions[index];
            if (!item)
              return (
                <rect
                  key={`vacancy-${index}`}
                  x={point.x - 5}
                  y={point.y - 5}
                  width={10}
                  height={10}
                  className="congress-vacancy"
                >
                  <title>Sin mandato acreditado en esta fecha</title>
                </rect>
              );
            const highlighted = item.member.person === selectedId;
            return (
              <g
                key={item.member.person}
                ref={(node) => {
                  refs.current[index] = node;
                }}
                role="button"
                tabIndex={index === tabIndex ? 0 : -1}
                aria-label={`${item.member.name} · ${item.group.shortName} · ${item.member.constituency}`}
                className={`congress-position ${highlighted ? "selected" : ""}`}
                style={{ opacity: matches(item) ? 1 : 0.14 }}
                onPointerEnter={() => setSelectedId(item.member.person)}
                onFocus={() => {
                  setSelectedId(item.member.person);
                  setFocusIndex(index);
                }}
                onClick={() => openPerson(item.member.person)}
                onKeyDown={(e) => {
                  const offset =
                    e.key === "ArrowRight" || e.key === "ArrowDown"
                      ? 1
                      : e.key === "ArrowLeft" || e.key === "ArrowUp"
                        ? -1
                        : 0;
                  if (offset) {
                    e.preventDefault();
                    const next = (index + offset + total) % total;
                    setFocusIndex(next);
                    refs.current[next]?.focus();
                  }
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    openPerson(item.member.person);
                  }
                  if (e.key === "Home" || e.key === "End") {
                    e.preventDefault();
                    refs.current[e.key === "Home" ? 0 : total - 1]?.focus();
                  }
                }}
              >
                <circle cx={point.x} cy={point.y} r={11} fill="transparent" />
                <rect
                  x={point.x - 5.5}
                  y={point.y - 5.5}
                  width={11}
                  height={11}
                  fill={congressGroupColor(item.group.name)}
                />
                <title>
                  {item.member.name} · {item.group.shortName} ·{" "}
                  {item.member.constituency}
                </title>
              </g>
            );
          })}
          <text x={520} y={470} textAnchor="middle" className="congress-total">
            {total}
          </text>
          <text
            x={520}
            y={495}
            textAnchor="middle"
            className="congress-total-label"
          >
            MANDATOS DOCUMENTADOS
          </text>
        </svg>
        <aside
          className="congress-inspector"
          aria-label="Diputado seleccionado"
          aria-live="polite"
        >
          {selected ? (
            <>
              <div className="congress-deputy-portrait">
                {person ? (
                  <Portrait person={person} />
                ) : (
                  <span>{selected.member.name}</span>
                )}
              </div>
              <h3>{selected.member.name}</h3>
              <p style={{ color: congressGroupColor(selected.group.name) }}>
                {selected.group.shortName}
              </p>
              <dl>
                <dt>Circunscripción</dt>
                <dd>{selected.member.constituency || "No publicada"}</dd>
                <dt>Alta del mandato</dt>
                <dd>
                  {selected.member.start
                    ? dateLabel(selected.member.start)
                    : "No publicada"}
                </dd>
                {selected.member.end && (
                  <>
                    <dt>Baja del mandato</dt>
                    <dd>{dateLabel(selected.member.end)}</dd>
                  </>
                )}
                {selected.member.formation && (
                  <>
                    <dt>Candidatura electoral</dt>
                    <dd>{selected.member.formation}</dd>
                  </>
                )}
              </dl>
              <button
                className="text-button"
                onClick={() => openPerson(selected.member.person)}
              >
                Ver ficha
              </button>
              <Sources
                sources={[
                  {
                    label: "Ficha oficial · Congreso",
                    url: selected.member.source,
                  },
                  {
                    label: "Adscripción parlamentaria",
                    url: selected.group.source,
                  },
                ]}
              />
            </>
          ) : (
            <>
              <span className="eyebrow">Congreso de los Diputados</span>
              <h3>{legislature.label}</h3>
              <p>{dateLabel(date)}</p>
              <span className="congress-inspector-count">
                {total}
                <small>mandatos documentados</small>
              </span>
              <p className="small-note">
                Nombre y ficha de cada diputado al señalar su posición.
              </p>
            </>
          )}
        </aside>
      </div>
      <div className="seat-legend congress-group-legend">
        {groups.map((g) => (
          <button
            key={g.group.code}
            aria-pressed={groupFilter === g.group.code}
            onClick={() =>
              setGroupFilter(groupFilter === g.group.code ? null : g.group.code)
            }
          >
            <i style={{ background: congressGroupColor(g.group.name) }} />
            <span>{g.group.shortName}</span>
            <b>{g.members.length}</b>
          </button>
        ))}
      </div>
      {(query || groupFilter !== null) && (
        <div className="congress-search-results" aria-live="polite">
          <span>{found.length} coincidencias</span>
          {found.slice(0, 12).map((p) => (
            <button
              key={p.member.person}
              className="inline-link"
              onClick={() => openPerson(p.member.person)}
            >
              {p.member.name}
            </button>
          ))}
        </div>
      )}
      <p className="small-note congress-seating-note">
        Distribución esquemática por grupos, sin números de asiento físico. Los
        mandatos y adscripciones están fechados; el plano oficial de asientos de
        estas fechas está pendiente de incorporar.{" "}
        {total < 350 &&
          `${350 - total} posiciones sin mandato acreditado en esta fecha.`}
      </p>
      {total > 350 && (
        <p className="small-note">
          El inventario acredita más de 350 mandatos simultáneos en esta fecha.
          Se muestran todos, sin recortar el registro; la coincidencia temporal
          requiere revisión.
        </p>
      )}
    </section>
  );
}

export default function Congress({
  selectedSnapshot,
  openCongress,
  openPerson,
  active = true,
}: {
  selectedSnapshot?: string;
  openCongress: (id: string) => void;
  openPerson: (id: string) => void;
  active?: boolean;
}) {
  const [position, setPosition] = useState(() =>
    Math.max(
      0,
      congressChronology.findIndex((s) => s.id === selectedSnapshot) >= 0
        ? congressChronology.findIndex((s) => s.id === selectedSnapshot)
        : congressChronology.length - 1,
    ),
  );
  const [mode, setMode] = useState<"legislatures" | "timeline">("legislatures");
  const [stageId, setStageId] = useState("all");
  const [playing, setPlaying] = useState(false);
  useEffect(() => {
    setPlaying(false);
    if (!active) return;
    const index = congressChronology.findIndex(
      (s) => s.id === selectedSnapshot,
    );
    setPosition(index < 0 ? congressChronology.length - 1 : index);
  }, [selectedSnapshot, active]);
  const current = congressChronology[position];
  const stages = current ? congressGovernmentStages(current.legislature) : [];
  const stage = stages.find((s) => s.id === stageId);
  const effectiveStage =
    stage && current && congressStageContains(stage, current.date)
      ? stage
      : undefined;
  const steps = congressChronology.filter((s) =>
    mode === "timeline"
      ? true
      : s.legislature.id === current?.legislature.id &&
        (!effectiveStage || congressStageContains(effectiveStage, s.date)),
  );
  const localPosition = steps.findIndex((s) => s.id === current?.id);
  useEffect(() => {
    if (
      !playing ||
      !active ||
      localPosition < 0 ||
      localPosition >= steps.length - 1
    ) {
      setPlaying(false);
      return;
    }
    const timer = setTimeout(
      () =>
        setPosition(
          congressChronology.findIndex(
            (s) => s.id === steps[localPosition + 1].id,
          ),
        ),
      1800,
    );
    return () => clearTimeout(timer);
  }, [playing, active, position, mode, stageId]);
  if (!current)
    return <p className="small-note">No hay composiciones documentadas.</p>;
  function choose(id: string) {
    const index = congressChronology.findIndex((s) => s.id === id);
    if (index < 0) return;
    setPlaying(false);
    setPosition(index);
    openCongress(id);
  }
  function person(id: string) {
    setPlaying(false);
    if (selectedSnapshot !== current.id) openCongress(current.id);
    openPerson(id);
  }
  const legislature = current.legislature;
  const executive = snapshotAt(current.date);
  const board = legislature.board.filter((term) =>
    congressTermAt(term, current.date),
  );
  return (
    <div className="government-archive congress-archive">
      <div className="government-toolbar">
        <div
          className="archive-tabs"
          role="group"
          aria-label="Vista del Congreso"
        >
          <button
            aria-pressed={mode === "legislatures"}
            onClick={() => {
              setMode("legislatures");
              setPlaying(false);
            }}
          >
            Por legislaturas
          </button>
          <button
            aria-pressed={mode === "timeline"}
            onClick={() => {
              setMode("timeline");
              setStageId("all");
              setPlaying(false);
            }}
          >
            Cronología
          </button>
        </div>
        <select
          aria-label="Elegir legislatura del Congreso"
          value={legislature.id}
          onChange={(e) => {
            setStageId("all");
            choose(
              congressChronology
                .filter((s) => s.legislature.id === e.target.value)
                .at(-1)!.id,
            );
          }}
        >
          {congressLegislatures.map((leg) => (
            <option key={leg.id} value={leg.id}>
              {leg.label} · {leg.start.slice(0, 4)}
            </option>
          ))}
        </select>
      </div>
      {mode === "legislatures" && (
        <div className="congress-executive-filter">
          <select
            aria-label="Filtrar Congreso por composición del Gobierno"
            value={effectiveStage?.id ?? "all"}
            onChange={(e) => {
              const next = stages.find((s) => s.id === e.target.value);
              setStageId(next?.id ?? "all");
              const snapshot = congressChronology.find(
                (s) =>
                  s.legislature.id === legislature.id &&
                  (!next || congressStageContains(next, s.date)),
              );
              if (snapshot) choose(snapshot.id);
            }}
          >
            <option value="all">Todos los periodos de esta legislatura</option>
            {stages.map((s) => (
              <option
                key={s.id}
                value={s.id}
                disabled={
                  !congressChronology.some(
                    (snap) =>
                      snap.legislature.id === legislature.id &&
                      congressStageContains(s, snap.date),
                  )
                }
              >
                {s.government.name} · {s.label} · {dateLabel(s.date)}
              </option>
            ))}
          </select>
        </div>
      )}
      <section className="government-time">
        <div className="time-heading">
          <div>
            <span>Congreso · {legislature.label}</span>
            <h2 aria-live="polite">{dateLabel(current.date)}</h2>
          </div>
          <button
            className="icon-button"
            aria-label={
              playing
                ? "Pausar cronología del Congreso"
                : "Reproducir cronología del Congreso"
            }
            disabled={localPosition === steps.length - 1 && !playing}
            onClick={() => setPlaying(!playing)}
          >
            {playing ? <Pause size={18} /> : <Play size={18} />}
          </button>
        </div>
        <div className="timeline-control">
          <button
            className="icon-button"
            aria-label="Composición anterior del Congreso"
            disabled={localPosition <= 0}
            onClick={() => choose(steps[localPosition - 1].id)}
          >
            <ChevronLeft size={17} />
          </button>
          <input
            type="range"
            min={0}
            max={Math.max(0, steps.length - 1)}
            value={Math.max(0, localPosition)}
            aria-label="Fecha de composición del Congreso"
            aria-valuetext={dateLabel(current.date)}
            onChange={(e) => choose(steps[Number(e.target.value)].id)}
          />
          <button
            className="icon-button"
            aria-label="Composición siguiente del Congreso"
            disabled={localPosition >= steps.length - 1}
            onClick={() => choose(steps[localPosition + 1].id)}
          >
            <ChevronRight size={17} />
          </button>
        </div>
        <div className="time-extents">
          <span>{dateLabel(steps[0]?.date ?? current.date)}</span>
          <span>{dateLabel(steps.at(-1)?.date ?? current.date)}</span>
        </div>
        {executive && (
          <p className="congress-executive small-note">
            Ejecutivo en el archivo:{" "}
            <button
              className="inline-link"
              onClick={() =>
                person(
                  executive.members.find((m) => m.level === "president")!
                    .person,
                )
              }
            >
              {executive.government.name}
            </button>{" "}
            · {executive.label}
            {executive.date.length === 7 &&
              " · fecha del gabinete con precisión mensual"}
          </p>
        )}
        {legislature.number === 15 && (
          <p className="small-note">
            Composiciones anteriores a la disolución del 6 de octubre de 2026.
            La Diputación Permanente no se representa como un Pleno de 350
            diputados.
          </p>
        )}
      </section>
      <CongressHemicycle
        legislature={legislature}
        date={current.date}
        openPerson={person}
      />
      <section className="congress-board">
        <h2>Mesa del Congreso</h2>
        <div className="congress-board-grid">
          {board.map((term) => {
            const p = findPerson(term.person);
            return (
              <button
                key={`${term.person}-${term.role}`}
                className="government-node"
                onClick={() => person(term.person)}
              >
                <div className="government-portrait">
                  {p && <Portrait person={p} />}
                </div>
                <div>
                  <small>{term.role}</small>
                  <strong>{p?.name ?? term.name}</strong>
                  <span className="senate-term-date">
                    {term.start && dateLabel(term.start)}
                    {term.end && ` – ${dateLabel(term.end)}`}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
        {!board.length && (
          <p className="small-note">
            No hay integrantes de la Mesa acreditados en esta fecha.
          </p>
        )}
      </section>
      <Sources
        sources={[
          {
            label: "Congreso · datos abiertos de diputados",
            url: legislature.source,
          },
          { label: "Congreso · Mesa histórica", url: legislature.mesaSource },
          {
            label: "Congreso · grupos parlamentarios",
            url: "https://www.congreso.es/grupos/composicion-en-la-legislatura",
          },
        ]}
      />
    </div>
  );
}
