import { Fragment, useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Download,
  FileText,
  Search,
} from "lucide-react";
import {
  portraits,
  logos,
  organizations,
  people,
  findPerson,
  offices,
  reviewedAt,
  type Person,
  type Reference,
} from "./datos/catalogo";
import { ageAt } from "./edad";
import { useInfiniteList } from "../../src/app/useInfiniteList";
import { activityOf, matchesPerson, orderPeople, type Order } from "./orden";
import PartyDetail from "../../Partidos/interfaz/Ficha";
import { Portrait } from "./Retrato";
import {
  activityLabels,
  personActivity,
  type ActivityState,
} from "./actividad";
import { ownOfficeTerms } from "./relaciones";
export { Portrait } from "./Retrato";
import Sources from "../../src/app/Sources";
import {
  affiliationLabel,
  affiliationOptions,
  matchesAffiliation,
} from "./vinculaciones";
type Route = { kind: "person" | "party" | "office"; id: string };
const organizationsById = new Map(organizations.map((o) => [o.id, o]));
const options = affiliationOptions(people, organizations);
export default function Archive({
  initialRoute,
  close,
  openParty,
  onNavigate,
}: {
  initialRoute?: Route;
  close?: () => void;
  openParty?: (id: string) => void;
  onNavigate?: (route?: Route) => void;
}) {
  const [order, setOrder] = useState<Order>("name");
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [activityFilter, setActivityFilter] = useState<ActivityState | "all">(
    "all",
  );
  const [history, setHistory] = useState<Route[]>(
    initialRoute ? [initialRoute] : [],
  );
  const heading = useRef<HTMLHeadingElement>(null);
  const route = onNavigate ? initialRoute : history.at(-1);
  const person = route?.kind === "person" ? findPerson(route.id) : undefined;
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
  const foundPeople = useMemo(
    () =>
      orderPeople(
        people.filter(
          (p) =>
            matchesPerson(
              p,
              search,
              p.organization
                ? organizationsById.get(p.organization)?.fullName
                : undefined,
            ) &&
            matchesAffiliation(p, filter) &&
            (activityFilter === "all" || personActivity(p) === activityFilter),
        ),
        order,
      ),
    [search, filter, order, activityFilter],
  );
  const { visibleCount, sentinel } = useInfiniteList(
    foundPeople.length,
    `${search}|${filter}|${order}|${activityFilter}`,
    40,
    !route,
  );
  function go(kind: Route["kind"], id: string) {
    if (onNavigate) onNavigate({ kind, id });
    else setHistory((h) => [...h, { kind, id }]);
  }
  useEffect(() => {
    if (route) {
      heading.current?.focus({ preventScroll: true });
      if (!onNavigate)
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
      {!route && (
        <>
          <div className="archive-controls">
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
            <select
              aria-label="Filtrar personas por vinculación"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="all">Todas las vinculaciones</option>
              {options.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
              <option value="independent">Independientes</option>
              <option value="pending">Vinculación pendiente</option>
            </select>
            <select
              aria-label="Filtrar personas por actividad"
              value={activityFilter}
              onChange={(e) =>
                setActivityFilter(e.target.value as ActivityState | "all")
              }
            >
              <option value="all">Activos primero · todos</option>
              <option value="active">Actividad actual documentada</option>
              <option value="unknown">Actividad por confirmar</option>
              <option value="historical">Archivo histórico</option>
            </select>
            <select
              aria-label="Ordenar personas"
              value={order}
              onChange={(e) => setOrder(e.target.value as Order)}
            >
              <option value="name">Nombre · A–Z</option>
              <option value="recent">Actividad más reciente</option>
              <option value="oldest">Actividad más antigua</option>
              <option value="rank">Cargos más altos primero</option>
            </select>
          </div>
          <div className="people-grid">
            {foundPeople.slice(0, visibleCount).map((p, i) => (
              <Fragment key={p.id}>
                {(i === 0 ||
                  personActivity(foundPeople[i - 1]) !== personActivity(p)) && (
                  <h2 className="catalog-group-title">
                    {activityLabels[personActivity(p)]}
                  </h2>
                )}
                <button
                  className="person-card"
                  key={p.id}
                  onClick={() => go("person", p.id)}
                  aria-label={`Ficha de ${p.fullName ?? p.name}`}
                >
                  <div className="person-photo">
                    <Portrait person={p} />
                  </div>
                  <div className="person-card-body">
                    <h2>{p.fullName ?? p.name}</h2>
                    <div className="person-shutter">
                      <div>
                        <p className="person-party">
                          {affiliationLabel(p, organizations)}
                        </p>
                        <p>{activityOf(p).roles.join(" · ")}</p>
                      </div>
                    </div>
                  </div>
                </button>
              </Fragment>
            ))}
          </div>
          {foundPeople.length === 0 && (
            <p className="archive-empty">
              No hay fichas que coincidan con esta búsqueda.
            </p>
          )}
          <div
            ref={sentinel}
            className="infinite-sentinel"
            aria-hidden="true"
          />
        </>
      )}
      {route && (
        <>
          <button
            className="text-button archive-back"
            onClick={() =>
              onNavigate
                ? close
                  ? close()
                  : onNavigate(undefined)
                : history.length === 1 && close
                  ? close()
                  : setHistory((h) => h.slice(0, -1))
            }
          >
            <ArrowLeft size={16} />
            {history.length > 1
              ? "Volver a la ficha anterior"
              : close
                ? "Volver a partidos"
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
                    {person.photoLicenseUrl && (
                      <>
                        {" · "}
                        <a
                          href={person.photoLicenseUrl}
                          target="_blank"
                          rel="noreferrer"
                        >
                          {person.photoLicense ?? "Licencia"}
                        </a>
                      </>
                    )}
                    {person.photoLicense && !person.photoLicenseUrl && (
                      <> · {person.photoLicense}</>
                    )}
                    {person.photoDate && (
                      <>
                        <br />
                        {person.photoDate}
                      </>
                    )}
                  </p>
                )}
                <div className="identity-links">
                  {relatedParty && (
                    <button
                      onClick={() =>
                        openParty
                          ? openParty(relatedParty.id)
                          : go("party", relatedParty.id)
                      }
                    >
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
                {!!person.affiliations?.length && (
                  <article>
                    <h3>Vinculaciones políticas</h3>
                    <ol className="political-timeline">
                      {person.affiliations.map((affiliation, i) => (
                        <li key={i}>
                          <span>
                            {affiliation.period ??
                              "Periodo no precisado en la fuente"}
                          </span>
                          <h4>
                            {affiliation.kind === "association"
                              ? `Vinculación con ${affiliation.name}`
                              : affiliation.name}
                          </h4>
                          {affiliation.note && <p>{affiliation.note}</p>}
                          <a
                            href={affiliation.source.url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Fuente
                            <ArrowUpRight size={12} />
                          </a>
                          {affiliation.additionalSource && (
                            <a
                              href={affiliation.additionalSource.url}
                              target="_blank"
                              rel="noreferrer"
                            >
                              Periodo
                              <ArrowUpRight size={12} />
                            </a>
                          )}
                        </li>
                      ))}
                    </ol>
                  </article>
                )}
                {person.sections.includes("datos-personales.json") && (
                  <article>
                    <h3>Datos personales</h3>
                    <dl className="technical-data">
                      <div>
                        <dt>Nombre completo</dt>
                        <dd>{person.fullName ?? person.name}</dd>
                      </div>
                      {person.birth && (
                        <div>
                          <dt>Nacimiento</dt>
                          <dd>{person.birth}</dd>
                        </div>
                      )}
                      {person.birthNote && (
                        <div>
                          <dt>Contraste de fuentes</dt>
                          <dd>{person.birthNote}</dd>
                        </div>
                      )}
                      {person.deathYear ? (
                        <div>
                          <dt>Fallecimiento</dt>
                          <dd>
                            {person.deathDate
                              ? new Intl.DateTimeFormat("es-ES", {
                                  day: "numeric",
                                  month: "long",
                                  year: "numeric",
                                }).format(
                                  new Date(person.deathDate + "T12:00:00"),
                                )
                              : person.deathYear}
                          </dd>
                        </div>
                      ) : (
                        person.birthDate &&
                        ageAt(person.birthDate) <= 110 && (
                          <div>
                            <dt>Edad</dt>
                            <dd>{ageAt(person.birthDate)} años</dd>
                          </div>
                        )
                      )}
                    </dl>
                    {!!person.personalSources?.length && (
                      <Sources sources={person.personalSources} />
                    )}
                  </article>
                )}
                {!!person.education?.length && (
                  <article>
                    <h3>Formación</h3>
                    <ul className="education-list">
                      {person.education.map((e) => (
                        <li key={e}>{e}</li>
                      ))}
                    </ul>
                    {!!person.formationSources?.length && (
                      <Sources sources={person.formationSources} />
                    )}
                  </article>
                )}
                {!!person.institutionalBiography?.length && (
                  <article>
                    <h3>Datos biográficos institucionales</h3>
                    {person.institutionalBiography.map((item, i) => (
                      <div key={i}>
                        <p>{item.text}</p>
                        <Sources sources={[item.source]} />
                      </div>
                    ))}
                  </article>
                )}
                {(person.summary || person.timeline.length > 0) && (
                  <article>
                    <span className="eyebrow">FICHA INFORMATIVA</span>
                    <h3>Trayectoria</h3>
                    <p>{person.summary}</p>
                    <ol className="political-timeline">
                      {person.timeline.map((t, i) => (
                        <li key={i}>
                          <span>{t.period}</span>
                          <h4>{t.title}</h4>
                          <a
                            href={t.source.url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Fuente
                            <ArrowUpRight size={12} />
                          </a>
                        </li>
                      ))}
                    </ol>
                  </article>
                )}
                {!!person.dossier?.length && (
                  <article>
                    <h3>Actuaciones y controversias</h3>
                    {person.dossier.map((d) => (
                      <div className="dossier-item" key={d.date + d.title}>
                        <time>{d.date}</time>
                        <h4>{d.title}</h4>
                        <p>{d.text}</p>
                        <p className="small-note">{d.status}</p>
                        <Sources
                          sources={[d.source, ...(d.additionalSources ?? [])]}
                        />
                      </div>
                    ))}
                  </article>
                )}
                {!!ownOfficeTerms(person).length && (
                  <article>
                    <h3>Relaciones por cargo</h3>
                    <ol className="political-timeline">
                      {ownOfficeTerms(person).map((m) => (
                        <li key={`${m.name}-${m.period}`}>
                          <span>{m.period}</span>
                          <h4>
                            {m.office ? (
                              <button
                                className="inline-link"
                                onClick={() => go("office", m.office!)}
                              >
                                {m.name}
                              </button>
                            ) : (
                              m.name
                            )}
                          </h4>
                          {m.source && <Sources sources={[m.source]} />}
                        </li>
                      ))}
                    </ol>
                  </article>
                )}
                {!!person.congressGroups?.length && (
                  <article>
                    <h3>Adscripciones en el Congreso</h3>
                    <p className="small-note">
                      Grupos parlamentarios del periodo indicado; no acreditan
                      por sí solos militancia ni afiliación actual.
                    </p>
                    <ol className="political-timeline">
                      {person.congressGroups.map((term) => (
                        <li key={`${term.title}-${term.period}`}>
                          <span>{term.period}</span>
                          <h4>{term.title}</h4>
                          <Sources sources={[term.source]} />
                        </li>
                      ))}
                    </ol>
                  </article>
                )}
                {person.activity && (
                  <article>
                    <h3>Actividad documentada</h3>
                    <p>{person.activity.reason}</p>
                    <Sources sources={person.activity.sources} />
                  </article>
                )}
                {!!relatedParty?.documents.length && (
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
                {!!person.references.length && (
                  <article>
                    <span className="eyebrow">FUENTES</span>
                    <h3>Documentación de esta ficha</h3>
                    <Sources sources={person.references} />
                    <p className="small-note">
                      Trayectoria resumida; no es una evaluación de gestión ni
                      un historial exhaustivo de actuaciones. Datos revisados el{" "}
                      {reviewedAt}.
                    </p>
                  </article>
                )}
              </div>
            </div>
          )}
          {party && <PartyDetail party={party} heading={heading} go={go} />}
          {office && (
            <article className="office-detail" key={office.id}>
              <span className="eyebrow">HISTORIA DEL CARGO</span>
              <h2 ref={heading} tabIndex={-1}>
                {office.name}
              </h2>
              <p>{office.description}</p>
              <div className="office-chain">
                {office.members.map((m, i) => {
                  const p = findPerson(m.person)!;
                  return (
                    <button
                      key={`${m.person}-${i}`}
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
