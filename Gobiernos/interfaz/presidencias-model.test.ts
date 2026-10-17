import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import {
  cabinetFor,
  durationLabel,
  eventKind,
  eventTopics,
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
  it("conserva registros canónicos y muestra sus vínculos sin repetirlos dentro de una etapa", () => {
    const stageIds = [
      ...presidencies.flatMap((p) => p.stages),
      "pre-arias",
      "pre-santiago",
    ];
    expect(new Set(stageIds).size).toBe(stages.length);
    expect(stageIds.sort()).toEqual(stages.map((s) => s.id).sort());
    const visible = stageIds.flatMap((id) => eventsFor(id));
    expect(new Set(visible.map((e) => e.id)).size).toBe(events.length);
    expect(new Set(events.map((e) => e.id)).size).toBe(events.length);
    for (const id of stageIds) {
      const local = eventsFor(id);
      expect(new Set(local.map((e) => e.id)).size).toBe(local.length);
      expect(local.map((e) => e.date)).toEqual(
        local
          .map((e) => e.date)
          .sort()
          .reverse(),
      );
      expect(eventsFor(id, true)).toEqual([...local].reverse());
    }
    for (const event of visible) {
      expect(event.sources.length).toBeGreaterThan(0);
      for (const id of event.sources)
        expect(sources[id]?.url).toMatch(/^https:\/\//);
    }
  });
  it("muestra Filesa en origen y resolución conservando la atribución y el amparo parcial", () => {
    const filesa = eventsFor("iii-gonzalez").filter(
      (e) => e.caseId === "filesa",
    );
    const amparo = filesa.find((e) => e.id === "2001-06-04-filesa-amparo")!;
    expect(judicialLabel(amparo)).toBe("Condena por falsedad anulada");
    expect(eventsFor("vi-aznar").some((e) => e.caseId === "filesa")).toBe(true);
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
  it("separa el catálogo del BOE del análisis editorial y conserva fuentes originales", () => {
    const norms = events.filter((e) => e.boeId);
    expect(norms.length).toBeGreaterThan(3000);
    expect(events.length).toBeGreaterThan(3200);
    expect(
      norms.some(
        (e) =>
          e.date.startsWith("1978") &&
          e.title
            .toLocaleLowerCase("es")
            .includes("derogación de la ley 41/1975"),
      ),
    ).toBe(true);
    for (const norm of norms) {
      expect(eventKind(norm)).toBe("legislation");
      expect(norm.date <= researchDate).toBe(true);
      expect(sources[norm.sources[0]].url).toContain(norm.boeId);
      expect(norm.verification).toBe("metadatos-oficiales-boe");
      expect(eventTopics(norm).length).toBeGreaterThan(0);
    }
  });
  it("permite consultar los hechos compartidos y la crisis de investiduras sin mezclar responsabilidades", () => {
    for (const id of ["ix-zapatero", "xiv-sanchez", "xv-sanchez"]) {
      expect(
        eventsFor(id).some((e) => e.id === "2026-05-19-plus-ultra-zapatero"),
      ).toBe(true);
    }
    expect(
      eventsFor("xii-rajoy").some(
        (e) => e.id === "2018-05-24-guertel-audiencia",
      ),
    ).toBe(true);
    expect(eventsFor("xi-rajoy").length).toBeGreaterThan(4);
    const david = events.find((e) => e.id === "2026-07-14-david-sentencia")!;
    expect(david.summary).toContain("absolvió de tráfico de influencias");
    expect(judicialLabel(david)).toContain("no firme");
    const plus = events.find((e) => e.id === "2026-05-19-plus-ultra-zapatero")!;
    expect(
      plus.displayStages?.find((link) => link.stage === "ix-zapatero")?.reason,
    ).toContain("después");
  });
  it("distingue el año del salario mínimo y su publicación, sin convertir la mensualidad en salario neto", () => {
    const wage = events.find((e) => e.id === "2026-02-19-smi-2026")!;
    expect(wage.title).toContain("1 221 euros");
    expect(wage.date).toBe("2026-02-19");
    expect(eventKind(wage)).toBe("balance");
    expect(wage.attribution).toContain("no demuestra por sí sola");
    const old = events.find((e) => e.id === "1998-12-30-smi-1999")!;
    expect(old.title).toContain("69.270 pesetas");
    expect(old.stage).toBe("vi-aznar");
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
