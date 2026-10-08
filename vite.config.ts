/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { partyCatalogPlugin } from "./Partidos/interfaz/lectura";
import { personCatalogPlugin } from "./Políticos/interfaz/lectura";
export default defineConfig({
  plugins: [react(), partyCatalogPlugin(), personCatalogPlugin()],
  base: "./",
  test: { maxWorkers: 1, isolate: false },
});
