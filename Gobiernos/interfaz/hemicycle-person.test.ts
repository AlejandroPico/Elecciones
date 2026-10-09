import { describe, expect, it } from "vitest";
import {
  compactGroupLabel,
  memberConstituency,
  memberParty,
} from "./hemicycle-person";
import type { Person } from "../../Políticos/interfaz/datos/tipos";

const source = {
  label: "Ficha institucional",
  url: "https://example.org/ficha?legis=15",
};
const affiliation = (
  name: string,
  period?: string,
  kind: "membership" | "association" = "membership",
): NonNullable<Person["affiliations"]>[number] => ({
  organization: null,
  name,
  period,
  kind,
  source,
});
describe("Ficha breve del hemiciclo", () => {
  it("separa el partido de la coalición con la que se presentó", () => {
    expect(
      memberParty(
        { source: source.url, formation: "Sumar" },
        {
          affiliations: [
            affiliation("Podemos", "desde 2014"),
            affiliation("Sumar", "2023-08-11 — 2026-10-06", "association"),
          ],
        },
        "2026-10-05",
      ),
    ).toEqual({ label: "Partido", name: "Podemos" });
  });
  it("no proyecta una afiliación posterior sobre un mandato histórico", () => {
    const person = {
      affiliations: [
        affiliation("AP", "1980 — 1988"),
        affiliation("PP", "desde 1989"),
      ],
    };
    expect(memberParty({ source: "" }, person, "1986-06-22")?.name).toBe("AP");
    expect(memberParty({ source: "" }, person, "1996-03-03")?.name).toBe("PP");
  });
  it("distingue afiliación sin fechas y candidatura; no inventa un partido", () => {
    expect(
      memberParty(
        { source: "" },
        { affiliations: [affiliation("PSC")] },
        "1980-03-20",
      )?.label,
    ).toBe("Afiliación documentada");
    expect(
      memberParty(
        { source: "", formation: "Coalición" },
        undefined,
        "2026-10-05",
      )?.label,
    ).toBe("Candidatura");
    expect(
      memberParty({ source: "" }, undefined, "2026-10-05"),
    ).toBeUndefined();
  });
  it("obtiene el origen del Senado de la ficha de esa misma legislatura", () => {
    const person = {
      senateMandates: [
        {
          title:
            "Mandato en el Senado · XV · Electa:  Fuerteventura (LAS PALMAS) .",
          period: "2023 — 2026",
          source,
        },
      ],
    };
    expect(memberConstituency({ source: source.url }, person)).toBe(
      "Fuerteventura (LAS PALMAS)",
    );
    expect(
      memberConstituency(
        { source: source.url, constituency: "Madrid" },
        person,
      ),
    ).toBe("Madrid");
    expect(
      memberConstituency({ source: "otra legislatura" }, person),
    ).toBeUndefined();
  });
  it("compacta la etiqueta conservando la identidad del grupo", () => {
    expect(compactGroupLabel("GRUPO PARLAMENTARIO MIXTO (GPMX )")).toBe(
      "MIXTO",
    );
    expect(
      compactGroupLabel(
        "GRUPO PARLAMENTARIO VASCO EN EL SENADO (EAJ-PNV) (GPV )",
      ),
    ).toBe("VASCO (EAJ-PNV)");
    expect(compactGroupLabel("Junts per Catalunya")).toBe(
      "Junts per Catalunya",
    );
  });
});
