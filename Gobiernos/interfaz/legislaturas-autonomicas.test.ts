import { expect, it } from "vitest";
import { institutions } from "./norte-model";
import type { CatalanGovernment, CatalanParliament } from "./catalonia-model";
import {
  legislatureChronology,
  legislatureLibrary,
  regionalPosition,
} from "./legislaturas-autonomicas";

const governments = import.meta.glob<CatalanGovernment>(
  "../Autonomías/*/Gobierno/*/composicion.json",
  { eager: true, import: "default" },
);
const parliaments = import.meta.glob<CatalanParliament>(
  "../Autonomías/*/Parlamento/*/composicion.json",
  { eager: true, import: "default" },
);
function library(territory: string) {
  const data = institutions(
    Object.fromEntries(
      Object.entries(governments).filter(([path]) =>
        path.includes(`/${territory}/`),
      ),
    ),
    Object.fromEntries(
      Object.entries(parliaments).filter(([path]) =>
        path.includes(`/${territory}/`),
      ),
    ),
  );
  const chronology = legislatureChronology(
    data.governmentChronology,
    data.governments,
    data.parliaments,
  );
  return {
    data,
    chronology,
    library: legislatureLibrary(chronology, data.parliaments),
  };
}

it("usa ordinales parlamentarios compactos en los diecinueve territorios sin perder instantáneas", () => {
  const territories = new Set(
    Object.keys(governments).map((p) => p.split("/")[2]),
  );
  expect(territories.size).toBe(19);
  for (const territory of territories) {
    const result = library(territory);
    expect(result.library.flatMap((p) => p.steps)).toHaveLength(
      result.chronology.length,
    );
    expect(new Set(result.library.map((p) => p.id)).size).toBe(
      result.library.length,
    );
    for (const p of result.library)
      expect(p.label, territory).toMatch(
        /^(?:[IVXLCDM]+(?:–[IVXLCDM]+)?|Provisional|Foral)$/,
      );
    for (const step of result.data.governmentChronology)
      expect(result.chronology.some((s) => s.id === step.id)).toBe(true);
    for (const p of result.data.parliaments) {
      expect(
        legislatureLibrary(
          result.data.parliamentChronology,
          result.data.parliaments,
        ).some((r) => r.id === p.id),
        `${territory}: ${p.label}`,
      ).toBe(true);
    }
  }
});
it("reúne los relevos de una legislatura y conserva las legislaturas sin nueva investidura", () => {
  const baleares = library("Illes Balears");
  const fourth = baleares.library.find((p) => p.label === "IV")!;
  expect(
    new Set(fourth.steps.map((s) => s.period.id)).size,
  ).toBeGreaterThanOrEqual(3);
  const aragon = library("Aragón").library;
  expect(
    aragon
      .find((p) => p.label === "III")!
      .steps.some((s) => s.period.id === "aragon-gobierno-1995-01-18"),
  ).toBe(true);
  const madrid = library("Madrid").library;
  expect(madrid.some((p) => p.label === "VI")).toBe(true);
  expect(madrid.some((p) => p.label === "VII")).toBe(true);
  const catalonia = library("Cataluña");
  expect(catalonia.library.some((p) => p.label === "XIII–XIV")).toBe(true);
  const twelfth = catalonia.library.find((p) => p.label === "XII")!;
  expect(twelfth.steps.some((s) => s.date === "2020-09-30")).toBe(true);
});
it("recupera la etapa gubernamental del mapa sin saltar al gobierno actual", () => {
  const { chronology } = library("Illes Balears");
  expect(
    chronology[regionalPosition(chronology, "at-1996-07-01")].period.id,
  ).toBe("baleares-gobierno-1996-06-17");
  const legacy = "baleares-gobierno-1995-07-31-1995-07-31";
  expect(chronology[regionalPosition(chronology, legacy)].id).toBe(legacy);
});
