import { lazy, Suspense, useEffect, useState } from "react";
import { ChevronDown, Landmark } from "lucide-react";
import territories from "../Autonomías/territorios.json";
export { territories };
const Catalonia = lazy(() => import("./Catalonia"));
const Madrid = lazy(() => import("./Madrid"));
const Valencia = lazy(() => import("./Valencia"));
const Andalucia = lazy(() => import("./Andalucia"));
const Canarias = lazy(() => import("./Canarias"));
const Ceuta = lazy(() => import("./Ceuta"));
const Melilla = lazy(() => import("./Melilla"));
const CastillaLaMancha = lazy(() => import("./CastillaLaMancha"));
const CastillaLeon = lazy(() => import("./CastillaLeon"));
const Aragon = lazy(() => import("./Aragon"));
const PaisVasco = lazy(() => import("./PaisVasco"));
const Navarra = lazy(() => import("./Navarra"));
const Asturias = lazy(() => import("./Asturias"));
const Cantabria = lazy(() => import("./Cantabria"));
const AutonomyMap = lazy(() => import("./AutonomyMap"));
export function autonomyEntry(
  region: string,
  section: "government" | "parliament",
) {
  return `${region}:${section}`;
}
export function readAutonomyEntry(id?: string) {
  const [region, section, snapshot] = (id ?? "").split(":");
  const territory = territories.find((t) => t.id === region);
  return territory && (section === "government" || section === "parliament")
    ? { territory, section, ...(snapshot ? { snapshot } : {}) }
    : undefined;
}
export function AutonomyMenu({
  selected,
  openSection,
  openOverview,
  active,
}: {
  selected?: string;
  openSection: (id: string) => void;
  openOverview: () => void;
  active: boolean;
}) {
  const route = readAutonomyEntry(selected);
  const [open, setOpen] = useState(!!route);
  const [expanded, setExpanded] = useState<string[]>(
    route ? [route.territory.id] : [],
  );
  useEffect(() => {
    const current = readAutonomyEntry(selected);
    if (current) {
      setOpen(true);
      setExpanded((items) => [...new Set([...items, current.territory.id])]);
    }
  }, [selected]);
  return (
    <div className="navigation-item autonomy-menu">
      <button
        className={active ? "active" : ""}
        aria-expanded={open}
        aria-current={active && !route ? "page" : undefined}
        onClick={() => {
          setOpen(!open);
          openOverview();
        }}
      >
        <Landmark size={17} />
        <span>Gobiernos autonómicos</span>
        <ChevronDown
          size={13}
          className={`tree-chevron ${open ? "open" : ""}`}
        />
      </button>
      <div className={`survey-tree ${open ? "open" : ""}`} inert={!open}>
        <div>
          {territories.map((territory) => {
            const expandedRegion = expanded.includes(territory.id);
            return (
              <div key={territory.id}>
                <button
                  aria-expanded={expandedRegion}
                  onClick={() =>
                    setExpanded(
                      expandedRegion
                        ? expanded.filter((id) => id !== territory.id)
                        : [...expanded, territory.id],
                    )
                  }
                >
                  <span>{territory.name}</span>
                  <ChevronDown
                    size={12}
                    className={`tree-chevron ${expandedRegion ? "open" : ""}`}
                  />
                </button>
                <div
                  className={`survey-tree ${expandedRegion ? "open" : ""}`}
                  inert={!expandedRegion}
                >
                  <div>
                    <button
                      aria-current={
                        route?.territory.id === territory.id &&
                        route.section === "government"
                          ? "page"
                          : undefined
                      }
                      onClick={() =>
                        openSection(autonomyEntry(territory.id, "government"))
                      }
                    >
                      Gobierno
                    </button>
                    <button
                      aria-current={
                        route?.territory.id === territory.id &&
                        route.section === "parliament"
                          ? "page"
                          : undefined
                      }
                      onClick={() =>
                        openSection(autonomyEntry(territory.id, "parliament"))
                      }
                    >
                      {territory.kind === "ciudad" || territory.id === "madrid"
                        ? "Asamblea"
                        : territory.id === "valencia"
                          ? "Les Corts"
                          : "Parlamento"}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
export default function Autonomies({
  selected,
  openSection,
  openPerson,
  active = true,
}: {
  selected?: string;
  openSection: (id: string) => void;
  openPerson: (id: string) => void;
  active?: boolean;
}) {
  const [last, setLast] = useState(selected);
  useEffect(() => {
    if (active) setLast(selected);
  }, [selected, active]);
  const route = readAutonomyEntry(active ? selected : last);
  const Institution =
    route?.territory.id === "cataluna"
      ? Catalonia
      : route?.territory.id === "madrid"
        ? Madrid
        : route?.territory.id === "valencia"
          ? Valencia
          : route?.territory.id === "andalucia"
            ? Andalucia
            : route?.territory.id === "canarias"
              ? Canarias
              : route?.territory.id === "ceuta"
                ? Ceuta
                : route?.territory.id === "melilla"
                  ? Melilla
                  : route?.territory.id === "castilla-la-mancha"
                    ? CastillaLaMancha
                    : route?.territory.id === "castilla-y-leon"
                      ? CastillaLeon
                      : route?.territory.id === "aragon"
                        ? Aragon
                        : route?.territory.id === "pais-vasco"
                          ? PaisVasco
                          : route?.territory.id === "navarra"
                            ? Navarra
                            : route?.territory.id === "asturias"
                              ? Asturias
                              : route?.territory.id === "cantabria"
                                ? Cantabria
                                : undefined;
  return (
    <div className="section-content">
      <h1 className="section-title">
        {route
          ? `${route.territory.name} · ${route.section === "government" ? "Gobierno" : route.territory.kind === "ciudad" || route.territory.id === "madrid" ? "Asamblea" : route.territory.id === "valencia" ? "Les Corts" : "Parlamento"}`
          : "Gobiernos autonómicos"}
      </h1>
      {Institution && route ? (
        <Suspense
          fallback={
            <span className="sr-only" role="status">
              Cargando {route.territory.name}
            </span>
          }
        >
          <Institution
            key={`${route.territory.id}:${route.section}`}
            section={route.section as "government" | "parliament"}
            selected={route.snapshot}
            openSection={openSection}
            openPerson={openPerson}
            active={active}
          />
        </Suspense>
      ) : !route ? (
        <Suspense
          fallback={
            <span className="sr-only" role="status">
              Cargando mapa autonómico
            </span>
          }
        >
          <AutonomyMap
            openGovernment={(territory) =>
              openSection(autonomyEntry(territory, "government"))
            }
          />
        </Suspense>
      ) : (
        <p className="small-note">Contenido pendiente de incorporar.</p>
      )}
    </div>
  );
}
