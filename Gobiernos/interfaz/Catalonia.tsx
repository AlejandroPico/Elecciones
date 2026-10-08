import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Pause, Play } from "lucide-react";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";
import { Portrait } from "../../Políticos/interfaz/Retrato";
import Sources from "../../src/app/Sources";
import Hemicycle from "./Hemicycle";
import { dateLabel } from "./government-model";
import {
  catalanGovernments,
  catalanParliaments,
  catalanGovernmentChronology,
  catalanParliamentChronology,
  catalanTermAt,
  catalanGroupsAt,
  type CatalanTerm,
} from "./catalonia-model";

export default function Catalonia({
  section,
  selected,
  openSection,
  openPerson,
  active,
}: {
  section: "government" | "parliament";
  selected?: string;
  openSection: (id: string) => void;
  openPerson: (id: string) => void;
  active: boolean;
}) {
  const government = section === "government";
  const chronology = government
    ? catalanGovernmentChronology
    : catalanParliamentChronology;
  const periods = government ? catalanGovernments : catalanParliaments;
  const [position, setPosition] = useState(
    Math.max(
      0,
      chronology.findIndex((s) => s.id === selected) >= 0
        ? chronology.findIndex((s) => s.id === selected)
        : chronology.length - 1,
    ),
  );
  const [mode, setMode] = useState<"legislatures" | "timeline">("legislatures");
  const [playing, setPlaying] = useState(false);
  useEffect(() => {
    setPlaying(false);
    if (!active) return;
    const index = chronology.findIndex((s) => s.id === selected);
    setPosition(index < 0 ? chronology.length - 1 : index);
  }, [selected, active, section]);
  const current = chronology[position];
  const steps = chronology.filter(
    (s) => mode === "timeline" || s.period.id === current?.period.id,
  );
  const local = steps.findIndex((s) => s.id === current?.id);
  useEffect(() => {
    if (!playing || !active || local < 0 || local >= steps.length - 1) {
      setPlaying(false);
      return;
    }
    const timer = setTimeout(
      () =>
        setPosition(chronology.findIndex((s) => s.id === steps[local + 1].id)),
      1800,
    );
    return () => clearTimeout(timer);
  }, [playing, position, mode, active, section]);
  if (!current)
    return <p className="small-note">No hay composiciones documentadas.</p>;
  function choose(id: string) {
    setPlaying(false);
    setPosition(chronology.findIndex((s) => s.id === id));
    openSection(`cataluna:${section}:${id}`);
  }
  function person(id: string) {
    setPlaying(false);
    if (selected !== current.id)
      openSection(`cataluna:${section}:${current.id}`);
    openPerson(id);
  }
  function node(member: CatalanTerm) {
    const p = findPerson(member.person);
    return (
      <button
        className="government-node"
        key={member.person + member.role}
        onClick={() => person(member.person)}
      >
        <div className="government-portrait">
          {p && <Portrait person={p} />}
        </div>
        <div>
          <small>{member.role}</small>
          <strong>{p?.name ?? member.name}</strong>
          <span className="senate-term-date">
            {member.start && dateLabel(member.start)}
            {member.end && ` – ${dateLabel(member.end)}`}
          </span>
        </div>
      </button>
    );
  }
  const gp = government
    ? catalanGovernments.find((p) => p.id === current.period.id)
    : undefined;
  const pp = !government
    ? catalanParliaments.find((p) => p.id === current.period.id)
    : undefined;
  const cabinet = gp?.terms.filter((m) => catalanTermAt(m, current.date)) ?? [];
  // Cada persona aparece una vez en el organigrama; acumular competencias, no duplicar retratos.
  const members = [
    ...new Map(
      cabinet.map((m) => [
        m.person,
        {
          ...m,
          role: cabinet
            .filter((t) => t.person === m.person)
            .map((t) => t.role)
            .join(" · "),
          level: cabinet.find(
            (t) => t.person === m.person && t.level === "president",
          )
            ? "president"
            : cabinet.find((t) => t.person === m.person && t.level === "vice")
              ? "vice"
              : m.level,
        },
      ]),
    ).values(),
  ];
  const mesa =
    pp?.board.filter((m) => pp.currentOnly || catalanTermAt(m, current.date)) ??
    [];
  return (
    <div className="government-archive congress-archive catalonia-archive">
      <div className="government-toolbar">
        <div
          className="archive-tabs"
          role="group"
          aria-label={`Vista del ${government ? "Gobierno" : "Parlamento"} de Cataluña`}
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
              setPlaying(false);
            }}
          >
            Cronología
          </button>
        </div>
      </div>
      <div
        className="government-library"
        aria-label={`Biblioteca del ${government ? "Gobierno" : "Parlamento"} de Cataluña`}
      >
        {periods.map((p) => (
          <button
            key={p.id}
            className={p.id === current.period.id ? "active" : ""}
            aria-pressed={p.id === current.period.id}
            onClick={() =>
              choose(chronology.filter((s) => s.period.id === p.id).at(-1)!.id)
            }
          >
            <span>{p.start.slice(0, 4)}</span>
            <strong>{p.label}</strong>
          </button>
        ))}
      </div>
      <section className="government-time">
        <div className="time-heading">
          <div>
            <span>{gp?.name ?? current.period.label}</span>
            <h2 aria-live="polite">{dateLabel(current.date)}</h2>
          </div>
          <button
            className="icon-button"
            aria-label={
              playing
                ? "Pausar cronología de Cataluña"
                : "Reproducir cronología de Cataluña"
            }
            disabled={local >= steps.length - 1 && !playing}
            onClick={() => setPlaying(!playing)}
          >
            {playing ? <Pause size={18} /> : <Play size={18} />}
          </button>
        </div>
        <div className="timeline-control">
          <button
            className="icon-button"
            aria-label="Composición anterior de Cataluña"
            disabled={local <= 0}
            onClick={() => choose(steps[local - 1].id)}
          >
            <ChevronLeft size={17} />
          </button>
          <input
            type="range"
            min={0}
            max={Math.max(0, steps.length - 1)}
            value={Math.max(0, local)}
            aria-label="Fecha de composición de Cataluña"
            aria-valuetext={dateLabel(current.date)}
            onChange={(e) => choose(steps[Number(e.target.value)].id)}
          />
          <button
            className="icon-button"
            aria-label="Composición siguiente de Cataluña"
            disabled={local >= steps.length - 1}
            onClick={() => choose(steps[local + 1].id)}
          >
            <ChevronRight size={17} />
          </button>
        </div>
        <div className="time-extents">
          <span>{dateLabel(steps[0].date)}</span>
          <span>{dateLabel(steps.at(-1)!.date)}</span>
        </div>
        {gp && (
          <p className="small-note">
            Composición según nombramientos y ceses del cuadro institucional. El
            cierre sin cese individual corresponde a la siguiente composición
            documentada; no implica una fecha de retirada personal.
          </p>
        )}
        {pp?.currentOnly && (
          <p className="small-note">
            Registro nominal vigente consultado el {dateLabel(pp.checkedAt)}. No
            se proyecta esta lista hacia fechas anteriores.
          </p>
        )}
      </section>
      {gp && (
        <>
          <div className="government-organigram">
            <div className="president-tier">
              {members.filter((m) => m.level === "president").map(node)}
            </div>
            {!!members.filter((m) => m.level === "vice").length && (
              <section className="government-tier">
                <h3>Vicepresidencia y coordinación</h3>
                <div className="vice-tier">
                  {members.filter((m) => m.level === "vice").map(node)}
                </div>
              </section>
            )}
            <section className="government-tier">
              <h3>Consell Executiu</h3>
              <div className="minister-tier">
                {members.filter((m) => m.level === "minister").map(node)}
              </div>
            </section>
          </div>
          {!!gp.incidents.length && (
            <details className="senate-senators">
              <summary>Notas del registro histórico</summary>
              {gp.incidents.map((note) => (
                <p className="small-note" key={note}>
                  {note}
                </p>
              ))}
            </details>
          )}
          <p className="small-note">
            Las medidas del artículo 155 se aplicaron tras el cese de octubre de
            2017. El gabinete de Torra fue nombrado el 29 de mayo de 2018 y tomó
            posesión el 2 de junio; el cuadro distingue el nombramiento de la
            restitución efectiva.
          </p>
        </>
      )}
      {pp && (
        <>
          <Hemicycle
            chamber="Parlament de Catalunya"
            label={pp.label}
            date={current.date}
            groups={catalanGroupsAt(pp, current.date)}
            capacity={135}
            openPerson={person}
            note={
              pp.note +
              " Distribución esquemática por grupos; no asigna el asiento físico de cada diputado."
            }
          />
          <section className="congress-board">
            <h2>Mesa del Parlament</h2>
            <div className="congress-board-grid">{mesa.map(node)}</div>
          </section>
        </>
      )}
      <Sources
        sources={[
          {
            label: gp
              ? "Parlament · composición del Govern"
              : "Parlament · composición de la legislatura",
            url: current.period.source,
          },
          {
            label: "Parlament · archivo de legislaturas",
            url: "https://www.parlament.cat/web/composicio/legislatures-anteriors/index.html",
          },
          {
            label: "Parlament · dossier histórico de gobiernos",
            url: "https://www.parlament.cat/web/documentacio/recursos-documentals/dossiers-tematics/sumari/index.html?p_id=DOSSIER_TEMATIC_02",
          },
        ]}
      />
    </div>
  );
}
