import guideIndexJson from '../generated/public/guide-index.json';
import type {
  CitizenGuide,
  GuideCluster,
  PublicGuideIndexEntry,
} from '../types/guide';

const guideIndex = guideIndexJson as PublicGuideIndexEntry[];
const publicGuideModules = import.meta.glob(
  '/src/content/generated/public/guides/*.json',
);

const normalizeQuery = (value: string): string => value.trim().toLocaleLowerCase();

export function getPublishedGuides(locale: 'en' | 'bn' = 'en'): PublicGuideIndexEntry[] {
  return guideIndex.filter((guide) => guide.publishedLocales.includes(locale));
}

export function getGuidesByCluster(
  cluster: GuideCluster,
  locale: 'en' | 'bn' = 'en',
): PublicGuideIndexEntry[] {
  return getPublishedGuides(locale).filter((guide) => guide.cluster === cluster);
}

export function searchGuides(
  query: string,
  locale: 'en' | 'bn' = 'en',
): PublicGuideIndexEntry[] {
  const normalized = normalizeQuery(query);
  if (!normalized) return getPublishedGuides(locale);

  return getPublishedGuides(locale).filter((guide) =>
    guide.titleEn.toLocaleLowerCase().includes(normalized)
    || guide.titleBn?.toLocaleLowerCase().includes(normalized)
    || guide.searchIntent.toLocaleLowerCase().includes(normalized)
    || guide.metaDescription.toLocaleLowerCase().includes(normalized)
    || guide.route.toLocaleLowerCase().includes(normalized),
  );
}

export function findPublishedGuideByRoute(
  route: string,
  locale: 'en' | 'bn' = 'en',
): PublicGuideIndexEntry | undefined {
  const normalized = route.replace(/^\/+|\/+$/g, '');
  return getPublishedGuides(locale).find((guide) => guide.route === normalized)
    ?? guideIndex.find((guide) => guide.route === normalized && guide.publishedLocales.length > 0);
}

export async function loadPublicGuide(
  id: number,
  locale: 'en' | 'bn',
): Promise<CitizenGuide> {
  const key = `/src/content/generated/public/guides/${String(id).padStart(3, '0')}.${locale}.json`;
  const loader = publicGuideModules[key];

  if (!loader) {
    throw new Error(`Published guide ${id} (${locale}) not found in public export`);
  }

  const module = await loader() as { default: CitizenGuide };
  return module.default;
}
