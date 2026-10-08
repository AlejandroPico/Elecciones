import {
  lazy,
  Suspense,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  ArrowUpRight,
  Check,
  ChevronDown,
  ChartNoAxesCombined,
  Expand,
  Landmark,
  Clock3,
  FileText,
  ListChecks,
  Moon,
  Sun,
  Sunrise,
  Users,
  X,
} from "lucide-react";
import { categories, questions } from "../../Elecciones";
import {
  calculate,
  parseParties,
  similarity,
  type Answers,
  type Party,
} from "../../Elecciones/interfaz/perfil/model";
import {
  AxisRows,
  CoordinateChart,
  RadarChart,
} from "../../Elecciones/interfaz/perfil/Charts";
import Progress from "../../Elecciones/interfaz/cuestionario/Progress";
import { createAdvanceClock } from "../../Elecciones/interfaz/cuestionario/avance";
const Programs = lazy(() => import("../../Partidos/interfaz/Programs"));
import { contexts } from "../../Elecciones/Generales Noviembre 2026/contextos";
import favicon from "../../favicon.svg";
import { useNavigation, type View, type Entry } from "./navigation";
const Archive = lazy(() => import("../../Políticos/interfaz/Archive"));
const Governments = lazy(() => import("../../Gobiernos/interfaz/Governments"));
const Senate = lazy(() => import("../../Gobiernos/interfaz/Senate"));
const Congress = lazy(() => import("../../Gobiernos/interfaz/Congress"));
import Autonomies, { AutonomyMenu } from "../../Gobiernos/interfaz/Autonomies";
const Offices = lazy(() => import("../../Gobiernos/interfaz/Offices"));
type Modal = "method" | "privacy" | "about" | "reset" | "context" | null;
type Theme = "auto" | "morning" | "afternoon" | "night";
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
  const navigation = useNavigation();
  const { view, entry: archiveEntry } = navigation.route;
  const setView = (nextView: View) => navigation.navigate({ view: nextView });
  const [modal, setModal] = useState<Modal>(null);
  const [mobileMenu, setMobileMenu] = useState(() => window.innerWidth > 720);
  const [surveyMenu, setSurveyMenu] = useState(false);
  const [governmentMenu, setGovernmentMenu] = useState(() =>
    ["governments", "congress", "senate"].includes(navigation.route.view),
  );
  const [themeMode, setThemeMode] = useState<Theme>("auto");
  const [clock, setClock] = useState(new Date());
  const [activeCategory, setActiveCategory] = useState(categories[0].id);
  const [draftImportance, setDraftImportance] = useState<
    Record<string, 1 | 2 | 3>
  >({});
  const [parties, setParties] = useState<Party[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [importMessage, setImportMessage] = useState("");
  const questionRef = useRef<HTMLHeadingElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const advanceClock = useRef(createAdvanceClock());
  const [countdownQuestion, setCountdownQuestion] = useState<string | null>(
    null,
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
    if (
      advanceClock.current.start(() => {
        setModal(null);
        if (index === questions.length - 1) openView("results");
        else navigate(index + 1);
      })
    )
      setCountdownQuestion(question.id);
  }
  function cancelAdvance() {
    advanceClock.current.cancel();
    setCountdownQuestion(null);
  }
  function navigate(nextIndex: number) {
    cancelAdvance();
    setIndex(Math.max(0, Math.min(questions.length - 1, nextIndex)));
    setView("survey");
    if (window.innerWidth <= 720) setMobileMenu(false);
  }
  function openView(nextView: View) {
    cancelAdvance();
    setView(nextView);
    if (window.innerWidth <= 720) setMobileMenu(false);
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
  useEffect(() => () => advanceClock.current.cancel(), []);
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
  function openArchive(kind: "person" | "party", id: string) {
    openEntry({ kind, id });
  }
  function openEntry(entry?: Entry) {
    cancelAdvance();
    navigation.navigate({
      view: entry
        ? entry.kind === "party"
          ? "programs"
          : entry.kind === "office"
            ? "offices"
            : entry.kind === "government"
              ? "governments"
              : entry.kind === "senate"
                ? "senate"
                : entry.kind === "congress"
                  ? "congress"
                  : entry.kind === "autonomy"
                    ? "autonomies"
                    : "archive"
        : view,
      entry,
    });
    if (window.innerWidth <= 720) setMobileMenu(false);
  }
  useEffect(() => {
    cancelAdvance();
    setModal(null);
  }, [navigation.route]);
  const themes = [
    { id: "auto", name: "Automático", icon: Clock3 },
    { id: "morning", name: "Mañana", icon: Sunrise },
    { id: "afternoon", name: "Tarde", icon: Sun },
    { id: "night", name: "Noche", icon: Moon },
  ] as const;
  const themeIndex = themes.findIndex((t) => t.id === themeMode);
  const ThemeIcon = themes[themeIndex].icon;
  return (
    <>
      <a
        href="#content"
        className="skip-link"
        onClick={(event) => {
          event.preventDefault();
          document.getElementById("content")?.focus();
        }}
      >
        Saltar al contenido
      </a>
      <button
        className="brand-toggle"
        aria-label={mobileMenu ? "Cerrar navegación" : "Abrir navegación"}
        aria-expanded={mobileMenu}
        onClick={() => setMobileMenu(!mobileMenu)}
      >
        <img src={favicon} alt="Elecciones" />
      </button>
      {mobileMenu && (
        <button
          className="navigation-shade"
          aria-label="Cerrar navegación"
          onClick={() => setMobileMenu(false)}
        />
      )}
      <aside
        className={`sidebar ${mobileMenu ? "open" : ""}`}
        inert={!mobileMenu}
      >
        <div className="brand">
          <span>Elecciones</span>
        </div>
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
              { id: "programs", name: "Partidos", icon: FileText },
              { id: "archive", name: "Archivo político", icon: Users },
              { id: "offices", name: "Cargos e historia", icon: Landmark },
              {
                id: "governments",
                name: "Gobiernos centrales",
                icon: Landmark,
              },
            ] as const
          ).map((item) => (
            <div key={item.id} className="navigation-item">
              <button
                className={
                  view === item.id ||
                  (item.id === "governments" &&
                    ["congress", "senate"].includes(view))
                    ? "active"
                    : ""
                }
                onClick={() => {
                  if (item.id === "survey") {
                    setSurveyMenu(!surveyMenu);
                    return;
                  }
                  if (item.id === "governments") {
                    setGovernmentMenu(!governmentMenu);
                    return;
                  }
                  openView(item.id);
                }}
                aria-expanded={
                  item.id === "survey"
                    ? surveyMenu
                    : item.id === "governments"
                      ? governmentMenu
                      : undefined
                }
                aria-current={view === item.id ? "page" : undefined}
              >
                <item.icon size={17} />
                <span>{item.name}</span>
                {(item.id === "survey" || item.id === "governments") && (
                  <ChevronDown
                    className={
                      (item.id === "survey" ? surveyMenu : governmentMenu)
                        ? "tree-chevron open"
                        : "tree-chevron"
                    }
                    size={13}
                  />
                )}
              </button>
              {item.id === "survey" && (
                <div
                  className={`survey-tree ${surveyMenu ? "open" : ""}`}
                  inert={!surveyMenu}
                >
                  <div>
                    <button onClick={() => openView("survey")}>
                      Consultar cuestionario
                    </button>
                    <button onClick={() => setModal("reset")}>
                      Nueva encuesta
                    </button>
                  </div>
                </div>
              )}
              {item.id === "governments" && (
                <div
                  className={`survey-tree ${governmentMenu ? "open" : ""}`}
                  inert={!governmentMenu}
                >
                  <div>
                    <button
                      aria-current={view === "governments" ? "page" : undefined}
                      onClick={() => openView("governments")}
                    >
                      Gobierno
                    </button>
                    <button
                      aria-current={view === "congress" ? "page" : undefined}
                      onClick={() => openView("congress")}
                    >
                      Congreso
                    </button>
                    <button
                      aria-current={view === "senate" ? "page" : undefined}
                      onClick={() => openView("senate")}
                    >
                      Senado
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
          <AutonomyMenu
            selected={view === "autonomies" ? archiveEntry?.id : undefined}
            openSection={(id) => openEntry({ kind: "autonomy", id })}
          />
        </nav>
        <div className="sidebar-bottom">
          <button
            className="appearance-cycle quiet-button"
            aria-label={`Apariencia: ${themes[themeIndex].name}. Cambiar a ${themes[(themeIndex + 1) % themes.length].name}`}
            onClick={() =>
              setThemeMode(themes[(themeIndex + 1) % themes.length].id)
            }
          >
            <ThemeIcon size={16} />
            <span>Apariencia · {themes[themeIndex].name.toLowerCase()}</span>
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
        tabIndex={-1}
        className={`main-content ${mobileMenu ? "navigation-open" : "navigation-closed"} ${view === "survey" ? "survey-view" : ""}`}
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
                    <button
                      className="context-toggle icon-button"
                      aria-label="Ampliar contexto de la pregunta"
                      title="Ampliar contexto"
                      onClick={() => setModal("context")}
                    >
                      <Expand size={17} />
                    </button>
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
                            onChange={() => {}}
                            onClick={() => selectValue(choice.value)}
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
                    <span className="answer-countdown" aria-hidden="true">
                      {countdownQuestion === question.id && (
                        <i key={question.id} />
                      )}
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
              </div>
            </div>
            <Progress answers={answers} index={index} navigate={navigate} />
          </>
        )}
        {view === "results" && (
          <div className="section-content">
            <h1 className="section-title">Mi perfil</h1>
            <p className="results-summary">
              {answered} {answered === 1 ? "respuesta" : "respuestas"} ·{" "}
              {omitted} {omitted === 1 ? "omisión" : "omisiones"} ·{" "}
              {questions.length - answered - omitted}{" "}
              {questions.length - answered - omitted === 1
                ? "pendiente"
                : "pendientes"}
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
        <Suspense
          fallback={
            <span className="sr-only" role="status">
              Cargando archivo
            </span>
          }
        >
          {navigation.visited.has("programs") && (
            <div className="section-content" hidden={view !== "programs"}>
              <h1 className="section-title">Partidos</h1>
              <Suspense
                fallback={
                  <span className="sr-only" role="status">
                    Cargando partidos
                  </span>
                }
              >
                {archiveEntry?.kind === "party" ? (
                  <Archive
                    initialRoute={{ kind: "party", id: archiveEntry.id }}
                    onNavigate={openEntry}
                    close={() => openView("programs")}
                  />
                ) : null}
                <div hidden={archiveEntry?.kind === "party"}>
                  <Programs openParty={(id) => openArchive("party", id)} />
                </div>
                <details className="positions-import result-card prose">
                  <summary>Posiciones documentadas</summary>

                  <p>
                    Importación temporal de un archivo de posiciones. No
                    interpreta programas PDF.
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
                </details>
              </Suspense>
            </div>
          )}
          {navigation.visited.has("archive") && (
            <div className="section-content" hidden={view !== "archive"}>
              <h1 className="section-title">Archivo político</h1>
              <Suspense
                fallback={
                  <span className="sr-only" role="status">
                    Cargando archivo
                  </span>
                }
              >
                <Archive
                  initialRoute={
                    view === "archive" && archiveEntry?.kind === "person"
                      ? { kind: "person", id: archiveEntry.id }
                      : undefined
                  }
                  onNavigate={openEntry}
                  openParty={(id) => openArchive("party", id)}
                />
              </Suspense>
            </div>
          )}
          {navigation.visited.has("governments") && (
            <div className="section-content" hidden={view !== "governments"}>
              <h1 className="section-title">Gobierno</h1>
              <Suspense
                fallback={
                  <span className="sr-only" role="status">
                    Cargando gobiernos
                  </span>
                }
              >
                <Governments
                  openPerson={(id) => openArchive("person", id)}
                  active={view === "governments"}
                  selectedSnapshot={
                    view === "governments" ? archiveEntry?.id : undefined
                  }
                  openGovernment={(id) =>
                    navigation.navigate({
                      view: "governments",
                      entry: { kind: "government", id },
                    })
                  }
                />
              </Suspense>
            </div>
          )}
          {navigation.visited.has("offices") && (
            <div className="section-content" hidden={view !== "offices"}>
              <h1 className="section-title">Cargos e historia</h1>
              <Suspense
                fallback={
                  <span className="sr-only" role="status">
                    Cargando cargos
                  </span>
                }
              >
                <Offices
                  openPerson={(id) => openArchive("person", id)}
                  selectedOffice={
                    view === "offices" ? archiveEntry?.id : undefined
                  }
                  openOffice={(id) => {
                    cancelAdvance();
                    navigation.navigate({
                      view: "offices",
                      entry: id ? { kind: "office", id } : undefined,
                    });
                  }}
                />
              </Suspense>
            </div>
          )}
          {navigation.visited.has("congress") && (
            <div className="section-content" hidden={view !== "congress"}>
              <h1 className="section-title">Congreso</h1>
              <Suspense
                fallback={
                  <span className="sr-only" role="status">
                    Cargando Congreso
                  </span>
                }
              >
                <Congress
                  active={view === "congress"}
                  openPerson={(id) => openArchive("person", id)}
                  selectedSnapshot={
                    view === "congress" ? archiveEntry?.id : undefined
                  }
                  openCongress={(id) =>
                    navigation.navigate({
                      view: "congress",
                      entry: { kind: "congress", id },
                    })
                  }
                />
              </Suspense>
            </div>
          )}
          {navigation.visited.has("autonomies") && (
            <div hidden={view !== "autonomies"}>
              <Autonomies
                selected={view === "autonomies" ? archiveEntry?.id : undefined}
              />
            </div>
          )}
          {navigation.visited.has("senate") && (
            <div className="section-content" hidden={view !== "senate"}>
              <h1 className="section-title">Senado</h1>
              <Suspense
                fallback={
                  <span className="sr-only" role="status">
                    Cargando Senado
                  </span>
                }
              >
                <Senate
                  active={view === "senate"}
                  openPerson={(id) => openArchive("person", id)}
                  selectedSnapshot={
                    view === "senate" ? archiveEntry?.id : undefined
                  }
                  openSenate={(id) =>
                    navigation.navigate({
                      view: "senate",
                      entry: { kind: "senate", id },
                    })
                  }
                />
              </Suspense>
            </div>
          )}
        </Suspense>
      </main>
      {modal && (
        <Dialog
          title={
            modal === "context"
              ? "Contexto de la pregunta"
              : modal === "about"
                ? "Elecciones"
                : modal === "privacy"
                  ? "Privacidad"
                  : modal === "method"
                    ? "Método"
                    : "¿Empezar una nueva encuesta?"
          }
          close={() => setModal(null)}
        >
          {modal === "context" && (
            <div className="expanded-context prose">
              <h3>{question.text}</h3>
              <p>{contexts[question.id].scope}</p>
              <h3>Aspectos que puedes valorar</h3>
              {contexts[question.id].considerations.map((p) => (
                <p key={p}>{p}</p>
              ))}
              <small>
                Se explica la propuesta del cuestionario, no la legislación
                vigente.
              </small>
            </div>
          )}
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
                  El archivo político reúne fichas personales y documentos.
                  Gobiernos centrales permite recorrer el Ejecutivo, el Congreso
                  y el Senado desde 1977. El hemiciclo del Congreso enlaza los
                  mandatos individuales y sus cambios de grupo; su distribución
                  es esquemática. El menú autonómico queda preparado para
                  ampliar sus contenidos.
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
                  <dd>0.8.0</dd>
                </div>
                <div>
                  <dt>Creación</dt>
                  <dd>6 de octubre de 2026</dd>
                </div>
                <div>
                  <dt>Actualización</dt>
                  <dd>8 de octubre de 2026</dd>
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
