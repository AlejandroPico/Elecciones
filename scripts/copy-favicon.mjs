import { copyFile } from "node:fs/promises";
await copyFile(
  new URL("../favicon.svg", import.meta.url),
  new URL("../dist/favicon.svg", import.meta.url),
);
