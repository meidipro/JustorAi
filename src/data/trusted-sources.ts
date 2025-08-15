// Trusted Legal Sources Database for Bangladesh
// Comprehensive list of authoritative legal sources for external search

export interface LegalSource {
  id: string;
  name: string;
  nameInBangla?: string;
  baseUrl: string;
  reliability: number; // 0-1 scale
  category: SourceCategory;
  searchCapable: boolean;
  apiEndpoint?: string;
  searchMethod: 'api' | 'scraping' | 'rss';
  updateFrequency: 'daily' | 'weekly' | 'monthly';
  coverageAreas: string[];
  description: string;
  contactInfo?: ContactInfo;
}

export interface ContactInfo {
  phone?: string;
  email?: string;
  emergencyLine?: string;
  address?: string;
}

export type SourceCategory = 
  | 'government'
  | 'judicial' 
  | 'legislative'
  | 'legal_aid'
  | 'human_rights'
  | 'academic'
  | 'professional'
  | 'international';

export const TRUSTED_LEGAL_SOURCES: LegalSource[] = [
  // Government Sources
  {
    id: 'molj_bd',
    name: 'Ministry of Law, Justice and Parliamentary Affairs',
    nameInBangla: 'আইন, বিচার ও সংসদ বিষয়ক মন্ত্রণালয়',
    baseUrl: 'https://www.lawjustice.gov.bd',
    reliability: 0.97,
    category: 'government',
    searchCapable: true,
    searchMethod: 'scraping',
    updateFrequency: 'weekly',
    coverageAreas: ['legislation', 'policy', 'amendments', 'notifications'],
    description: 'Official government source for laws and legal policy'
  },
  
  {
    id: 'bangladesh_code',
    name: 'Bangladesh Code (Official)',
    nameInBangla: 'বাংলাদেশ কোড',
    baseUrl: 'http://bdlaws.minlaw.gov.bd',
    reliability: 0.99,
    category: 'legislative',
    searchCapable: true,
    searchMethod: 'api',
    updateFrequency: 'monthly',
    coverageAreas: ['acts', 'ordinances', 'rules', 'regulations'],
    description: 'Complete database of Bangladesh laws and regulations'
  },

  // Judicial Sources
  {
    id: 'supreme_court_bd',
    name: 'Supreme Court of Bangladesh',
    nameInBangla: 'বাংলাদেশ সুপ্রিম কোর্ট',
    baseUrl: 'https://supremecourt.gov.bd',
    reliability: 0.98,
    category: 'judicial',
    searchCapable: true,
    searchMethod: 'scraping',
    updateFrequency: 'daily',
    coverageAreas: ['judgments', 'case_law', 'precedents', 'court_rules'],
    description: 'Highest court judgments and legal precedents'
  },

  {
    id: 'high_court_bd',
    name: 'High Court Division',
    nameInBangla: 'হাইকোর্ট বিভাগ',
    baseUrl: 'https://hcd.gov.bd',
    reliability: 0.96,
    category: 'judicial',
    searchCapable: true,
    searchMethod: 'scraping',
    updateFrequency: 'daily',
    coverageAreas: ['high_court_judgments', 'writs', 'constitutional_matters'],
    description: 'High Court Division judgments and orders'
  },

  // Legal Aid Organizations
  {
    id: 'blast_bd',
    name: 'Bangladesh Legal Aid and Services Trust',
    nameInBangla: 'বাংলাদেশ আইনি সহায়তা ও সেবা ট্রাস্ট',
    baseUrl: 'https://www.blast.org.bd',
    reliability: 0.95,
    category: 'legal_aid',
    searchCapable: true,
    searchMethod: 'scraping',
    updateFrequency: 'weekly',
    coverageAreas: ['legal_aid', 'human_rights', 'public_interest', 'advice'],
    description: 'Leading legal aid organization providing free legal services',
    contactInfo: {
      phone: '+880-2-9611402',
      emergencyLine: '16430',
      email: 'info@blast.org.bd'
    }
  },

  {
    id: 'dlac_bd',
    name: 'Directorate of Legal Aid',
    nameInBangla: 'আইনি সহায়তা অধিদপ্তর',
    baseUrl: 'https://dlac.gov.bd',
    reliability: 0.94,
    category: 'government',
    searchCapable: true,
    searchMethod: 'scraping',
    updateFrequency: 'weekly',
    coverageAreas: ['legal_aid', 'government_services', 'citizen_rights'],
    description: 'Government legal aid services directorate'
  },

  // Human Rights Organizations
  {
    id: 'nhrc_bd',
    name: 'National Human Rights Commission',
    nameInBangla: 'জাতীয় মানবাধিকার কমিশন',
    baseUrl: 'https://nhrc.org.bd',
    reliability: 0.93,
    category: 'human_rights',
    searchCapable: true,
    searchMethod: 'scraping',
    updateFrequency: 'weekly',
    coverageAreas: ['human_rights', 'complaints', 'investigations', 'reports'],
    description: 'National human rights protection and monitoring'
  },

  {
    id: 'hrpb',
    name: 'Human Rights and Peace for Bangladesh',
    nameInBangla: 'বাংলাদেশের জন্য মানবাধিকার ও শান্তি',
    baseUrl: 'https://www.hrpb.org',
    reliability: 0.85,
    category: 'human_rights',
    searchCapable: true,
    searchMethod: 'scraping',
    updateFrequency: 'weekly',
    coverageAreas: ['human_rights', 'advocacy', 'monitoring', 'reports'],
    description: 'Human rights advocacy and monitoring organization'
  },

  // Professional Bodies
  {
    id: 'bar_council_bd',
    name: 'Bangladesh Bar Council',
    nameInBangla: 'বাংলাদেশ বার কাউন্সিল',
    baseUrl: 'https://www.bangladeshbarcouncil.org',
    reliability: 0.92,
    category: 'professional',
    searchCapable: true,
    searchMethod: 'scraping',
    updateFrequency: 'monthly',
    coverageAreas: ['legal_profession', 'ethics', 'regulations', 'licensing'],
    description: 'Regulatory body for legal profession in Bangladesh'
  },

  {
    id: 'dshe_bar',
    name: 'Dhaka Bar Association',
    nameInBangla: 'ঢাকা বার এসোসিয়েশন',
    baseUrl: 'https://www.dhakabar.org',
    reliability: 0.88,
    category: 'professional',
    searchCapable: false,
    searchMethod: 'scraping',
    updateFrequency: 'monthly',
    coverageAreas: ['local_legal_issues', 'lawyer_directory', 'advocacy'],
    description: 'Dhaka district bar association'
  },

  // Academic Sources
  {
    id: 'du_law',
    name: 'University of Dhaka Law Faculty',
    nameInBangla: 'ঢাকা বিশ্ববিদ্যালয় আইন অনুষদ',
    baseUrl: 'https://www.law.du.ac.bd',
    reliability: 0.87,
    category: 'academic',
    searchCapable: true,
    searchMethod: 'scraping',
    updateFrequency: 'monthly',
    coverageAreas: ['legal_research', 'academic_papers', 'law_journals'],
    description: 'Premier law faculty academic resources'
  },

  // International Sources (for comparative law)
  {
    id: 'un_ohchr',
    name: 'UN Office of High Commissioner for Human Rights',
    nameInBangla: 'জাতিসংঘ মানবাধিকার হাইকমিশনার কার্যালয়',
    baseUrl: 'https://www.ohchr.org',
    reliability: 0.96,
    category: 'international',
    searchCapable: true,
    searchMethod: 'api',
    updateFrequency: 'weekly',
    coverageAreas: ['international_law', 'human_rights', 'treaties', 'monitoring'],
    description: 'International human rights standards and monitoring'
  }
];

