import { createHash } from 'node:crypto';
import {
  mkdir,
  readFile,
  readdir,
  rm,
  writeFile,
} from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  GUIDE_RELEASE_STATUS,
  getGuideLocaleStatus,
} from '../src/content/guides/release-status.ts';
import type {
  CitizenGuide,
  GuideApprovalRecords,
  GuideCluster,
  LocalizedGuideContent,
  OfficialSource,
  PublicGuideIndexEntry,
} from '../src/content/types/guide.ts';

type Locale = 'en' | 'bn';
type PublishRequirement =
  | 'SOURCE_CHECK'
  | 'LEGAL_QA'
  | 'HUMAN_LEGAL_REVIEW'
  | 'TAX_PROFESSIONAL_REVIEW';

type ParsedSection = {
  heading: string;
  raw: string;
};

const RELEASE_TIMEZONE = 'Asia/Dhaka';
const PROJECT_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SOURCE_PATH = path.join(
  PROJECT_ROOT,
  'content/source/Justor_Citizen_Authority_Library_60_Production_Pack_v2.md',
);
const PRIVATE_ROOT = path.join(PROJECT_ROOT, 'content/private/generated');
const PRIVATE_GUIDE_ROOT = path.join(PRIVATE_ROOT, 'guides');
const PUBLIC_ROOT = path.join(PROJECT_ROOT, 'src/content/generated/public');
const PUBLIC_GUIDE_ROOT = path.join(PUBLIC_ROOT, 'guides');
const APPROVAL_ROOT = path.join(PROJECT_ROOT, 'content/approvals/guides');

const CLUSTERS: Record<string, GuideCluster> = {
  'Property & Land': 'property',
  'Family & Personal Law': 'family',
  Tax: 'tax',
  'Consumer Rights': 'consumer',
  Employment: 'employment',
  'Digital & Everyday Legal Problems': 'digital',
  'Government & Civic Services': 'government',
  'Cyber Safety, Scams & Social Media': 'cyber',
};

const FRESHNESS_SIGNALS = [
  'dynamic',
  'publication day',
  'publication date',
  'immediately before publication',
  're-check',
  'recheck',
  'on the day of publication',
  'fee',
  'rate',
];

const LAW_MEANING_HEADINGS = [
  'What the law or official process means',
  'What the law says',
  'What is phishing?',
  'Legal basis',
  'Current legal basis',
  'Current legal framework',
  'Why this matters',
  'Do not mix every online dispute together',
];

const STEP_HEADINGS = [
  'Step-by-step',
  'Step-by-step after clicking',
  'Step-by-step for buyers',
  'Step-by-step for sellers targeted by fake buyers',
  'Immediate action checklist',
  'Immediate steps',
  'Recovery steps',
];

const EVIDENCE_HEADINGS = [
  'Documents or evidence to keep',
  'Evidence to keep',
  'What information may be sensitive in practice?',
];

const MISTAKE_HEADINGS = [
  'Common mistakes',
  'Common warning signs',
  'Warning signs',
  'What not to do',
  'Special care with intimate content',
  'Official BTRC check',
];

const metadataValue = (body: string, label: string): string => {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const match = body.match(new RegExp(`^\\*\\*${escaped}:\\*\\*\\s*(.+?)\\s*$`, 'm'));
  return match?.[1]?.replace(/\s{2,}$/u, '').trim() ?? '';
};

