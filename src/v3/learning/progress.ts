import type { CardState, LearningCatalog, LearningSection } from './types';

const KEY = 'justor-learning-progress-v1';
const REPORTS_KEY = 'justor-learning-reports-v1';

export type ProgressMap = Record<string, { state: CardState; seen: number; revealed: number; at: string }>;

const read = (): ProgressMap => {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return {};
    return JSON.parse(raw) as ProgressMap;
  } catch {
    return {};
  }
};

const write = (map: ProgressMap): void => {
  localStorage.setItem(KEY, JSON.stringify(map));
};

export const getProgress = (): ProgressMap => read();

export const setCardProgress = (cardId: string, state: CardState, revealed = true): void => {
  const map = read();
  const prev = map[cardId];
  map[cardId] = {
    state,
    seen: (prev?.seen ?? 0) + 1,
    revealed: (prev?.revealed ?? 0) + (revealed ? 1 : 0),
    at: new Date().toISOString(),
  };
  write(map);
};

export const sectionStats = (section: LearningSection, map = read()) => {
  let got = 0;
  let review = 0;
  for (const card of section.cards) {
    const row = map[card.id];
    if (row?.state === 'got_it') got += 1;
    else if (row?.state === 'review_again') review += 1;
  }
  const done = got + review;
  const total = section.cards.length;
  const pct = total ? Math.round((done / total) * 100) : 0;
  const status = done === 0 ? 'not_started' : done < total ? 'in_progress' : review > 0 ? 'has_review_queue' : 'complete';
  return { got, review, done, total, pct, status };
};

export const subjectStats = (catalog: LearningCatalog, map = read()) => {
  let done = 0;
  let total = 0;
  let continueSlug = catalog.sections[0]?.slug ?? '';
  let bestPartial = -1;
  for (const section of catalog.sections) {
    const s = sectionStats(section, map);
    done += s.done;
    total += s.total;
    if (s.status === 'in_progress' || s.status === 'has_review_queue') {
      const score = s.pct;
      if (score > bestPartial) {
        bestPartial = score;
        continueSlug = section.slug;
      }
    } else if (s.status === 'not_started' && bestPartial < 0 && continueSlug === catalog.sections[0]?.slug) {
      continueSlug = section.slug;
    }
  }
  return { done, total, pct: total ? Math.round((done / total) * 100) : 0, continueSlug };
};

export const reviewQueue = (section: LearningSection, map = read()) =>
  section.cards.filter((card) => map[card.id]?.state === 'review_again');

export const addReport = (cardId: string, issueType: string, note: string, version: number): void => {
  try {
    const raw = localStorage.getItem(REPORTS_KEY);
    const list = raw ? JSON.parse(raw) as unknown[] : [];
    list.push({ cardId, issueType, note, version, at: new Date().toISOString() });
    localStorage.setItem(REPORTS_KEY, JSON.stringify(list));
  } catch {
    /* ignore quota */
  }
};
