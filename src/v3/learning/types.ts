export type CardState = 'got_it' | 'review_again';
export type AssetType = 'image' | 'lottie' | 'spline' | 'icon';

export interface LearningCard {
  id: string;
  slug: string;
  sort_order: number;
  card_type: string;
  label: string;
  hook_en: string;
  hook_bn: string;
  question_en: string;
  question_bn: string;
  answer_en: string;
  answer_bn: string;
  explanation_en: string;
  explanation_bn: string;
  key_principle_en: string;
  key_principle_bn: string;
  act_name: string;
  section_label: string;
  authority_type: string;
  authority_note?: string | null;
  asset_type: AssetType;
  asset_url?: string | null;
  review_status: string;
  content_version: number;
}

export interface LearningSection {
  id: string;
  slug: string;
  title_en: string;
  title_bn: string;
  estimated_minutes: number;
  sort_order: number;
  status: string;
  card_count: number;
  cards: LearningCard[];
}

export interface ComingSoonSubject {
  slug: string;
  title_en: string;
  title_bn: string;
}

export interface LearningSubject {
  id: string;
  slug: string;
  title_en: string;
  title_bn: string;
  description_en: string;
  description_bn: string;
  level_tag: string;
  status: string;
  coming_soon: ComingSoonSubject[];
}

export interface LearningCatalog {
  subject: LearningSubject;
  sections: LearningSection[];
}

export interface LearningHandoff {
  subjectId: string;
  sectionId: string;
  sessionId: string;
  gotItCardIds: string[];
  reviewCardIds: string[];
  language: 'en' | 'bn';
}
