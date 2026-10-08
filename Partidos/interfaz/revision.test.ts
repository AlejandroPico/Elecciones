import { expect, it } from "vitest";
import { organizations, logos } from "./catalogo";
import { compareParties } from "./orden";

it("ordena por el resultado documentado y mantiene separadas las coaliciones y sus integrantes", () => {
  const parties = new Map(organizations.map((p) => [p.id, p]));
  const results = organizations.flatMap((p) => p.electoralResults ?? []).filter((r) => r.date === "2023-07-23" && r.chamber === "congreso");
  expect(results.reduce((sum, r) => sum + (r.seats ?? 0), 0)).toBe(350);
  expect(results).toHaveLength(59);
  expect(parties.get("sumar-coalicion-2023")?.electoralResults?.[0].seats).toBe(31);
  expect(parties.get("sumar")?.electoralResults?.length ?? 0).toBe(0);
  expect(logos["sumar-coalicion-2023"]).toBeTruthy();
  expect([...organizations].sort(compareParties("representation"))[0].id).toBe("pp");
});

it("conserva documentos de programas, estatutos e historia y no transfiere identidades homónimas", () => {
  expect(Object.keys(logos).length).toBeGreaterThan(250);
  const resources = organizations.flatMap((p) => p.publicResources ?? []);
  for (const kind of ["programa", "estatutos", "historia"]) expect(resources.some((r) => r.kind === kind)).toBe(true);
  for (const r of resources) expect(["https:", "http:"]).toContain(new URL(r.url).protocol);
  const reused = organizations.find((p) => p.id === "registro-1250")!;
  expect(reused.founding).toBeUndefined();
  expect(reused.wikidata).toBeUndefined();
  for (const p of organizations) for (const date of [p.founding, p.dissolution]) if (date) expect(Number(date.date.slice(0, 4))).toBeGreaterThanOrEqual(1800);
});
