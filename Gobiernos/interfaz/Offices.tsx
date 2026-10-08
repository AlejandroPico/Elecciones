import { useState } from "react";
import { ArrowLeft, ArrowUpRight, Search } from "lucide-react";
import { offices } from "./catalogo";
import { findPerson } from "../../Políticos/interfaz/datos/catalogo";
import { Portrait } from "../../Políticos/interfaz/Retrato";
export default function Offices({
  openPerson,
  selectedOffice,
  openOffice,
}: {
  openPerson: (id: string) => void;
  selectedOffice?: string;
  openOffice?: (id?: string) => void;
}) {
  const [search, setSearch] = useState("");
  const [group, setGroup] = useState("all");
  const [selected, setSelected] = useState<string | null>(null);
  const office = offices.find((o) => o.id === (openOffice ? selectedOffice : selected));
  const priority = [
    "Gobierno",
    "Cortes Generales",
    "Secretarías de Estado",
    "Subsecretarías",
    "Secretarías generales",
    "Direcciones generales",
    "Administración territorial",
    "Instituciones",
    "Administración central",
  ];
  const groups = [...new Set(offices.map((o) => o.group))].sort(
    (a, b) => priority.indexOf(a) - priority.indexOf(b),
  );
  const normal = (s: string) =>
    s
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();
  return (
    <section className="offices-directory">
      {office ? (
        <>
          <button
            className="text-button archive-back"
            onClick={() => openOffice ? openOffice() : setSelected(null)}
          >
            <ArrowLeft size={16} />
            Volver a cargos
          </button>
          <h2>{office.name}</h2>
          <p className="small-note">
            {office.description.replace(/\s*No hay ficha todavía\.$/, "")}
          </p>
          {office.department && (
            <p className="small-note">{office.department}</p>
          )}
          {office.members.length ? (
            <div className="office-chain">
              {office.members.map((m, i) => {
                const p = findPerson(m.person);
                return p ? (
                  <button
                    key={`${m.person}-${i}`}
                    onClick={() => openPerson(p.id)}
                  >
                    <Portrait person={p} />
                    <div>
                      <span className="eyebrow">{m.period}</span>
                      <h3>{p.fullName ?? p.name}</h3>
                    </div>
                  </button>
                ) : null;
              })}
            </div>
          ) : (
            <p className="archive-empty">No hay ficha todavía.</p>
          )}
          <a
            className="text-button"
            href={office.source.url}
            target="_blank"
            rel="noreferrer"
          >
            {office.source.label}
            <ArrowUpRight size={14} />
          </a>
        </>
      ) : (
        <>
          <div className="archive-controls office-controls">
            <label className="archive-search">
              <Search size={16} />
              <input
                type="search"
                aria-label="Buscar cargo"
                placeholder="Buscar cargo"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </label>
            <select
              aria-label="Filtrar cargos por institución"
              value={group}
              onChange={(e) => setGroup(e.target.value)}
            >
              <option value="all">Todas las instituciones</option>
              {[...new Set(offices.map((o) => o.group))].map((g) => (
                <option key={g}>{g}</option>
              ))}
            </select>
          </div>
          {groups
            .filter((g) => group === "all" || group === g)
            .map((g) => {
              const found = offices
                .filter(
                  (o) =>
                    o.group === g &&
                    normal(o.name + " " + (o.department ?? "")).includes(
                      normal(search).trim(),
                    ),
                )
                .sort(
                  (a, b) =>
                    (a.id === "presidencia"
                      ? -1
                      : b.id === "presidencia"
                        ? 1
                        : Number(b.id.startsWith("vicepresidencia")) -
                          Number(a.id.startsWith("vicepresidencia"))) ||
                    a.name.localeCompare(b.name, "es"),
                );
              return found.length ? (
                <div className="office-category" key={g}>
                  <h2>{g}</h2>
                  <div className="office-list">
                    {found.map((o) => (
                      <button key={o.id} onClick={() => openOffice ? openOffice(o.id) : setSelected(o.id)}>
                        <span>
                          {o.name}
                          {o.department && <em>{o.department}</em>}
                        </span>
                        <small>
                          {o.members.length ? "Titulares" : "Ficha pendiente"}
                        </small>
                      </button>
                    ))}
                  </div>
                </div>
              ) : null;
            })}
          {!offices.some(
            (o) =>
              (group === "all" || o.group === group) &&
              normal(o.name + " " + (o.department ?? "")).includes(
                normal(search).trim(),
              ),
          ) && (
            <p className="archive-empty">
              No hay cargos que coincidan con esta búsqueda.
            </p>
          )}
        </>
      )}
    </section>
  );
}