// Emergency Contact Numbers for Legal Assistance
export const EMERGENCY_LEGAL_CONTACTS = {
  legal_aid_helpline: '16430',
  police_emergency: '999',
  fire_emergency: '199',
  blast_hotline: '+880-2-9611402',
  women_helpline: '109',
  child_helpline: '1098',
  anti_corruption: '106'
};

// Quick Reference Legal Categories
export const LEGAL_CATEGORIES = {
  criminal_law: ['arrest', 'police', 'crime', 'criminal', 'bail', 'custody'],
  civil_law: ['contract', 'property', 'tort', 'civil', 'damages'],
  family_law: ['marriage', 'divorce', 'child', 'custody', 'maintenance'],
  constitutional_law: ['rights', 'constitution', 'fundamental', 'petition'],
  labour_law: ['employment', 'worker', 'labour', 'workplace', 'salary'],
  commercial_law: ['business', 'company', 'trade', 'commercial', 'banking'],
  administrative_law: ['government', 'service', 'administration', 'public'],
  tax_law: ['tax', 'vat', 'income', 'customs', 'revenue']
};

// Source Priority Matrix (for different types of queries)
export const SOURCE_PRIORITY_MATRIX = {
  arrest_rights: ['supreme_court_bd', 'blast_bd', 'nhrc_bd', 'bangladesh_code'],
  property_disputes: ['bangladesh_code', 'high_court_bd', 'dlac_bd'],
  labour_issues: ['molj_bd', 'blast_bd', 'bangladesh_code'],
  family_matters: ['bangladesh_code', 'blast_bd', 'dlac_bd'],
  human_rights: ['nhrc_bd', 'blast_bd', 'hrpb', 'un_ohchr'],
  constitutional: ['supreme_court_bd', 'high_court_bd', 'bangladesh_code'],
  business_law: ['molj_bd', 'bangladesh_code', 'bar_council_bd']
};

export default TRUSTED_LEGAL_SOURCES;