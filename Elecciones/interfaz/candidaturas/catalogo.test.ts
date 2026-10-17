import { expect, it } from "vitest";
import { organizations, logos } from "../../../Partidos/interfaz/catalogo";
import {
  documentUrl,
  documentsFor,
  electionResearch,
  electoralDocuments,
  matchesScope,
  participationFor,
} from "./catalogo";

it("resuelve las entidades y las marcas de los anuncios sin convertirlos en listas proclamadas", () => {
  expect(new Set(electionResearch.entries.map((entry) => entry.id)).size).toBe(
    electionResearch.entries.length,
  );
  for (const entry of electionResearch.entries) {
    expect(organizations.some((party) => party.id === entry.organization)).toBe(
      true,
    );
    expect(logos[entry.organization]).toBeTruthy();
    expect(entry.status).not.toBe("proclaimed");
    for (const source of entry.sources)
      expect(new URL(source.url).protocol).toBe("https:");
  }
  expect(
    electionResearch.entries.find((entry) => entry.id === "alianca-catalana")
      ?.status,
  ).toBe("not-running");
  expect(
    electionResearch.entries.find((entry) => entry.id === "escanos-en-blanco")
      ?.status,
  ).toBe("preparing");
});

it("filtra cámara y territorio sin certificar papeletas de ámbito desconocido", () => {
  const canarias = electionResearch.entries.find(
    (entry) => entry.id === "cc-primero-canarias",
  )!;
  expect(matchesScope(canarias, "congreso", "Las Palmas")).toBe(true);
  expect(matchesScope(canarias, "senado", "Las Palmas")).toBe(false);
  expect(matchesScope(canarias, "senado", "Gran Canaria")).toBe(true);
  expect(matchesScope(canarias, "congreso", "Madrid")).toBe(false);
  expect(
    matchesScope(
      electionResearch.entries.find((entry) => entry.id === "frente-amplio")!,
      "congreso",
      "Barcelona",
    ),
  ).toBe(true);
  expect(
    matchesScope(
      electionResearch.entries.find((entry) => entry.id === "podemos")!,
      "congreso",
      "Madrid",
    ),
  ).toBe(true);
  expect(
    matchesScope(
      electionResearch.entries.find((entry) => entry.id === "psoe")!,
      "congreso",
      "Madrid",
    ),
  ).toBe(false);
  expect(participationFor("upn").some((entry) => entry.id === "pp-upn")).toBe(
    true,
  );
  expect(
    matchesScope(
      electionResearch.entries.find((entry) => entry.id === "d21")!,
      "senado",
      "Madrid",
    ),
  ).toBe(false);
});

it("sirve originales locales y conserva la elección de los antecedentes y la procedencia de los espejos", () => {
  expect(electoralDocuments.length).toBeGreaterThan(10);
  for (const document of electoralDocuments) {
    expect(documentUrl(document)).toBeTruthy();
    expect(document.sha256).toMatch(/^[a-f0-9]{64}$/);
    expect(document.scoringEligible).toBe(false);
    if (document.kind === "historical") {
      expect(document.electionDate).toBe("2023-07-23");
      expect(document.file.startsWith("Generales Julio 2023/")).toBe(true);
    }
    if (document.sourceKind === "mirror")
      expect(document.downloadedFrom).not.toBe(document.source);
  }
  expect(documentsFor("psoe")[0].sourceKind).toBe("mirror");
  expect(documentsFor("registro-4086")[0].kind).toBe("permanent");
});
