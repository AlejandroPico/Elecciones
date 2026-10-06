import { useEffect, useRef, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  BookOpen,
  Download,
  FileText,
  Landmark,
  Search,
  Users,
} from "lucide-react";
import {
  portraits,
  organizations,
  people,
  offices,
  reviewedAt,
  type Person,
  type Reference,
} from "../Elecciones/Generales Noviembre 2026/archivo-politico";
type Route = { kind: "person" | "party" | "office"; id: string };
function Portrait({ person }: { person: Person }) {
  const [error, setError] = useState(false);
  return person.portrait && !error ? (
    <img
      src={portraits[person.portrait]}
      alt={person.name}
      loading="lazy"
      onError={() => setError(true)}
    />
  ) : (
    <div className="portrait-placeholder">
      <span>{person.initials}</span>
      <small>Retrato pendiente</small>
    </div>
  );
}
function Sources({ sources }: { sources: Reference[] }) {
  return (
    <ul className="reference-list">
      {sources.map((s) => (
        <li key={s.url}>
          <a href={s.url} target="_blank" rel="noreferrer">
            {s.label}
            <ArrowUpRight size={14} />
          </a>
        </li>
      ))}
    </ul>
  );
}
export default function Archive() {
  const [tab, setTab] = useState<"people" | "parties" | "offices">("people");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [history, setHistory] = useState<Route[]>([]);
  const heading = useRef<HTMLHeadingElement>(null);
  const route = history.at(-1);
  const person =
    route?.kind === "person"
      ? people.find((p) => p.id === route.id)
      : undefined;
  const party =
    route?.kind === "party"
      ? organizations.find((p) => p.id === route.id)
      : undefined;
  const office =
    route?.kind === "office"
      ? offices.find((o) => o.id === route.id)
      : undefined;
  const relatedParty = person
    ? organizations.find((p) => p.id === person.organization)
    : undefined;
  const match = (text: string) =>
    text
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .includes(
        search
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "")
          .toLowerCase()
          .trim(),
      );
  const foundPeople = people.filter(
    (p) =>
      match(`${p.name} ${p.role} ${p.relation}`) &&
      (filter === "all" ||
        p.organization === filter ||
        (filter === "other" && !p.organization)),
  );
  function go(kind: Route["kind"], id: string) {
    setHistory((h) => [...h, { kind, id }]);
  }
  useEffect(() => {
    if (route) {
      heading.current?.focus({ preventScroll: true });
      heading.current?.scrollIntoView({
        block: "nearest",
        behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "instant"
          : "smooth",
      });
    }
  }, [route]);
  return (
    <section className="archive">
      <div className="archive-banner">
        <BookOpen size={18} />
        <p>
          Archivo inicial · {people.length} personas y {organizations.length}{" "}
          partidos. Las fichas no acreditan candidatura en 2026.
        </p>
        <span>Revisado: {reviewedAt}</span>
      </div>
      {!route && (
        <>
          <div className="archive-controls">
            <div
              className="archive-tabs"
              role="group"
              aria-label="Contenido del archivo"
            >
              <button
                aria-pressed={tab === "people"}
                className={tab === "people" ? "active" : ""}
                onClick={() => {
                  setTab("people");
                  setSearch("");
                }}
              >
                <Users size={16} />
                Personas
              </button>
              <button
                aria-pressed={tab === "parties"}
                className={tab === "parties" ? "active" : ""}
                onClick={() => {
                  setTab("parties");
                  setSearch("");
                }}
              >
                <FileText size={16} />
                Partidos
              </button>
              <button
                aria-pressed={tab === "offices"}
                className={tab === "offices" ? "active" : ""}
                onClick={() => {
                  setTab("offices");
                  setSearch("");
                }}
              >
                <Landmark size={16} />
                Cargos e historia
              </button>
            </div>
            <label className="archive-search">
              <Search size={16} />
              <input
                type="search"
                aria-label="Buscar en el archivo"
                placeholder="Buscar nombre, partido o cargo"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </label>
          </div>
          {tab === "people" && (
            <>
              <div className="archive-filter">
                <span>{foundPeople.length} fichas</span>
                <select
                  aria-label="Filtrar personas por vinculación"
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                >
                  <option value="all">Todas las vinculaciones</option>
                  {organizations.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                  <option value="other">
                    Sin partido asociado en la ficha
                  </option>
                </select>
              </div>
              <div className="people-grid">
                {foundPeople.map((p, i) => (
                  <button
                    className="person-card"
                    key={p.id}
                    onClick={() => go("person", p.id)}
                  >
                    <div className="person-photo">
                      <Portrait person={p} />
                      <span className="person-number">
                        {String(i + 1).padStart(2, "0")}
                      </span>
                    </div>
                    <div className="person-card-body">
                      <span className="eyebrow">{p.relation}</span>
                      <h2>{p.name}</h2>
                      <p>{p.role}</p>
                      <span className="card-link">
                        Ver ficha
                        <ArrowUpRight size={16} />
                      </span>
                    </div>
                  </button>
                ))}
              </div>
              {foundPeople.length === 0 && (
                <p className="archive-empty">
                  No hay fichas que coincidan con esta búsqueda.
                </p>
              )}
            </>
          )}
          {tab === "parties" && (
            <div className="party-grid">
              {organizations
                .filter((p) => match(`${p.name} ${p.fullName}`))
                .map((p) => (
                  <button
                    className="organization-card"
                    key={p.id}
                    onClick={() => go("party", p.id)}
                  >
                    <span className="organization-mark">{p.name}</span>
                    <span className="eyebrow">PARTIDO POLÍTICO</span>
                    <h2>{p.fullName}</h2>
                    <p>{p.foundation}</p>
                    <span className="card-link">
                      Historia, personas y documentos
                      <ArrowUpRight size={16} />
                    </span>
                  </button>
                ))}
            </div>
          )}
          {tab === "offices" && (
            <div className="office-grid">
              {offices
                .filter((o) => match(o.name))
                .map((o) => (
                  <article className="office-card" key={o.id}>
                    <Landmark size={23} />
                    <h2>{o.name}</h2>
                    <p>{o.description}</p>
                    <div className="office-preview">
                      {o.members.map((m) => (
                        <button
                          key={m.person}
                          onClick={() => go("person", m.person)}
                        >
                          <span>{m.period}</span>
                          <strong>
                            {people.find((p) => p.id === m.person)?.name}
                          </strong>
                          <ArrowRight size={14} />
                        </button>
                      ))}
                    </div>
                    <button
                      className="profile-link"
                      onClick={() => go("office", o.id)}
                    >
                      Ver la secuencia de titulares
                      <ArrowUpRight size={15} />
                    </button>
                  </article>
                ))}
            </div>
          )}
          <p className="archive-footnote">
            Catálogo parcial en ampliación. Las listas proclamadas se
            incorporarán por elección, cámara y circunscripción, con posición y
            suplencia. La pertenencia a una lista no implica un nombramiento
            ministerial.
          </p>
        </>
      )}
      {route && (
        <>
          <button
            className="text-button archive-back"
            onClick={() => setHistory((h) => h.slice(0, -1))}
          >
            <ArrowLeft size={16} />
            {history.length > 1
              ? "Volver a la ficha anterior"
              : "Volver al archivo"}
          </button>
          {person && (
            <div className="biography-layout" key={person.id}>
              <aside className="biography-identity">
                <div className="biography-photo">
                  <Portrait person={person} />
                </div>
                <div className="biography-name">
                  <span className="eyebrow">{person.relation}</span>
                  <h2 ref={heading} tabIndex={-1}>
                    {person.name}
                  </h2>
                  <p>{person.role}</p>
                </div>
                {person.photoCredit && (
                  <p className="photo-credit">
                    Imagen: {person.photoCredit}.{" "}
                    <a
                      href={person.photoSource}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Origen
                      <ArrowUpRight size={10} />
                    </a>
                  </p>
                )}
                <div className="identity-links">
                  {relatedParty && (
                    <button onClick={() => go("party", relatedParty.id)}>
                      Ficha de {relatedParty.name}
                      <ArrowRight size={15} />
                    </button>
                  )}
                  {person.offices.map((id) => (
                    <button key={id} onClick={() => go("office", id)}>
                      {offices.find((o) => o.id === id)?.name}
                      <ArrowRight size={15} />
                    </button>
                  ))}
                </div>
              </aside>
              <div className="biography-content">
                <article>
                  <span className="eyebrow">FICHA INFORMATIVA</span>
                  <h3>Trayectoria</h3>
                  <p>{person.summary}</p>
                  <ol className="political-timeline">
                    {person.timeline.map((t, i) => (
                      <li key={i}>
                        <span>{t.period}</span>
                        <h4>{t.title}</h4>
                        <a href={t.source.url} target="_blank" rel="noreferrer">
                          Fuente
                          <ArrowUpRight size={12} />
                        </a>
                      </li>
                    ))}
                  </ol>
                </article>
                {person.offices.map((id) => {
                  const o = offices.find((o) => o.id === id)!;
                  return (
                    <article key={id}>
                      <span className="eyebrow">RELACIONES POR CARGO</span>
                      <h3>{o.name}</h3>
                      <div className="relation-nodes">
                        {o.members.map((m) => (
                          <button
                            key={m.person}
                            className={m.person === person.id ? "current" : ""}
                            disabled={m.person === person.id}
                            onClick={() => go("person", m.person)}
                          >
                            <span>{m.period}</span>
                            <strong>
                              {people.find((p) => p.id === m.person)?.name}
                            </strong>
                            <ArrowRight size={14} />
                          </button>
                        ))}
                      </div>
                    </article>
                  );
                })}
                {relatedParty && (
                  <article>
                    <span className="eyebrow">DOCUMENTACIÓN</span>
                    <h3>Programas del partido</h3>
                    <p>
                      Los documentos de 2023 se ofrecen como archivo histórico.
                      El programa de 2026 no está incorporado.
                    </p>
                    {relatedParty.documents.map((d) => (
                      <a
                        className="document-link"
                        key={d.url}
                        href={d.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        <FileText size={21} />
                        <span>
                          <strong>{d.title}</strong>
                          <small>{d.election} · PDF</small>
                        </span>
                        <Download size={17} />
                      </a>
                    ))}
                  </article>
                )}
                <article>
                  <span className="eyebrow">FUENTES PRIMARIAS</span>
                  <h3>Documentación de esta ficha</h3>
                  <Sources sources={person.references} />
                  <p className="small-note">
                    Trayectoria resumida; no es una evaluación de gestión ni un
                    historial exhaustivo de actuaciones. Datos revisados el{" "}
                    {reviewedAt}.
                  </p>
                </article>
              </div>
            </div>
          )}
          {party && (
            <div className="party-detail" key={party.id}>
              <div className="party-detail-head">
                <span className="organization-mark">{party.name}</span>
                <div>
                  <span className="eyebrow">FICHA DE PARTIDO</span>
                  <h2 ref={heading} tabIndex={-1}>
                    {party.fullName}
                  </h2>
                  <p>Fundación: {party.foundation}</p>
                </div>
              </div>
              <p className="party-description">{party.summary}</p>
              <div className="party-detail-grid">
                <article>
                  <span className="eyebrow">ARCHIVO DOCUMENTAL</span>
                  <h3>Programas publicados</h3>
                  {party.documents.map((d) => (
                    <a
                      className="document-link"
                      href={d.url}
                      target="_blank"
                      rel="noreferrer"
                      key={d.url}
                    >
                      <FileText size={22} />
                      <span>
                        <strong>{d.title}</strong>
                        <small>{d.election} · PDF</small>
                      </span>
                      <Download size={17} />
                    </a>
                  ))}
                  <p className="small-note">
                    Puedes abrir el PDF y descargarlo desde el visor. No es un
                    programa de 2026 ni se usa para puntuar el banco piloto.
                  </p>
                  <h3>Personas en el archivo</h3>
                  <div className="related-people">
                    {people
                      .filter((p) => p.organization === party.id)
                      .map((p) => (
                        <button key={p.id} onClick={() => go("person", p.id)}>
                          <Portrait person={p} />
                          <span>
                            {p.name}
                            <small>{p.role}</small>
                          </span>
                          <ArrowRight size={16} />
                        </button>
                      ))}
                  </div>
                </article>
                <article>
                  <span className="eyebrow">SELECCIÓN HISTÓRICA</span>
                  <h3>Etapas documentadas</h3>
                  <ol className="political-timeline">
                    {party.history.map((h, i) => (
                      <li key={i}>
                        <span>{h.period}</span>
                        {h.person ? (
                          <button
                            className="timeline-link"
                            onClick={() => go("person", h.person!)}
                          >
                            {h.title}
                            <ArrowUpRight size={14} />
                          </button>
                        ) : (
                          <h4>{h.title}</h4>
                        )}
                      </li>
                    ))}
                  </ol>
                  <p className="small-note">
                    Esta selección todavía no reúne todos los dirigentes desde
                    la fundación.
                  </p>
                  <Sources sources={party.references} />
                </article>
              </div>
            </div>
          )}
          {office && (
            <article className="office-detail" key={office.id}>
              <span className="eyebrow">HISTORIA DEL CARGO</span>
              <h2 ref={heading} tabIndex={-1}>
                {office.name}
              </h2>
              <p>{office.description}</p>
              <div className="office-chain">
                {office.members.map((m) => {
                  const p = people.find((p) => p.id === m.person)!;
                  return (
                    <button
                      key={m.person}
                      onClick={() => go("person", m.person)}
                    >
                      <Portrait person={p} />
                      <div>
                        <span className="eyebrow">{m.period}</span>
                        <h3>{p.name}</h3>
                        <p>{p.relation}</p>
                      </div>
                      <ArrowRight size={19} />
                    </button>
                  );
                })}
              </div>
              <Sources sources={[office.source]} />
            </article>
          )}
        </>
      )}
    </section>
  );
}
