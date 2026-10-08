import { lazy, Suspense, useEffect, useState } from "react";
import { ChevronDown, Landmark } from "lucide-react";
import territories from "../Autonomías/territorios.json";
export { territories };
const Catalonia = lazy(() => import("./Catalonia"));
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
}: {
  selected?: string;
  openSection: (id: string) => void;
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
        className={route ? "active" : ""}
        aria-expanded={open}
        onClick={() => setOpen(!open)}
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
                      {territory.kind === "ciudad" ? "Asamblea" : "Parlamento"}
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
  return (
    <div className="section-content">
      <h1 className="section-title">
        {route
          ? `${route.territory.name} · ${route.section === "government" ? "Gobierno" : route.territory.kind === "ciudad" ? "Asamblea" : "Parlamento"}`
          : "Gobiernos autonómicos"}
      </h1>
      {route?.territory.id === "cataluna" ? (
        <Suspense
          fallback={
            <span className="sr-only" role="status">
              Cargando Cataluña
            </span>
          }
        >
          <Catalonia
            key={route.section}
            section={route.section as "government" | "parliament"}
            selected={route.snapshot}
            openSection={openSection}
            openPerson={openPerson}
            active={active}
          />
        </Suspense>
      ) : (
        <p className="small-note">Contenido pendiente de incorporar.</p>
      )}
    </div>
  );
}
