import type { LearningCatalog, LearningSection } from './types';
import bundled from './contract-act-v1.json' with { type: 'json' };

export const learningCatalog = bundled as LearningCatalog;

export const getSection = (slug: string): LearningSection | undefined =>
  learningCatalog.sections.find((section) => section.slug === slug);
