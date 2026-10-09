import { useEffect, useId, useRef, useState } from "react";
import { Minus, Plus, RotateCcw, Search } from "lucide-react";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";
import { Portrait } from "../../Políticos/interfaz/Retrato";
import { dateLabel } from "./government-model";
import {
  compactGroupLabel,
  memberConstituency,
  memberParty,
} from "./hemicycle-person";
import { congressDiagramPoints, congressGroupColor } from "./congress-model";
import {
  constrainCamera,
  homeCamera,
  revealPoint,
  zoomCamera,
  wheelCamera,
  type Camera,
} from "./hemicycle-camera";
import "./congress.css";

export type HemicycleMember = {
  person: string;
  name: string;
  start: string | null;
  end: string | null;
  source: string;
  constituency?: string;
  formation?: string;
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
  openPerson,
}: {
  chamber: string;
  label: string;
  date: string;
  groups: HemicycleGroup[];
  capacity?: number;
  note: string;
  openPerson: (id: string) => void;
}) {
  const chamberOf = `${chamber.startsWith("Asamblea") ? "de la" : "del"} ${chamber}`;
  const chamberIn = `${chamber.startsWith("Asamblea") ? "en la" : "en el"} ${chamber}`;
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
  const [camera, setCamera] = useState<Camera>(homeCamera);
  const [dragging, setDragging] = useState(false);
  const svg = useRef<SVGSVGElement>(null);
  const cameraRef = useRef(camera);
  cameraRef.current = camera;
  const refs = useRef<(SVGGElement | null)[]>([]);
  const drag = useRef<{
    id: number;
    x: number;
    y: number;
    camera: Camera;
    moved: boolean;
  } | null>(null);
  const suppressClick = useRef(false);
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
  useEffect(() => {
    const element = svg.current;
    if (!element) return;
    function wheel(event: WheelEvent) {
      if (!event.deltaY) return;
      const matrix = element!.getScreenCTM();
      if (!matrix) return;
      const point = new DOMPoint(event.clientX, event.clientY).matrixTransform(
        matrix.inverse(),
      );
      const delta =
        event.deltaY *
        (event.deltaMode === 1
          ? 16
          : event.deltaMode === 2
            ? element!.clientHeight
            : 1);
      const next = wheelCamera(cameraRef.current, delta, point.x, point.y);
      if (!next) return;
      event.preventDefault();
      cameraRef.current = next;
      setCamera(next);
    }
    // React delega la rueda como pasiva; el visor necesita detener el scroll al ampliar.
    element.addEventListener("wheel", wheel, { passive: false });
    return () => element.removeEventListener("wheel", wheel);
  }, []);
  function focus(index: number) {
    setFocusIndex(index);
    setCamera((c) => revealPoint(c, points[index]));
    refs.current[index]?.focus({ preventScroll: true });
  }
  function open(id: string) {
    if (!suppressClick.current) openPerson(id);
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
          <div
            className="hemicycle-zoom"
            role="group"
            aria-label={`Zoom ${chamberOf}`}
          >
            <button
              className="icon-button"
              disabled={camera.zoom <= 1}
              aria-label={`Alejar hemiciclo ${chamberOf}`}
              onClick={() => setCamera((c) => zoomCamera(c, c.zoom / 1.3))}
            >
              <Minus size={15} />
            </button>
            <span>{Math.round(camera.zoom * 100)}%</span>
            <button
              className="icon-button"
              disabled={camera.zoom >= 4}
              aria-label={`Acercar hemiciclo ${chamberOf}`}
              onClick={() => setCamera((c) => zoomCamera(c, c.zoom * 1.3))}
            >
              <Plus size={15} />
            </button>
            <button
              className="icon-button"
              aria-label={`Restablecer hemiciclo ${chamberOf}`}
              onClick={() => setCamera(homeCamera)}
            >
              <RotateCcw size={14} />
            </button>
          </div>
          <svg
            ref={svg}
            className={`congress-diagram ${dragging ? "dragging" : ""}`}
            viewBox="0 0 1040 550"
            preserveAspectRatio="xMidYMid meet"
            role="group"
            aria-label={`Hemiciclo esquemático ${chamberOf}. ${total} mandatos. Flechas: recorrer personas. Enter: abrir ficha. Zoom con la rueda o los botones; arrastrar para desplazar.`}
            onPointerDown={(e) => {
              if (e.button !== 0) return;
              drag.current = {
                id: e.pointerId,
                x: e.clientX,
                y: e.clientY,
                camera,
                moved: false,
              };
              suppressClick.current = false;
            }}
            onPointerMove={(e) => {
              const d = drag.current;
              if (!d || e.pointerId !== d.id) return;
              if (Math.hypot(e.clientX - d.x, e.clientY - d.y) < 5 && !d.moved)
                return;
              d.moved = true;
              suppressClick.current = true;
              setDragging(true);
              e.currentTarget.setPointerCapture(e.pointerId);
              const scale = Math.min(
                e.currentTarget.clientWidth / 1040,
                e.currentTarget.clientHeight / 550,
              );
              setCamera(
                constrainCamera({
                  ...d.camera,
                  x: d.camera.x + (e.clientX - d.x) / scale,
                  y: d.camera.y + (e.clientY - d.y) / scale,
                }),
              );
            }}
            onPointerUp={() => {
              drag.current = null;
              setDragging(false);
            }}
            onPointerCancel={() => {
              drag.current = null;
              setDragging(false);
            }}
            onKeyDown={(e) => {
              if (["+", "=", "-", "0"].includes(e.key)) {
                e.preventDefault();
                setCamera((c) =>
                  e.key === "0"
                    ? homeCamera
                    : zoomCamera(c, c.zoom * (e.key === "-" ? 1 / 1.3 : 1.3)),
                );
              }
            }}
          >
            <g
              transform={`translate(${camera.x} ${camera.y}) scale(${camera.zoom})`}
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
                      if (!drag.current?.moved)
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
                    <rect
                      x={point.x - 5.5}
                      y={point.y - 5.5}
                      width={11}
                      height={11}
                      fill={congressGroupColor(item.group.name)}
                    />
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
              <p>{dateLabel(date)}</p>
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
