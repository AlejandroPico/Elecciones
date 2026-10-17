import { useEffect, useRef, useState } from "react";
import { ArrowUpRight, ChevronDown, Search, RotateCcw } from "lucide-react";
import portraits from "virtual:presidencias-retratos";
import { PortraitImage } from "../../Políticos/interfaz/ImagenRetrato";
import DragRail from "./DragRail";
import {
  cabinetFor,
  durationLabel,
  eventKind,
  eventTopics,
  events,
  eventsFor,
  judicialLabel,
  kinds,
  matchesEvent,
  presentationCriteria,
  presidencies,
  researchDate,
  researchDateLabel,
  sources,
  stages,
  timelinePosition,
  topics,
  type EventKind,
  type PresidencyEvent,
} from "./presidencias-model";
import "./presidencias.css";

function EventRecord({
  event,
  stageId,
}: {
  event: PresidencyEvent;
  stageId: string;
}) {
  const kind = eventKind(event);
  const resolution = stages.find(
    (stage) => stage.id === event.stageAtMilestone,
  );
  const judicial = judicialLabel(event);
  const related = stages.filter((stage) =>
    event.relatedStages?.includes(stage.id),
  );
  const link = event.displayStages?.find((item) => item.stage === stageId);
  const origin = stages.find((stage) => stage.id === event.stage);
  return (
    <details
      className="pres-event"
      data-kind={kind}
      id={`hecho-${stageId}-${event.id}`}
    >
      <summary>
        <time dateTime={event.date}>{researchDateLabel(event.date, true)}</time>
        <div className="pres-event-copy">
          <div className="pres-event-meta">
            <span className="pres-event-kind">
              {kinds.find((k) => k.id === kind)!.label}
            </span>
            {resolution && event.stage === stageId && (
              <span>Hito posterior · {resolution.legislature}</span>
            )}
            {event.stage !== stageId && <span>Hecho vinculado</span>}
          </div>
          <h4>{event.title}</h4>
          <p>{event.summary}</p>
          {judicial && (
            <span className="pres-judicial">
              {judicial}
              {event.statusAtSource &&
                ` · ${researchDateLabel(event.statusAtSource, true)}`}
            </span>
          )}
          <span className="pres-event-more">
            Contexto y fuentes <ChevronDown size={12} aria-hidden="true" />
          </span>
        </div>
      </summary>
      <div className="pres-event-detail">
        {link && (
          <p>
            <strong>Relación con esta etapa.</strong> {link.reason}
          </p>
        )}
        {event.stage !== stageId && origin && (
          <p>
            <strong>Contexto de origen.</strong> {origin.president} ·{" "}
            {origin.legislature ?? "Transición"}.
          </p>
        )}
        <p>{event.attribution}</p>
        {event.factsPeriod && (
          <p>
            <strong>Periodo de los hechos.</strong> {event.factsPeriod}
          </p>
        )}
        {resolution && (
          <p>
            <strong>Gobierno en la fecha del hito.</strong>{" "}
            {resolution.president} · {resolution.legislature}. La atribución de
            los hechos se conserva en su etapa de origen.
          </p>
        )}
        {related.length > 0 && (
          <p>
            <strong>Alcance compartido.</strong>{" "}
            {related
              .map((stage) => `${stage.president} · ${stage.legislature}`)
              .join("; ")}
            .
          </p>
        )}
        <ul className="pres-sources">
          {event.sources.map((id) => {
            const source = sources[id];
            return (
              <li key={id}>
                <a href={source.url} target="_blank" rel="noreferrer">
                  {source.title} <ArrowUpRight size={12} aria-hidden="true" />
                </a>
                <span>
                  {source.kind === "primary"
                    ? "Fuente primaria"
                    : source.kind === "agency"
                      ? "Agencia de información"
                      : "Hemeroteca"}
                  . {source.limits}
                </span>
              </li>
            );
          })}
        </ul>
        {event.pending.length > 0 && (
          <p className="pres-research-pending">
            <strong>En revisión.</strong> {event.pending.join(" ")}
          </p>
        )}
      </div>
    </details>
  );
}

