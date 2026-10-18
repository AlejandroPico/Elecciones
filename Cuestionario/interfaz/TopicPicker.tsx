import { useState } from "react";
import { bank, type Draws } from "./sesion";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";

export default function TopicPicker({
  initial,
  draws,
  answers,
  apply,
  profile,
}: {
  initial: string[];
  draws: Draws;
  answers: Answers;
  apply: (ids: string[]) => void;
  profile: () => void;
}) {
  const [selected, setSelected] = useState(initial);
  const [search, setSearch] = useState("");
  const matches = (title: string) =>
    title
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLocaleLowerCase("es")
      .includes(
        search
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "")
          .toLocaleLowerCase("es"),
      );
  const toggle = (id: string) =>
    setSelected((s) =>
      s.includes(id) ? s.filter((i) => i !== id) : [...s, id],
    );
  return (
    <section
      className="section-content topic-picker"
      aria-labelledby="topics-title"
    >
      <header className="topic-heading">
        <h1 id="topics-title" className="section-title">
          Cuestionario
        </h1>
        <button className="quiet-button" onClick={profile}>
          Mi perfil
        </button>
      </header>
      <div className="topic-toolbar">
        <input
          aria-label="Buscar tema"
          type="search"
          placeholder="Buscar tema"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button
          className="quiet-button"
          onClick={() => setSelected(bank.categories.map((c) => c.id))}
        >
          Todos
        </button>
        <button className="quiet-button" onClick={() => setSelected([])}>
          Ninguno
        </button>
      </div>
      <p className="topic-note">
        10 preguntas aleatorias por tema. Puedes parar y retomar en cualquier
        momento durante esta visita. Cambiar de temas conserva tus respuestas y
        el sorteo.
      </p>
      <div className="topic-groups">
        {bank.groups.map((group) => {
          const topics = bank.categories.filter(
            (c) => group.categoryIds.includes(c.id) && matches(c.title),
          );
          return topics.length ? (
            <section key={group.title}>
              <h2>{group.title}</h2>
              <div className="topic-options">
                {topics.map((c) => {
                  const answered = (draws[c.id] ?? []).filter(
                    (id) => answers[id]?.value != null,
                  ).length;
                  const skipped = (draws[c.id] ?? []).filter(
                    (id) => answers[id]?.value === null,
                  ).length;
                  return (
                    <label
                      key={c.id}
                      className={selected.includes(c.id) ? "selected" : ""}
                    >
                      <input
                        type="checkbox"
                        checked={selected.includes(c.id)}
                        onChange={() => toggle(c.id)}
                      />
                      <span>{c.title}</span>
                      {answered + skipped > 0 && (
                        <small>
                          {answered} resp.{skipped ? ` · ${skipped} omit.` : ""}
                        </small>
                      )}
                    </label>
                  );
                })}
              </div>
            </section>
          ) : null;
        })}
      </div>
      {!bank.categories.some((c) => matches(c.title)) && (
        <p role="status">No hay temas con ese nombre.</p>
      )}
      <div className="topic-start">
        <span aria-live="polite">
          {selected.length} {selected.length === 1 ? "tema" : "temas"} · hasta{" "}
          {selected.length * 10} preguntas
        </span>
        <button
          className="primary-button"
          disabled={!selected.length}
          onClick={() => apply(selected)}
        >
          {Object.keys(draws).length ? "Continuar" : "Empezar"}
        </button>
      </div>
      <p className="topic-footnote">
        Comparación experimental con documentos históricos y generales. Las
        codificaciones están abiertas a revisión; no equivalen a programas
        nacionales de 2026.
      </p>
    </section>
  );
}
