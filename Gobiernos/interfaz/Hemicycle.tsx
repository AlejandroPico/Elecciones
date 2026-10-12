import { useEffect, useId, useRef, useState } from "react";
import { Search } from "lucide-react";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";
import { Portrait } from "../../Políticos/interfaz/Retrato";
import { dateLabel } from "./government-model";
import {
  compactGroupLabel,
  memberConstituency,
  memberParty,
} from "./hemicycle-person";
import { congressDiagramPoints, congressGroupColor } from "./congress-model";
import "./congress.css";

export type HemicycleMember = {
  person: string;
  name: string;
  start: string | null;
  end: string | null;
  source: string;
  constituency?: string;
  formation?: string;
  formationLabel?: string;
};
export type HemicycleGroup = {
  id: string;
  name: string;
  label: string;
  source: string;
  members: HemicycleMember[];
};
const normalize = (value: string) =>
  value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("es");
export function matchesMember(
  member: HemicycleMember,
  group: string,
  selected: string[],
  query: string,
) {
  return (
    (!selected.length || selected.includes(group)) &&
    normalize(`${member.name} ${member.constituency ?? ""}`).includes(
      normalize(query),
    )
  );
}

export default function Hemicycle({
  chamber,
  label,
  date,
  groups,
  capacity,
  note,
  dateCaption,
  openPerson,
}: {
  chamber: string;
  label: string;
  date: string;
  groups: HemicycleGroup[];
  capacity?: number;
  note: string;
  dateCaption?: string;
  openPerson: (id: string) => void;
}) {
  const chamberOf = `${chamber.startsWith("Asamblea") ? "de la" : chamber.startsWith("Les ") ? "de" : "del"} ${chamber}`;
  const chamberIn = `${chamber.startsWith("Asamblea") ? "en la" : chamber.startsWith("Les ") ? "en" : "en el"} ${chamber}`;
  const headingId = useId();
  const positions = groups.flatMap((group) =>
    group.members.map((member) => ({ member, group })),
  );
  const total = positions.length;
  const points = congressDiagramPoints(Math.max(capacity ?? total, total));
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<string[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [focusIndex, setFocusIndex] = useState(0);
  const refs = useRef<(SVGGElement | null)[]>([]);
  const selected = positions.find((p) => p.member.person === selectedId);
  const person = selected && findPerson(selected.member.person);
  const constituency = selected && memberConstituency(selected.member, person);
  const party = selected && memberParty(selected.member, person, date);
  const matches = (p: (typeof positions)[number]) =>
    matchesMember(p.member, p.group.id, filters, query);
  const found = positions.filter(matches);
  const filtering = !!query || !!filters.length;
  useEffect(() => {
    setSelectedId(null);
    setFilters([]);
    setFocusIndex(0);
  }, [date, label, chamber]);
  function focus(index: number) {
    setFocusIndex(index);
    refs.current[index]?.focus({ preventScroll: true });
  }
  function open(id: string) {
    openPerson(id);
  }
  return (
    <section className="congress-hemicycle" aria-labelledby={headingId}>
      <div className="congress-graph-heading">
        <h2 id={headingId}>Hemiciclo · {chamber}</h2>
        <span aria-live="polite">
          {filtering ? `${found.length} / ${total}` : total} mandatos
          documentados · {label}
        </span>
      </div>
      <div className="congress-search">
        <label>
          <Search size={15} />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar persona o circunscripción"
            aria-label={`Buscar en el hemiciclo ${chamberOf}`}
          />
        </label>
        {filtering && (
          <button
            className="text-button"
            onClick={() => {
              setFilters([]);
              setQuery("");
            }}
          >
            Todos los grupos
          </button>
        )}
      </div>
      <div className="congress-diagram-layout">
        <div className="hemicycle-widget">
          <svg
            className="congress-diagram"
            viewBox="0 0 1040 550"
            preserveAspectRatio="xMidYMid meet"
            role="group"
            aria-label={`Hemiciclo esquemático ${chamberOf}. ${total} mandatos. Flechas: recorrer personas. Enter: abrir ficha.`}
          >
            <g className="hemicycle-tiers" aria-hidden="true">
              {Array.from({ length: 8 }, (_, row) => {
                const radius = 145 + row * 46;
                return (
                  <path
                    key={row}
                    d={`M ${520 - radius} 495 A ${radius} ${radius} 0 0 1 ${520 + radius} 495`}
                  />
                );
              })}
            </g>
            <g>
              {points.map((point, index) => {
                const item = positions[index];
                if (!item)
                  return (
                    <circle
                      key={`vacancy-${index}`}
                      cx={point.x}
                      cy={point.y}
                      r={5.5}
                      className="congress-vacancy"
                    >
                      <title>
                        Sin identificación en la composición documentada
                      </title>
                    </circle>
                  );
                return (
                  <g
                    key={item.member.person}
                    ref={(node) => {
                      refs.current[index] = node;
                    }}
                    role="button"
                    tabIndex={
                      index === (positions[focusIndex] ? focusIndex : 0)
                        ? 0
                        : -1
                    }
                    aria-label={`${item.member.name} · ${item.group.label}${item.member.constituency ? ` · ${item.member.constituency}` : ""}`}
                    className={`congress-position ${item.member.person === selectedId ? "selected" : ""}`}
                    style={{ opacity: matches(item) ? 1 : 0.14 }}
                    onPointerEnter={() => {
                      setSelectedId(item.member.person);
                    }}
                    onFocus={() => {
                      setSelectedId(item.member.person);
                      setFocusIndex(index);
                    }}
                    onClick={() => open(item.member.person)}
                    onKeyDown={(e) => {
                      const offset = ["ArrowRight", "ArrowDown"].includes(e.key)
                        ? 1
                        : ["ArrowLeft", "ArrowUp"].includes(e.key)
                          ? -1
                          : 0;
                      if (offset) {
                        e.preventDefault();
                        focus((index + offset + total) % total);
                      }
                      if (["Home", "End"].includes(e.key)) {
                        e.preventDefault();
                        focus(e.key === "Home" ? 0 : total - 1);
                      }
                      if (["Enter", " "].includes(e.key)) {
                        e.preventDefault();
                        openPerson(item.member.person);
                      }
                    }}
                  >
                    <circle
                      cx={point.x}
                      cy={point.y}
                      r={11}
                      fill="transparent"
                    />
                    <circle
                      className="congress-seat-halo"
                      cx={point.x}
                      cy={point.y}
                      r={9}
                    />
                    <g
                      transform={`translate(${point.x} ${point.y}) rotate(${90 - (point.angle * 180) / Math.PI})`}
                    >
                      <path
                        className="congress-seat"
                        d="M -6 4 V -2 A 6 6 0 0 1 6 -2 V 4 Q 0 7 -6 4 Z"
                        fill={congressGroupColor(item.group.name)}
                      />
                      <path
                        className="congress-seat-detail"
                        d="M -3.5 2.5 Q 0 4 3.5 2.5"
                      />
                    </g>
                    <title>
                      {item.member.name} · {item.group.label}
                    </title>
                  </g>
                );
              })}
              <text
                x={520}
                y={470}
                textAnchor="middle"
                className="congress-total"
              >
                {filtering ? `${found.length} / ${total}` : total}
              </text>
              <text
                x={520}
                y={495}
                textAnchor="middle"
                className="congress-total-label"
              >
                MANDATOS DOCUMENTADOS
              </text>
            </g>
          </svg>
        </div>
      </div>
      <div className="hemicycle-details">
        <div
          className="seat-legend congress-group-legend"
          role="group"
          aria-label={`Seleccionar grupos ${chamberOf}`}
        >
          {groups.map((g) => (
            <button
              key={g.id}
              title={g.name}
              aria-pressed={filters.includes(g.id)}
              onClick={() =>
                setFilters((current) =>
                  current.includes(g.id)
                    ? current.filter((id) => id !== g.id)
                    : [...current, g.id],
                )
              }
            >
              <i style={{ background: congressGroupColor(g.name) }} />
              <span>{compactGroupLabel(g.label)}</span>
              <b>{g.members.length}</b>
            </button>
          ))}
        </div>
        <aside
          className="congress-inspector"
          aria-label={`Persona seleccionada ${chamberIn}`}
          aria-live="polite"
          aria-atomic="true"
        >
          {selected ? (
            <button
              className="hemicycle-person-card"
              onClick={() => openPerson(selected.member.person)}
              aria-label={`Abrir ficha de ${selected.member.name}`}
            >
              <div className="congress-deputy-portrait">
                {person ? (
                  <Portrait person={person} />
                ) : (
                  <span aria-hidden="true">
                    {selected.member.name
                      .split(" ")
                      .map((n) => n[0])
                      .slice(0, 2)
                      .join("")}
                  </span>
                )}
              </div>
              <div className="hemicycle-person-info">
                <h3>{selected.member.name}</h3>
                {constituency && (
                  <p className="hemicycle-constituency">{constituency}</p>
                )}
                <p
                  className="hemicycle-person-group"
                  title={selected.group.name}
                >
                  <i
                    style={{
                      background: congressGroupColor(selected.group.name),
                    }}
                  />
                  {compactGroupLabel(selected.group.label)}
                </p>
                {party && (
                  <p className="hemicycle-person-party">
                    <span>{party.label}:</span> {party.name}
                  </p>
                )}
              </div>
            </button>
          ) : (
            <div className="hemicycle-person-empty">
              <span className="eyebrow">{chamber}</span>
              <h3>{label}</h3>
              <p>{dateCaption ?? dateLabel(date)}</p>
            </div>
          )}
        </aside>
      </div>
      {filtering && (
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
      <p className="small-note congress-seating-note">{note}</p>
    </section>
  );
}
