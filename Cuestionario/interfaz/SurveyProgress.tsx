import { useEffect, useRef } from "react";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";
import DragRail from "../../Gobiernos/interfaz/DragRail";
import { bank, type SessionQuestion } from "./sesion";

export default function SurveyProgress({
  questions,
  current,
  answers,
  navigate,
}: {
  questions: SessionQuestion[];
  current: string;
  answers: Answers;
  navigate: (id: string) => void;
}) {
  const active = useRef<HTMLDivElement>(null);
  useEffect(() => {
    active.current?.scrollIntoView({
      block: "nearest",
      inline: "nearest",
      behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "instant"
        : "smooth",
    });
  }, [questions.find((q) => q.id === current)?.category]);
  return (
    <nav className="session-progress" aria-label="Navegación por preguntas">
      <DragRail
        className="session-progress-strip"
        aria-label="Temas seleccionados; arrastra para recorrerlos"
      >
        {bank.categories.map((category) => {
          const items = questions.filter((q) => q.category === category.id);
          if (!items.length) return null;
          const index = items.findIndex((q) => q.id === current),
            expanded = index >= 0;
          return (
            <div
              key={category.id}
              ref={expanded ? active : undefined}
              className={`session-track ${expanded ? "expanded" : ""}`}
            >
              <button
                className="session-track-title"
                onClick={() =>
                  navigate(items.find((q) => !answers[q.id])?.id ?? items[0].id)
                }
                title={category.title}
              >
                {category.title}
              </button>
              {expanded && (
                <span
                  className="session-track-count"
                  style={{ left: `${((index + 0.5) / items.length) * 100}%` }}
                >
                  {index + 1} de {items.length}
                </span>
              )}
              <div className="session-track-baseline" />
              {expanded && (
                <div
                  className="session-track-front"
                  style={{ width: `${((index + 1) / items.length) * 100}%` }}
                />
              )}
              <div className="session-track-items">
                {items.map((q, i) => {
                  const a = answers[q.id];
                  const color = !a
                    ? "pending"
                    : a.value === null
                      ? "omitted"
                      : a.value === -2
                        ? "negative strong"
                        : a.value === -1
                          ? "negative moderate"
                          : a.value === 2
                            ? "positive strong"
                            : a.value === 1
                              ? "positive moderate"
                              : "neutral";
                  return (
                    <button
                      key={q.id}
                      className={`session-step ${color}`}
                      style={
                        {
                          "--weight": `${a?.importance === 3 ? 7 : a?.importance === 2 ? 5 : 3}px`,
                        } as React.CSSProperties
                      }
                      aria-label={`${category.title}, pregunta ${i + 1}${a ? (a.value === null ? ", omitida" : `, respondida: ${a.value === -2 ? "muy en desacuerdo" : a.value === -1 ? "en desacuerdo" : a.value === 2 ? "muy de acuerdo" : a.value === 1 ? "de acuerdo" : "neutral"}`) : ", pendiente"}`}
                      aria-current={q.id === current ? "step" : undefined}
                      title={q.text}
                      onClick={() => navigate(q.id)}
                    />
                  );
                })}
              </div>
            </div>
          );
        })}
      </DragRail>
    </nav>
  );
}
