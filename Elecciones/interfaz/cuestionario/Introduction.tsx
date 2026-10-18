import { useEffect, useState } from "react";
import "./Introduction.css";

export default function Introduction({
  start,
  topics,
  count,
}: {
  start: () => void;
  topics: string[];
  count: number;
}) {
  const [paused, setPaused] = useState(false);
  const [remaining, setRemaining] = useState(12);
  useEffect(() => {
    if (paused) return;
    const timer = setInterval(() => {
      if (!document.hidden) setRemaining((value) => Math.max(0, value - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [paused]);
  useEffect(() => {
    if (remaining === 0) start();
  }, [remaining, start]);
  return (
    <section
      className="survey-introduction"
      aria-labelledby="introduction-title"
    >
      <h1 id="introduction-title">Antes de empezar</h1>
      <p>
        Hasta {count} preguntas · {topics.length} temas
      </p>
      <ul className="introduction-topics">
        {topics.map((title) => (
          <li key={title}>{title}</li>
        ))}
      </ul>
      <ol className="introduction-instructions">
        <li>
          Responde de muy en desacuerdo a muy de acuerdo. También puedes omitir
          una pregunta.
        </li>
        <li>
          Después de responder tienes <strong>tres segundos</strong> para
          ajustar la importancia: normal, alta o esencial. Por defecto es
          normal; cambiarla no reinicia el plazo.
        </li>
        <li>
          Puedes consultar Mi perfil desde la primera respuesta y volver a
          responder cuando quieras. El perfil incluye el cálculo y la cobertura
          documental de cada comparación.
        </li>
      </ol>
      <p className="small-note">
        Puedes volver a cualquier pregunta desde la barra inferior o cambiar de
        tema. Las respuestas se conservan durante esta visita; se pierden al
        recargar o cerrar la página.
      </p>
      <div className="introduction-actions">
        <button
          className="quiet-button"
          aria-pressed={paused}
          onClick={() => setPaused(!paused)}
        >
          {paused ? "Reanudar presentación" : "Pausar presentación"}
        </button>
        <button className="primary-button" onClick={start}>
          Empezar
        </button>
      </div>
      <span className="introduction-time">
        {paused
          ? "Presentación en pausa"
          : `Inicio automático en ${remaining} s`}
      </span>
    </section>
  );
}
