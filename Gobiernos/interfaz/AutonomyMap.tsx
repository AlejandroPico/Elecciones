import { ChevronLeft, ChevronRight } from "lucide-react";
import { useId, useLayoutEffect, useMemo, useRef, useState } from "react";
import mapPortraits from "virtual:presidencias-retratos";
import { PortraitImage } from "../../Políticos/interfaz/ImagenRetrato";
import { dateLabel } from "./government-model";
import {
  geography,
  mapCheckedAt,
  mapParties,
  provincesAt,
  autonomiesAt,
  mapDates,
  mapDate,
  tooltipPosition,
  type MapProvince,
} from "./mapa-model";
import "./mapa.css";

export default function AutonomyMap({
  openGovernment,
  selected: selectedRoute,
  openDate,
}: {
  openGovernment: (territory: string, date: string) => void;
  selected?: string;
  openDate: (date: string) => void;
}) {
  const date = mapDate(selectedRoute);
  const id = useId().replace(/:/g, "");
  const [selectedId, setSelectedId] = useState<string>();
  const mapProvinces = useMemo(() => provincesAt(date), [date]);
  const mapAutonomies = useMemo(
    () => autonomiesAt(mapProvinces),
    [mapProvinces],
  );
  const selected = mapProvinces.find((p) => p.id === selectedId);
  const setSelected = (province?: MapProvince) => setSelectedId(province?.id);
  const dates = useMemo(() => [...new Set([...mapDates, date])].sort(), [date]);
  const timeIndex = dates.indexOf(date);
  const tooltip = useRef<HTMLDivElement>(null);
  const point = useRef({ x: 0, y: 0 });
  const touch = useRef(false);
  const pinned = useRef<string | undefined>(undefined);
  const person = selected && mapPortraits[selected.presidency.person];
  const autonomy = mapAutonomies.find((a) => a.id === selected?.territory);
  function position() {
    if (!tooltip.current) return;
    const { width, height } = tooltip.current.getBoundingClientRect();
    const { left, top } = tooltipPosition(
      point.current.x,
      point.current.y,
      width,
      height,
      window.innerWidth,
      window.innerHeight,
    );
    tooltip.current.style.transform = `translate3d(${left}px, ${top}px, 0)`;
  }
  useLayoutEffect(position, [selected]);
  useLayoutEffect(() => {
    window.addEventListener("resize", position);
    return () => window.removeEventListener("resize", position);
  }, []);
  function clear() {
    pinned.current = undefined;
    setSelected(undefined);
  }
  return (
    <div
      className="autonomy-map"
      onKeyDown={(e) => {
        if (e.key === "Escape") clear();
      }}
    >
      <div className="map-caption">
        <span>Presidencias autonómicas</span>
        <span>Formación de la presidencia</span>
      </div>
      <div className="map-history">
        <button
          className="icon-button"
          aria-label="Cambio autonómico anterior"
          disabled={timeIndex === 0}
          onClick={() => openDate(dates[timeIndex - 1])}
        >
          <ChevronLeft size={18} />
        </button>
        <div>
          <time dateTime={date} aria-live="polite">
            {dateLabel(date)}
          </time>
          <input
            type="range"
            min={0}
            max={dates.length - 1}
            value={timeIndex}
            aria-label="Cronología del mapa autonómico"
            aria-valuetext={dateLabel(date)}
            onChange={(event) => openDate(dates[Number(event.target.value)])}
          />
          <div className="map-history-years">
            <span>{dates[0].slice(0, 4)}</span>
            <span>{mapCheckedAt.slice(0, 4)}</span>
          </div>
        </div>
        <button
          className="icon-button"
          aria-label="Cambio autonómico siguiente"
          disabled={timeIndex === dates.length - 1}
          onClick={() => openDate(dates[timeIndex + 1])}
        >
          <ChevronRight size={18} />
        </button>
        <button
          className="map-present"
          disabled={date === mapCheckedAt}
          onClick={() => openDate(mapCheckedAt)}
        >
          Actual
        </button>
      </div>
      <svg
        className="political-map"
        viewBox={geography.viewBox}
        role="group"
        aria-label="Mapa de las presidencias de las 17 comunidades y Ceuta y Melilla"
        onPointerLeave={() => {
          if (!touch.current) clear();
        }}
      >
        <defs>
          <radialGradient id={`${id}-fade`} cx="50%" cy="44%" r="64%">
            <stop offset="52%" stopColor="white" />
            <stop offset="100%" stopColor="black" />
          </radialGradient>
          <mask id={`${id}-mask`}>
            <rect width="1100" height="690" fill={`url(#${id}-fade)`} />
          </mask>
          <clipPath id={`${id}-main`}>
            <rect x="12" y="0" width="1076" height="690" />
          </clipPath>
          <clipPath id={`${id}-ceuta`}>
            <rect x="630" y="722" width="184" height="100" />
          </clipPath>
          <clipPath id={`${id}-melilla`}>
            <rect x="845" y="722" width="160" height="100" />
          </clipPath>
        </defs>
        <g className="map-context" aria-hidden="true">
          {geography.neighbours.map((country) => (
            <path
              key={`${country.name}:${country.panel}`}
              d={country.path}
              clipPath={`url(#${id}-${country.panel})`}
              mask={country.panel === "main" ? `url(#${id}-mask)` : undefined}
            />
          ))}
          <path d={geography.unassigned} clipPath={`url(#${id}-main)`} />
        </g>
        <g className="map-country-labels" aria-hidden="true">
          <text x="140" y="391" transform="rotate(-78 140 391)">
            Portugal
          </text>
          <text x="892" y="70">
            Francia
          </text>
          <text x="819" y="118" className="map-small-label">
            Andorra
          </text>
          <text x="500" y="667">
            Marruecos
          </text>
        </g>
        <g className="map-provinces" aria-hidden="true">
          {mapProvinces.map((province) => (
            <path
              key={province.id}
              d={province.path}
              fill={province.presidency.color}
            />
          ))}
        </g>
        {/* La autonomía se eleva como un conjunto; las áreas provinciales no se mueven. */}
        {autonomy && (
          <g
            key={autonomy.id}
            className="map-autonomy-raised"
            data-territory={autonomy.id}
            aria-hidden="true"
          >
            {autonomy.provinces.map((province) => (
              <path
                key={province.id}
                d={province.path}
                fill={province.presidency.color}
              />
            ))}
          </g>
        )}
        <g className="map-hits">
          {mapProvinces.map((province) => (
            <path
              key={province.id}
              d={province.path}
              data-city={
                province.panel === "ceuta" ||
                province.panel === "melilla" ||
                undefined
              }
              tabIndex={0}
              role="button"
              aria-label={`${province.name} · ${province.presidency.territoryName} · ${province.presidency.name} · ${province.presidency.partyLabel}. Abrir gobierno de ${province.presidency.territoryName}`}
              aria-disabled={!province.presidency.person}
              aria-describedby={
                selected?.id === province.id ? `${id}-tooltip` : undefined
              }
              onPointerEnter={(event) => {
                touch.current = event.pointerType === "touch";
                point.current = { x: event.clientX, y: event.clientY };
                setSelected(province);
              }}
              onPointerMove={(event) => {
                point.current = { x: event.clientX, y: event.clientY };
                position();
              }}
              onPointerDown={(event) => {
                touch.current = event.pointerType === "touch";
              }}
              onFocus={(event) => {
                const box = event.currentTarget.getBoundingClientRect();
                point.current = {
                  x: box.x + box.width / 2,
                  y: box.y + box.height / 2,
                };
                setSelected(province);
              }}
              onBlur={clear}
              onClick={() => {
                if (!province.presidency.person) return;
                if (touch.current && pinned.current !== province.territory) {
                  pinned.current = province.territory;
                  setSelected(province);
                  return;
                }
                openGovernment(province.territory, date);
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  if (province.presidency.person)
                    openGovernment(province.territory, date);
                }
              }}
            />
          ))}
        </g>
        <g className="map-insets" aria-hidden="true">
          <path d="M40 691H419L445 718M611 717V830H817M837 717V830H1019" />
          <text x="60" y="682">
            Canarias
          </text>
          <text x="721" y="706" textAnchor="middle">
            Ceuta
          </text>
          <text x="927" y="706" textAnchor="middle">
            Melilla
          </text>
          <text x="820" y="847" textAnchor="middle" className="map-small-label">
            Ciudades ampliadas
          </text>
        </g>
      </svg>
      <div className="map-footer">
        <div className="map-legend" aria-label="Partidos de las presidencias">
          {Object.entries(mapParties)
            .filter(([key]) =>
              mapProvinces.some((p) => p.presidency.party === key),
            )
            .map(([key, party]) => (
              <span key={key}>
                <i style={{ background: party.color }} />
                {party.label}
              </span>
            ))}
        </div>
        <details className="map-sources">
          <summary>Fuentes</summary>
          <div>
            <p>
              El color identifica la formación vinculada a la presidencia por la
              fuente de cada mandato, también en sus provincias; puede ser una
              coalición y no acredita militancia diaria. Las fechas históricas
              siguen el criterio documental de las composiciones. El gris indica
              falta de datos; no significa ausencia de gobierno. Los
              nombramientos y los intervalos se consultan en cada gobierno.
            </p>
            <p>
              Cartografía:{" "}
              <a
                href="https://www.ign.es/wfs-inspire/unidades-administrativas?service=WFS&amp;request=GetCapabilities"
                target="_blank"
                rel="noreferrer"
              >
                © IGN
              </a>{" "}
              ·{" "}
              <a
                href="https://creativecommons.org/licenses/by/4.0/"
                target="_blank"
                rel="noreferrer"
              >
                CC BY 4.0
              </a>
              . Países vecinos:{" "}
              <a
                href="https://www.naturalearthdata.com/about/terms-of-use/"
                target="_blank"
                rel="noreferrer"
              >
                Natural Earth · dominio público
              </a>
              . Proyección y simplificación adaptadas a esta vista; inserciones
              a distinta escala.
            </p>
            <ul>
              {mapProvinces
                .filter(
                  (p, index, all) =>
                    all.findIndex((r) => r.territory === p.territory) === index,
                )
                .map(({ presidency: p }) => (
                  <li key={p.territory}>
                    {p.territoryName} ·{" "}
                    {p.source ? (
                      <a
                        href={p.tenureSource}
                        target="_blank"
                        rel="noreferrer"
                        title={p.dateBasis}
                      >
                        Inicio de la presidencia
                      </a>
                    ) : (
                      "Sin intervalo documentado"
                    )}
                    {p.source && p.source !== p.tenureSource && (
                      <>
                        {" "}
                        ·{" "}
                        <a href={p.source} target="_blank" rel="noreferrer">
                          Nombramiento
                        </a>
                      </>
                    )}
                    {p.partySource && (
                      <>
                        {" "}
                        ·{" "}
                        <a
                          href={p.partySource}
                          target="_blank"
                          rel="noreferrer"
                        >
                          {p.partySource.includes("wikipedia.org")
                            ? "Wikipedia · vinculación"
                            : "Vinculación política"}
                        </a>
                      </>
                    )}
                  </li>
                ))}
            </ul>
          </div>
        </details>
      </div>
      {selected && (
        <div
          className={`map-person ${selected.presidency.person ? "" : "map-person-empty"}`}
          role="tooltip"
          id={`${id}-tooltip`}
          ref={tooltip}
        >
          {selected.presidency.person && (
            <div className="map-person-photo">
              <PortraitImage
                src={person?.src}
                name={selected.presidency.name}
                initials={selected.presidency.name
                  .split(" ")
                  .slice(0, 2)
                  .map((part) => part[0])
                  .join("")}
              />
            </div>
          )}
          <div>
            <small>
              {selected.name} · {selected.presidency.territoryName}
            </small>
            <strong>{selected.presidency.name}</strong>
            {selected.presidency.person && (
              <span>{selected.presidency.partyLabel}</span>
            )}
            {selected.presidency.inOfficeSince && (
              <time dateTime={selected.presidency.inOfficeSince}>
                {date === mapCheckedAt
                  ? "En el cargo desde"
                  : "Desde (fecha documental)"}{" "}
                · {dateLabel(selected.presidency.inOfficeSince)}
              </time>
            )}
            {date !== mapCheckedAt &&
              selected.presidency.title.includes("sustitución") && (
                <span>{selected.presidency.title}</span>
              )}
          </div>
        </div>
      )}
    </div>
  );
}
