import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import {
  cabinetFor,
  durationLabel,
  eventKind,
  events,
  eventsFor,
  judicialLabel,
  matchesEvent,
  presidencies,
  researchDate,
  researchDateLabel,
  sources,
  stages,
  stagesFor,
  timelinePosition,
} from "./presidencias-model";

describe("histórico documentado de presidencias", () => {
  it("conserva todos los hechos una sola vez, incluidos contexto y resoluciones posteriores", () => {
    const stageIds = [
      ...presidencies.flatMap((p) => p.stages),
      "pre-arias",
      "pre-santiago",
    ];
    expect(new Set(stageIds).size).toBe(stages.length);
    expect(stageIds.sort()).toEqual(stages.map((s) => s.id).sort());
    const visible = stageIds.flatMap(eventsFor);
    expect(new Set(visible.map((e) => e.id)).size).toBe(events.length);
    expect(visible.map((e) => e.id).sort()).toEqual(
      events.map((e) => e.id).sort(),
    );
    for (const event of visible) {
      expect(event.sources.length).toBeGreaterThan(0);
      for (const id of event.sources)
        expect(sources[id]?.url).toMatch(/^https:\/\//);
    }
  });
  it("mantiene Filesa y su amparo en la época de origen, sin atribuirlos al presidente de la sentencia", () => {
    const filesa = eventsFor("iii-gonzalez").filter(
      (e) => e.caseId === "filesa",
    );
    expect(filesa).toHaveLength(2);
    expect(filesa.map((e) => e.stageAtMilestone)).toEqual([
      "vi-aznar",
      "vii-aznar",
    ]);
    expect(judicialLabel(filesa[1])).toBe("Condena por falsedad anulada");
    expect(eventsFor("vi-aznar").some((e) => e.caseId === "filesa")).toBe(
      false,
    );
  });
  it("no transforma la responsabilidad civil del PP ni una investigación en condenas de la presidencia", () => {
    const guertel = events.find((e) => e.caseId === "guertel-primera-epoca")!;
    expect(judicialLabel(guertel)).toBe(
      "Condenas individuales y responsabilidad civil",
    );
    const investigation = events.find(
      (e) => e.id === "2025-06-27-cerdan-investigacion",
    )!;
    expect(judicialLabel(investigation)).toBe(
      "Investigación · actualización pendiente",
    );
    expect(investigation.statusAtSource).toBe("2025-06-27");
    const masks = events.filter((e) => e.caseId === "koldo-mascarillas");
    expect(masks).toHaveLength(2);
    expect(masks.every((e) => e.caseId !== investigation.caseId)).toBe(true);
  });
  it("resuelve las dos presidencias de I y XII hacia sus composiciones correspondientes", () => {
    expect(cabinetFor("i-suarez", "adolfo-suarez-gonzalez")).toBeTruthy();
    expect(
      cabinetFor("i-calvo-sotelo", "leopoldo-calvo-sotelo-y-bustelo"),
    ).toBeTruthy();
    expect(cabinetFor("i-suarez", "adolfo-suarez-gonzalez")).not.toBe(
      cabinetFor("i-calvo-sotelo", "leopoldo-calvo-sotelo-y-bustelo"),
    );
    expect(cabinetFor("xii-rajoy", "rajoy")).not.toBe(
      cabinetFor("xii-sanchez", "sanchez"),
    );
    expect(cabinetFor("pre-suarez", "adolfo-suarez-gonzalez")).toBeUndefined();
  });
  it("enlaza siete identidades y sus retratos existentes sin copiar las biografías", () => {
    expect(presidencies).toHaveLength(7);
    for (const p of presidencies) {
      const base = new URL(`../../Políticos/${p.folder}/`, import.meta.url);
      const meta = JSON.parse(
        readFileSync(new URL("ficha.json", base), "utf8"),
      );
      const image = JSON.parse(
        readFileSync(new URL("retrato.json", base), "utf8"),
      );
      expect(meta.id).toBe(p.person);
      expect(readFileSync(new URL(image.file, base)).length).toBeGreaterThan(
        100,
      );
      expect(stagesFor(p.person).length).toBe(p.stages.length);
    }
  });
  it("respeta fechas mensuales y anuales sin inventar días", () => {
    expect(researchDateLabel("2002-11")).toBe("noviembre de 2002");
    expect(researchDateLabel("1981")).toBe("1981");
    expect(researchDateLabel("2025-06-26")).toContain("26");
    expect(durationLabel("2018-06-01", "2026-10-17")).toBe("8 años y 4 meses");
    expect(durationLabel("1976-07-01", "1976-07-03")).toBe("2 días");
  });
  it("representa tiempo real hasta el corte documental sin convertirlo en un saldo político", () => {
    for (const p of presidencies) {
      const position = timelinePosition(p.from, p.until ?? researchDate);
      expect(position.left).toBeGreaterThanOrEqual(0);
      expect(position.width).toBeGreaterThan(0);
      expect(position.left + position.width).toBeLessThanOrEqual(100.00001);
    }
    const last = presidencies.at(-1)!;
    const position = timelinePosition(last.from, researchDate);
    expect(position.left + position.width).toBeCloseTo(100);
  });
  it("combina búsqueda sin tildes y categoría, conservando las anulaciones y los resultados mixtos", () => {
    const partial = events.find((e) => e.id === "2025-06-26-amnistia-tc")!;
    expect(eventKind(partial)).toBe("balance");
    expect(matchesEvent(partial, "constitucional amnistia", "balance")).toBe(
      true,
    );
    expect(matchesEvent(partial, "amnistia", "scandal")).toBe(false);
    const amparo = events.find((e) => e.id === "2001-06-04-filesa-amparo")!;
    expect(matchesEvent(amparo, "sala", "scandal")).toBe(true);
    expect(
      events.filter((e) =>
        matchesEvent(e, "sin coincidencias deliberadamente", "all"),
      ),
    ).toHaveLength(0);
  });
});
