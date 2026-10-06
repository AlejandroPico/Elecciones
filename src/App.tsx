import { useEffect, useRef, useState, type ReactNode } from "react";
import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  Check,
  ChevronDown,
  Download,
  Globe2,
  Info,
  Landmark,
  ListChecks,
  LockKeyhole,
  Menu,
  Moon,
  RotateCcw,
  ShieldCheck,
  SlidersHorizontal,
  Sun,
  Sunrise,
  X,
  ChartNoAxesCombined,
  FileText,
  Scale,
  CircleHelp,
  Upload,
  Users,
} from "lucide-react";
import { categories, election, questions, VERSION } from "./data";
import {
  calculate,
  parseParties,
  restore,
  similarity,
  STORAGE_KEY,
  type Party,
} from "./model";
import { AxisRows, CoordinateChart, RadarChart } from "./Charts";
import favicon from "../favicon.svg";
import Archive from "./Archive";
type View = "survey" | "results" | "programs" | "archive";
type Modal = "settings" | "method" | "privacy" | "about" | "reset" | null;
type Theme = "auto" | "morning" | "afternoon" | "night";
function readSession() {
  try {
    return restore(localStorage.getItem(STORAGE_KEY));
  } catch {
    return restore(null);
  }
}
function readPreferences(): { theme: Theme; timezone: string } {
  try {
    const d = JSON.parse(
      localStorage.getItem("elecciones:preferences") ?? "{}",
    );
    return {
      theme: ["auto", "morning", "afternoon", "night"].includes(d.theme)
        ? d.theme
        : "auto",
      timezone: [
        "device",
        "Europe/Madrid",
        "Atlantic/Canary",
        "Europe/London",
        "America/New_York",
        "America/Argentina/Buenos_Aires",
      ].includes(d.timezone)
        ? d.timezone
        : "device",
    };
  } catch {
    return { theme: "auto", timezone: "device" };
  }
}
function Dialog({
  title,
  eyebrow,
  children,
  close,
}: {
  title: string;
  eyebrow: string;
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
    <dialog
      ref={ref}
      onCancel={close}
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          const r = e.currentTarget.getBoundingClientRect();
          if (
            e.clientX < r.left ||
            e.clientX > r.right ||
            e.clientY < r.top ||
            e.clientY > r.bottom
          )
            close();
        }
      }}
      aria-labelledby="dialog-title"
    >
      <div className="dialog-head">
        <span className="eyebrow">{eyebrow}</span>
        <button className="icon-button" onClick={close} aria-label="Cerrar">
          <X size={20} />
        </button>
      </div>
      <h2 id="dialog-title">{title}</h2>
      {children}
    </dialog>
  );
}
const choices = [
  { value: -2, label: "Muy en desacuerdo" },
  { value: -1, label: "En desacuerdo" },
  { value: 0, label: "Neutral" },
  { value: 1, label: "De acuerdo" },
  { value: 2, label: "Muy de acuerdo" },
];
function download(data: unknown) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = "elecciones-mi-perfil.json";
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export default function App() {
  const [session, setSession] = useState(readSession);
  const { answers, index } = session;
  const [preferences, setPreferences] = useState(readPreferences);
  const [view, setView] = useState<View>("survey");
  const [modal, setModal] = useState<Modal>(null);
  const [mobileMenu, setMobileMenu] = useState(false);
  const [activeCategory, setActiveCategory] = useState(categories[0].id);
  const [chart, setChart] = useState<"coordinates" | "radar">("coordinates");
  const [parties, setParties] = useState<Party[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [importMessage, setImportMessage] = useState("");
  const [storageError, setStorageError] = useState(false);
  const [draftImportance, setDraftImportance] = useState<
    Record<string, 1 | 2 | 3>
  >({});
  const [clock, setClock] = useState(new Date());
  const inputFile = useRef<HTMLInputElement>(null);
  const questionRef = useRef<HTMLHeadingElement>(null);
  const q = questions[index],
    category = categories.find((c) => c.id === q.category)!;
  const resultCategory = categories.find((c) => c.id === activeCategory)!;
  const scores = calculate(answers);
  const resolved = questions.filter((q) => Object.hasOwn(answers, q.id)).length;
  const scored = questions.filter((q) => answers[q.id]?.value != null).length;
  const progress = Math.round((resolved / questions.length) * 100);
  const current = answers[q.id];
  const importance = current?.importance ?? draftImportance[q.id] ?? 1;
  const overlays = parties.filter((p) => selected.includes(p.id));
  const hour = Number(
    new Intl.DateTimeFormat("en-GB", {
      hour: "2-digit",
      hourCycle: "h23",
      timeZone:
        preferences.timezone === "device" ? undefined : preferences.timezone,
    }).format(clock),
  );
  const theme =
    preferences.theme === "auto"
      ? hour >= 7 && hour < 14
        ? "morning"
        : hour >= 14 && hour < 20
          ? "afternoon"
          : "night"
      : preferences.theme;
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);
  useEffect(() => {
    const timer = setInterval(() => setClock(new Date()), 30000);
    return () => clearInterval(timer);
  }, []);
  useEffect(() => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ version: VERSION, ...session }),
      );
      localStorage.setItem(
        "elecciones:preferences",
        JSON.stringify(preferences),
      );
      setStorageError(false);
    } catch {
      setStorageError(true);
    }
  }, [session, preferences]);
  function selectValue(value: number | null) {
    setSession((s) => ({
      ...s,
      answers: { ...s.answers, [q.id]: { value, importance } },
    }));
  }
  function next() {
    if (!current) return;
    if (index === questions.length - 1) setView("results");
    else setSession((s) => ({ ...s, index: s.index + 1 }));
  }
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
      const opts = q.type === "binary" ? [-2, 2] : [-2, -1, 0, 1, 2];
      const n = Number(e.key);
      if (n >= 1 && n <= opts.length) {
        e.preventDefault();
        selectValue(opts[n - 1]);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });
  useEffect(() => {
    if (view === "survey") {
      questionRef.current?.focus({ preventScroll: true });
      questionRef.current?.scrollIntoView({
        block: "nearest",
        behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "instant"
          : "smooth",
      });
    }
  }, [index, view]);
  useEffect(() => {
    document
      .getElementById("content")
      ?.scrollIntoView({
        block: "start",
        behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
          ? "instant"
          : "smooth",
      });
  }, [view]);
  function jump(id: string) {
    const items = questions.filter((q) => q.category === id);
    const target = items.find((q) => !Object.hasOwn(answers, q.id)) ?? items[0];
    setSession((s) => ({ ...s, index: questions.indexOf(target) }));
    setView("survey");
    setMobileMenu(false);
  }
  async function importFile(file?: File) {
    if (!file) return;
    try {
      if (file.size > 2_000_000)
        throw new Error("El archivo supera el límite de 2 MB.");
      const imported = parseParties(JSON.parse(await file.text()));
      setParties(imported);
      setSelected(imported.slice(0, 3).map((p) => p.id));
      setImportMessage(
        `${imported.length} candidaturas importadas en esta sesión. No se han publicado.`,
      );
    } catch (e) {
      setImportMessage(
        e instanceof Error ? e.message : "No se ha podido leer el archivo.",
      );
    }
    if (inputFile.current) inputFile.current.value = "";
  }
  const isComplete = resolved === questions.length;
  return (
    <>
      <a href="#content" className="skip-link">
        Saltar al contenido
      </a>
      <header className="topbar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            setView("survey");
          }}
          aria-label="Elecciones, cuestionario"
        >
          <img src={favicon} alt="" />
          <span>
            elecciones<span className="brand-dot">.</span>
          </span>
        </a>
        <div className="election-label">
          <span className="live-dot" />
          <span>
            España <span className="divider">/</span> Generales 2026
          </span>
        </div>
        <div className="top-actions">
          <span className="private-label">
            <LockKeyhole size={13} /> Respuestas en tu dispositivo
          </span>
          <button
            className="theme-button"
            onClick={() => setModal("settings")}
            aria-label="Configurar apariencia y horario"
          >
            {theme === "night" ? (
              <Moon size={17} />
            ) : theme === "morning" ? (
              <Sunrise size={17} />
            ) : (
              <Sun size={17} />
            )}
            <span>
              {preferences.theme === "auto"
                ? "Automático"
                : theme === "morning"
                  ? "Mañana"
                  : theme === "afternoon"
                    ? "Tarde"
                    : "Noche"}
            </span>
            <ChevronDown size={13} />
          </button>
          <button
            className="mobile-menu icon-button"
            onClick={() => setMobileMenu(!mobileMenu)}
            aria-label="Abrir navegación"
            aria-expanded={mobileMenu}
          >
            <Menu size={20} />
          </button>
        </div>
      </header>
      <div className="app-layout">
        <aside className={`sidebar ${mobileMenu ? "open" : ""}`}>
          <div className="sidebar-main">
            <span className="eyebrow sidebar-label">TU CUESTIONARIO</span>
            <nav className="main-nav" aria-label="Secciones">
              <button
                className={view === "survey" ? "active" : ""}
                onClick={() => {
                  setView("survey");
                  setMobileMenu(false);
                }}
              >
                <ListChecks size={18} />
                Cuestionario
                <span className="nav-counter">
                  {resolved}/{questions.length}
                </span>
              </button>
              <button
                className={view === "results" ? "active" : ""}
                onClick={() => {
                  setView("results");
                  setMobileMenu(false);
                }}
              >
                <ChartNoAxesCombined size={18} />
                Mi perfil
              </button>
              <button
                className={view === "programs" ? "active" : ""}
                onClick={() => {
                  setView("programs");
                  setMobileMenu(false);
                }}
              >
                <FileText size={18} />
                Programas y partidos
              </button>
            </nav>
            <button
              className={`archive-nav ${view === "archive" ? "active" : ""}`}
              onClick={() => {
                setView("archive");
                setMobileMenu(false);
              }}
            >
              <Users size={18} />
              Archivo político
            </button>
            <div className="sidebar-rule" />
            <span className="eyebrow sidebar-label">TEMAS</span>
            <nav className="category-nav" aria-label="Temas del cuestionario">
              {categories.map((c, i) => {
                const items = questions.filter((q) => q.category === c.id),
                  count = items.filter((q) =>
                    Object.hasOwn(answers, q.id),
                  ).length;
                return (
                  <button
                    key={c.id}
                    className={
                      view === "survey" && c.id === q.category ? "current" : ""
                    }
                    onClick={() => jump(c.id)}
                  >
                    <span className="category-number">
                      {count === items.length ? (
                        <Check size={13} />
                      ) : (
                        String(i + 1).padStart(2, "0")
                      )}
                    </span>
                    <span>{c.name}</span>
                    <span className="category-count">
                      {count}/{items.length}
                    </span>
                  </button>
                );
              })}
            </nav>
          </div>
          <div className="sidebar-bottom">
            <div className="saved-status">
              <span className={storageError ? "warning-dot" : "live-dot"} />
              <span>
                {storageError
                  ? "Guardado local no disponible"
                  : "Progreso guardado localmente"}
              </span>
            </div>
            <button className="quiet-button" onClick={() => setModal("reset")}>
              <RotateCcw size={14} /> Nueva encuesta
            </button>
            <div className="sidebar-footer">
              <button onClick={() => setModal("about")}>Acerca de</button>
              <span>·</span>
              <button onClick={() => setModal("privacy")}>Privacidad</button>
            </div>
          </div>
        </aside>
        <main id="content" className="main-content">
          <div className="page-heading">
            <div>
              <span className="eyebrow">
                {view === "survey"
                  ? "CUESTIONARIO POLÍTICO"
                  : view === "results"
                    ? "TUS COORDENADAS"
                    : view === "archive"
                      ? "ENCICLOPEDIA POLÍTICA"
                      : "DOCUMENTACIÓN ELECTORAL"}
              </span>
              <h1>
                {view === "survey"
                  ? "Tus posiciones, tema a tema."
                  : view === "results"
                    ? "Mi perfil político."
                    : view === "archive"
                      ? "Personas, partidos e historia."
                      : "Programas y partidos."}
              </h1>
            </div>
            {view !== "archive" && (
              <button
                className="text-button method-button"
                onClick={() => setModal("method")}
              >
                <CircleHelp size={16} /> Cómo se calcula
              </button>
            )}
          </div>
          {view === "survey" && (
            <>
              <div className="progress-panel">
                <div className="progress-caption">
                  <span>
                    {isComplete
                      ? "Cuestionario completado"
                      : "Progreso del cuestionario"}
                  </span>
                  <span>
                    <strong>{resolved}</strong> / {questions.length} preguntas{" "}
                    <span className="progress-percent">{progress}%</span>
                  </span>
                </div>
                <div
                  className="progress-track"
                  role="progressbar"
                  aria-label="Progreso del cuestionario"
                  aria-valuenow={resolved}
                  aria-valuemin={0}
                  aria-valuemax={questions.length}
                >
                  <div style={{ width: `${progress}%` }} />
                </div>
              </div>
              <div className="survey-layout">
                <section className="question-card">
                  <div className="question-meta">
                    <span className="category-tag">
                      <Landmark size={14} />
                      {category.name}
                    </span>
                    <span className="question-index">
                      {String(index + 1).padStart(2, "0")}{" "}
                      <span>/ {questions.length}</span>
                    </span>
                  </div>
                  <div className="question-body" key={q.id}>
                    <span className="eyebrow">{category.description}</span>
                    <h2 ref={questionRef} tabIndex={-1}>
                      {q.text}
                    </h2>
                    <p className="question-context">{q.context}</p>
                    <fieldset
                      className={`answer-options ${q.type === "binary" ? "binary" : ""}`}
                    >
                      <legend>
                        {q.type === "binary"
                          ? "¿Estás de acuerdo con esta propuesta?"
                          : "¿En qué medida estás de acuerdo?"}
                      </legend>
                      {(q.type === "binary"
                        ? [
                            { value: -2, label: "No" },
                            { value: 2, label: "Sí" },
                          ]
                        : choices
                      ).map((choice, i) => (
                        <label
                          className={`answer-option ${current?.value === choice.value ? "selected" : ""}`}
                          key={choice.value}
                        >
                          <input
                            type="radio"
                            name={q.id}
                            checked={current?.value === choice.value}
                            onChange={() => selectValue(choice.value)}
                          />
                          <span className="choice-symbol">
                            {current?.value === choice.value ? (
                              <Check size={18} />
                            ) : (
                              <span
                                className="choice-dot"
                                style={{
                                  width: `${8 + Math.abs(choice.value) * 3}px`,
                                  height: `${8 + Math.abs(choice.value) * 3}px`,
                                }}
                              />
                            )}
                          </span>
                          <span>{choice.label}</span>
                          <kbd>{i + 1}</kbd>
                        </label>
                      ))}
                    </fieldset>
                    <button
                      className={`skip-answer ${current?.value === null ? "chosen" : ""}`}
                      onClick={() => selectValue(null)}
                    >
                      {current?.value === null ? (
                        <Check size={14} />
                      ) : (
                        <CircleHelp size={14} />
                      )}{" "}
                      No sé / prefiero omitir
                    </button>
                  </div>
                  <div className="importance-panel">
                    <div>
                      <span>Importancia para ti</span>
                      <small>Pondera esta respuesta en tu perfil</small>
                    </div>
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
                      ).map((o) => (
                        <button
                          key={o.value}
                          aria-pressed={importance === o.value}
                          className={importance === o.value ? "active" : ""}
                          onClick={() => {
                            if (current)
                              setSession((s) => ({
                                ...s,
                                answers: {
                                  ...s.answers,
                                  [q.id]: { ...current, importance: o.value },
                                },
                              }));
                            else
                              setDraftImportance((d) => ({
                                ...d,
                                [q.id]: o.value,
                              }));
                          }}
                        >
                          {o.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="question-footer">
                    <button
                      className="text-button"
                      disabled={index === 0}
                      onClick={() =>
                        setSession((s) => ({ ...s, index: s.index - 1 }))
                      }
                    >
                      <ArrowLeft size={16} />
                      Anterior
                    </button>
                    <span className="question-save" role="status">
                      {current
                        ? current.value === null
                          ? "Pregunta omitida"
                          : "Respuesta guardada"
                        : "Elige una respuesta"}
                    </span>
                    <button
                      className="primary-button"
                      disabled={!current}
                      onClick={next}
                    >
                      {index === questions.length - 1
                        ? "Ver mi perfil"
                        : "Continuar"}
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </section>
                <aside className="live-profile">
                  <div className="panel-title">
                    <div>
                      <span className="eyebrow">EN DIRECTO</span>
                      <h2>Tu posición</h2>
                    </div>
                    <span
                      className="live-indicator"
                      title="Se actualiza con tus respuestas"
                    />
                  </div>
                  <div
                    className="chart-tabs"
                    role="group"
                    aria-label="Tipo de gráfico"
                  >
                    <button
                      className={chart === "coordinates" ? "active" : ""}
                      onClick={() => setChart("coordinates")}
                    >
                      Coordenadas
                    </button>
                    <button
                      className={chart === "radar" ? "active" : ""}
                      onClick={() => setChart("radar")}
                    >
                      Vista radial
                    </button>
                  </div>
                  <div className="live-chart-title">
                    {chart === "coordinates"
                      ? category.name
                      : "Ocho dimensiones"}
                  </div>
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
                  <div className="chart-legend">
                    <span className="legend-dot" />
                    Tu perfil
                    {overlays.map((p) => (
                      <span key={p.id}>
                        <i style={{ background: p.color }} />
                        {p.name}
                      </span>
                    ))}
                  </div>
                  {chart === "coordinates" ? (
                    <AxisRows category={category} scores={scores} />
                  ) : (
                    <p className="chart-note">
                      Cada radio muestra el primer eje de un tema. Centro: −100;
                      borde: +100. Los ejes sin respuestas quedan sin trazar.
                    </p>
                  )}
                  <button
                    className="profile-link"
                    onClick={() => {
                      setActiveCategory(category.id);
                      setView("results");
                    }}
                  >
                    Explorar mi perfil
                    <ArrowUpRight size={16} />
                  </button>
                  <p className="pilot-note">
                    <Info size={14} />
                    <span>
                      Banco piloto de 48 preguntas. Los resultados son
                      orientativos.
                    </span>
                  </p>
                </aside>
              </div>
              <div className="bottom-note">
                <ShieldCheck size={15} />
                <span>
                  Puedes pausar y volver más tarde desde este navegador.
                </span>
                <button onClick={() => setModal("privacy")}>
                  Privacidad
                  <ArrowUpRight size={12} />
                </button>
              </div>
            </>
          )}
          {view === "results" && (
            <>
              <div className="results-summary">
                <span className="status-badge">
                  {isComplete ? "Completado" : "Perfil parcial"}
                </span>
                <p>
                  <strong>{scored}</strong> respuestas valoradas ·{" "}
                  {resolved - scored} omitidas · {questions.length - resolved}{" "}
                  pendientes
                </p>
                <div>
                  <button
                    className="text-button"
                    onClick={() =>
                      download({
                        version: VERSION,
                        election: election.id,
                        answers,
                        scores,
                      })
                    }
                  >
                    <Download size={16} />
                    Exportar mi perfil
                  </button>
                  <button
                    className="primary-button"
                    onClick={() => {
                      const nextIndex = questions.findIndex(
                        (q) => !Object.hasOwn(answers, q.id),
                      );
                      setSession((s) => ({
                        ...s,
                        index: nextIndex < 0 ? s.index : nextIndex,
                      }));
                      setView("survey");
                    }}
                  >
                    {isComplete ? "Revisar respuestas" : "Seguir respondiendo"}
                    <ArrowRight size={16} />
                  </button>
                </div>
              </div>
              <div className="results-layout">
                <section className="result-card">
                  <div className="panel-title">
                    <div>
                      <span className="eyebrow">MAPA POR TEMA</span>
                      <h2>Posiciones independientes</h2>
                    </div>
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
                  </div>
                  <CoordinateChart
                    category={resultCategory}
                    scores={scores}
                    parties={overlays}
                  />
                  <AxisRows category={resultCategory} scores={scores} />
                </section>
                <section className="result-card">
                  <div className="panel-title">
                    <div>
                      <span className="eyebrow">VISTA DE CONJUNTO</span>
                      <h2>Ocho dimensiones</h2>
                    </div>
                  </div>
                  <RadarChart scores={scores} parties={overlays} />
                  <p className="chart-note">
                    Un radio por tema, correspondiente a su primer eje. −100 en
                    el centro y +100 en el borde. La extensión indica posición,
                    no calidad ni afinidad general.
                  </p>
                  <div className="chart-legend">
                    <span className="legend-dot" />
                    Tu perfil
                    {overlays.map((p) => (
                      <span key={p.id}>
                        <i style={{ background: p.color }} />
                        {p.name}
                      </span>
                    ))}
                  </div>
                </section>
              </div>
              <section className="comparison-card">
                <div className="panel-title">
                  <div>
                    <span className="eyebrow">COMPARACIÓN DOCUMENTADA</span>
                    <h2>Candidaturas</h2>
                  </div>
                  <button
                    className="text-button"
                    onClick={() => setView("programs")}
                  >
                    Ver fuentes
                    <ArrowUpRight size={16} />
                  </button>
                </div>
                {parties.length === 0 ? (
                  <div className="empty-state">
                    <Scale size={28} />
                    <div>
                      <h3>Los programas aún no están incorporados</h3>
                      <p>
                        Cuando haya posiciones documentadas podrás superponer
                        candidaturas y comparar coincidencias por pregunta.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="party-list">
                    {parties.map((p) => {
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
                          <span
                            className="party-color"
                            style={{ background: p.color }}
                          />
                          <span>
                            <strong>{p.name}</strong>
                            <small>
                              {s.shared} preguntas comunes de {s.answered}{" "}
                              respondidas. Las posiciones desconocidas se
                              excluyen.
                            </small>
                          </span>
                          <b>
                            {s.percent === null
                              ? "Sin datos comunes"
                              : `${Math.round(s.percent)}%`}
                          </b>
                        </label>
                      );
                    })}
                  </div>
                )}
              </section>
              <details className="all-axes">
                <summary>
                  Ver las 16 dimensiones y su cobertura
                  <ChevronDown size={17} />
                </summary>
                <div className="axes-grid">
                  {categories.map((c) => (
                    <section key={c.id}>
                      <h3>{c.name}</h3>
                      <AxisRows category={c} scores={scores} />
                    </section>
                  ))}
                </div>
              </details>
            </>
          )}
          {view === "programs" && (
            <>
              <section className="program-intro">
                <span className="status-badge">
                  Banco piloto · sin catálogo oficial
                </span>
                <h2>Una posición necesita una fuente.</h2>
                <p>
                  La comparación se construirá a partir de los programas de las
                  candidaturas. Cada posición tendrá una referencia verificable;
                  las ausencias y ambigüedades quedarán sin puntuación.
                </p>
                <div className="program-facts">
                  <div>
                    <span>Ámbito</span>
                    <strong>Congreso y Senado · España</strong>
                  </div>
                  <div>
                    <span>Fecha de la convocatoria</span>
                    <strong>29 de noviembre de 2026</strong>
                  </div>
                  <div>
                    <span>Referencia de convocatoria</span>
                    <a href={election.source} target="_blank" rel="noreferrer">
                      Consultar BOE
                      <ArrowUpRight size={14} />
                    </a>
                  </div>
                </div>
                <p className="source-note">{election.verification}</p>
              </section>
              <section className="result-card import-card">
                <div className="panel-title">
                  <div>
                    <span className="eyebrow">PREPARACIÓN DEL CATÁLOGO</span>
                    <h2>Importar posiciones documentadas</h2>
                  </div>
                  <Upload size={22} />
                </div>
                <p>
                  Permite probar la comparación con un archivo JSON que siga el
                  formato del repositorio. Se carga solo en esta sesión; no
                  publica datos ni interpreta automáticamente un PDF.
                </p>
                <input
                  ref={inputFile}
                  type="file"
                  accept=".json,application/json"
                  hidden
                  onChange={(e) => void importFile(e.target.files?.[0])}
                />
                <button
                  className="primary-button"
                  onClick={() => inputFile.current?.click()}
                >
                  <Upload size={16} />
                  Seleccionar archivo
                </button>
                <p className="import-message" role="status">
                  {importMessage}
                </p>
                {parties.map((p) => (
                  <details className="party-sources" key={p.id}>
                    <summary>
                      <span
                        className="party-color"
                        style={{ background: p.color }}
                      />
                      {p.name}
                      <small>
                        {Object.keys(p.positions).length} posiciones
                      </small>
                    </summary>
                    <ul>
                      {Object.entries(p.positions).map(([id, position]) => (
                        <li key={id}>
                          <strong>
                            {questions.find((q) => q.id === id)?.text}
                          </strong>
                          <p>
                            Puntuación: {position.value} · {position.reference}
                          </p>
                          <a
                            href={position.source}
                            target="_blank"
                            rel="noreferrer"
                          >
                            Fuente original
                            <ArrowUpRight size={12} />
                          </a>
                        </li>
                      ))}
                    </ul>
                  </details>
                ))}
              </section>
            </>
          )}
          {view === "archive" && <Archive />}
          <footer className="content-footer">
            <span>
              ELECCIONES <span> / </span> Versión 0.1
            </span>
            <button onClick={() => setModal("method")}>Metodología</button>
            <span className="pilot-label">Edición piloto</span>
          </footer>
        </main>
      </div>
      {modal === "settings" && (
        <Dialog
          eyebrow="PREFERENCIAS"
          title="Apariencia y horario"
          close={() => setModal(null)}
        >
          <p>
            El modo automático cambia según la hora de la zona seleccionada.
          </p>
          <div className="theme-options">
            {(
              [
                { value: "auto", label: "Automático", icon: SlidersHorizontal },
                { value: "morning", label: "Mañana", icon: Sunrise },
                { value: "afternoon", label: "Tarde", icon: Sun },
                { value: "night", label: "Noche", icon: Moon },
              ] as const
            ).map((o) => (
              <button
                key={o.value}
                className={preferences.theme === o.value ? "active" : ""}
                aria-pressed={preferences.theme === o.value}
                onClick={() =>
                  setPreferences((p) => ({ ...p, theme: o.value }))
                }
              >
                <o.icon size={23} />
                {o.label}
              </button>
            ))}
          </div>
          <label className="setting-label">
            <Globe2 size={16} />
            Zona horaria
            <select
              value={preferences.timezone}
              onChange={(e) =>
                setPreferences((p) => ({ ...p, timezone: e.target.value }))
              }
            >
              <option value="device">La de mi dispositivo</option>
              <option value="Europe/Madrid">Madrid / Barcelona</option>
              <option value="Atlantic/Canary">Islas Canarias</option>
              <option value="Europe/London">Londres</option>
              <option value="America/New_York">Nueva York</option>
              <option value="America/Argentina/Buenos_Aires">
                Buenos Aires
              </option>
            </select>
          </label>
          <div className="schedule">
            <span>07–14 h · Mañana</span>
            <span>14–20 h · Tarde</span>
            <span>20–07 h · Noche</span>
          </div>
          <p className="small-note">
            No se solicita tu ubicación. El horario usa la zona del dispositivo
            o la que elijas.
          </p>
        </Dialog>
      )}
      {modal === "method" && (
        <Dialog
          eyebrow="METODOLOGÍA · V0.1"
          title="Cómo se construye tu perfil"
          close={() => setModal(null)}
        >
          <div className="prose">
            <p>
              El banco piloto tiene 48 preguntas, 8 temas y 16 ejes
              independientes. Es una base de trabajo pendiente de revisión de
              neutralidad, equilibrio y validez. No asigna una etiqueta
              ideológica general.
            </p>
            <h3>Respuestas y ponderación</h3>
            <p>
              La escala asigna −2, −1, 0, +1 y +2. Las preguntas de sí o no usan
              −2 y +2. «Neutral» aporta 0; «no sé / prefiero omitir» no aporta
              puntuación. La importancia normal, alta y esencial pesa 1, 2 y 3.
            </p>
            <p>
              Cada pregunta tiene un eje y una dirección explícitos. La media
              ponderada de respuestas se normaliza entre −100 y +100. Un eje sin
              respuestas no tiene coordenada; el punto aparece cuando hay
              respuestas en ambos ejes.
            </p>
            <h3>Cobertura y comparación</h3>
            <p>
              La cobertura cuenta respuestas válidas, no preguntas omitidas. Con
              pocas respuestas la posición es provisional. Las candidaturas se
              comparan solo en preguntas con una respuesta tuya y una posición
              documentada.
            </p>
            <p>
              Coincidencia = 100 × (1 − media ponderada de la distancia entre
              respuestas / 4). No es una probabilidad de voto ni una
              recomendación. Compara también la cobertura: dos porcentajes con
              distinta evidencia no tienen el mismo alcance.
            </p>
            <h3>Fuentes y revisión</h3>
            <p>
              Las posiciones desconocidas o ambiguas se excluyen. El catálogo
              necesita revisión humana y referencias a propuestas concretas; un
              programa completo no se convierte automáticamente en una
              puntuación. Las preguntas sobre actualidad requerirán contexto
              fechado y fuentes antes de añadirse.
            </p>
          </div>
        </Dialog>
      )}
      {modal === "privacy" && (
        <Dialog
          eyebrow="PRIVACIDAD"
          title="Tus respuestas, en tu dispositivo"
          close={() => setModal(null)}
        >
          <div className="prose">
            <p>
              Esta versión guarda respuestas, progreso y preferencias en el
              almacenamiento local del navegador. No usa cookies de seguimiento,
              no solicita nombre o correo y no envía las respuestas a un
              servidor.
            </p>
            <p>
              «Nueva encuesta» borra las respuestas y comienza de nuevo. Las
              preferencias se conservan. En un dispositivo compartido, otra
              persona que use el mismo navegador puede ver el progreso guardado.
            </p>
            <h3>Estadísticas internas</h3>
            <p>
              Todavía no hay recogida central de resultados, ni autenticación
              con Google. Si se incorpora, la participación estadística será
              opcional y separada del acceso a la encuesta; se explicará qué se
              envía y para qué.
            </p>
            <p>
              No publicaríamos perfiles individuales. La propuesta técnica es
              acumular recuentos por respuesta y versión del cuestionario, con
              acceso interno y sin nombres.
            </p>
            <h3>Alojamiento</h3>
            <p>
              El proveedor que aloje la web puede registrar datos técnicos de
              las visitas, como la dirección IP. El guardado local de respuestas
              no implica anonimato absoluto frente al proveedor.
            </p>
            <a
              href="https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection"
              target="_blank"
              rel="noreferrer"
            >
              Datos técnicos en GitHub Pages
              <ArrowUpRight size={14} />
            </a>
          </div>
        </Dialog>
      )}
      {modal === "about" && (
        <Dialog
          eyebrow="ACERCA DEL PROYECTO"
          title="Elecciones"
          close={() => setModal(null)}
        >
          <div className="about-brand">
            <img src={favicon} alt="Una mano deposita un sobre en una urna" />
            <p>
              Cuestionario político por temas.
              <br />
              Posiciones, cobertura y fuentes.
            </p>
          </div>
          <div className="prose">
            <p>
              Elecciones es un proyecto personal de{" "}
              <strong>Alejandro Pico Perez</strong> para explorar posiciones
              políticas y, cuando se incorporen los programas, compararlas con
              las propuestas de las candidaturas.
            </p>
            <p>
              El cuestionario organiza preguntas por temas. Las respuestas
              dibujan coordenadas independientes y una vista radial. Puedes
              indicar su importancia, omitir preguntas, revisar respuestas y
              conservar el progreso en el navegador.
            </p>
            <p>
              La primera edición se centra en las elecciones generales de
              España. El banco actual es piloto: falta la revisión editorial y
              el catálogo de posiciones de los partidos. El archivo político
              ofrece fichas iniciales de personas y partidos, documentos
              históricos y navegación entre titulares de cargos. La estructura
              permite añadir otras convocatorias y territorios.
            </p>
          </div>
          <dl className="project-meta">
            <div>
              <dt>Autor</dt>
              <dd>Alejandro Pico Perez</dd>
            </div>
            <div>
              <dt>Versión</dt>
              <dd>0.1.0 · Edición piloto</dd>
            </div>
            <div>
              <dt>Creación</dt>
              <dd>
                <time dateTime="2026-10-06">6 de octubre de 2026</time>
              </dd>
            </div>
            <div>
              <dt>Última actualización</dt>
              <dd>
                <time dateTime="2026-10-06">6 de octubre de 2026</time>
              </dd>
            </div>
          </dl>
          <nav className="about-links" aria-label="Autor y código">
            <a
              href="https://alejandropico.github.io/Portfolio/"
              target="_blank"
              rel="noreferrer"
            >
              Portfolio de Alejandro Pico
              <ArrowUpRight size={18} />
            </a>
            <a
              href="https://github.com/AlejandroPico/Elecciones"
              target="_blank"
              rel="noreferrer"
            >
              Elecciones en GitHub
              <ArrowUpRight size={18} />
            </a>
          </nav>
        </Dialog>
      )}
      {modal === "reset" && (
        <Dialog
          eyebrow="NUEVA ENCUESTA"
          title="¿Volver a empezar?"
          close={() => setModal(null)}
        >
          <p>
            Se borrarán las respuestas guardadas en este navegador. Puedes
            exportar tu perfil antes de hacerlo.
          </p>
          <div className="dialog-actions">
            <button
              className="text-button"
              onClick={() =>
                download({
                  version: VERSION,
                  election: election.id,
                  answers,
                  scores,
                })
              }
            >
              <Download size={16} />
              Exportar perfil
            </button>
            <button
              className="primary-button"
              onClick={() => {
                setSession({ answers: {}, index: 0 });
                setDraftImportance({});
                setView("survey");
                setModal(null);
              }}
            >
              Borrar y empezar
              <RotateCcw size={16} />
            </button>
          </div>
        </Dialog>
      )}
    </>
  );
}
