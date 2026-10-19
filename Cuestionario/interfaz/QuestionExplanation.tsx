import { useEffect, useState } from "react";
import type { SessionQuestion } from "./sesion";
type Explanation = {
  paragraphs: string[];
  terms: { term: string; meaning: string }[];
  originContext?: { proposalId: string; text: string } | null;
};
type Document = { questions: Record<string, Explanation> };
const files = import.meta.glob<string>("../explicaciones/generadas/*.json", {
  eager: true,
  query: "?url&no-inline",
  import: "default",
});
const cache = new Map<string, Document>();
export default function QuestionExplanation({
  question,
}: {
  question: SessionQuestion;
}) {
  const [content, setContent] = useState<Explanation | null>(
    cache.get(question.category)?.questions[question.id] ?? null,
  );
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const saved = cache.get(question.category)?.questions[question.id];
    setContent(saved ?? null);
    setFailed(false);
    if (saved) return;
    const controller = new AbortController();
    const url = files[`../explicaciones/generadas/${question.category}.json`];
    fetch(url, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok)
          throw new Error("No se ha podido cargar la explicación");
        const data = (await response.json()) as Document;
        const item = data.questions?.[question.id];
        if (
          !item ||
          !Array.isArray(item.paragraphs) ||
          item.paragraphs.length < 4
        )
          throw new Error("Explicación incompleta");
        cache.set(question.category, data);
        setContent(item);
      })
      .catch((error) => {
        if (error.name !== "AbortError") setFailed(true);
      });
    return () => controller.abort();
  }, [question.id, question.category, attempt]);
  if (failed)
    return (
      <div role="alert">
        <p>No se ha podido cargar la explicación.</p>
        <button
          className="quiet-button"
          onClick={() => setAttempt((a) => a + 1)}
        >
          Reintentar
        </button>
      </div>
    );
  if (!content) return <p role="status">Cargando explicación…</p>;
  return (
    <div className="question-explanation">
      <p className="explanation-plain">{content.paragraphs[0]}</p>
      {content.originContext && (
        <section>
          <h3>La propuesta de la que parte</h3>
          <p>{content.originContext.text}</p>
        </section>
      )}
      <section>
        <h3>Qué significa y cómo funcionaría</h3>
        <p>{content.paragraphs[1]}</p>
      </section>
      {content.terms.length > 0 && (
        <dl className="explanation-terms">
          {content.terms.map((term) => (
            <div key={term.term}>
              <dt>{term.term}</dt>
              <dd>{term.meaning}</dd>
            </div>
          ))}
        </dl>
      )}
      <section>
        <h3>Un ejemplo</h3>
        <p>{content.paragraphs[2]}</p>
      </section>
      <section>
        <h3>Qué conviene distinguir</h3>
        <p>{content.paragraphs[3]}</p>
      </section>
      {content.paragraphs.slice(4).map((p, i) => (
        <p key={i}>{p}</p>
      ))}
    </div>
  );
}
