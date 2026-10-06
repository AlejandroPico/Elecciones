import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  ArrowUpRight,
  Check,
  ChevronDown,
  ChartNoAxesCombined,
  Clock3,
  FileText,
  ListChecks,
  Menu,
  Moon,
  RotateCcw,
  Sun,
  Sunrise,
  Users,
  X,
} from "lucide-react";
import { categories, election, questions } from "../Elecciones";
import {
  calculate,
  parseParties,
  similarity,
  type Answers,
  type Party,
} from "./model";
import { AxisRows, CoordinateChart, RadarChart } from "./Charts";
import Progress from "./Progress";
import Archive from "./Archive";
import favicon from "../favicon.svg";
type View = "survey" | "results" | "programs" | "archive";
type Modal = "method" | "privacy" | "about" | "reset" | null;
type Theme = "auto" | "morning" | "afternoon" | "night";
type Chart = "coordinates" | "radar";
const choices = [
  { value: -2, label: "Muy en desacuerdo" },
  { value: -1, label: "En desacuerdo" },
  { value: 0, label: "Neutral" },
  { value: 1, label: "De acuerdo" },
  { value: 2, label: "Muy de acuerdo" },
];
function Dialog({
  title,
  children,
  close,
}: {
  title: string;
  children: ReactNode;
  close: () => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const d = ref.current!;
    d.showModal();
    return () => d.close();
  }, []);
  return (
    <dialog ref={ref} onCancel={close} aria-labelledby="dialog-title">
      <div className="dialog-head">
        <h2 id="dialog-title">{title}</h2>
        <button className="icon-button" onClick={close} aria-label="Cerrar">
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}
export default function App() {
  const [answers, setAnswers] = useState<Answers>({});
  const [index, setIndex] = useState(0);
  const [view, setView] = useState<View>("survey");
  const [modal, setModal] = useState<Modal>(null);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [themeMode, setThemeMode] = useState<Theme>("auto");
  const [clock, setClock] = useState(new Date());
  const [chart, setChart] = useState<Chart>("coordinates");
  const [activeCategory, setActiveCategory] = useState(categories[0].id);
  const [draftImportance, setDraftImportance] = useState<
    Record<string, 1 | 2 | 3>
  >({});
  const [parties, setParties] = useState<Party[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [importMessage, setImportMessage] = useState("");
  const questionRef = useRef<HTMLHeadingElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const advanceTimer = useRef<ReturnType<typeof setTimeout> | undefined>(
    undefined,
  );
  const question = questions[index];
  const category = categories.find((c) => c.id === question.category)!;
  const resultCategory = categories.find((c) => c.id === activeCategory)!;
  const current = answers[question.id];
  const importance = current?.importance ?? draftImportance[question.id] ?? 1;
  const scores = calculate(answers);
  const overlays = parties.filter((p) => selected.includes(p.id));
  const answered = questions.filter((q) => answers[q.id]?.value != null).length;
  const omitted = questions.filter((q) => answers[q.id]?.value === null).length;
  const hour = clock.getHours();
  const theme =
    themeMode === "auto"
      ? hour >= 7 && hour < 14
        ? "morning"
        : hour >= 14 && hour < 20
          ? "afternoon"
          : "night"
      : themeMode;
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);
  useEffect(() => {
    const timer = setInterval(() => setClock(new Date()), 30000);
    return () => clearInterval(timer);
  }, []);
  useEffect(() => {
    // Retirar solo los datos locales de la edición anterior; no hay guardado nuevo.
    try {
      localStorage.removeItem("elecciones:session");
      localStorage.removeItem("elecciones:preferences");
    } catch {
      /* El almacenamiento no es necesario. */
    }
  }, []);
  function selectValue(value: number | null) {
    const updated = { ...answers, [question.id]: { value, importance } };
    setAnswers(updated);
    clearTimeout(advanceTimer.current);
    const items = questions.filter((item) => item.category === category.id);
    if (!current && items.every((item) => Object.hasOwn(updated, item.id))) {
      const currentTheme = categories.findIndex(
        (item) => item.id === category.id,
      );
      const following = [
        ...categories.slice(currentTheme + 1),
        ...categories.slice(0, currentTheme),
      ];
      const nextTheme = following.find((theme) =>
        questions.some(
          (item) =>
            item.category === theme.id && !Object.hasOwn(updated, item.id),
        ),
      );
      const nextIndex = nextTheme
        ? questions.findIndex(
            (item) =>
              item.category === nextTheme.id &&
              !Object.hasOwn(updated, item.id),
          )
        : -1;
      // Mostrar la última respuesta antes de compactar el tema completado.
      advanceTimer.current = setTimeout(
        () => (nextIndex < 0 ? openView("results") : navigate(nextIndex)),
        650,
      );
    }
  }
  function navigate(nextIndex: number) {
    clearTimeout(advanceTimer.current);
    setIndex(Math.max(0, Math.min(questions.length - 1, nextIndex)));
    setView("survey");
    setMobileMenu(false);
  }
  function openView(nextView: View) {
    clearTimeout(advanceTimer.current);
    setView(nextView);
    setMobileMenu(false);
  }
  useEffect(() => {
    if (view === "survey") {
      questionRef.current?.focus({ preventScroll: true });
      document.querySelector(".survey-stage")?.scrollTo({
        top: 0,
        behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "instant"
          : "smooth",
      });
    }
  }, [index, view]);
  useEffect(() => () => clearTimeout(advanceTimer.current), []);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (
        view !== "survey" ||
        modal ||
        e.ctrlKey ||
        e.altKey ||
        e.metaKey ||
        /INPUT|SELECT|TEXTAREA/.test((e.target as HTMLElement).tagName)
      )
        return;
      const options = question.type === "binary" ? [-2, 2] : [-2, -1, 0, 1, 2];
      const n = Number(e.key);
      if (n >= 1 && n <= options.length) {
        e.preventDefault();
        selectValue(options[n - 1]);
      }
      if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
        e.preventDefault();
        navigate(index + (e.key === "ArrowLeft" ? -1 : 1));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });
  async function importFile(file?: File) {
    if (!file) return;
    try {
      if (file.size > 2_000_000) throw new Error("El archivo supera 2 MB.");
      const data = parseParties(JSON.parse(await file.text()));
      setParties(data);
      setSelected(data.slice(0, 3).map((p) => p.id));
      setImportMessage(`${data.length} candidaturas cargadas temporalmente.`);
    } catch (e) {
      setImportMessage(
        e instanceof Error ? e.message : "No se ha podido leer el archivo.",
      );
    }
    if (fileRef.current) fileRef.current.value = "";
  }
  const legend = (
    <div className="chart-legend">
      <span>
        <i className="legend-dot" />
        Tu perfil
      </span>
      {overlays.map((p) => (
        <span key={p.id}>
          <i style={{ background: p.color }} />
          {p.name}
        </span>
      ))}
    </div>
  );
  return (
    <>
      <a href="#content" className="skip-link">
        Saltar al contenido
      </a>
      <button
        className="mobile-toggle icon-button"
        aria-label={mobileMenu ? "Cerrar navegación" : "Abrir navegación"}
        aria-expanded={mobileMenu}
        onClick={() => setMobileMenu(!mobileMenu)}
      >
        {mobileMenu ? <X size={22} /> : <Menu size={22} />}
      </button>
      {mobileMenu && (
        <button
          className="navigation-shade"
          aria-label="Cerrar navegación"
          onClick={() => setMobileMenu(false)}
        />
      )}
      <aside className={`sidebar ${mobileMenu ? "open" : ""}`}>
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            openView("survey");
          }}
          aria-label="Elecciones, cuestionario"
        >
          <img src={favicon} alt="" />
          <span>Elecciones</span>
        </a>
        <div className="election-name">
          Generales
          <br />
          Noviembre 2026
        </div>
        <nav className="main-nav" aria-label="Secciones">
          {(
            [
              { id: "survey", name: "Cuestionario", icon: ListChecks },
              { id: "results", name: "Mi perfil", icon: ChartNoAxesCombined },
              { id: "programs", name: "Programas y partidos", icon: FileText },
              { id: "archive", name: "Archivo político", icon: Users },
            ] as const
          ).map((item) => (
            <button
              key={item.id}
              className={view === item.id ? "active" : ""}
              onClick={() => openView(item.id)}
              aria-current={view === item.id ? "page" : undefined}
            >
              <item.icon size={17} />
              <span>{item.name}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="appearance" role="group" aria-label="Apariencia">
            {(
              [
                { id: "auto", name: "Automático", icon: Clock3 },
                { id: "morning", name: "Mañana", icon: Sunrise },
                { id: "afternoon", name: "Tarde", icon: Sun },
                { id: "night", name: "Noche", icon: Moon },
              ] as const
            ).map((item) => (
              <button
                key={item.id}
                aria-label={item.name}
                title={item.name}
                aria-pressed={themeMode === item.id}
                onClick={() => setThemeMode(item.id)}
              >
                <item.icon size={18} />
              </button>
            ))}
          </div>
          <button className="quiet-button" onClick={() => setModal("reset")}>
            <RotateCcw size={15} />
            Nueva encuesta
          </button>
          <nav className="sidebar-footer" aria-label="Información del proyecto">
            <button onClick={() => setModal("about")}>Acerca de</button>
            <button onClick={() => setModal("method")}>Método</button>
            <button onClick={() => setModal("privacy")}>Privacidad</button>
          </nav>
        </div>
      </aside>
      <main
        id="content"
        className={`main-content ${view === "survey" ? "survey-view" : ""}`}
      >
        {view === "survey" && (
          <>
            <div className="survey-stage">
              <div className="survey-layout">
                <section className="question-card" aria-label="Pregunta">
                  <div className="question-body" key={question.id}>
                    <h1 ref={questionRef} tabIndex={-1}>
                      {question.text}
                    </h1>
                    <p className="question-context">{question.context}</p>
                    <fieldset
                      className={`answer-options ${question.type === "binary" ? "binary" : ""}`}
                    >
                      <legend className="sr-only">Respuesta</legend>
                      {(question.type === "binary"
                        ? [
                            { value: -2, label: "No" },
                            { value: 2, label: "Sí" },
                          ]
                        : choices
                      ).map((choice) => (
                        <label
                          key={choice.value}
                          className={`answer-option ${current?.value === choice.value ? "selected" : ""}`}
                        >
                          <input
                            type="radio"
                            name={question.id}
                            checked={current?.value === choice.value}
                            onChange={() => selectValue(choice.value)}
                          />
                          <span>{choice.label}</span>
                        </label>
                      ))}
                    </fieldset>
                    <button
                      className={`skip-answer ${current?.value === null ? "chosen" : ""}`}
                      aria-pressed={current?.value === null}
                      onClick={() => selectValue(null)}
                    >
                      {current?.value === null && <Check size={14} />}No sé /
                      prefiero omitir
                    </button>
                  </div>
                  <div className="importance-panel">
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
                          onClick={() =>
                            current
                              ? setAnswers((a) => ({
                                  ...a,
                                  [question.id]: {
                                    ...current,
                                    importance: option.value,
                                  },
                                }))
                              : setDraftImportance((d) => ({
                                  ...d,
                                  [question.id]: option.value,
                                }))
                          }
                        >
                          {option.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </section>
                <details className="chart-drawer">
                  <summary aria-label="Mostrar u ocultar gráfica">
                    <ChartNoAxesCombined size={19} />
                    <ChevronDown size={14} />
                  </summary>
                  <div className="chart-drawer-body">
                    <select
                      aria-label="Tipo de gráfico"
                      value={chart}
                      onChange={(e) => setChart(e.target.value as Chart)}
                    >
                      <option value="coordinates">
                        Coordenadas · {category.name}
                      </option>
                      <option value="radar">Vista radial</option>
                    </select>
                    {chart === "coordinates" ? (
                      <CoordinateChart
                        category={category}
                        scores={scores}
                        parties={overlays}
                        compact
                      />
                    ) : (
                      <RadarChart scores={scores} parties={overlays} />
                    )}
                    {legend}
                  </div>
                </details>
              </div>
            </div>
            <Progress
              answers={answers}
              index={index}
              navigate={navigate}
              showResults={() => openView("results")}
            />
          </>
        )}
        {view === "results" && (
          <div className="section-content">
            <h1 className="section-title">Mi perfil</h1>
            <p className="results-summary">
              {answered} respuestas · {omitted} omisiones ·{" "}
              {questions.length - answered - omitted} pendientes
            </p>
            <div className="results-layout">
              <section className="result-card">
                <select
                  aria-label="Tema del gráfico"
                  value={activeCategory}
                  onChange={(e) => setActiveCategory(e.target.value)}
                >
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
                <CoordinateChart
                  category={resultCategory}
                  scores={scores}
                  parties={overlays}
                />
                <AxisRows category={resultCategory} scores={scores} />
              </section>
              <section className="result-card">
                <h2>Vista radial</h2>
                <RadarChart scores={scores} parties={overlays} />
                {legend}
                <p className="chart-note">
                  Primer eje de cada tema. −100 en el centro; +100 en el borde.
                  Los ejes sin datos no se trazan.
                </p>
              </section>
            </div>
            <section className="comparison-card">
              <h2>Candidaturas</h2>
              {!parties.length ? (
                <p>No hay posiciones de programas incorporadas.</p>
              ) : (
                parties.map((p) => {
                  const s = similarity(answers, p);
                  return (
                    <label key={p.id} className="party-row">
                      <input
                        type="checkbox"
                        checked={selected.includes(p.id)}
                        onChange={(e) =>
                          setSelected(
                            e.target.checked
                              ? [...selected, p.id]
                              : selected.filter((id) => id !== p.id),
                          )
                        }
                      />
                      <i style={{ background: p.color }} />
                      <span>
                        <strong>{p.name}</strong>
                        <small>
                          {s.shared} preguntas comunes de {s.answered}{" "}
                          respondidas
                        </small>
                      </span>
                      <b>
                        {s.percent === null
                          ? "Sin datos comunes"
                          : `${Math.round(s.percent)} %`}
                      </b>
                    </label>
                  );
                })
              )}
            </section>
            <details className="all-axes">
              <summary>
                Las 16 dimensiones
                <ChevronDown size={16} />
              </summary>
              <div className="axes-grid">
                {categories.map((c) => (
                  <section key={c.id}>
                    <h2>{c.name}</h2>
                    <AxisRows category={c} scores={scores} />
                  </section>
                ))}
              </div>
            </details>
          </div>
        )}
        {view === "programs" && (
          <div className="section-content">
            <h1 className="section-title">Programas y partidos</h1>
            <section className="result-card prose">
              <p>
                Los programas de 2026 aún no están incorporados. Las posiciones
                desconocidas o ambiguas quedan sin puntuación.
              </p>
              <p>
                <a href={election.source} target="_blank" rel="noreferrer">
                  Convocatoria · BOE
                  <ArrowUpRight size={14} />
                </a>
              </p>
              <h2>Posiciones documentadas</h2>
              <p>
                Importación temporal de un archivo de posiciones. No interpreta
                programas PDF.
              </p>
              <input
                ref={fileRef}
                type="file"
                accept=".json,application/json"
                hidden
                onChange={(e) => void importFile(e.target.files?.[0])}
              />
              <button
                className="outline-button"
                onClick={() => fileRef.current?.click()}
              >
                Seleccionar archivo
              </button>
              <p role="status">{importMessage}</p>
              {parties.map((p) => (
                <details className="party-sources" key={p.id}>
                  <summary>
                    {p.name} · {Object.keys(p.positions).length} posiciones
                  </summary>
                  <ul>
                    {Object.entries(p.positions).map(([id, position]) => (
                      <li key={id}>
                        <p>{questions.find((q) => q.id === id)?.text}</p>
                        <p>
                          {position.value} · {position.reference}
                        </p>
                        <a
                          href={position.source}
                          target="_blank"
                          rel="noreferrer"
                        >
                          Fuente original
                          <ArrowUpRight size={13} />
                        </a>
                      </li>
                    ))}
                  </ul>
                </details>
              ))}
            </section>
          </div>
        )}
        {view === "archive" && (
          <div className="section-content">
            <h1 className="section-title">Archivo político</h1>
            <Archive />
          </div>
        )}
      </main>
      {modal && (
        <Dialog
          title={
            modal === "about"
              ? "Elecciones"
              : modal === "privacy"
                ? "Privacidad"
                : modal === "method"
                  ? "Método"
                  : "¿Empezar una nueva encuesta?"
          }
          close={() => setModal(null)}
        >
          {modal === "about" && (
            <>
              <div className="about-brand">
                <img
                  src={favicon}
                  alt="Una mano deposita un sobre en una urna"
                />
              </div>
              <div className="prose">
                <p>
                  Proyecto personal de <strong>Alejandro Pico Perez</strong>{" "}
                  para consultar posiciones políticas por temas y compararlas
                  con programas documentados.
                </p>
                <p>
                  48 preguntas piloto, 8 temas y 16 ejes. Permite ponderar
                  respuestas, omitirlas y revisarlas desde la barra de progreso.
                  El archivo político contiene una selección inicial de
                  personas, partidos, documentos históricos y cargos.
                </p>
                <p>
                  No guarda respuestas ni preferencias. Al recargar la página se
                  comienza de nuevo. Falta revisar el banco editorial e
                  incorporar los programas y candidaturas de 2026.
                </p>
              </div>
              <dl className="project-meta">
                <div>
                  <dt>Versión</dt>
                  <dd>0.2.0</dd>
                </div>
                <div>
                  <dt>Creación</dt>
                  <dd>6 de octubre de 2026</dd>
                </div>
                <div>
                  <dt>Actualización</dt>
                  <dd>7 de octubre de 2026</dd>
                </div>
              </dl>
              <nav className="about-links">
                <a
                  href="https://alejandropico.github.io/Portfolio/"
                  target="_blank"
                  rel="noreferrer"
                >
                  Portfolio
                  <ArrowUpRight size={16} />
                </a>
                <a
                  href="https://github.com/AlejandroPico/Elecciones"
                  target="_blank"
                  rel="noreferrer"
                >
                  GitHub
                  <ArrowUpRight size={16} />
                </a>
              </nav>
            </>
          )}
          {modal === "privacy" && (
            <div className="prose">
              <p>
                Las respuestas y preferencias solo existen en memoria durante
                esta visita. No se guardan, no se exportan y no se envían a un
                servidor. Al recargar o cerrar la página se pierden.
              </p>
              <p>
                Esta edición retira los datos locales que guardaba la versión
                anterior. No utiliza cookies de seguimiento, estadísticas
                centrales ni cuentas de Google.
              </p>
              <p>
                El alojamiento puede registrar datos técnicos de las visitas.{" "}
                <a
                  href="https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection"
                  target="_blank"
                  rel="noreferrer"
                >
                  Información de GitHub Pages
                </a>
                .
              </p>
            </div>
          )}
          {modal === "method" && (
            <div className="prose">
              <p>
                Banco piloto pendiente de revisión de neutralidad, equilibrio y
                validez. No asigna una etiqueta ideológica general.
              </p>
              <h3>Puntuación</h3>
              <p>
                La escala usa −2, −1, 0, +1 y +2; las respuestas binarias, −2 y
                +2. Neutral aporta cero. Una omisión no aporta puntuación. La
                importancia normal, alta y esencial pesa 1, 2 y 3.
              </p>
              <p>
                Cada pregunta tiene un eje y una dirección explícitos. La media
                ponderada se normaliza entre −100 y +100. Un eje sin respuestas
                no tiene coordenada. El mapa combina dos ejes; la vista radial
                resume el primero de cada tema.
              </p>
              <h3>Comparación</h3>
              <p>
                Coincidencia = 100 × (1 − media ponderada de la distancia entre
                respuestas / 4). Solo incluye preguntas con respuesta y posición
                documentada. No es una probabilidad de voto ni una
                recomendación. Las ausencias de evidencia no equivalen a
                neutralidad.
              </p>
            </div>
          )}
          {modal === "reset" && (
            <>
              <p>Se vaciarán las respuestas de esta visita.</p>
              <div className="dialog-actions">
                <button
                  className="outline-button"
                  onClick={() => setModal(null)}
                >
                  Cancelar
                </button>
                <button
                  className="primary-button"
                  onClick={() => {
                    setAnswers({});
                    setDraftImportance({});
                    navigate(0);
                    setModal(null);
                  }}
                >
                  Empezar de nuevo
                </button>
              </div>
            </>
          )}
        </Dialog>
      )}
    </>
  );
}
