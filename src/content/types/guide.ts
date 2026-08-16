export type LocaleReleaseStatus = 'missing' | 'draft' | 'review' | 'published';

export type GuideStatus = LocaleReleaseStatus;

export type GuideCluster =
  | 'property'
  | 'family'
  | 'tax'
  | 'consumer'
  | 'employment'
  | 'digital'
  | 'government'
  | 'cyber';

export interface OfficialSource {
  label: string;
  type: 'primary' | 'official' | 'secondary';
  url?: string;
}

export interface LocalizedGuideContent {
  title: string;
  directAnswer: string;
  atAGlance: {
    whoFor: string;
    legalBasis: string;
    mainRule: string;
    updateStatus: string;
  };
  lawMeaning: string;
  steps: string[];
  evidence: string[];
  simpleExample: string;
  commonMistakes: string[];
  whatIf: Array<{ question: string; answer: string }>;
  specialistTrigger: string;
  faqs: Array<{ question: string; answer: string }>;
  disclaimer: string;
}

export interface CitizenGuide {
  id: number;
  cluster: GuideCluster;
  route: string;
  sourceRoutePrefix: 'guides' | 'action-guides';
  seo: {
    title: string;
    description: string;
    searchIntent: string;
  };
  verification: {
    lastSourceChecked: string;
    publishGateRaw: string;
    freshnessRequirementRaw?: string;
  };
  officialSources: OfficialSource[];
  updateHistory: string[];
  relatedPages: Array<{ label: string; route: string }>;
  content: {
    en: LocalizedGuideContent;
    bn?: LocalizedGuideContent;
  };
  contentVersion: string;
  contentHashes: {
    en: string;
    bn?: string;
  };
  releaseStatus: {
    en: LocaleReleaseStatus;
    bn?: LocaleReleaseStatus;
  };
  publicationBadges?: {
    locale: 'en' | 'bn';
    sourceChecked: boolean;
    humanReviewed: boolean;
  };
}

export interface PublicGuideIndexEntry {
  id: number;
  cluster: GuideCluster;
  route: string;
  sourceRoutePrefix: 'guides' | 'action-guides';
  titleEn: string;
  titleBn?: string;
  metaDescription: string;
  searchIntent: string;
  publishedLocales: Array<'en' | 'bn'>;
}

export interface SourceCheckRecord {
  status: 'pending' | 'approved' | 'rejected';
  locale: 'en' | 'bn';
  contentHash: string;
  checkedAt?: string;
  checkerId?: string;
}

export interface ReviewRecord {
  status: 'pending' | 'approved' | 'rejected';
  locale: 'en' | 'bn';
  contentVersion: string;
  contentHash: string;
  reviewedAt?: string;
  reviewerId?: string;
}

export interface LegalQaRecord {
  status: 'pending' | 'approved' | 'rejected';
  locale: 'en' | 'bn';
  contentHash: string;
  approvedAt?: string;
  approverId?: string;
}

export interface TaxReviewRecord {
  status: 'pending' | 'approved' | 'rejected';
  locale: 'en' | 'bn';
  contentHash: string;
  approvedAt?: string;
  approverId?: string;
}

export interface GuideApprovalRecords {
  sourceCheck?: Partial<Record<'en' | 'bn', SourceCheckRecord>>;
  humanReview?: Partial<Record<'en' | 'bn', ReviewRecord>>;
  legalQa?: Partial<Record<'en' | 'bn', LegalQaRecord>>;
  taxReview?: Partial<Record<'en' | 'bn', TaxReviewRecord>>;
}