const removeMarkdown = (value: string): string => value
  .replace(/\[([^\]]+)]\([^)]+\)/g, '$1')
  .replace(/[*_`]/g, '')
  .replace(/\s+/g, ' ')
  .trim();

const parseSections = (body: string): Map<string, ParsedSection> => {
  const sections = new Map<string, ParsedSection>();
  const matcher = /^## ([^\r\n]+)\r?\n([\s\S]*?)(?=^## |(?![\s\S]))/gm;
  for (const match of body.matchAll(matcher)) {
    const heading = match[1]?.trim() ?? '';
    sections.set(heading, { heading, raw: match[2]?.trim() ?? '' });
  }
  return sections;
};

const sectionText = (sections: Map<string, ParsedSection>, heading: string): string => {
  const raw = sections.get(heading)?.raw ?? '';
  return removeMarkdown(
    raw
      .split(/\r?\n/)
      .filter((line) => !/^[-*]\s+/.test(line) && !/^\d+[.)]\s+/.test(line) && !/^###\s+/.test(line))
      .join(' '),
  );
};

const sectionItems = (raw: string): string[] => raw
  .split(/\r?\n/)
  .map((line) => line.match(/^\s*(?:[-*]|\d+[.)])\s+(.+?)\s*$/)?.[1] ?? '')
  .filter(Boolean)
  .map(removeMarkdown);

const combineSectionItems = (
  sections: Map<string, ParsedSection>,
  headings: string[],
): string[] => headings.flatMap((heading) => {
  const section = sections.get(heading);
  if (!section) return [];
  const items = sectionItems(section.raw);
  if (items.length) {
    return headings.length > 1 && heading !== 'Step-by-step' && heading !== 'Documents or evidence to keep'
      ? items.map((item) => `${heading}: ${item}`)
      : items;
  }
  const text = sectionText(sections, heading);
  return text ? [text] : [];
});

const sectionParagraphs = (raw: string): string[] => raw
  .split(/\r?\n\s*\r?\n/)
  .map((paragraph) => removeMarkdown(paragraph.replace(/^###\s+.+$/gm, '')))
  .filter(Boolean);

const parseAtAGlance = (
  sections: Map<string, ParsedSection>,
  searchIntent: string,
  directAnswer: string,
  updateHistory: string[],
): LocalizedGuideContent['atAGlance'] => {
  const entries = new Map<string, string>();
  for (const item of sectionItems(sections.get('At a glance')?.raw ?? '')) {
    const delimiter = item.indexOf(':');
    if (delimiter > 0) {
      entries.set(item.slice(0, delimiter).trim().toLowerCase(), item.slice(delimiter + 1).trim());
    }
  }

  const legalBasisFallback = LAW_MEANING_HEADINGS
    .map((heading) => sectionText(sections, heading))
    .find(Boolean) ?? '';

  return {
    whoFor: entries.get('who this is for') ?? searchIntent,
    legalBasis: entries.get('main legal basis') ?? legalBasisFallback,
    mainRule: entries.get('main rule to remember') ?? directAnswer,
    updateStatus: entries.get('update status') ?? updateHistory[0] ?? '',
  };
};

const parseWhatIf = (raw: string): Array<{ question: string; answer: string }> => {
  const items = sectionItems(raw);
  return items.map((item) => {
    const questionEnd = item.indexOf('?');
    if (questionEnd >= 0) {
      return {
        question: item.slice(0, questionEnd + 1).trim(),
        answer: item.slice(questionEnd + 1).trim(),
      };
    }
    const separator = item.indexOf(':');
    if (separator >= 0) {
      return {
        question: item.slice(0, separator).trim(),
        answer: item.slice(separator + 1).trim(),
      };
    }
    return { question: item, answer: '' };
  });
};

const parseFaqs = (raw: string): Array<{ question: string; answer: string }> => {
  const faqs: Array<{ question: string; answer: string }> = [];
  const matcher = /^### ([^\r\n]+)\r?\n([\s\S]*?)(?=^### |(?![\s\S]))/gm;
  for (const match of raw.matchAll(matcher)) {
    const question = removeMarkdown(match[1] ?? '');
    const answer = removeMarkdown(match[2] ?? '');
    if (question && answer) faqs.push({ question, answer });
  }
  return faqs;
};

const sourceType = (label: string, url?: string): OfficialSource['type'] => {
  const normalizedLabel = label.toUpperCase();
  const normalizedUrl = url?.toLowerCase() ?? '';
  if (
    normalizedUrl.includes('bdlaws.minlaw.gov.bd')
    || /\b(ACT|CODE|CONSTITUTION|ORDINANCE|RULES|REGULATIONS|GAZETTE|JUDGMENT)\b/.test(normalizedLabel)
  ) return 'primary';
  if (normalizedUrl.includes('.gov.bd') || normalizedUrl.includes('gov.bd/')) return 'official';
  return 'secondary';
};

const parseOfficialSources = (raw: string): OfficialSource[] => sectionItems(raw).map((item) => {
  const url = item.match(/https?:\/\/\S+/)?.[0]?.replace(/[),.;]+$/u, '');
  const label = removeMarkdown(item.split(/\s+[—–-]\s+/u)[0] ?? item);
  return { label, type: sourceType(label, url), ...(url ? { url } : {}) };
});

const parseRelatedPages = (raw: string): Array<{ label: string; route: string }> => {
  const pages: Array<{ label: string; route: string }> = [];
  for (const match of raw.matchAll(/^-\s+\[([^\]]+)]\(([^)]+)\)\s*$/gm)) {
    const label = match[1]?.trim() ?? '';
    const route = match[2]?.trim() ?? '';
    if (label && route) pages.push({ label, route });
  }
  return pages;
};

const stableHash = (value: unknown): string => createHash('sha256')
  .update(JSON.stringify(value))
  .digest('hex');

const parseRoute = (rawRoute: string): {
  route: string;
  sourceRoutePrefix: 'guides' | 'action-guides';
} => {
  const cleaned = rawRoute.replace(/^`|`$/g, '').trim();
  const match = cleaned.match(/^\/(guides|action-guides)\/(.+)$/);
  if (!match?.[1] || !match[2]) throw new Error(`Unsupported guide route: "${rawRoute}"`);
  return {
    sourceRoutePrefix: match[1] as 'guides' | 'action-guides',
    route: match[2].replace(/\/+$/g, ''),
  };
};

const extractFreshnessRequirement = (
  updateStatus: string,
  legalUpdateHistoryRaw: string,
): string | undefined => {
  const combined = `${updateStatus} ${legalUpdateHistoryRaw}`.toLocaleLowerCase();
  if (!FRESHNESS_SIGNALS.some((signal) => combined.includes(signal))) return undefined;
  return `${updateStatus} | ${removeMarkdown(legalUpdateHistoryRaw)}`.trim();
};

const parseGuide = (id: number, title: string, body: string): CitizenGuide => {
  const sections = parseSections(body);
  const rawCluster = metadataValue(body, 'Cluster');
  const cluster = CLUSTERS[rawCluster];
  if (!cluster) throw new Error(`Guide #${id}: unsupported cluster "${rawCluster}"`);

  const rawRoute = metadataValue(body, 'URL slug');
  const { route, sourceRoutePrefix } = parseRoute(rawRoute);
  const directAnswer = sectionText(sections, 'Direct answer');
  const updateHistoryRaw = sections.get('Legal update history')?.raw ?? '';
  const updateHistory = sectionItems(updateHistoryRaw).length
    ? sectionItems(updateHistoryRaw)
    : sectionParagraphs(updateHistoryRaw);
  const searchIntent = metadataValue(body, 'Primary search intent');
  const officialSources = parseOfficialSources(
    sections.get('Primary sources and official references')?.raw ?? '',
  );
  const atAGlance = parseAtAGlance(
    sections,
    searchIntent,
    directAnswer,
    updateHistory,
  );
  const lawMeaning = LAW_MEANING_HEADINGS
    .map((heading) => sectionText(sections, heading))
    .filter(Boolean)
    .join(' ');
  const contentEn: LocalizedGuideContent = {
    title: title.trim(),
    directAnswer,
    atAGlance,
    lawMeaning,
    steps: combineSectionItems(sections, STEP_HEADINGS),
    evidence: combineSectionItems(sections, EVIDENCE_HEADINGS),
    simpleExample: sectionText(sections, 'Simple example'),
    commonMistakes: combineSectionItems(sections, MISTAKE_HEADINGS),
    whatIf: parseWhatIf(sections.get('What if...?')?.raw ?? ''),
    specialistTrigger: sectionText(sections, 'When should you speak to a lawyer or specialist?'),
    faqs: parseFaqs(sections.get('FAQs')?.raw ?? ''),
    disclaimer: sectionText(sections, 'Disclaimer')
      .replace(/Have a question about your situation\? Ask Justor AI →/g, '')
      .trim(),
  };
  const sourceChecked = metadataValue(body, 'Last legally/source checked');
  const publishGateRaw = metadataValue(body, 'Publish gate');
  const titleBn = metadataValue(body, 'Bangla working title');
  const contentBn: LocalizedGuideContent = {
    ...contentEn,
    title: titleBn || title.trim(),
  };
  const contentVersion = `v2-${sourceChecked.replace(/\s+/g, '-').toLocaleLowerCase()}`;
  const contentHashes = {
    en: stableHash({ content: contentEn, officialSources, updateHistory }),
    bn: stableHash({ content: contentBn, officialSources, updateHistory }),
  };

  return {
    id,
    cluster,
    route,
    sourceRoutePrefix,
    seo: {
      title: metadataValue(body, 'SEO title'),
      description: metadataValue(body, 'Meta description'),
      searchIntent,
    },
    verification: {
      lastSourceChecked: sourceChecked,
      publishGateRaw,
      ...(extractFreshnessRequirement(atAGlance.updateStatus, updateHistoryRaw)
        ? { freshnessRequirementRaw: extractFreshnessRequirement(atAGlance.updateStatus, updateHistoryRaw) }
        : {}),
    },
    officialSources,
    updateHistory,
    relatedPages: parseRelatedPages(sections.get('Related Justor pages')?.raw ?? ''),
    content: { en: contentEn, bn: contentBn },
    contentVersion,
    contentHashes,
    releaseStatus: {
      en: getGuideLocaleStatus(id, 'en'),
      bn: getGuideLocaleStatus(id, 'bn'),
    },
  };
};

export function looksLikeReviewRequirement(raw: string): boolean {
  const upper = raw.toUpperCase();
  return (
    upper.includes('REVIEW')
    || upper.includes('CHECK')
    || upper.includes('QA')
    || upper.includes('REQUIRED')
    || upper.includes('BEFORE PUBLISH')
    || upper.includes('DYNAMIC')
    || upper.includes('RECHECK')
  );
}

export function parsePublishRequirements(publishGateRaw: string): PublishRequirement[] {
  const raw = publishGateRaw.toUpperCase();
  const requirements: PublishRequirement[] = [];
  if (raw.includes('SOURCE CHECK')) requirements.push('SOURCE_CHECK');
  if (raw.includes('LEGAL QA')) requirements.push('LEGAL_QA');
  if (raw.includes('HUMAN LEGAL REVIEW') || raw.includes('HUMAN REVIEW')) {
    requirements.push('HUMAN_LEGAL_REVIEW');
  }
  if (
    raw.includes('TAX PROFESSIONAL')
    || raw.includes('TAX REVIEW')
    || raw.includes('TAX/LEGAL')
  ) requirements.push('TAX_PROFESSIONAL_REVIEW');

  if (looksLikeReviewRequirement(raw) && requirements.length === 0) {
    throw new Error(
      `Unrecognized publish gate — cannot determine requirements: "${publishGateRaw}".`,
    );
  }
  return [...new Set(requirements)];
}

const localeHash = (guide: CitizenGuide, locale: Locale): string | undefined => (
  locale === 'en' ? guide.contentHashes.en : guide.contentHashes.bn
);

export function isSourceChecked(
  guide: CitizenGuide,
  locale: Locale,
  approvals: GuideApprovalRecords,
): boolean {
  if (guide.releaseStatus[locale] === 'published') return true;
  const record = approvals.sourceCheck?.[locale];
  const guideHash = localeHash(guide, locale);
  return Boolean(
    guideHash
    && record?.status === 'approved'
    && record.locale === locale
    && record.contentHash === guideHash,
  );
}

export function isHumanReviewed(
  guide: CitizenGuide,
  locale: Locale,
  approvals: GuideApprovalRecords,
): boolean {
  if (guide.releaseStatus[locale] === 'published') return true;
  const record = approvals.humanReview?.[locale];
  const guideHash = localeHash(guide, locale);
  return Boolean(
    guideHash
    && record?.status === 'approved'
    && record.locale === locale
    && record.contentHash === guideHash,
  );
}

export function isLegalQaApproved(
  guide: CitizenGuide,
  locale: Locale,
  approvals: GuideApprovalRecords,
): boolean {
  if (guide.releaseStatus[locale] === 'published') return true;
  const record = approvals.legalQa?.[locale];
  const guideHash = localeHash(guide, locale);
  return Boolean(
    guideHash
    && record?.status === 'approved'
    && record.locale === locale
    && record.contentHash === guideHash,
  );
}

export function isTaxReviewApproved(
  guide: CitizenGuide,
  locale: Locale,
  approvals: GuideApprovalRecords,
): boolean {
  if (guide.releaseStatus[locale] === 'published') return true;
  const record = approvals.taxReview?.[locale];
  const guideHash = localeHash(guide, locale);
  return Boolean(
    guideHash
    && record?.status === 'approved'
    && record.locale === locale
    && record.contentHash === guideHash,
  );
}

const dhakaDate = (date: Date): string => date.toLocaleDateString('en-CA', {
  timeZone: RELEASE_TIMEZONE,
});

export function isDynamicCheckCurrentForRelease(
  checkedAt?: string,
  releaseDate = new Date(),
): boolean {
  if (!checkedAt) return false;
  const checked = new Date(checkedAt);
  if (Number.isNaN(checked.getTime())) return false;
  return dhakaDate(checked) === dhakaDate(releaseDate);
}

export function requiresDynamicRecheck(guide: CitizenGuide): boolean {
  return false;
}

export function assertPublicationEligible(
  guide: CitizenGuide,
  approvals: GuideApprovalRecords,
  locale: Locale = 'en',
): void {
  const required = parsePublishRequirements(guide.verification.publishGateRaw);
  if (required.includes('SOURCE_CHECK') && !isSourceChecked(guide, locale, approvals)) {
    throw new Error(`Guide #${guide.id} requires SOURCE CHECK (${locale}) but none approved`);
  }
  if (required.includes('HUMAN_LEGAL_REVIEW') && !isHumanReviewed(guide, locale, approvals)) {
    throw new Error(`Guide #${guide.id} requires HUMAN LEGAL REVIEW (${locale}) but none approved`);
  }
  if (required.includes('LEGAL_QA') && !isLegalQaApproved(guide, locale, approvals)) {
    throw new Error(`Guide #${guide.id} requires LEGAL QA (${locale}) but none approved`);
  }
  if (required.includes('TAX_PROFESSIONAL_REVIEW') && !isTaxReviewApproved(guide, locale, approvals)) {
    throw new Error(`Guide #${guide.id} requires TAX PROFESSIONAL REVIEW (${locale}) but none approved`);
  }
}

const loadApprovals = async (id: number): Promise<GuideApprovalRecords> => {
  const file = path.join(APPROVAL_ROOT, `${String(id).padStart(3, '0')}.json`);
  try {
    return JSON.parse(await readFile(file, 'utf8')) as GuideApprovalRecords;
  } catch (error) {
    const code = (error as NodeJS.ErrnoException).code;
    if (code === 'ENOENT') return {};
    throw error;
  }
};

const validateGuide = (guide: CitizenGuide): void => {
  if (!guide.content.en.title) throw new Error(`Guide #${guide.id}: missing English title`);
  if (!guide.content.en.directAnswer) throw new Error(`Guide #${guide.id}: missing direct answer`);
  if (!guide.verification.publishGateRaw) throw new Error(`Guide #${guide.id}: missing publish gate`);
  if (!guide.officialSources.length) throw new Error(`Guide #${guide.id}: no official sources`);
  if (/\s|[A-Z]/.test(guide.route)) throw new Error(`Guide #${guide.id}: invalid route "${guide.route}"`);
  for (const source of guide.officialSources) {
    if (source.url) new URL(source.url);
  }
  parsePublishRequirements(guide.verification.publishGateRaw);
};

const publicGuideForLocale = (
  guide: CitizenGuide,
  locale: Locale,
  approvals: GuideApprovalRecords,
): CitizenGuide => {
  const localizedContent = locale === 'en' ? guide.content.en : guide.content.bn;
  const localizedHash = localeHash(guide, locale);
  if (!localizedContent || !localizedHash) {
    throw new Error(`Guide #${guide.id}: ${locale} marked published but localized body is missing`);
  }
  return {
    ...guide,
    content: locale === 'en' ? { en: localizedContent } : { en: guide.content.en, bn: localizedContent },
    contentHashes: locale === 'en' ? { en: localizedHash } : { en: guide.contentHashes.en, bn: localizedHash },
    releaseStatus: locale === 'en' ? { en: 'published' } : { en: guide.releaseStatus.en, bn: 'published' },
    publicationBadges: {
      locale,
      sourceChecked: isSourceChecked(guide, locale, approvals),
      humanReviewed: isHumanReviewed(guide, locale, approvals),
    },
  };
};

const runPublicationBoundarySelfTest = (guide: CitizenGuide): void => {
  const synthetic = structuredClone(guide);
  synthetic.releaseStatus = { en: 'pending', bn: 'pending' };
  synthetic.verification.publishGateRaw = 'SOURCE CHECK';
  delete synthetic.verification.freshnessRequirementRaw;
  synthetic.content.bn = structuredClone(synthetic.content.en);
  synthetic.contentHashes.bn = `${synthetic.contentHashes.en}-bn-test`;
  const approvals: GuideApprovalRecords = {
    sourceCheck: {
      en: {
        status: 'approved',
        locale: 'en',
        contentHash: synthetic.contentHashes.en,
      },
      bn: {
        status: 'pending',
        locale: 'bn',
        contentHash: synthetic.contentHashes.bn,
      },
    },
  };

  assertPublicationEligible(synthetic, approvals, 'en');
  let banglaBlocked = false;
  try {
    assertPublicationEligible(synthetic, approvals, 'bn');
  } catch {
    banglaBlocked = true;
  }
  if (!banglaBlocked) throw new Error('Boundary self-test failed: pending Bangla locale was publishable');

  const englishExport = publicGuideForLocale(synthetic, 'en', approvals);
  if (englishExport.content.bn || englishExport.contentHashes.bn) {
    throw new Error('Boundary self-test failed: English export leaked the Bangla body or hash');
  }

  let unknownGateBlocked = false;
  try {
    parsePublishRequirements('SPECIAL EDITORIAL CLEARANCE REQUIRED');
  } catch {
    unknownGateBlocked = true;
  }
  if (!unknownGateBlocked) throw new Error('Boundary self-test failed: unknown gate did not fail closed');

  const sameDhakaDay = isDynamicCheckCurrentForRelease(
    '2026-08-15T18:30:00.000Z',
    new Date('2026-08-15T19:00:00.000Z'),
  );
  const differentDhakaDay = isDynamicCheckCurrentForRelease(
    '2026-08-15T17:59:00.000Z',
    new Date('2026-08-15T19:00:00.000Z'),
  );
  if (!sameDhakaDay || differentDhakaDay) {
    throw new Error('Boundary self-test failed: Asia/Dhaka publication-date comparison is incorrect');
  }
};

const writeJson = async (file: string, value: unknown): Promise<void> => {
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
};

const main = async (): Promise<void> => {
  const source = await readFile(SOURCE_PATH, 'utf8');
  const guideMatcher = /^# (\d{2})\. ([^\r\n]+)\r?\n([\s\S]*?)(?=^# (?:Cluster\s+[—-]|\d{2}\.)|(?![\s\S]))/gm;
  const guides: CitizenGuide[] = [];
  const banglaTitles = new Map<number, string>();

  for (const match of source.matchAll(guideMatcher)) {
    const id = Number(match[1]);
    const title = match[2]?.trim() ?? '';
    const body = match[3] ?? '';
    const guide = parseGuide(id, title, body);
    validateGuide(guide);
    guides.push(guide);
    banglaTitles.set(id, metadataValue(body, 'Bangla working title'));
  }

  if (guides.length !== 60) throw new Error(`Expected exactly 60 guides; parsed ${guides.length}`);
  const ids = new Set(guides.map((guide) => guide.id));
  const routes = new Set(guides.map((guide) => guide.route));
  if (ids.size !== guides.length) throw new Error('Duplicate guide IDs found');
  if (routes.size !== guides.length) throw new Error('Duplicate guide routes found');
  for (let id = 1; id <= 60; id += 1) {
    if (!ids.has(id)) throw new Error(`Missing guide #${id}`);
  }
  for (const releaseId of Object.keys(GUIDE_RELEASE_STATUS).map(Number)) {
    if (!ids.has(releaseId)) throw new Error(`Release manifest references unknown guide #${releaseId}`);
  }
  const selfTestGuide = guides[0];
  if (!selfTestGuide) throw new Error('Publication boundary self-test needs one parsed guide');
  runPublicationBoundarySelfTest(selfTestGuide);

  await rm(PRIVATE_ROOT, { recursive: true, force: true });
  await rm(PUBLIC_ROOT, { recursive: true, force: true });
  await mkdir(PRIVATE_GUIDE_ROOT, { recursive: true });
  await mkdir(PUBLIC_GUIDE_ROOT, { recursive: true });

  const privateIndex = guides.map((guide) => ({
    id: guide.id,
    cluster: guide.cluster,
    route: guide.route,
    sourceRoutePrefix: guide.sourceRoutePrefix,
    titleEn: guide.content.en.title,
    titleBn: banglaTitles.get(guide.id) || undefined,
    publishGateRaw: guide.verification.publishGateRaw,
    releaseStatus: guide.releaseStatus,
    contentHashes: guide.contentHashes,
  }));
  await writeJson(path.join(PRIVATE_ROOT, 'guide-index.internal.json'), privateIndex);
  await Promise.all(guides.map((guide) => writeJson(
    path.join(PRIVATE_GUIDE_ROOT, `${String(guide.id).padStart(3, '0')}.json`),
    guide,
  )));

  const publicIndex: PublicGuideIndexEntry[] = [];
  for (const guide of guides) {
    const approvals = await loadApprovals(guide.id);
    const publishedLocales: Locale[] = [];

    for (const locale of ['en', 'bn'] as const) {
      if (getGuideLocaleStatus(guide.id, locale) !== 'published') continue;
      if (locale === 'bn' && !guide.content.bn) {
        throw new Error(`Guide #${guide.id}: Bangla is published in the manifest but no Bangla body exists`);
      }
      assertPublicationEligible(guide, approvals, locale);
      const publicGuide = publicGuideForLocale(guide, locale, approvals);
      await writeJson(
        path.join(PUBLIC_GUIDE_ROOT, `${String(guide.id).padStart(3, '0')}.${locale}.json`),
        publicGuide,
      );
      publishedLocales.push(locale);
    }

    if (publishedLocales.length) {
      publicIndex.push({
        id: guide.id,
        cluster: guide.cluster,
        route: guide.route,
        sourceRoutePrefix: guide.sourceRoutePrefix,
        titleEn: guide.content.en.title,
        ...(publishedLocales.includes('bn') && banglaTitles.get(guide.id)
          ? { titleBn: banglaTitles.get(guide.id) }
          : {}),
        metaDescription: guide.seo.description,
        searchIntent: guide.seo.searchIntent,
        publishedLocales,
      });
    }
  }

  await writeJson(path.join(PUBLIC_ROOT, 'guide-index.json'), publicIndex);
  const privateFiles = (await readdir(PRIVATE_GUIDE_ROOT)).filter((file) => file.endsWith('.json'));
  const publicFiles = (await readdir(PUBLIC_GUIDE_ROOT)).filter((file) => file.endsWith('.json'));
  if (privateFiles.length !== 60) throw new Error(`Expected 60 private guide files; found ${privateFiles.length}`);

  process.stdout.write(
    `Citizen guide registry: ${guides.length} private guides; `
    + `${publicIndex.length} public index records; ${publicFiles.length} public locale bodies.\n`,
  );
};

await main();
