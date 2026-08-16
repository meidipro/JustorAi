import type { Language } from './services';

const copy = {
  en: {
    library: 'Library', guides: 'Guides', updates: 'Updates', trust: 'Trust', about: 'About', signIn: 'Sign In', start: 'Start Justor',
    controlledBeta: 'Controlled beta', primarySource: 'Primary Source', sourceChecked: 'Source Checked', humanReviewed: 'Human Legal Reviewed', sourceLinked: 'Source linked',
    unavailableTitle: 'This section has no published records.', unavailableBody: 'Nothing is shown here until a connected record is ready for public use.',
    noResults: 'No matching published record was found.', noResultsBody: 'Try a broader term or another category.', search: 'Search', continue: 'Continue', menu: 'Menu', close: 'Close', language: 'বাংলা',
    heroKicker: 'Bangladesh Legal Intelligence', heroHeadline: 'Choose how you use Justor.', heroBody: 'Research, learn, or find practical legal guidance.',
    citizen: 'Citizen', student: 'Law Student', professional: 'Legal Professional', citizenPromise: 'Know what to do next.', studentPromise: 'Learn from the law itself.', professionalPromise: 'Research with authority.',
    citizenBody: 'Practical guidance, evidence and official routes.', studentBody: 'Understand statutes, cases and legal concepts with AI.', professionalBody: 'Laws, cases, amendments and source-linked research.', exploreLibrary: 'Explore Legal Library',
    productProof: 'Product proof', verifyHeading: "Don't just get an answer.<br>Verify it.", verifyBody: 'Citations are controls—not decoration. Select one to inspect the supporting authority.',
    libraryHeading: 'Start with the law.<br>Then use AI.', libraryExplore: 'Explore the library', libraryPlaceholder: 'Search an Act, section, case or legal topic...',
    trustMethod: 'Trust method', trustHeading: 'Important legal information should lead back to authority.', trustBody: 'Primary Source identifies the authority itself. Source Checked describes a checked relationship. Human Legal Reviewed applies only to an approved content version.', readTrust: 'Read the Trust Method',
    incubation: 'Incubation', incubationStatement: 'Justor AI is incubated at NSU Startups Next.', incubationSupport: "Part of the NSU Startups Next incubation program, supporting the team's product development, validation and startup growth.",
    earlyHeading: 'Help shape the next version of Justor.', earlyBody: 'Early access is available for citizens, law students and legal professionals.', earlyCta: 'Request early access',
    startHeading: 'How will you use Justor?', startBody: 'One platform. Three purpose-built experiences. You can switch later.',
    continueCitizen: 'Continue as Citizen', continueStudent: 'Continue as Law Student', continueProfessional: 'Continue as Legal Professional',
    professionalKicker: 'Professional Research', professionalHeading: 'What are you researching?', professionalSubtitle: 'Search Bangladesh law, locate authority or check the current legal position.', professionalPlaceholder: 'Describe an issue, find precedent, locate a provision or check current law...',
    researchIssue: 'Research Legal Issue', findPrecedent: 'Find Precedent', findStatute: 'Find Statute', checkAmendment: 'Check Amendment', recentUpdates: 'Recent Legal Updates', secondaryModule: 'Secondary module', viewAll: 'View all',
    sourcesShown: 'Sources shown with live answers', switchExperience: 'Switch experience', newResearch: 'New Research',
    signInQuotaPrefix: 'Sign in to use', answersPerDay: 'AI answers per day during beta', dailyAllowance: 'Daily allowance',
    researchHome: 'Research Home', legalLibrary: 'Legal Library', cases: 'Cases', statutes: 'Statutes', amendments: 'Amendments', studyHome: 'Study Home', askJustor: 'Ask Justor', concepts: 'Concepts', home: 'Home',
    mobileResearch: 'Research', mobileStudy: 'Study', mobileAsk: 'Ask', mobileStart: 'Start',
    studentKicker: 'Justor for Law Students', studentHeading: 'Learn cases, statutes and legal principles with source-linked AI assistance.', studentAllowance: '30 AI answers per day during beta.', continueGoogle: 'Continue with Google', publicReading: 'Public library and guide reading remain available without an account.',
    citizenKicker: 'Practical legal guidance', citizenHeading: 'What happened?', citizenSubtitle: 'Describe your problem or choose a topic. Justor checks the Citizen Legal Guides first.', problemPlaceholder: 'Describe your problem in your own words...', findGuidance: 'Find guidance', chooseTopic: 'Choose a topic', citizenGuides: 'Citizen Legal Guides', publishedGuidance: 'Published guidance', browseDirectory: 'Browse directory',
    couldntFind: "Couldn't find what you need?", askSituation: 'Ask Justor about your situation.', citizenAiGate: 'AI access requires Google Sign-In. Citizen beta includes 3 AI answers per day.', continueBrowsing: 'Continue browsing guides',
    libraryPageHeading: 'Search Bangladesh law.', libraryPageBody: 'Find canonical laws, sections, cases, amendments, guides and updates from the connected legal source.', publishedRecords: 'published records returned',
    guidePageHeading: 'Find the practical route.', guidePageBody: 'Search published guidance by problem or browse a clear topic directory.', guidePlaceholder: 'Search a problem or keyword...', topics: 'Topics', publishedLibrary: 'Published library', browseGuides: 'Browse guides', loadMore: 'Load more',
    updatesHeading: 'Track what changed.', updatesBody: 'Amendments, procedural changes and official sources returned by the connected legal-data service.',
    loginKicker: 'Bangladesh Legal Intelligence', loginBrandHeading: 'Continue with authority beside the answer.', loginBrandBody: 'Google Sign-In protects AI access, quota and saved workspace data.', loginHeading: 'Continue to Justor', loginBody: 'Use Google to continue to your selected experience.', returnPublic: 'Return to public website',
  },
  bn: {
    library: 'লাইব্রেরি', guides: 'গাইড', updates: 'আপডেট', trust: 'বিশ্বাসযোগ্যতা', about: 'আমাদের সম্পর্কে', signIn: 'সাইন ইন', start: 'জাস্টর শুরু করুন',
    controlledBeta: 'নিয়ন্ত্রিত বেটা', primarySource: 'প্রাথমিক উৎস', sourceChecked: 'উৎস যাচাইকৃত', humanReviewed: 'আইন বিশেষজ্ঞ কর্তৃক পর্যালোচিত', sourceLinked: 'উৎস সংযুক্ত',
    unavailableTitle: 'এই অংশে কোনো প্রকাশিত রেকর্ড নেই।', unavailableBody: 'প্রকাশের জন্য প্রস্তুত সংযুক্ত রেকর্ড না আসা পর্যন্ত এখানে কিছু দেখানো হবে না।',
    noResults: 'মিলযুক্ত প্রকাশিত রেকর্ড পাওয়া যায়নি।', noResultsBody: 'আরও সাধারণ শব্দ বা অন্য বিভাগ দিয়ে চেষ্টা করুন।', search: 'খুঁজুন', continue: 'এগিয়ে যান', menu: 'মেনু', close: 'বন্ধ করুন', language: 'EN',
    heroKicker: 'বাংলাদেশের আইনি তথ্য ও গবেষণা', heroHeadline: 'আপনি Justor কীভাবে ব্যবহার করবেন?', heroBody: 'গবেষণা করুন, শিখুন অথবা ব্যবহারিক আইনি নির্দেশনা খুঁজুন।',
    citizen: 'নাগরিক', student: 'আইনের শিক্ষার্থী', professional: 'আইন পেশাজীবী', citizenPromise: 'পরবর্তী করণীয় জানুন।', studentPromise: 'মূল আইন থেকেই শিখুন।', professionalPromise: 'কর্তৃত্বপূর্ণ উৎসসহ গবেষণা করুন।',
    citizenBody: 'বাস্তব করণীয়, প্রমাণ ও সরকারি সেবার পথ।', studentBody: 'উৎস-সংযুক্ত সহায়তায় মামলা, আইন ও আইনি ধারণা।', professionalBody: 'যাচাইযোগ্য উৎসসহ আইন, মামলা, সংশোধনী ও আইনি বিষয়।', exploreLibrary: 'আইনি লাইব্রেরি দেখুন',
    productProof: 'পণ্যের প্রমাণ', verifyHeading: 'শুধু উত্তর নয়।<br>উৎসও যাচাই করুন।', verifyBody: 'উদ্ধৃতিগুলো কেবল সাজসজ্জা নয়। সহায়ক কর্তৃত্বপূর্ণ উৎস দেখতে উদ্ধৃতি নির্বাচন করুন।',
    libraryHeading: 'আগে আইন দেখুন।<br>তারপর এআই ব্যবহার করুন।', libraryExplore: 'লাইব্রেরি দেখুন', libraryPlaceholder: 'আইন, ধারা, মামলা বা আইনি বিষয় খুঁজুন...',
    trustMethod: 'বিশ্বাসযোগ্যতার পদ্ধতি', trustHeading: 'গুরুত্বপূর্ণ আইনি তথ্যের সঙ্গে কর্তৃত্বপূর্ণ উৎস থাকা উচিত।', trustBody: 'Primary Source মূল কর্তৃপক্ষকে চিহ্নিত করে। Source Checked মানে উৎস ও বক্তব্যের সম্পর্ক যাচাই করা হয়েছে। Human Legal Reviewed কেবল অনুমোদিত নির্দিষ্ট সংস্করণে প্রযোজ্য।', readTrust: 'বিশ্বাসযোগ্যতার পদ্ধতি পড়ুন',
    incubation: 'ইনকিউবেশন', incubationStatement: 'Justor AI, NSU Startups Next-এ ইনকিউবেটেড।', incubationSupport: 'NSU Startups Next ইনকিউবেশন প্রোগ্রামের অংশ হিসেবে দলটি পণ্য উন্নয়ন, যাচাই ও স্টার্টআপ বিকাশে সহায়তা পাচ্ছে।',
    earlyHeading: 'Justor-এর পরবর্তী সংস্করণ গড়তে সহায়তা করুন।', earlyBody: 'নাগরিক, আইনের শিক্ষার্থী ও আইন পেশাজীবীদের জন্য প্রাথমিক প্রবেশাধিকার রয়েছে।', earlyCta: 'প্রাথমিক প্রবেশাধিকার চান',
    startHeading: 'আপনি Justor কীভাবে ব্যবহার করবেন?', startBody: 'একটি প্ল্যাটফর্ম। তিনটি উদ্দেশ্যভিত্তিক অভিজ্ঞতা। পরে পরিবর্তন করতে পারবেন।',
    continueCitizen: 'নাগরিক হিসেবে এগিয়ে যান', continueStudent: 'শিক্ষার্থী হিসেবে এগিয়ে যান', continueProfessional: 'আইন পেশাজীবী হিসেবে এগিয়ে যান',
    professionalKicker: 'পেশাগত আইনি গবেষণা', professionalHeading: 'আপনি কী নিয়ে গবেষণা করছেন?', professionalSubtitle: 'বাংলাদেশের আইন খুঁজুন, কর্তৃত্বপূর্ণ উৎস দেখুন বা বর্তমান আইনি অবস্থান যাচাই করুন।', professionalPlaceholder: 'একটি আইনি বিষয় লিখুন, নজির বা ধারা খুঁজুন, কিংবা সংশোধনী যাচাই করুন...',
    researchIssue: 'আইনি বিষয় গবেষণা', findPrecedent: 'নজির খুঁজুন', findStatute: 'আইন খুঁজুন', checkAmendment: 'সংশোধনী যাচাই', recentUpdates: 'সাম্প্রতিক আইনি আপডেট', secondaryModule: 'সহায়ক অংশ', viewAll: 'সব দেখুন',
    sourcesShown: 'লাইভ উত্তরের সঙ্গে উৎস দেখানো হবে', switchExperience: 'অভিজ্ঞতা পরিবর্তন', newResearch: 'নতুন গবেষণা',
    signInQuotaPrefix: 'ব্যবহার করতে সাইন ইন করুন:', answersPerDay: 'টি এআই উত্তর প্রতিদিন (বেটা)', dailyAllowance: 'দৈনিক সীমা',
    researchHome: 'গবেষণা হোম', legalLibrary: 'আইনি লাইব্রেরি', cases: 'মামলা', statutes: 'আইনসমূহ', amendments: 'সংশোধনী', studyHome: 'পড়াশোনার হোম', askJustor: 'Justor-কে জিজ্ঞাসা করুন', concepts: 'আইনি ধারণা', home: 'হোম',
    mobileResearch: 'গবেষণা', mobileStudy: 'পড়াশোনা', mobileAsk: 'জিজ্ঞাসা', mobileStart: 'শুরু',
    studentKicker: 'আইনের শিক্ষার্থীদের জন্য Justor', studentHeading: 'উৎস-সংযুক্ত এআই সহায়তায় মামলা, আইন ও আইনি নীতি শিখুন।', studentAllowance: 'বেটা পর্যায়ে প্রতিদিন ৩০টি এআই উত্তর।', continueGoogle: 'Google দিয়ে এগিয়ে যান', publicReading: 'অ্যাকাউন্ট ছাড়াই পাবলিক লাইব্রেরি ও গাইড পড়া যাবে।',
    citizenKicker: 'ব্যবহারিক আইনি নির্দেশনা', citizenHeading: 'কী ঘটেছে?', citizenSubtitle: 'আপনার সমস্যা লিখুন বা একটি বিষয় বেছে নিন। Justor প্রথমে Citizen Legal Guides-এ খুঁজবে।', problemPlaceholder: 'নিজের ভাষায় আপনার সমস্যাটি লিখুন...', findGuidance: 'নির্দেশনা খুঁজুন', chooseTopic: 'একটি বিষয় বেছে নিন', citizenGuides: 'নাগরিক আইনি গাইড', publishedGuidance: 'প্রকাশিত নির্দেশনা', browseDirectory: 'গাইড তালিকা দেখুন',
    couldntFind: 'প্রয়োজনীয় তথ্য খুঁজে পাননি?', askSituation: 'আপনার পরিস্থিতি সম্পর্কে Justor-কে জিজ্ঞাসা করুন।', citizenAiGate: 'এআই ব্যবহারের জন্য Google Sign-In প্রয়োজন। নাগরিক বেটায় প্রতিদিন ৩টি এআই উত্তর রয়েছে।', continueBrowsing: 'গাইড দেখা চালিয়ে যান',
    libraryPageHeading: 'বাংলাদেশের আইন খুঁজুন।', libraryPageBody: 'সংযুক্ত আইনি উৎস থেকে আইন, ধারা, মামলা, সংশোধনী, গাইড ও আপডেট খুঁজুন।', publishedRecords: 'টি প্রকাশিত রেকর্ড পাওয়া গেছে',
    guidePageHeading: 'ব্যবহারিক সমাধানের পথ খুঁজুন।', guidePageBody: 'সমস্যা লিখে প্রকাশিত নির্দেশনা খুঁজুন বা পরিষ্কার বিষয়ভিত্তিক তালিকা দেখুন।', guidePlaceholder: 'সমস্যা বা মূল শব্দ লিখে খুঁজুন...', topics: 'বিষয়সমূহ', publishedLibrary: 'প্রকাশিত লাইব্রেরি', browseGuides: 'গাইড দেখুন', loadMore: 'আরও দেখুন',
    updatesHeading: 'কী পরিবর্তন হয়েছে দেখুন।', updatesBody: 'সংযুক্ত আইনি-তথ্য সেবা থেকে সংশোধনী, প্রক্রিয়াগত পরিবর্তন ও সরকারি উৎস দেখানো হয়।',
    loginKicker: 'বাংলাদেশের আইনি তথ্য ও গবেষণা', loginBrandHeading: 'উত্তরের পাশেই কর্তৃত্বপূর্ণ উৎস রাখুন।', loginBrandBody: 'Google Sign-In এআই ব্যবহার, কোটা ও সংরক্ষিত ওয়ার্কস্পেস তথ্য সুরক্ষিত রাখে।', loginHeading: 'Justor-এ এগিয়ে যান', loginBody: 'আপনার নির্বাচিত অভিজ্ঞতায় যেতে Google ব্যবহার করুন।', returnPublic: 'পাবলিক ওয়েবসাইটে ফিরুন',
  },
} as const;

export type CopyKey = keyof typeof copy.en;

export const ui = (language: Language, key: CopyKey): string => copy[language][key];

export const parseLocalizedPath = (pathname: string): { language: Language; routePath: string } => {
  if (pathname === '/bn' || pathname.startsWith('/bn/')) {
    const routePath = pathname.slice(3) || '/';
    return { language: 'bn', routePath };
  }
  return { language: 'en', routePath: pathname || '/' };
};

export const localizedPath = (path: string, language: Language): string => {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  if (language === 'en') return normalized;
  return normalized === '/' ? '/bn/' : `/bn${normalized}`;
};
