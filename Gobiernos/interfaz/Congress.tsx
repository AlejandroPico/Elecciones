import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Pause, Play } from "lucide-react";
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
} from "./congress-model";
import Hemicycle from "./Hemicycle";
import "./congress.css";

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
      </div>
      <div
        className="government-library"
        aria-label="Biblioteca de legislaturas del Congreso"
      >
        {congressLegislatures.map((leg) => (
          <button
            key={leg.id}
            className={leg.id === legislature.id ? "active" : ""}
            aria-pressed={leg.id === legislature.id}
            onClick={() => {
              setStageId("all");
              choose(
                congressChronology
                  .filter((s) => s.legislature.id === leg.id)
                  .at(-1)!.id,
              );
            }}
          >
            <span>{leg.start.slice(0, 4)}</span>
            <strong>{leg.label}</strong>
          </button>
        ))}
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
      <Hemicycle
        chamber="Congreso"
        label={legislature.label}
        date={current.date}
        capacity={350}
        groups={congressGroupsAt(legislature, current.date).map((g) => ({
          id: String(g.group.code),
          name: g.group.name,
          label: g.group.shortName,
          source: g.group.source,
          members: g.members,
        }))}
        openPerson={person}
        note="Distribución esquemática por grupos, sin números de asiento físico. Los mandatos y adscripciones están fechados; el plano oficial de asientos de estas fechas está pendiente de incorporar."
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
