import React from "react";
import ReactDOM from "react-dom/client";
import App from "./app/App";
import "@fontsource-variable/dm-sans/wght.css";
import "@fontsource-variable/manrope/wght.css";
import "./app/styles.css";
import "../Políticos/interfaz/archive.css";
import "./app/refinement.css";
import "../Gobiernos/interfaz/governments.css";
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
import "../Elecciones/interfaz/cuestionario/Progress.css";

import "../Partidos/interfaz/partidos.css";
