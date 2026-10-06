import { categories, questions, VERSION } from "../Elecciones";
export type Answer = { value: number | null; importance: 1 | 2 | 3 };
export type Answers = Record<string, Answer>;
export type Score = { value: number | null; answered: number; total: number };
export type PartyPosition = {
  value: number;
  source: string;
  reference: string;
};
export type Party = {
  id: string;
  name: string;
  color: string;
  positions: Record<string, PartyPosition>;
};
export const axes = categories.flatMap((c) => c.axes);
export function calculate(answers: Answers): Record<string, Score> {
  return Object.fromEntries(
    axes.map((axis) => {
      const items = questions.filter((q) => q.axis === axis.id);
      let sum = 0,
        weight = 0,
        answered = 0;
      for (const q of items) {
        const a = answers[q.id];
        if (a && a.value !== null) {
          sum += (a.value / 2) * q.direction * a.importance;
          weight += a.importance;
          answered++;
        }
      }
      return [
        axis.id,
        {
          value: weight ? (sum / weight) * 100 : null,
          answered,
          total: items.length,
        },
      ];
    }),
  );
}
export function similarity(answers: Answers, party: Party) {
  let sum = 0,
    weight = 0,
    shared = 0;
  const answered = questions.filter((q) => answers[q.id]?.value != null).length;
  for (const q of questions) {
    const a = answers[q.id],
      p = party.positions[q.id];
    if (a?.value != null && p) {
      sum += (Math.abs(a.value - p.value) / 4) * a.importance;
      weight += a.importance;
      shared++;
    }
  }
  return {
    percent: weight ? (1 - sum / weight) * 100 : null,
    shared,
    answered,
  };
}
export function partyScores(party: Party): Record<string, Score> {
  return calculate(
    Object.fromEntries(
      Object.entries(party.positions).map(([id, p]) => [
        id,
        { value: p.value, importance: 1 },
      ]),
    ),
  );
}
export function parseParties(raw: unknown): Party[] {
  if (!raw || typeof raw !== "object")
    throw new Error("El archivo debe contener un objeto JSON.");
  const data = raw as { version?: unknown; parties?: unknown };
  if (data.version !== VERSION)
    throw new Error("La versión del banco de preguntas no coincide.");
  if (!Array.isArray(data.parties) || data.parties.length > 100)
    throw new Error("Incluye una lista de hasta 100 candidaturas.");
  const ids = new Set<string>();
  return data.parties.map((p: unknown) => {
    if (!p || typeof p !== "object") throw new Error("Candidatura no válida.");
    const party = p as Party;
    if (
      typeof party.id !== "string" ||
      !/^[a-z0-9-]{1,80}$/.test(party.id) ||
      ids.has(party.id)
    )
      throw new Error("Identificador de candidatura no válido o repetido.");
    ids.add(party.id);
    if (
      typeof party.name !== "string" ||
      !party.name.trim() ||
      party.name.length > 120 ||
      typeof party.color !== "string" ||
      !/^#[0-9a-f]{6}$/i.test(party.color)
    )
      throw new Error("Nombre o color de candidatura no válido.");
    if (
      !party.positions ||
      typeof party.positions !== "object" ||
      Array.isArray(party.positions)
    )
      throw new Error("Faltan las posiciones documentadas.");
    for (const [id, position] of Object.entries(party.positions)) {
      const q = questions.find((q) => q.id === id);
      if (
        !q ||
        !position ||
        typeof position !== "object" ||
        ![-2, -1, 0, 1, 2].includes(position.value) ||
        (q.type === "binary" && ![-2, 2].includes(position.value))
      )
        throw new Error(`Posición no válida: ${id}.`);
      if (
        typeof position.source !== "string" ||
        !/^https:\/\//.test(position.source)
      )
        throw new Error(`Falta una fuente HTTPS en ${id}.`);
      try {
        new URL(position.source);
      } catch {
        throw new Error(`Fuente no válida: ${id}.`);
      }
      if (
        typeof position.reference !== "string" ||
        !position.reference.trim() ||
        position.reference.length > 2000
      )
        throw new Error(`Falta una referencia concreta en ${id}.`);
    }
    return {
      id: party.id,
      name: party.name,
      color: party.color,
      positions: party.positions,
    };
  });
}
