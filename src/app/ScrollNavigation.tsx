import { useEffect, useRef, useState, type ReactNode } from "react";
import { ChevronDown, ChevronUp } from "lucide-react";

/** El desplazamiento sigue siendo nativo: rueda, pantalla táctil y teclado. */
export default function ScrollNavigation({
  children,
}: {
  children: ReactNode;
}) {
  const viewport = useRef<HTMLElement>(null);
  const content = useRef<HTMLDivElement>(null);
  const [edges, setEdges] = useState({ above: false, below: false });
  function update() {
    const el = viewport.current;
    if (!el) return;
    const above = el.scrollTop > 2;
    const below = el.scrollTop + el.clientHeight < el.scrollHeight - 2;
    setEdges((old) =>
      old.above === above && old.below === below ? old : { above, below },
    );
  }
  useEffect(() => {
    const observer = new ResizeObserver(update);
    observer.observe(viewport.current!);
    observer.observe(content.current!);
    update();
    return () => observer.disconnect();
  }, []);
  function move(direction: number) {
    const el = viewport.current!;
    const reduced = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    el.scrollBy({
      top: direction * el.clientHeight * 0.65,
      behavior: reduced ? "instant" : "smooth",
    });
  }
  return (
    <div
      className={`navigation-scroll ${edges.above ? "has-above" : ""} ${edges.below ? "has-below" : ""}`}
    >
      <nav
        ref={viewport}
        className="main-nav"
        aria-label="Secciones"
        tabIndex={0}
        onScroll={update}
      >
        <div ref={content} className="navigation-scroll-content">
          {children}
        </div>
      </nav>
      {edges.above && (
        <button
          className="navigation-scroll-hint above"
          aria-label="Ver secciones anteriores"
          onClick={() => move(-1)}
        >
          <ChevronUp size={15} />
        </button>
      )}
      {edges.below && (
        <button
          className="navigation-scroll-hint below"
          aria-label="Ver más secciones"
          onClick={() => move(1)}
        >
          <ChevronDown size={15} />
        </button>
      )}
    </div>
  );
}
