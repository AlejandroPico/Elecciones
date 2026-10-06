import { ArrowLeft, ArrowRight, Check, Minus } from "lucide-react";
import {
  categories,
  questions,
  type Category,
  type Question,
} from "../Elecciones";
import type { Answers } from "./model";
export function progressGroups(
  answers: Answers,
  index: number,
  themes: Category[] = categories,
  bank: Question[] = questions,
) {
  return themes.map((category) => {
    const items = bank.flatMap((question, i) =>
      question.category === category.id
        ? [
            {
              question,
              index: i,
              state: !Object.hasOwn(answers, question.id)
                ? "pending"
                : answers[question.id].value === null
                  ? "skipped"
                  : "answered",
            },
          ]
        : [],
    );
    return {
      category,
      items,
      completed: items.filter((item) => item.state !== "pending").length,
      active: items.some((item) => item.index === index),
    };
  });
}
export default function Progress({
  answers,
  index,
  navigate,
  showResults,
}: {
  answers: Answers;
  index: number;
  navigate: (index: number) => void;
  showResults: () => void;
}) {
  return (
    <nav className="question-progress" aria-label="Navegación por preguntas">
      <button
        className="progress-arrow"
        aria-label="Pregunta anterior"
        disabled={index === 0}
        onClick={() => navigate(index - 1)}
      >
        <ArrowLeft size={19} />
      </button>
      <div className="progress-groups">
        {progressGroups(answers, index).map(
          ({ category, items, completed, active }, i) => (
            <div
              key={category.id}
              className={`progress-group ${active ? "expanded" : "collapsed"} ${completed === items.length ? "complete" : ""}`}
            >
              {active ? (
                <>
                  <div className="progress-topic">
                    <span>{category.name}</span>
                    <span>
                      {completed} / {items.length}
                    </span>
                  </div>
                  <div className="progress-segments">
                    {items.map((item, j) => (
                      <button
                        key={item.question.id}
                        className={`progress-segment ${item.state} ${item.index === index ? "current" : ""}`}
                        aria-label={`${category.name}, pregunta ${j + 1}: ${item.question.text}${item.state === "skipped" ? " (omitida)" : item.state === "answered" ? " (respondida)" : ""}`}
                        aria-current={item.index === index ? "step" : undefined}
                        onClick={() => navigate(item.index)}
                        title={item.question.text}
                      >
                        {item.state === "answered" ? (
                          <Check size={12} />
                        ) : item.state === "skipped" ? (
                          <Minus size={12} />
                        ) : null}
                      </button>
                    ))}
                  </div>
                </>
              ) : (
                <button
                  className="collapsed-topic"
                  title={`${category.name} · ${completed}/${items.length}`}
                  aria-label={`${category.name}, ${completed} de ${items.length} preguntas completadas`}
                  onClick={() =>
                    navigate(
                      (
                        items.find((item) => item.state === "pending") ??
                        items[0]
                      ).index,
                    )
                  }
                >
                  <span
                    className="collapsed-fill"
                    style={{ height: `${(completed / items.length) * 100}%` }}
                  />
                  <span className="collapsed-number">
                    {completed === items.length ? (
                      <Check size={15} />
                    ) : (
                      String(i + 1).padStart(2, "0")
                    )}
                  </span>
                  <span className="collapsed-name">{category.name}</span>
                </button>
              )}
            </div>
          ),
        )}
      </div>
      <button
        className="progress-arrow"
        aria-label={
          index === questions.length - 1
            ? "Ver mi perfil"
            : "Pregunta siguiente"
        }
        onClick={() =>
          index === questions.length - 1 ? showResults() : navigate(index + 1)
        }
      >
        <ArrowRight size={19} />
      </button>
    </nav>
  );
}
