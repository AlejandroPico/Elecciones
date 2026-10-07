/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { partyCatalogPlugin } from "./Partidos/interfaz/lectura";
export default defineConfig({
  plugins: [react(), partyCatalogPlugin()],
  base: "./",
  test: { maxWorkers: 1, isolate: false },
});
