import { createHash } from "node:crypto";
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { expect, it } from "vitest";
import audit from "../revisiones/2026-10-08/informe.json";
import preservation from "../revisiones/2026-10-08/conservacion.json";
import { people, portraits, findPerson, organizations } from "./datos/catalogo";
import { matchesAffiliation } from "./vinculaciones";
import { matchesPerson } from "./orden";

it("la revisión conserva las identidades y los recursos anteriores al reunir duplicados", () => {
  for (const id of preservation.originalIds) {
    const person = findPerson(id);
    expect(person, id).toBeTruthy();
    expect(
      audit.records.some(
        (r) => r.id === person!.id && r.previousIds.includes(id),
      ),
    ).toBe(true);
  }
  const identifiers = people.flatMap((p) => [p.id, ...(p.legacyIds ?? [])]);
  expect(new Set(identifiers).size).toBe(identifiers.length);
  const wikidata = people.map((p) => p.wikidata).filter(Boolean);
  expect(new Set(wikidata).size).toBe(wikidata.length);
  for (const resource of preservation.resources) {
    const person = findPerson(resource.person)!;
    const folder = join(process.cwd(), "Políticos", person.fullName!);
    const hashes = readdirSync(folder)
      .filter((name) => !name.endsWith(".json"))
      .map((name) =>
        createHash("sha256")
          .update(readFileSync(join(folder, name)))
          .digest("hex"),
      );
    expect(hashes, `${person.name}: ${resource.file}`).toContain(
      resource.sha256,
    );
  }
});

it("las fotografías y vinculaciones revisadas tienen recursos y fuentes individuales", () => {
  for (const person of people) {
    expect(portraits[person.id], person.name).toBeTruthy();
    expect(person.photoCredit, person.name).toBeTruthy();
    expect(new URL(person.photoSource!).protocol).toBe("https:");
    for (const affiliation of person.affiliations ?? []) {
      expect(new URL(affiliation.source.url).protocol).toBe("https:");
      if (affiliation.organization)
        expect(
          organizations.some((p) => p.id === affiliation.organization),
        ).toBe(true);
    }
  }
});

it("los filtros encuentran cambios de partido y sus federaciones regionales", () => {
  const abascal = findPerson("santiago-abascal")!;
  expect(matchesAffiliation(abascal, "pp")).toBe(true);
  expect(matchesAffiliation(abascal, "vox")).toBe(true);
  expect(matchesAffiliation(findPerson("juan-manuel-moreno")!, "pp")).toBe(
    true,
  );
  expect(
    matchesAffiliation(findPerson("joan-clos-i-matheu")!, "registro-351"),
  ).toBe(true);
  expect(
    people.filter((p) => matchesAffiliation(p, "pp")).length,
  ).toBeGreaterThan(40);
  expect(
    people.filter((p) => matchesAffiliation(p, "psoe")).length,
  ).toBeGreaterThan(50);
});

it("una candidatura independiente no se transforma en militancia y un dato desconocido no se inventa", () => {
  const mariscal = findPerson("margarita-mariscal-de-gante-y-miron")!;
  expect(mariscal.affiliationStatus).toBe("independent");
  expect(matchesAffiliation(mariscal, "pp")).toBe(true);
  expect(
    mariscal.affiliations?.find((a) => a.organization === "pp")?.kind,
  ).toBe("association");
  expect(findPerson("mateos")?.affiliationStatus).toBe("pending");
  expect(findPerson("sanchez-martinez")?.birthDate).toBeFalsy();
});

it("las correcciones conservan nombres habituales, estudios acreditados y fechas contrastadas", () => {
  expect(findPerson("jose-guirao")?.education?.join(" ")).toContain(
    "Licenciatura en Filología Hispánica",
  );
  expect(findPerson("jose-guirao")?.education?.join(" ")).not.toMatch(
    /doctorado/i,
  );
  expect(findPerson("jose-barrionuevo-pena")?.birthDate).toBe("1942-03-13");
  expect(findPerson("enrique-mugica-herzog")?.deathDate).toBe("2020-04-11");
  expect(findPerson("mateos")?.birthDate).toBe("1962-10-13");
  expect(findPerson("carmen-calvo-poyato")?.id).toBe(
    "maria-del-carmen-calvo-poyato",
  );
  expect(
    matchesPerson(findPerson("valeriano-gomez-sanchez")!, "Valeriano Gómez"),
  ).toBe(true);
  const moreno = findPerson("juan-manuel-moreno")!;
  expect(
    moreno.timeline.some(
      (t) =>
        t.title === "Diputado en las Cortes Generales por Cantabria" &&
        t.period.includes("2000"),
    ),
  ).toBe(true);
  expect(
    moreno.timeline.find(
      (t) => t.title === "Diputado en las Cortes Generales por Málaga",
    )?.period,
  ).not.toContain("Cantabria");
  expect(
    people.every((p) =>
      p.timeline.every((t) => !["Familia", "Educación"].includes(t.title)),
    ),
  ).toBe(true);
});
