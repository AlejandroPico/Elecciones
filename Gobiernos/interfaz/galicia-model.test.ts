import { expect, it } from "vitest";
import { galicianInstitutions as galicia } from "./galicia-model";
import {
  archivedGroups,
  catalanGroupsAt,
  catalanTermAt,
} from "./catalonia-model";
import { congressGroupColor } from "./congress-model";
import {
  findPerson,
  people,
  portraits,
} from "../../Políticos/interfaz/datos/catalogo";
import audit from "../../Políticos/revisiones/2026-10-16-galicia/informe.json";
import conservation from "../revisiones/2026-10-16-galicia/conservacion.json";

it("conserva el catálogo y resuelve las doce legislaturas y catorce etapas presidenciales", () => {
  expect(people.length).toBeGreaterThanOrEqual(audit.totalPeople);
  expect(audit.baselinePeople).toBe(11556);
  for (const id of conservation.baselineIds)
    expect(findPerson(id), id).toBeTruthy();
  expect(galicia.parliaments).toHaveLength(12);
  expect(galicia.governments).toHaveLength(14);
  expect(galicia.governments.at(-1)!.start).toBe("1982-01-12");
  expect(galicia.governments[0].start).toBe("2024-04-11");
  for (const period of [...galicia.parliaments, ...galicia.governments]) {
    const records =
      "records" in period
        ? [...period.records, ...period.board, ...(period.archiveBoard ?? [])]
        : [...period.terms, ...(period.archiveTerms ?? [])];
    for (const r of records) {
      expect(findPerson(r.person), r.name).toBeTruthy();
      expect(r.source, r.name).toMatch(/^https:\/\//);
      expect(r.name).not.toMatch(/Cargo:|\*|�|María de la González/);
      if (r.start && r.end) expect(r.start < r.end, r.name).toBe(true);
    }
    if ("records" in period) {
      const deputies = new Set(period.records.map((r) => r.person));
      for (const member of [...period.board, ...(period.archiveBoard ?? [])])
        expect(deputies.has(member.person), member.name).toBe(true);
    }
  }
});

it("reconstruye los 71 o 75 escaños y separa los relevos del hemiciclo archivado", () => {
  for (const period of galicia.parliaments) {
    const members = period.currentOnly
      ? catalanGroupsAt(period, period.checkedAt).flatMap((g) => g.members)
      : archivedGroups(period).flatMap((g) => g.members);
    expect(members, period.id).toHaveLength(period.capacity!);
    expect(new Set(members.map((m) => m.person)).size).toBe(period.capacity);
    expect(new Set(period.records.map((m) => m.person)).size).toBe(
      period.records.length,
    );
    if (!period.currentOnly) {
      expect(period.nominalOnly).toBe(true);
      expect(period.groups).toHaveLength(0);
      expect(
        period.records.every((m) => m.start === null && m.end === null),
      ).toBe(true);
      expect(period.archiveBoard!.length).toBeGreaterThanOrEqual(5);
    }
  }
  const first = galicia.parliaments.at(-1)!;
  expect(first.capacity).toBe(71);
  expect(
    galicia.parliaments.find((p) => p.label === "Legislatura II")!.capacity,
  ).toBe(71);
  const ninth = galicia.parliaments.find((p) => p.label === "Legislatura IX")!;
  expect(ninth.archivedComposition!.note).toContain("proclamados electos");
  expect(ninth.archivedComposition!.source).toContain("20121107");
  const eleventh = galicia.parliaments.find(
    (p) => p.label === "Legislatura XI",
  )!;
  expect(
    archivedGroups(eleventh)
      .map((g) => g.members.length)
      .sort((a, b) => a - b),
  ).toEqual([14, 19, 42]);
  expect(
    archivedGroups(eleventh)
      .find((g) => /Socialistas/.test(g.name))!
      .members.some((m) => m.name === "Martín Seco García"),
  ).toBe(true);
});

it("ofrece todos los retratos vigentes y refleja los relevos de la Mesa y de Mar", () => {
  const chamber = galicia.parliaments[0];
  const executive = galicia.governments[0];
  const date = executive.checkedAt;
  const cabinet = executive.terms.filter((m) =>
    m.observedAt ? m.observedAt === date : catalanTermAt(m, date),
  );
  expect(chamber.currentOnly).toBe(true);
  expect(chamber.records).toHaveLength(75);
  expect(chamber.board).toHaveLength(5);
  expect(cabinet).toHaveLength(13);
  for (const m of [...chamber.records, ...chamber.board, ...cabinet])
    expect(portraits[m.person], m.name).toBeTruthy();
  expect(chamber.board.find((m) => /1ª/.test(m.role))!.name).toBe(
    "Raquel Arias Rodríguez",
  );
  expect(cabinet.find((m) => /do Mar/.test(m.role))!.name).toBe(
    "Marta Villaverde Acuña",
  );
  expect(cabinet.some((m) => m.name === "Alfonso Villares Bermúdez")).toBe(
    false,
  );
  expect(
    catalanGroupsAt(chamber, date)
      .map((g) => g.members.length)
      .sort((a, b) => a - b),
  ).toEqual([1, 9, 25, 40]);
  expect(catalanGroupsAt(chamber, "2024-03-18")).toHaveLength(0);
  expect(findPerson("galicia-armando-ojea-bouzo")!.birth).toBe(
    "Vilar de Barrio · 1962",
  );
  expect(findPerson("galicia-armando-ojea-bouzo")!.birthDate).toBeFalsy();
  expect(audit.portraitErrors).toHaveLength(0);
});

it("muestra los nombramientos de consellerías solo en las instantáneas acreditadas", () => {
  for (const government of galicia.governments) {
    for (const term of government.terms.filter((m) => m.observedAt)) {
      expect(term.start).toBeNull();
      expect(term.end).toBeNull();
      expect(
        galicia.governmentChronology.some(
          (s) => s.period.id === government.id && s.date === term.observedAt,
        ),
      ).toBe(true);
    }
    if (government.preferredDate)
      expect(
        galicia.governmentChronology.some(
          (s) =>
            s.period.id === government.id &&
            s.date === government.preferredDate,
        ),
      ).toBe(true);
  }
  const tourino = galicia.governments.find((p) => p.start.startsWith("2005"))!;
  const health = tourino.terms.find((m) => /Rubio/.test(m.name))!;
  expect(health.name).toBe("María José Rubio Vidal");
  expect(
    findPerson(health.person)!.references.some((s) =>
      s.url.includes("20050805/Anuncio1C19A"),
    ),
  ).toBe(true);
  const oldest = galicia.governments.at(-1)!;
  expect(oldest.archiveTerms!.length).toBeGreaterThan(10);
  expect(
    oldest.archiveTerms!.every((m) => m.start === null && m.end === null),
  ).toBe(true);
  const solla = galicia.parliaments
    .find((p) => p.label === "Legislatura X")!
    .archiveBoard!.find((m) => /Solla/.test(m.name))!;
  expect(solla.name).toBe("Eva Solla Fernández");
  expect(findPerson("galicia-eva-solla-gonzalez")!.id).toBe(solla.person);
  expect(congressGroupColor("Bloque Nacionalista Galego")).not.toBe("#9199a8");
  expect(congressGroupColor("En Marea")).not.toBe("#9199a8");
});
