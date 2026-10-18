import raw from "../sesiones-banco.json";
import type { Answers } from "../../Elecciones/interfaz/perfil/model";

export type Evidence = {
  proposalId: string;
  documentId: string;
  pdfPages?: number[];
  textLines?: number[];
  measure?: number;
};
export type Position = {
  value: number | null;
  basis: string;
  evidence: Evidence[];
};
export type SessionQuestion = {
  id: string;
  category: string;
  concept: string;
  text: string;
  selectionKey: string;
  scope: { territory: string; sourceElection: string } | null;
  positions: Record<string, Position>;
};
export const bank = raw as Omit<typeof raw, "questions"> & {
  questions: SessionQuestion[];
};
export const questionById = new Map(bank.questions.map((q) => [q.id, q]));
export const sourceById = new Map(bank.sources.map((s) => [s.id, s]));
export const LIMIT = 10;

/** Rejection sampling avoids modulo bias; no Math.random sorting or persistent identifier. */
export function secureIndex(max: number) {
  if (!Number.isInteger(max) || max < 1 || max > 0x100000000)
    throw new Error("Rango de sorteo inválido");
  const boundary = Math.floor(0x100000000 / max) * max;
  const value = new Uint32Array(1);
  do {
    crypto.getRandomValues(value);
  } while (value[0] >= boundary);
  return value[0] % max;
}

export function sampleCategory(
  category: string,
  questions: SessionQuestion[] = bank.questions,
  randomIndex: (max: number) => number = secureIndex,
) {
  // Select decisions first so equivalent wording cannot buy extra lottery tickets.
  const groups = new Map<string, SessionQuestion[]>();
  for (const q of questions.filter((q) => q.category === category))
    groups.set(q.selectionKey, [...(groups.get(q.selectionKey) ?? []), q]);
  const pool = [...groups.values()];
  for (let i = pool.length - 1; i > 0; i--) {
    const j = randomIndex(i + 1);
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool
    .slice(0, LIMIT)
    .map((group) => group[randomIndex(group.length)].id);
}

export type Draws = Record<string, string[]>;
export function selectTopics(
  draws: Draws,
  categoryIds: string[],
  randomIndex = secureIndex,
): Draws {
  const next = { ...draws };
  for (const id of categoryIds)
    if (!next[id]) next[id] = sampleCategory(id, bank.questions, randomIndex);
  return next;
}
export function sessionQuestions(draws: Draws, selected: string[]) {
  return selected.flatMap((id) =>
    (draws[id] ?? []).map((qid) => questionById.get(qid)!),
  );
}

/** One decision contributes once, even if a future cross-topic route displays it twice. */
export function uniqueResponses(
  answers: Answers,
  questions: SessionQuestion[] = bank.questions,
) {
  const byId =
    questions === bank.questions
      ? questionById
      : new Map(questions.map((q) => [q.id, q]));
  const decisions = new Map<
    string,
    { question: SessionQuestion; answer: Answers[string] }
  >();
  for (const [id, answer] of Object.entries(answers)) {
    const question = byId.get(id);
    if (question) decisions.set(question.selectionKey, { question, answer });
  }
  return [...decisions.values()];
}

export function compare(
  answers: Answers,
  party: string,
  category?: string,
  questions: SessionQuestion[] = bank.questions,
) {
  const responded = uniqueResponses(answers, questions).filter(
    ({ question, answer }) =>
      answer.value !== null && (!category || question.category === category),
  );
  const contributions = responded.flatMap(({ question, answer }) => {
    const position = question.positions[party];
    return position?.value != null && position.evidence.length
      ? [
          {
            question,
            answer,
            position,
            distance: Math.abs(answer.value! - position.value) / 4,
            weight: answer.importance,
          },
        ]
      : [];
  });
  const weight = contributions.reduce((n, c) => n + c.weight, 0);
  const distance = contributions.reduce((n, c) => n + c.distance * c.weight, 0);
  return {
    percent: weight ? 100 * (1 - distance / weight) : null,
    coverage: responded.length
      ? (contributions.length / responded.length) * 100
      : 0,
    shared: contributions.length,
    answered: responded.length,
    weight,
    distance,
    contributions,
  };
}

export function userAxis(
  answers: Answers,
  axis: (typeof raw.maps)[number]["x"],
) {
  const directions = new Map<string, number>();
  axis.indicators.forEach((i) =>
    i.questionIds.forEach((id) => directions.set(id, i.direction)),
  );
  const contributions = uniqueResponses(answers).flatMap(
    ({ question, answer }) => {
      const direction = directions.get(question.id);
      return direction && answer.value !== null
        ? [
            {
              question,
              answer,
              direction,
              numerator: (answer.value / 2) * direction * answer.importance,
            },
          ]
        : [];
    },
  );
  const weight = contributions.reduce((n, c) => n + c.answer.importance, 0);
  const numerator = contributions.reduce((n, c) => n + c.numerator, 0);
  return {
    value: weight ? (100 * numerator) / weight : null,
    weight,
    numerator,
    contributions,
  };
}
