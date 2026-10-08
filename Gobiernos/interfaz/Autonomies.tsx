import { useEffect, useState } from "react";
import { ChevronDown, Landmark } from "lucide-react";
import territories from "../Autonomías/territorios.json";
export { territories };
export function autonomyEntry(
  region: string,
  section: "government" | "parliament",
) {
  return `${region}:${section}`;
}
export function readAutonomyEntry(id?: string) {
  const [region, section] = (id ?? "").split(":");
  const territory = territories.find((t) => t.id === region);
  return territory && (section === "government" || section === "parliament")
    ? { territory, section }
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
                        selected === autonomyEntry(territory.id, "government")
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
                        selected === autonomyEntry(territory.id, "parliament")
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
export default function Autonomies({ selected }: { selected?: string }) {
  const route = readAutonomyEntry(selected);
  return (
    <div className="section-content">
      <h1 className="section-title">
        {route
          ? `${route.territory.name} · ${route.section === "government" ? "Gobierno" : route.territory.kind === "ciudad" ? "Asamblea" : "Parlamento"}`
          : "Gobiernos autonómicos"}
      </h1>
      <p className="small-note">Contenido pendiente de incorporar.</p>
    </div>
  );
}
