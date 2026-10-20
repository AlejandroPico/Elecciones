import raw from "../sesiones-banco.json";
import indices from "../indices-perfil.json";
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
export const bank = { ...raw, maps: indices.charts } as Omit<
  typeof raw,
  "questions"
> & {
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
  const totalWeight = responded.reduce((n, r) => n + r.answer.importance, 0);
  const unknownWeight = totalWeight - weight;
  const agreement = weight - distance;
  return {
    percent: weight ? 100 * (1 - distance / weight) : null,
    coverage: responded.length
      ? (contributions.length / responded.length) * 100
      : 0,
    shared: contributions.length,
    answered: responded.length,
    weight,
    distance,
    totalWeight,
    unknownWeight,
    weightedCoverage: totalWeight ? (100 * weight) / totalWeight : 0,
    // Bounds over ALL answered decisions, with unknown agreement anywhere in [0, 1].
    // This is an identification interval, never a confidence interval or a new score.
    overallRange: totalWeight
      ? ([
          (100 * agreement) / totalWeight,
          (100 * (agreement + unknownWeight)) / totalWeight,
        ] as [number, number])
      : null,
    contributions,
  };
}

export function userAxis(
  answers: Answers,
  axis: (typeof raw.maps)[number]["x"],
  questions: SessionQuestion[] = bank.questions,
) {
  const responses = uniqueResponses(answers, questions);
  const seen = new Set<string>();
  const indicators = axis.indicators.map((indicator) => {
    const ids = new Set(indicator.questionIds);
    const entries = responses.flatMap(({ question, answer }) => {
      if (
        !ids.has(question.id) ||
        question.scope ||
        answer.value === null ||
        seen.has(question.selectionKey)
      )
        return [];
      seen.add(question.selectionKey);
      return [
        {
          question,
          answer,
          direction: indicator.direction,
          numerator:
            (answer.value / 2) * indicator.direction * answer.importance,
        },
      ];
    });
    const entryWeight = entries.reduce((n, c) => n + c.answer.importance, 0);
    return {
      indicator,
      entries,
      value: entryWeight
        ? (100 * entries.reduce((n, c) => n + c.numerator, 0)) / entryWeight
        : null,
      // Several equivalent formulations do not multiply an indicator's influence.
      weight: entries.length ? entryWeight / entries.length : 0,
    };
  });
  const known = indicators.filter((i) => i.value !== null);
  const contributions = indicators.flatMap((i) => i.entries);
  const weight = known.reduce((n, c) => n + c.weight, 0);
  const numerator = known.reduce((n, c) => n + (c.value! / 100) * c.weight, 0);
  return {
    value: weight ? (100 * numerator) / weight : null,
    weight,
    numerator,
    contributions,
    count: known.length,
    total: axis.indicators.length,
    indicators,
  };
}

/** The party map uses the same explicitly signed indicators, never inferred ideology. */
export function documentaryAxis(
  party: string,
  axis: (typeof raw.maps)[number]["x"],
  questions: SessionQuestion[] = bank.questions,
) {
  const lookup =
    questions === bank.questions
      ? questionById
      : new Map(questions.map((q) => [q.id, q]));
  const seen = new Set<string>();
  const contributions = axis.indicators.map((indicator) => {
    const ambiguous = indicator.questionIds.some((id) => {
      const q = lookup.get(id),
        p = q?.positions[party];
      return (
        !q?.scope &&
        p?.value === null &&
        p.evidence.some(
          (e) => sourceById.get(e.documentId)?.kind !== "territorial",
        )
      );
    });
    const entries = [...new Set(indicator.questionIds)].flatMap((id) => {
      const question = lookup.get(id),
        position = question?.positions[party];
      if (
        !question ||
        question.scope ||
        seen.has(id) ||
        position?.value == null ||
        !position.evidence.length
      )
        return [];
      const evidence = position.evidence.filter(
        (e) => sourceById.get(e.documentId)?.kind !== "territorial",
      );
      if (!evidence.length) return [];
      seen.add(id);
      return [{ question, position: { ...position, evidence } }];
    });
    const values = new Set(entries.map((e) => e.position.value));
    return {
      indicator,
      entries,
      value:
        values.size === 1 && !ambiguous
          ? 50 * [...values][0]! * indicator.direction
          : null,
    };
  });
  const known = contributions.filter((c) => c.value !== null);
  return {
    value: known.length
      ? known.reduce((n, c) => n + c.value!, 0) / known.length
      : null,
    count: known.length,
    total: contributions.length,
    contributions,
  };
}

export function representedResponses(answers: Answers) {
  const ids = new Set(
    bank.maps.flatMap((m) =>
      [m.x, m.y].flatMap((a) => a.indicators.flatMap((i) => i.questionIds)),
    ),
  );
  return uniqueResponses(answers).filter(
    (r) =>
      r.answer.value !== null && !r.question.scope && ids.has(r.question.id),
  );
}