function EventList({
  entries,
  stageId,
}: {
  entries: PresidencyEvent[];
  stageId: string;
}) {
  const [count, setCount] = useState(16);
  const sentinel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!sentinel.current || count >= entries.length) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setCount((value) => value + 24);
      },
      { rootMargin: "700px" },
    );
    observer.observe(sentinel.current);
    return () => observer.disconnect();
  }, [count, entries.length]);
  return (
    <div className="pres-events" data-total={entries.length}>
      {entries.slice(0, count).map((event) => (
        <EventRecord key={event.id} event={event} stageId={stageId} />
      ))}
      {count < entries.length && (
        <div ref={sentinel} className="pres-load-sentinel" aria-hidden="true" />
      )}
    </div>
  );
}

export default function Presidencies({
  selectedPresident,
  openPresident,
  openPerson,
  openGovernment,
}: {
  selectedPresident?: string;
  openPresident: (id?: string) => void;
  openPerson: (id: string) => void;
  openGovernment: (id: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState<EventKind | "all">("all");
  const [legislature, setLegislature] = useState("all");
  const [ascending, setAscending] = useState(false);
  const [topic, setTopic] = useState("all");
  const [year, setYear] = useState("all");
  const years = [...new Set(events.map((event) => event.date.slice(0, 4)))]
    .sort()
    .reverse();
  const selected = presidencies.find(
    (p) => p.person === selectedPresident,
  )?.person;
  const ordinals = [
    ...new Set(
      stages.map((s) => s.legislature).filter((s): s is string => !!s),
    ),
  ].reverse();
  const visibleStages = (ids: string[]) => {
    const records = stages.filter(
      (s) =>
        ids.includes(s.id) &&
        (legislature === "all" ||
          (legislature === "context"
            ? !s.legislature
            : s.legislature === legislature)),
    );
    return ascending ? records : records.reverse();
  };
  const filteredEvents = (stage: string) =>
    eventsFor(stage, ascending).filter(
      (event) =>
        matchesEvent(event, query, kind) &&
        (topic === "all" || eventTopics(event).includes(topic)) &&
        (year === "all" || event.date.startsWith(year)),
    );
  const visible = (
    ascending ? presidencies : [...presidencies].reverse()
  ).filter(
    (p) =>
      (!selected || p.person === selected) &&
      visibleStages(p.stages).some((s) => filteredEvents(s.id).length),
  );
  const context = !selected
    ? visibleStages(["pre-arias", "pre-santiago"]).filter(
        (s) => filteredEvents(s.id).length,
      )
    : [];
  const filtersActive =
    !!selected ||
    !!query ||
    kind !== "all" ||
    legislature !== "all" ||
    topic !== "all" ||
    year !== "all";
  const renderStage = (stage: (typeof stages)[number], person?: string) => {
    const entries = filteredEvents(stage.id);
    if (!entries.length) return null;
    const cabinet = person && cabinetFor(stage.id, person);
    return (
      <section
        className="pres-legislature"
        key={stage.id}
        aria-labelledby={`etapa-${stage.id}`}
      >
        <header>
          <div>
            <h3 id={`etapa-${stage.id}`}>
              {stage.legislature ?? "Transición"}
            </h3>
            <span>{stage.periodLabel}</span>
          </div>
          {cabinet && (
            <button onClick={() => openGovernment(cabinet)}>
              Composición <ArrowUpRight size={13} aria-hidden="true" />
            </button>
          )}
        </header>
        <EventList
          key={[stage.id, query, kind, topic, year, ascending].join(":")}
          entries={entries}
          stageId={stage.id}
        />
      </section>
    );
  };
  const renderContext = () =>
    context.length > 0 && (
      <section
        className="pres-context"
        aria-label="Contexto previo a las presidencias democráticas"
      >
        <div className="pres-context-heading">
          <span>1975 — 1976</span>
          <h2>Transición previa</h2>
        </div>
        <div>
          {context.map((stage) => (
            <section key={stage.id}>
              <h3 className="pres-context-name">{stage.president}</h3>
              {renderStage(stage)}
            </section>
          ))}
        </div>
      </section>
    );
  return (
    <div className="presidencies">
      <div className="pres-heading">
        <div>
          <p>Archivo de presidencias</p>
          <h1>Gobiernos centrales</h1>
        </div>
        <details className="pres-method">
          <summary>
            Criterios y cobertura <ChevronDown size={13} aria-hidden="true" />
          </summary>
          <div>
            <h2>Lectura del archivo</h2>
            <p>{presentationCriteria.colorPolicy}</p>
            <p>
              Selección documentada en ampliación. Una ley aprobada no acredita
              por sí sola un resultado favorable. Las fechas de consulta no
              convierten una resolución antigua en el estado judicial actual;
              cada caso conserva su fecha y sus pendientes.
            </p>
            <p>
              «Leyes y medidas» incorpora el índice normativo del BOE: la fecha
              corresponde a su publicación y el asunto procede de su título
              oficial. Estos registros documentales se distinguen de los
              acontecimientos desarrollados y no acreditan resultados. El
              inventario semanal identifica las lagunas de hemeroteca; no se ha
              completado una revisión íntegra de todas las semanas.
            </p>
            <p>{presentationCriteria.dateBasis}</p>
            {presentationCriteria.dateSources.map((url, index) => (
              <a key={url} href={url} target="_blank" rel="noreferrer">
                {index
                  ? "Nombramiento de 2018 · BOE"
                  : "Cronología de presidencias · La Moncloa"}{" "}
                <ArrowUpRight size={12} />
              </a>
            ))}
            <small>
              Revisión documental · {researchDateLabel(researchDate)}
            </small>
          </div>
        </details>
      </div>
      <section
        className="pres-histogram"
        aria-labelledby="pres-histogram-title"
      >
        <div className="pres-histogram-head">
          <h2 id="pres-histogram-title">Tiempo en la Presidencia</h2>
          <span>Hasta {researchDateLabel(researchDate, true)}</span>
        </div>
        <div className="pres-histogram-axis" aria-hidden="true">
          <span />
          <div>
            {[1976, 1986, 1996, 2006, 2016, 2026].map((year) => (
              <span key={year}>{year}</span>
            ))}
          </div>
          <span />
        </div>
        {presidencies.map((p) => {
          const position = timelinePosition(p.from, p.until ?? researchDate);
          return (
            <button
              key={p.person}
              className="pres-histogram-row"
              aria-pressed={selected === p.person}
              onClick={() =>
                openPresident(selected === p.person ? undefined : p.person)
              }
              title={`${p.name}: ${researchDateLabel(p.from)} — ${p.until ? researchDateLabel(p.until) : `corte ${researchDateLabel(researchDate)}`}`}
              aria-label={`Consultar presidencia de ${p.name}, ${durationLabel(p.from, p.until ?? researchDate)}${p.until ? "" : " hasta el corte del archivo"}`}
            >
              <span>{p.shortName}</span>
              <span className="pres-histogram-track">
                <i
                  style={{
                    left: `${position.left}%`,
                    width: `${position.width}%`,
                  }}
                />
              </span>
              <small>{durationLabel(p.from, p.until ?? researchDate)}</small>
            </button>
          );
        })}
      </section>
      <div className="pres-filters">
        <label className="pres-search">
          <Search size={16} aria-hidden="true" />
          <input
            aria-label="Buscar en las presidencias"
            placeholder="Buscar un hecho, una ley o un caso"
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
        <select
          aria-label="Filtrar por presidencia"
          value={selected ?? "all"}
          onChange={(e) =>
            openPresident(e.target.value === "all" ? undefined : e.target.value)
          }
        >
          <option value="all">Todas las presidencias</option>
          {[...presidencies].reverse().map((p) => (
            <option key={p.person} value={p.person}>
              {p.name}
            </option>
          ))}
        </select>
        <select
          aria-label="Orden del histórico"
          value={ascending ? "asc" : "desc"}
          onChange={(e) => setAscending(e.target.value === "asc")}
        >
          <option value="desc">Más recientes primero</option>
          <option value="asc">Más antiguas primero</option>
        </select>
        {filtersActive && (
          <button
            className="icon-button"
            aria-label="Quitar filtros del histórico"
            onClick={() => {
              setQuery("");
              setKind("all");
              setLegislature("all");
              setTopic("all");
              setYear("all");
              openPresident();
            }}
          >
            <RotateCcw size={16} />
          </button>
        )}
      </div>
      <div className="pres-subfilters">
        <select
          aria-label="Filtrar por materia"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        >
          <option value="all">Todas las materias</option>
          {topics.map(([id, label]) => (
            <option key={id} value={id}>
              {label}
            </option>
          ))}
        </select>
        <select
          aria-label="Filtrar por año del acontecimiento"
          value={year}
          onChange={(e) => setYear(e.target.value)}
        >
          <option value="all">Todos los años</option>
          {years.map((value) => (
            <option key={value}>{value}</option>
          ))}
        </select>
      </div>
      <DragRail
        className="pres-kind-filter"
        role="group"
        aria-label="Tipo de acontecimiento"
      >
        <button aria-pressed={kind === "all"} onClick={() => setKind("all")}>
          Todo
        </button>
        {kinds.map((k) => (
          <button
            key={k.id}
            data-kind={k.id}
            aria-pressed={kind === k.id}
            onClick={() => setKind(k.id)}
          >
            <i />
            {k.label}
          </button>
        ))}
      </DragRail>
      <DragRail
        className="pres-legislature-filter"
        role="group"
        aria-label="Filtrar por legislatura"
      >
        <button
          aria-pressed={legislature === "all"}
          onClick={() => setLegislature("all")}
        >
          Todas
        </button>
        {(ascending ? [...ordinals].reverse() : ordinals).map((ordinal) => (
          <button
            key={ordinal}
            aria-pressed={legislature === ordinal}
            onClick={() => setLegislature(ordinal)}
          >
            {ordinal}
          </button>
        ))}
        <button
          aria-pressed={legislature === "context"}
          onClick={() => setLegislature("context")}
        >
          Transición
        </button>
      </DragRail>
      <div
        className="pres-history"
        aria-label="Hitos, resultados, crisis y escándalos por presidencia"
      >
        {ascending && renderContext()}
        {visible.map((p) => {
          const photo = portraits[p.person];
          const initials = p.name
            .split(" ")
            .slice(0, 2)
            .map((w) => w[0])
            .join("");
          return (
            <article
              className="pres-administration"
              key={p.person}
              aria-labelledby={`pres-${p.person}`}
            >
              <aside className="pres-person-column">
                <div className="pres-person-sticky">
                  <button
                    className="pres-portrait-button"
                    onClick={() => openPerson(p.person)}
                    aria-label={`Abrir ficha de ${p.name}`}
                  >
                    <PortraitImage
                      src={photo?.src}
                      name={p.name}
                      initials={initials}
                    />
                  </button>
                  <p className="pres-person-years">
                    {p.from.slice(0, 4)} —{" "}
                    {p.until?.slice(0, 4) ?? "corte 2026"}
                  </p>
                  <h2 id={`pres-${p.person}`}>{p.name}</h2>
                  <p className="pres-duration">
                    {durationLabel(p.from, p.until ?? researchDate)}
                    {!p.until && " hasta el corte"}
                  </p>
                  <p className="pres-person-dates">
                    {researchDateLabel(p.from, true)}
                    <br />
                    {p.until
                      ? researchDateLabel(p.until, true)
                      : `Corte: ${researchDateLabel(researchDate, true)}`}
                  </p>
                  <button
                    className="pres-bio-link"
                    onClick={() => openPerson(p.person)}
                  >
                    Ficha personal <ArrowUpRight size={13} aria-hidden="true" />
                  </button>
                  {photo && (
                    <a
                      className="pres-photo-credit"
                      href={photo.source}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {photo.credit}
                    </a>
                  )}
                </div>
              </aside>
              <div className="pres-administration-events">
                {visibleStages(p.stages).map((stage) =>
                  renderStage(stage, p.person),
                )}
              </div>
            </article>
          );
        })}
        {!ascending && renderContext()}
        {!visible.length && !context.length && (
          <div className="pres-empty" role="status">
            <h2>Sin coincidencias</h2>
            <p>Cambia la búsqueda, el tipo de hecho o la legislatura.</p>
          </div>
        )}
      </div>
    </div>
  );
}
