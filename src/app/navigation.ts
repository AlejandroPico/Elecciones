import { useEffect, useState } from "react";

export type View = "survey" | "results" | "programs" | "archive" | "offices" | "governments";
export type Entry = { kind: "person" | "party" | "office" | "government"; id: string };
export type Route = { view: View; entry?: Entry };
const paths: Record<View, string> = {
  survey: "cuestionario", results: "perfil", programs: "partidos",
  archive: "archivo", offices: "cargos", governments: "gobiernos",
};
export function routeHash(route: Route) {
  return `#/${paths[route.view]}${route.entry ? `/${route.entry.kind}/${encodeURIComponent(route.entry.id)}` : ""}`;
}
export function parseRoute(hash: string): Route {
  const [path, kind, encoded] = hash.replace(/^#\/?/, "").split("/");
  const view = (Object.keys(paths) as View[]).find((v) => paths[v] === path) ?? "survey";
  if (encoded && ((view === "archive" && kind === "person") ||
    (view === "programs" && kind === "party") || (view === "offices" && kind === "office") || (view === "governments" && kind === "government"))) {
    try { return { view, entry: { kind: kind as Entry["kind"], id: decodeURIComponent(encoded) } }; }
    catch { /* Una dirección incompleta vuelve a su directorio. */ }
  }
  return { view };
}

/** El historial pertenece al navegador, también al abrir fichas desde otras secciones. */
export function useNavigation() {
  const [route, setRoute] = useState(() => parseRoute(window.location.hash));
  const [visited, setVisited] = useState<Set<View>>(() => new Set([route.view]));
  useEffect(() => {
    const restoreScroll = window.history.state?.eleccionesScroll ?? 0;
    let frame = 0, attempts = 0;
    const restore = () => {
      window.scrollTo(0, restoreScroll);
      if (++attempts < 30 && Math.abs(window.scrollY - restoreScroll) > 2) frame = requestAnimationFrame(restore);
    };
    frame = requestAnimationFrame(restore);
    return () => cancelAnimationFrame(frame);
  }, [route]);
  useEffect(() => {
    window.history.replaceState({ ...window.history.state, elecciones: true }, "", routeHash(parseRoute(window.location.hash)));
    const restore = () => {
      const next = parseRoute(window.location.hash);
      setRoute(next);
      setVisited((seen) => new Set([...seen, next.view]));
    };
    window.addEventListener("popstate", restore);
    window.addEventListener("hashchange", restore);
    return () => {
      window.removeEventListener("popstate", restore);
      window.removeEventListener("hashchange", restore);
    };
  }, []);
  function navigate(next: Route) {
    const hash = routeHash(next);
    if (window.location.hash !== hash) {
      window.history.replaceState({ ...window.history.state, eleccionesScroll: window.scrollY }, "");
      window.history.pushState({ elecciones: true, eleccionesScroll: 0 }, "", hash);
    }
    setRoute(next);
    setVisited((seen) => new Set([...seen, next.view]));
  }
  return { route, visited, navigate };
}
