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
  ChevronDown,
  ChartNoAxesCombined,
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
const Questionnaire = lazy(
  () => import("../../Cuestionario/interfaz/Questionnaire"),
);
const Programs = lazy(() => import("../../Partidos/interfaz/Programs"));
const Coordinates = lazy(
  () => import("../../Cuestionario/interfaz/Coordinates"),
);
import favicon from "../../favicon.svg";
import { useNavigation, type View, type Entry } from "./navigation";
import ScrollNavigation from "./ScrollNavigation";
const Archive = lazy(() => import("../../Políticos/interfaz/Archive"));
const Governments = lazy(() => import("../../Gobiernos/interfaz/Governments"));
const Presidencies = lazy(
  () => import("../../Gobiernos/interfaz/Presidencies"),
);
const Senate = lazy(() => import("../../Gobiernos/interfaz/Senate"));
const Congress = lazy(() => import("../../Gobiernos/interfaz/Congress"));
import Autonomies, { AutonomyMenu } from "../../Gobiernos/interfaz/Autonomies";
const Offices = lazy(() => import("../../Gobiernos/interfaz/Offices"));
type Modal = "method" | "privacy" | "about" | "reset" | null;
type Theme = "auto" | "morning" | "afternoon" | "night";
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
  const [surveyEdition, setSurveyEdition] = useState(0);
  const navigation = useNavigation();
  const { view, entry: archiveEntry } = navigation.route;
  const setView = (nextView: View) => navigation.navigate({ view: nextView });
  const [modal, setModal] = useState<Modal>(null);
  const [mobileMenu, setMobileMenu] = useState(() => window.innerWidth > 720);
  const [surveyMenu, setSurveyMenu] = useState(() => view === "coordinates");
  const [governmentMenu, setGovernmentMenu] = useState(() =>
    ["central", "governments", "congress", "senate"].includes(
      navigation.route.view,
    ),
  );
  const [themeMode, setThemeMode] = useState<Theme>("auto");
  const [clock, setClock] = useState(new Date());
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
  function openView(nextView: View) {
    setView(nextView);
    if (window.innerWidth <= 720) setMobileMenu(false);
  }
  function openArchive(kind: "person" | "party", id: string) {
    openEntry({ kind, id });
  }
  function openEntry(entry?: Entry) {
    navigation.navigate({
      view: entry
        ? entry.kind === "party"
          ? "programs"
          : entry.kind === "office"
            ? "offices"
            : entry.kind === "presidency"
              ? "central"
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
        <ScrollNavigation>
          {(
            [
              { id: "survey", name: "Cuestionario", icon: ListChecks },
              { id: "results", name: "Mi perfil", icon: ChartNoAxesCombined },
              { id: "programs", name: "Partidos", icon: FileText },
              { id: "archive", name: "Archivo político", icon: Users },
              { id: "offices", name: "Cargos e historia", icon: Landmark },
              {
                id: "central",
                name: "Gobiernos centrales",
                icon: Landmark,
              },
            ] as const
          ).map((item) => (
            <div key={item.id} className="navigation-item">
              <button
                className={
                  view === item.id ||
                  (item.id === "survey" && view === "coordinates") ||
                  (item.id === "central" &&
                    ["governments", "congress", "senate"].includes(view))
                    ? "active"
                    : ""
                }
                onClick={() => {
                  if (item.id === "survey") {
                    setSurveyMenu(!surveyMenu);
                    return;
                  }
                  if (item.id === "central") {
                    setGovernmentMenu(!governmentMenu);
                    openView("central");
                    return;
                  }
                  openView(item.id);
                }}
                aria-expanded={
                  item.id === "survey"
                    ? surveyMenu
                    : item.id === "central"
                      ? governmentMenu
                      : undefined
                }
                aria-current={view === item.id ? "page" : undefined}
              >
                <item.icon size={17} />
                <span>{item.name}</span>
                {(item.id === "survey" || item.id === "central") && (
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
                    <button
                      onClick={() => openView("coordinates")}
                      aria-current={view === "coordinates" ? "page" : undefined}
                    >
                      Coordenadas políticas
                    </button>
                  </div>
                </div>
              )}
              {item.id === "central" && (
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
            active={view === "autonomies"}
            selected={view === "autonomies" ? archiveEntry?.id : undefined}
            openOverview={() => openView("autonomies")}
            openSection={(id) => openEntry({ kind: "autonomy", id })}
          />
        </ScrollNavigation>
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
        {(navigation.visited.has("survey") ||
          navigation.visited.has("results")) && (
          <Suspense
            fallback={
              <span className="sr-only" role="status">
                Cargando cuestionario
              </span>
            }
          >
            <Questionnaire
              key={surveyEdition}
              view={view}
              openView={openView}
              blocked={modal !== null}
            />
          </Suspense>
        )}
        <Suspense
          fallback={
            <span className="sr-only" role="status">
              Cargando archivo
            </span>
          }
        >
          {view === "coordinates" && <Coordinates />}
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
                  active={view === "archive"}
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
          {navigation.visited.has("central") && (
            <div className="section-content" hidden={view !== "central"}>
              <Suspense
                fallback={
                  <span className="sr-only" role="status">
                    Cargando presidencias
                  </span>
                }
              >
                <Presidencies
                  selectedPresident={
                    view === "central" ? archiveEntry?.id : undefined
                  }
                  openPresident={(id) =>
                    navigation.navigate({
                      view: "central",
                      entry: id ? { kind: "presidency", id } : undefined,
                    })
                  }
                  openPerson={(id) => openArchive("person", id)}
                  openGovernment={(id) => openEntry({ kind: "government", id })}
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
                active={view === "autonomies"}
                openPerson={(id) => openArchive("person", id)}
                openSection={(id) =>
                  navigation.navigate({
                    view: "autonomies",
                    entry: { kind: "autonomy", id },
                  })
                }
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
                  40 temas seleccionables y hasta diez preguntas aleatorias por
                  tema. Permite ponderar respuestas, omitirlas y revisarlas
                  desde la barra de progreso. El archivo político reúne fichas
                  personales y documentos. Gobiernos centrales incorpora un
                  histórico de presidencias, hitos, crisis y escándalos con
                  fuentes y permite recorrer el Ejecutivo, el Congreso y el
                  Senado desde 1977. El hemiciclo del Congreso enlaza los
                  mandatos individuales y sus cambios de grupo; su distribución
                  es esquemática. El menú autonómico queda preparado para
                  ampliar sus contenidos.
                </p>
                <p>
                  No guarda respuestas ni preferencias. Al recargar la página se
                  comienza de nuevo. El banco y sus codificaciones son
                  experimentales. Los documentos históricos no sustituyen los
                  programas y candidaturas de 2026.
                </p>
              </div>
              <dl className="project-meta">
                <div>
                  <dt>Versión</dt>
                  <dd>0.33.0</dd>
                </div>
                <div>
                  <dt>Creación</dt>
                  <dd>6 de octubre de 2026</dd>
                </div>
                <div>
                  <dt>Actualización</dt>
                  <dd>18 de octubre de 2026</dd>
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
                Los indicadores que ya tienen una dirección documentada
                conservan la media ponderada entre −100 y +100. Las demás
                respuestas participan en las afinidades por tema y en su
                desglose. El mapa de afinidad cruza coincidencia y cobertura; no
                asigna una etiqueta ideológica a una media de propuestas
                diferentes.
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
                    setSurveyEdition((n) => n + 1);
                    openView("survey");
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
