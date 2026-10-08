import type { RefObject } from "react";
import { ArrowUpRight, ArrowRight, FileText, Download } from "lucide-react";
import { people, findPerson } from "../../Políticos/interfaz/datos/catalogo";
import type { Organization } from "../../Políticos/interfaz/datos/tipos";
import { Portrait } from "../../Políticos/interfaz/Retrato";
import { PartyLogo } from "./Logotipo";
import Sources from "../../src/app/Sources";
import { matchesAffiliation } from "../../Políticos/interfaz/vinculaciones";
import { useInfiniteList } from "../../src/app/useInfiniteList";
function documentedDate(value: NonNullable<Organization["founding"]>) {
  if (value.precision <= 9) return value.date.slice(0, 4);
  return new Intl.DateTimeFormat("es-ES", value.precision === 10 ? { month: "long", year: "numeric" } : {day: "numeric", month:"long",year:"numeric"}).format(new Date(value.date+"T12:00:00"));
}
export default function PartyDetail({
  party,
  heading,
  go,
}: {
  party: Organization;
  heading: RefObject<HTMLHeadingElement | null>;
  go: (kind: "person", id: string) => void;
}) {
  const related = people.filter((p) => matchesAffiliation(p, party.id));
  const { visibleCount, sentinel } = useInfiniteList(related.length, party.id, 20);
  return (
    <div className="party-detail" key={party.id}>
      <div className="party-detail-head">
        <PartyLogo
          className={`party-profile-logo ${party.logoBackground === "dark" || ["pp", "eh-bildu", "bng", "pacma"].includes(party.id) ? "on-dark" : ""}`}
          party={party}
        />
        <div>
          <span className="eyebrow">FICHA DE PARTIDO</span>
          <h2 ref={heading} tabIndex={-1}>
            {party.fullName}
          </h2>
          {party.foundation && !party.foundation.startsWith("Pendiente") && (
            <p>Fundación: {party.foundation}</p>
          )}
          {!party.foundation && party.founding && <p>Fundación: {documentedDate(party.founding)}</p>}
          {party.dissolution && <p>Disolución documentada: {documentedDate(party.dissolution)}</p>}
          {(party.founding || party.dissolution) && <Sources sources={[...(party.founding ? [party.founding.source] : []), ...(party.dissolution ? [party.dissolution.source] : [])]} />}
        </div>
      </div>
      <p className="party-description">{party.summary}</p>
      {party.registration && (
        <dl className="technical-data party-registration">
          <div>
            <dt>Inscripción</dt>
            <dd>
              {new Intl.DateTimeFormat("es-ES").format(
                new Date(party.registration.date + "T12:00:00"),
              )}
            </dd>
          </div>
          <div>
            <dt>Localidad inscrita</dt>
            <dd>{party.registration.locality}</dd>
          </div>
          <div>
            <dt>Referencia registral</dt>
            <dd>
              <a
                href={party.registration.source}
                target="_blank"
                rel="noreferrer"
              >
                Registro {party.registration.id}
                <ArrowUpRight size={12} />
              </a>
            </dd>
          </div>
        </dl>
      )}
      {party.website && (
        <a
          className="document-link"
          href={party.website}
          target="_blank"
          rel="noreferrer"
        >
          Web oficial <ArrowUpRight size={16} />
        </a>
      )}
      <div className="party-detail-grid">
        {!!party.electoralResults?.length && (
          <article>
            <h3>Resultados electorales</h3>
            {party.electoralResults.map((result) => (
              <div key={`${result.date}-${result.chamber}`}>
                <p>{result.election} · {result.chamber === "congreso" ? "Congreso" : "Senado"}</p>
                <dl className="technical-data">
                  {result.seats !== undefined && <div><dt>Escaños</dt><dd>{result.seats}</dd></div>}
                  {result.votes !== undefined && <div><dt>Votos</dt><dd>{result.votes.toLocaleString("es-ES")}</dd></div>}
                  <div><dt>Candidatura</dt><dd>{result.candidature}</dd></div>
                </dl>
                <Sources sources={[result.source]} />
              </div>
            ))}
          </article>
        )}
        {!!party.publicResources?.length && (
          <article>
            <h3>Documentación pública</h3>
            {party.publicResources.map((resource) => (
              <a className="document-link" key={resource.url} href={resource.url} target="_blank" rel="noreferrer">
                <FileText size={20} />
                <span><strong>{resource.title}</strong><small>{resource.kind} {resource.date ? `· ${resource.date}` : "· fecha no indicada"}{resource.format ? ` · ${resource.format}` : ""}</small></span>
                {resource.format === "PDF" ? <Download size={16} /> : <ArrowUpRight size={16} />}
              </a>
            ))}
          </article>
        )}
        {!!party.documents.length && (
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
          </article>
        )}
        {!!related.length && (
          <article>
            <h3>Personas en el archivo</h3>
            <div className="related-people">
              {related.slice(0, visibleCount)
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
            <div ref={sentinel} className="infinite-sentinel" aria-hidden="true" />
          </article>
        )}
        {!!party.leadership.length && (
          <article className="party-leadership">
            <h3>Dirigentes</h3>
            <ol className="political-timeline">
              {party.leadership.map((leader, i) => (
                <li key={i}>
                  <span>{leader.period}</span>
                  <button
                    className="timeline-link"
                    onClick={() => go("person", leader.person)}
                  >
                    {findPerson(leader.person)?.fullName}
                    <ArrowUpRight size={14} />
                  </button>
                  <p>{leader.title}</p>
                  <Sources sources={[leader.source]} />
                </li>
              ))}
            </ol>
          </article>
        )}
        {!!party.history.length && (
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
              Esta selección todavía no reúne todos los dirigentes desde la
              fundación.
            </p>
            <Sources sources={party.references} />
          </article>
        )}
        {!party.history.length && !!party.references.length && (
          <article>
            <h3>Fuentes</h3>
            <Sources sources={party.references} />
          </article>
        )}
      </div>
    </div>
  );
}
