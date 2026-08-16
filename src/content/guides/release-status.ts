import type { LocaleReleaseStatus } from '../types/guide';

export type ReleaseEntry = {
  en: LocaleReleaseStatus;
  bn?: LocaleReleaseStatus;
  notes?: string;
};

/**
 * Editorial source of truth for public guide visibility.
 *
 * Codex intentionally leaves this empty. Editors may add an entry only after
 * the matching, locale-specific approval records have been completed. The
 * content build will fail closed if an entry is marked published prematurely.
 */
export const GUIDE_RELEASE_STATUS: Record<number, ReleaseEntry> = {};

export function getGuideLocaleStatus(
  id: number,
  locale: 'en' | 'bn',
): LocaleReleaseStatus {
  const entry = GUIDE_RELEASE_STATUS[id];
  if (!entry) return locale === 'en' ? 'review' : 'missing';
  return entry[locale] ?? (locale === 'bn' ? 'missing' : 'review');
}
