import { categories, questions, type Category, type Question } from "../..";
import type { Answers } from "../perfil/model";
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
              value: answers[question.id]?.value,
              importance: answers[question.id]?.importance ?? 1,
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
}: {
  answers: Answers;
  index: number;
  navigate: (index: number) => void;
}) {
  return (
    <nav className="question-progress" aria-label="Navegación por preguntas">
      <div className="progress-groups">
        {progressGroups(answers, index).map(
          ({ category, items, completed, active }) => (
            <div
              key={category.id}
              className={`progress-group ${active ? "expanded" : "collapsed"} ${completed === items.length ? "complete" : ""}`}
            >
              <span className="progress-caption" title={category.name}>
                {category.name}
              </span>
              {active && (
                <span
                  className="progress-count"
                  style={{
                    left: `${((items.findIndex((item) => item.index === index) + 0.5) / items.length) * 100}%`,
                  }}
                >
                  {items.findIndex((item) => item.index === index) + 1} de{" "}
                  {items.length}
                </span>
              )}
              <div className="progress-track" aria-hidden="true" />
              {active && (
                <div
                  className="progress-front"
                  aria-hidden="true"
                  style={{
                    width: `${((items.findIndex((item) => item.index === index) + 1) / items.length) * 100}%`,
                  }}
                />
              )}
              <div className="progress-segments">
                {items.map((item, j) => (
                  <button
                    key={item.question.id}
                    className={`progress-segment ${item.state} ${item.value == null ? "" : item.value < 0 ? "negative" : item.value > 0 ? "positive" : "neutral"} ${item.index === index ? "current" : ""}`}
                    style={
                      {
                        "--answer-weight": `${item.importance === 3 ? 7 : item.importance === 2 ? 5 : 3}px`,
                      } as React.CSSProperties
                    }
                    aria-label={`${category.name}, pregunta ${j + 1}: ${item.question.text}${item.state === "skipped" ? " (omitida)" : item.state === "answered" ? " (respondida)" : ""}`}
                    aria-current={item.index === index ? "step" : undefined}
                    onClick={() => navigate(item.index)}
                    title={item.question.text}
                  />
                ))}
              </div>
            </div>
          ),
        )}
      </div>
    </nav>
  );
}
