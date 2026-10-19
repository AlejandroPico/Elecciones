import {
  lazy,
  Suspense,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
} from "react";
import { Check, Expand, X } from "lucide-react";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";
import { createAdvanceClock } from "../../Elecciones/interfaz/cuestionario/avance";
import Introduction from "../../Elecciones/interfaz/cuestionario/Introduction";
import TopicPicker from "./TopicPicker";
import SurveyProgress from "./SurveyProgress";
const SurveyProfile = lazy(() => import("./SurveyProfile"));
const QuestionExplanation = lazy(() => import("./QuestionExplanation"));
import {
  bank,
  questionById,
  selectTopics,
  sessionQuestions,
  type Draws,
} from "./sesion";
import "./survey.css";

const choices = [
  { value: -2, label: "Muy en desacuerdo" },
  { value: -1, label: "En desacuerdo" },
  { value: 0, label: "Neutral" },
  { value: 1, label: "De acuerdo" },
  { value: 2, label: "Muy de acuerdo" },
];
export default function Questionnaire({
  view,
  openView,
  blocked,
  onStarted,
  resumeRequest,
}: {
  view: string;
  openView: (view: "survey" | "results") => void;
  blocked: boolean;
  onStarted: (started: boolean) => void;
  resumeRequest: number;
}) {
  const [answers, setAnswers] = useState<Answers>({});
  const [drafts, setDrafts] = useState<Record<string, 1 | 2 | 3>>({});
  const [draws, setDraws] = useState<Draws>({});
  const [selected, setSelected] = useState<string[]>([]);
  const [phase, setPhase] = useState<"topics" | "introduction" | "questions">(
    "topics",
  );
  const [currentId, setCurrentId] = useState<string | null>(null);
  const [countdown, setCountdown] = useState<string | null>(null);
  const [context, setContext] = useState(false);
  const timer = useRef(createAdvanceClock());
  const heading = useRef<HTMLHeadingElement>(null);
  const dialog = useRef<HTMLDialogElement>(null);
  const lastResume = useRef(resumeRequest);
  const questions = sessionQuestions(draws, selected);
  const question = currentId ? questionById.get(currentId) : undefined;
  const current = question ? answers[question.id] : undefined;
  const importance =
    current?.importance ?? (question ? drafts[question.id] : undefined) ?? 1;
  function cancel() {
    timer.current.cancel();
    setCountdown(null);
  }
  useLayoutEffect(() => {
    if (view !== "survey" || blocked || phase !== "questions") cancel();
  }, [view, blocked, phase]);
  useEffect(() => () => timer.current.cancel(), []);
  useEffect(() => {
    if (view === "survey" && phase === "questions")
      heading.current?.focus({ preventScroll: true });
  }, [currentId, view, phase]);
  useEffect(() => {
    if (context) dialog.current?.showModal();
    else dialog.current?.close();
  }, [context]);
  useEffect(() => {
    setContext(false);
  }, [view, currentId]);

  function navigate(id: string) {
    cancel();
    setContext(false);
    setCurrentId(id);
    setPhase("questions");
    openView("survey");
  }
  function apply(ids: string[]) {
    cancel();
    const ordered = bank.categories
      .filter((c) => ids.includes(c.id))
      .map((c) => c.id);
    const next = selectTopics(draws, ordered);
    setDraws(next);
    setSelected(ordered);
    onStarted(true);
    const items = sessionQuestions(next, ordered);
    setCurrentId(items.find((q) => !answers[q.id])?.id ?? items[0].id);
    setPhase(Object.keys(draws).length ? "questions" : "introduction");
  }
  function topics() {
    cancel();
    setPhase("topics");
    openView("survey");
  }
  function resume(id?: string) {
    if (id) {
      const q = questionById.get(id);
      if (q && !selected.includes(q.category))
        setSelected((s) =>
          bank.categories
            .filter((c) => [...s, q.category].includes(c.id))
            .map((c) => c.id),
        );
      navigate(id);
      return;
    }
    const next = questions.find((q) => !answers[q.id])?.id ?? currentId;
    if (next && questions.length) navigate(next);
    else topics();
  }
  function select(value: number | null) {
    if (!question) return;
    setAnswers((a) => ({
      ...a,
      [question.id]: {
        value,
        importance: a[question.id]?.importance ?? drafts[question.id] ?? 1,
      },
    }));
    if (
      timer.current.start(() => {
        setCountdown(null);
        setContext(false);
        const index = questions.findIndex((q) => q.id === question.id);
        if (index + 1 >= questions.length) openView("results");
        else navigate(questions[index + 1].id);
      })
    )
      setCountdown(question.id);
  }
  useLayoutEffect(() => {
    if (lastResume.current !== resumeRequest) {
      lastResume.current = resumeRequest;
      resume();
    }
  }, [resumeRequest]);
  useEffect(() => {
    function key(e: KeyboardEvent) {
      if (
        view !== "survey" ||
        phase !== "questions" ||
        blocked ||
        context ||
        e.ctrlKey ||
        e.metaKey ||
        e.altKey ||
        /INPUT|SELECT|TEXTAREA|BUTTON/.test((e.target as HTMLElement).tagName)
      )
        return;
      const n = Number(e.key);
      if (n >= 1 && n <= 5) {
        e.preventDefault();
        select(n - 3);
      }
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        const index = questions.findIndex((q) => q.id === currentId);
        const next = questions[index + (e.key === "ArrowLeft" ? -1 : 1)];
        if (next) {
          e.preventDefault();
          navigate(next.id);
        }
      }
    }
    window.addEventListener("keydown", key);
    return () => window.removeEventListener("keydown", key);
  });
  if (view === "results")
    return (
      <Suspense
        fallback={
          <p className="section-content" role="status">
            Cargando perfil
          </p>
        }
      >
        <SurveyProfile answers={answers} resume={resume} topics={topics} />
      </Suspense>
    );
  if (view !== "survey") return null;
  if (phase === "topics" || !question)
    return (
      <TopicPicker
        initial={selected}
        draws={draws}
        answers={answers}
        apply={apply}
        profile={() => openView("results")}
      />
    );
  if (phase === "introduction")
    return (
      <Introduction
        topics={bank.categories
          .filter((c) => selected.includes(c.id))
          .map((c) => c.title)}
        count={questions.length}
        start={() => setPhase("questions")}
      />
    );
  return (
    <div className="documentary-survey">
      <div className="survey-controls">
        <button className="quiet-button" onClick={topics}>
          Temas
        </button>
        <span>
          {bank.categories.find((c) => c.id === question.category)?.title}
        </span>
        <button className="quiet-button" onClick={() => openView("results")}>
          Mi perfil
        </button>
      </div>
      <div className="survey-stage">
        <div className="survey-layout">
          <section className="question-card" aria-label="Pregunta">
            <div className="question-body" key={question.id}>
              <h1 ref={heading} tabIndex={-1}>
                {question.text}
              </h1>
              <p className="question-context">
                {question.scope
                  ? `Ámbito autonómico: ${question.scope.territory} · ${question.scope.sourceElection}`
                  : question.concept}
              </p>
              <button
                className="context-toggle icon-button"
                aria-label="Ampliar contexto de la pregunta"
                onClick={() => {
                  cancel();
                  setContext(true);
                }}
              >
                <Expand size={17} />
              </button>
              <fieldset className="answer-options">
                <legend className="sr-only">Respuesta</legend>
                {choices.map((choice) => (
                  <label
                    key={choice.value}
                    className={`answer-option ${current?.value === choice.value ? "selected" : ""}`}
                  >
                    <input
                      type="radio"
                      name={question.id}
                      checked={current?.value === choice.value}
                      onChange={() => {}}
                      onClick={() => select(choice.value)}
                    />
                    <span>{choice.label}</span>
                  </label>
                ))}
              </fieldset>
              <button
                className={`skip-answer ${current?.value === null ? "chosen" : ""}`}
                aria-pressed={current?.value === null}
                onClick={() => select(null)}
              >
                {current?.value === null && <Check size={14} />}No sé / prefiero
                omitir
              </button>
            </div>
            <div className="importance-panel">
              <span className="answer-countdown" aria-hidden="true">
                {countdown === question.id && <i key={question.id} />}
              </span>
              <span>Importancia</span>
              <div
                className="segmented"
                role="group"
                aria-label="Importancia de la pregunta"
              >
                {(
                  [
                    { value: 1, label: "Normal" },
                    { value: 2, label: "Alta" },
                    { value: 3, label: "Esencial" },
                  ] as const
                ).map((option) => (
                  <button
                    key={option.value}
                    aria-pressed={importance === option.value}
                    onClick={() => {
                      if (current)
                        setAnswers((a) => ({
                          ...a,
                          [question.id]: {
                            ...a[question.id],
                            importance: option.value,
                          },
                        }));
                      else
                        setDrafts((d) => ({
                          ...d,
                          [question.id]: option.value,
                        }));
                    }}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </section>
        </div>
      </div>
      <SurveyProgress
        questions={questions}
        current={question.id}
        answers={answers}
        navigate={navigate}
      />
      {context && (
        <dialog
          className="question-explanation-dialog"
          ref={dialog}
          aria-labelledby="question-context-title"
          onCancel={() => setContext(false)}
        >
          <div className="dialog-head">
            <h2 id="question-context-title">{question.text}</h2>
            <button
              className="icon-button"
              aria-label="Cerrar contexto"
              onClick={() => setContext(false)}
            >
              <X size={20} />
            </button>
          </div>
          <Suspense fallback={<p role="status">Cargando explicación…</p>}>
            <QuestionExplanation question={question} />
          </Suspense>
        </dialog>
      )}
    </div>
  );
}
