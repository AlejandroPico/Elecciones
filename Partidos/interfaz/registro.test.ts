import { expect, it } from "vitest";
import manifest from "../registro-2026-10-07.json";
import { organizations, logos } from "./catalogo";
it("incluye cada resultado de la consulta oficial una vez, sin convertirlo en candidatura", () => {
  const registered = organizations.filter((p) => p.registration);
  expect(registered).toHaveLength(manifest.total);
  expect(new Set(registered.map((p) => p.registration!.id)).size).toBe(
    manifest.total,
  );
  expect(registered.map((p) => p.registration!.id).sort()).toEqual(
    [...manifest.ids].sort(),
  );
  expect(new Set(organizations.map((p) => p.id)).size).toBe(
    organizations.length,
  );
  for (const p of registered) {
    expect(new URL(p.registration!.source).hostname).toBe("servicio.mir.es");
    expect(p.registration!.date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  }
});
it("resuelve el logo local de UPN y conserva los recursos anteriores", () => {
  for (const id of ["upn", "pp", "psoe", "podemos", "vox", "junts", "erc"])
    expect(logos[id]).toBeTruthy();
  expect(organizations.some((p) => p.fullName === "TERUEL EXISTE")).toBe(true);
  expect(organizations.some((p) => p.fullName === "ALIANÇA CATALANA")).toBe(
    true,
  );
});
