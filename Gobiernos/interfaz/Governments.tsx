import { useEffect, useState } from "react";
import {
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  Pause,
  Play,
} from "lucide-react";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";
import { structureSnapshot } from "../XV Legislatura/estructura";
import { chronology, dateLabel, governments } from "./government-model";
import { Portrait } from "../../Políticos/interfaz/Retrato";
type Member = (typeof chronology)[number]["members"][number];
export default function Governments({
  openPerson,
  selectedSnapshot,
  openGovernment,
  active = true,
}: {
  openPerson: (id: string) => void;
  selectedSnapshot?: string;
  openGovernment?: (id: string) => void;
  active?: boolean;
}) {
  const [mode, setMode] = useState<"governments" | "timeline">("governments");
  const [position, setPosition] = useState(() => {
    const selected = chronology.findIndex((c) => c.id === selectedSnapshot);
    return selected >= 0 ? selected : chronology.length - 1;
  });
  const [playing, setPlaying] = useState(false);
  useEffect(() => {
    if (!active) { setPlaying(false); return; }
    if (openGovernment) {
      const next = chronology.findIndex((c) => c.id === selectedSnapshot);
      setPosition(next >= 0 ? next : chronology.length - 1);
      setPlaying(false);
    }
  }, [selectedSnapshot, active]);
  const current = chronology[position];
  const government = current.government;
  const president = current.members.find((m) => m.level === "president");
  const vice = current.members.filter((m) => m.level === "vicepresident");
  const ministers = current.members.filter((m) => m.level === "minister");
  const steps =
    mode === "timeline"
      ? chronology
      : chronology.filter((c) => c.government.id === government.id);
  const localPosition = steps.findIndex((c) => c.id === current.id);
  useEffect(() => {
    if (!playing) return;
    if (localPosition >= steps.length - 1) {
      setPlaying(false);
      return;
    }
    const timer = setTimeout(
      () =>
        setPosition(
          chronology.findIndex((c) => c.id === steps[localPosition + 1].id),
        ),
      1800,
    );
    return () => clearTimeout(timer);
  }, [playing, localPosition, steps, mode]);
  function choose(id: string) {
    setPlaying(false);
    setPosition(chronology.findIndex((c) => c.id === id));
    openGovernment?.(id);
  }
  const personNode = (m: Member, className = "") => {
    const p = findPerson(m.person);
    return (
      <button
        key={m.person + m.role}
        className={`government-node ${className}`}
        onClick={() => {
          if (selectedSnapshot !== current.id) openGovernment?.(current.id);
          openPerson(m.person);
        }}
        aria-label={`Ficha de ${p?.name ?? m.name}, ${m.role}`}
      >
        <div className="government-portrait">
          {p ? (
            <Portrait key={p.id} person={p} />
          ) : (
            <span>{m.name.slice(0, 2)}</span>
          )}
        </div>
        <div>
          <small>{m.role}</small>
          <strong>{p?.name ?? m.name}</strong>
        </div>
      </button>
    );
  };
  return (
    <div className="government-archive">
      <div className="government-toolbar">
        <div
          className="archive-tabs"
          role="group"
          aria-label="Vista de gobiernos"
        >
          <button
            aria-pressed={mode === "governments"}
            onClick={() => {
              setMode("governments");
              setPlaying(false);
            }}
          >
            Por gobiernos
          </button>
          <button
            aria-pressed={mode === "timeline"}
            onClick={() => {
              setMode("timeline");
              setPlaying(false);
            }}
          >
            Cronología
          </button>
        </div>
        <select
          aria-label="Elegir gobierno por legislatura"
          value={government.id}
          onChange={(e) =>
            choose(
              governments.find((g) => g.id === e.target.value)!.cabinets.at(-1)!
                .id,
            )
          }
        >
          {governments.map((g) => (
            <option key={g.id} value={g.id}>
              {g.legislature} · {g.cabinets[0].date.slice(0, 4)} ·{" "}
              {g.cabinets.at(-1)?.members.find((m) => m.level === "president")
                ?.name ?? "Gobierno de España"}
            </option>
          ))}
        </select>
      </div>
      {mode === "governments" && (
        <div
          className="government-library"
          aria-label="Biblioteca de gobiernos"
        >
          {governments.map((g) => (
            <button
              className={g.id === government.id ? "active" : ""}
              key={g.id}
              onClick={() => choose(g.cabinets.at(-1)!.id)}
            >
              <span>{g.cabinets[0].date.slice(0, 4)}</span>
              <strong>{g.legislature}</strong>
            </button>
          ))}
        </div>
      )}
      <section className="government-time">
        <div className="time-heading">
          <div>
            <span>{government.name}</span>
            <h2 aria-live="polite">{dateLabel(current.date)}</h2>
          </div>
          <button
            className="icon-button"
            disabled={localPosition === steps.length - 1 && !playing}
            aria-label={playing ? "Pausar cronología" : "Reproducir cronología"}
            onClick={() => setPlaying(!playing)}
          >
            {playing ? <Pause size={18} /> : <Play size={18} />}
          </button>
        </div>
        <div className="timeline-control">
          <button
            className="icon-button"
            disabled={localPosition === 0}
            aria-label="Composición anterior"
            onClick={() => choose(steps[localPosition - 1].id)}
          >
            <ChevronLeft size={17} />
          </button>
          <input
            type="range"
            min="0"
            max={steps.length - 1}
            value={localPosition}
            aria-label="Fecha del registro de gobierno"
            aria-valuetext={dateLabel(current.date)}
            onChange={(e) => choose(steps[Number(e.target.value)].id)}
          />
          <button
            className="icon-button"
            disabled={localPosition === steps.length - 1}
            aria-label="Composición siguiente"
            onClick={() => choose(steps[localPosition + 1].id)}
          >
            <ChevronRight size={17} />
          </button>
        </div>
        <div className="time-extents">
          <span>{dateLabel(steps[0].date)}</span>
          <span>{dateLabel(steps.at(-1)!.date)}</span>
        </div>
        <p className="small-note">
          {current.label}.{" "}
          {current.date.length === 7
            ? "La fuente precisa el mes, no el día del cambio."
            : "Fecha del registro de composición."}
        </p>
      </section>
      <div className="government-organigram" key={current.id}>
        {president && (
          <div className="president-tier">
            {personNode(president, "president-node")}
          </div>
        )}
        {!!vice.length && (
          <section className="government-tier">
            <h3>Vicepresidencias</h3>
            <div className="vice-tier">{vice.map((m) => personNode(m))}</div>
          </section>
        )}
        <section className="government-tier">
          <h3>Departamentos ministeriales</h3>
          <p className="small-note">
            Los departamentos de las vicepresidencias figuran en sus propias
            tarjetas.
          </p>
          <div className="minister-tier">
            {ministers.map((m) => personNode(m))}
          </div>
        </section>
        {current.id === governments[0].cabinets.at(-1)!.id && (
          <section className="government-tier extended-structure">
            <h3>Defensa · órganos superiores y directivos</h3>
            <p className="small-note">
              Instantánea consultada el 7 de octubre de 2026. Otros
              departamentos y periodos pendientes de incorporar.
            </p>
            <div className="structure-branches">
              {structureSnapshot.nodes
                .filter((n) => n.level === 2)
                .map((n) => (
                  <div key={n.person} className="structure-branch">
                    {personNode({ ...n, level: "minister" })}
                    <div className="structure-children">
                      {structureSnapshot.nodes
                        .filter((c) => c.parent === n.person)
                        .map((c) => personNode({ ...c, level: "minister" }))}
                    </div>
                  </div>
                ))}
            </div>
          </section>
        )}
      </div>
      <a
        className="source-link"
        href={government.source}
        target="_blank"
        rel="noreferrer"
      >
        Composición histórica · La Moncloa <ArrowUpRight size={14} />
      </a>
      <p className="government-coverage small-note">
        Gabinetes del archivo institucional desde 1977. Fichas históricas,
        retratos y órganos de segundo y tercer nivel en ampliación. Las líneas
        agrupan niveles del Ejecutivo; no asignan todos los ministerios a una
        vicepresidencia.
      </p>

    </div>
  );
}
