import type { Language, LegalSource } from './services';

export const copy = {
  en: {
    // Navigation & Roles
    legalProfessional: 'Legal Professional',
    lawStudent: 'Law Student',
    citizen: 'Citizen',
    student: 'Law Student',
    professional: 'Legal Professional',
    legalLibrary: 'Legal Library',
    library: 'Library',
    guides: 'Guides',
    updates: 'Updates',
    trust: 'Trust',
    about: 'About',
    team: 'Team',
    investors: 'Investors',
    signIn: 'Sign In',
    signOut: 'Sign Out',
    start: 'Start Justor',
    startJustor: 'Start Justor',
    resources: 'Resources',
    company: 'Company',
    product: 'Product',
    contact: 'Contact',
    language: 'বাংলা',
    menu: 'Menu',
    close: 'Close',
    continue: 'Continue',
    search: 'Search',
    cancel: 'Cancel',

    // Homepage
    controlledBeta: 'Controlled Beta',
    heroKicker: 'Bangladesh Legal Intelligence',
    heroHeadline: 'Choose how you use Justor.',
    heroBody: 'Research, learn, or find practical legal guidance.',
    professionalPromise: 'Research with authority.',
    studentPromise: 'Learn from the law itself.',
    citizenPromise: 'Know what to do next.',
    citizenBody: 'Find practical legal guidance.',
    studentBody: 'Learn cases and statutes.',
    professionalBody: 'Research laws and authority.',
    libraryHeading: 'Start with the law.<br>Then use AI.',
    libraryExplore: 'Explore Legal Library',
    exploreLibrary: 'Explore Legal Library',
    libraryPlaceholder: 'Search laws, sections, cases, updates…',
    homepageTagline: 'Bangladesh legal intelligence for guidance, learning and professional research.',
    verifyHeading: "Don't just get an answer.<br>Verify it.",
    verifyBody: 'Citations are controls—not decoration. Select one to inspect the supporting authority.',
    trustHeading: 'Important legal information should lead back to authority.',
    trustBody: 'Primary Source identifies the authority itself. Source Checked describes a checked relationship. Human Legal Reviewed applies only to an approved content version.',
    trustMethod: 'Trust Method',
    readTrust: 'Read the Trust Method',
    productProof: 'Live Verification Engine',

    // Incubation & Early Access
    incubation: 'Incubated by NSU Startups Next',
    incubationStatement: 'Backed by North South University incubation.',
    incubationSupport: 'Justor AI is developed with institutional mentorship and legal tech domain guidance.',
    earlyHeading: 'Request early access.',
    earlyBody: 'Join law chambers, legal clinics and universities shaping the future of Bangladesh legal intelligence.',
    earlyCta: 'Request Early Access',
    startHeading: 'Choose how you start.',
    startBody: 'Select your role to access customized legal intelligence and workflows.',

    // Citizen Sectors
    sectorProperty: 'Property & Land',
    sectorPropertyDesc: 'Disputes, inheritance, buying, renting',
    sectorFamily: 'Family & Marriage',
    sectorFamilyDesc: 'Divorce, custody, dowry, maintenance',
    sectorCriminal: 'Criminal & Police',
    sectorCriminalDesc: 'FIR, arrest, bail, complaints',
    sectorEmployment: 'Employment & Work',
    sectorEmploymentDesc: 'Unfair dismissal, unpaid wages, rights',
    sectorConsumer: 'Consumer & Contracts',
    sectorConsumerDesc: 'Fraud, loan disputes, contract issues',
    sectorRights: 'Rights & Documents',
    sectorRightsDesc: 'NID, passport, birth certificate',
    sectorBusiness: 'Business & Licensing',
    sectorBusinessDesc: 'Permits, trade license issues',

    // Citizen Guide Page Sections
    guideInvolves: 'What this situation involves',
    guideWhatToDo: 'What to do now',
    guideDocuments: 'Documents and evidence to keep',
    guideWhereToGo: 'Where to go',
    guideDeadlines: 'Important deadlines',
    guideWhenLawyer: 'When you need a lawyer',
    guideAskAi: 'Still confused? Ask Justor AI →',
    citizenDisclaimer: 'ℹ️ Justor provides a basic overview and general navigation guidance only. This is not legal advice. Consult a qualified lawyer in Bangladesh for advice on your specific case.',

    // Chat Workspace & Telemetry
    newResearch: 'New Research',
    recentResearch: 'Recent Research',
    askPlaceholder: 'Ask a legal question about Bangladesh law...',
    howAnswerProduced: 'How this answer was produced',
    sources: 'Sources',
    pendingVerification: 'Pending verification',
    sourceChecked: 'Source-checked',
    reporterVerified: 'Reporter verified',
    unreviewedCorpus: 'Unreviewed corpus',
    humanLegalReviewed: 'Human legal reviewed',
    viewFullProvision: 'View full provision',
    deleteResearchThread: 'Delete research thread',
    thisIsHelpful: 'This is helpful',
    reportAnIssue: 'Report an issue',
    copyAnswer: 'Copy answer',
    researchWithAuthority: 'Research with authority',
    directAnswer: 'Direct Answer',
    keyLegalBasis: 'Key Legal Basis',
    fullAnalysis: 'Full Analysis',
    professionalHelpHeading: 'Professional Legal Counsel',
    composerPrivacyHint: 'ℹ️ Remove names, NID/passport numbers, phone numbers and case identifiers unless essential.',
    researchingLoading: 'Researching Bangladesh law...',
    switchExperience: 'Switch experience',
    dailyAllowance: 'Daily allowance',
    signInQuotaPrefix: 'Sign in for',
    answersPerDay: 'answers per day',
    researchIssue: 'Describe an issue',
    findPrecedent: 'Find precedent',
    findStatute: 'Locate a provision',
    checkAmendment: 'Check current law',

    // Status Banners
    allSourcesChecked: 'All sources source-checked',
    someSourcesPending: 'Some sources not yet verified',
    basedOnAvailable: 'Based on available sources',

    // Error & Empty States
    noResults: 'No records found',
    noResultsBody: 'No matching records found in the corpus.',
    noResultsFound: 'No results found',
    noMatchingRecords: 'No matching records found in the corpus.',
    responseTimeout: 'Response timed out. Try again.',
    researchUnavailable: 'Research unavailable right now.',
    dailyLimitReached: 'Your daily limit has been reached.',
    signInToContinue: 'Sign in to continue.',
    sourceUrlNotIndexed: 'Source URL not yet indexed. Provision text shown above.',
    guestBannerNudge: "You're browsing as a guest. Sign in to save your research.",
    unavailableTitle: 'This section has no published records.',
    unavailableBody: 'Nothing is shown here until a connected record is ready for public use.',

    // Feedback Categories & Survey
    feedbackPrompt: 'Was this legal analysis accurate and helpful?',
    feedbackHelpful: 'Helpful',
    feedbackReportIssue: 'Report an issue',
    whatWentWrong: 'What went wrong?',
    selectIssueCategory: 'Select category...',
    wrongLaw: 'Wrong law or statute applied',
    wrongCitation: 'Incorrect section or case citation',
    outdatedLaw: 'Outdated or superseded legal text',
    missingAuthority: 'Missed a mandatory controlling authority',
    incompleteAnswer: 'Incomplete legal analysis',
    misunderstoodQuestion: 'Misunderstood facts / scenario',
    otherIssue: 'Other issue',
    submitFeedback: 'Submit Feedback',
    fbWrongLaw: 'Wrong law cited',
    fbWrongCitation: 'Wrong citation',
    fbOutdatedInfo: 'Outdated information',
    fbMissingAuthority: 'Missing authority',
    fbIncompleteAnswer: 'Incomplete answer',
    fbMisunderstood: 'Misunderstood question',
    fbOther: 'Other',
    feedbackRecorded: 'Your report has been recorded and queued for review.',

    // Public Library & Guides
    libraryPageHeading: 'Legal Library',
    libraryPageBody: 'Explore canonical laws, statutory sections, case precedents, and legal updates.',
    publishedRecords: 'Published canonical records',
    guidePageHeading: 'Citizen Legal Guides',
    guidePageBody: 'Plain-language legal guidance, procedures, and evidence checklists for Bangladesh citizens.',
    guidePlaceholder: 'Search legal guides by topic or problem...',
    topics: 'Topics',
    publishedLibrary: 'Published in Library',
    browseGuides: 'Browse Guides',
    loadMore: 'Load more',
    updatesHeading: 'Legal Updates & Gazette Notifications',
    updatesBody: 'Recent statutory amendments, High Court directives, and regulatory gazette notifications.',
    publicReading: 'Public reading mode',

    // Workspaces specific
    professionalKicker: 'Professional Legal Research',
    professionalHeading: 'What are you researching?',
    professionalSubtitle: 'Search Bangladesh law, locate authority or check the current legal position.',
    professionalPlaceholder: 'Describe an issue, find precedent, locate a provision or check current law...',
    studentKicker: 'Justor for Law Students',
    studentHeading: 'Learn cases, statutes and legal principles with source-linked AI assistance.',
    studentAllowance: '30 AI answers per day during beta.',
    citizenKicker: 'Practical Legal Guidance',
    citizenHeading: 'What happened?',
    citizenSubtitle: 'Describe your problem or choose a topic. Justor checks the Citizen Legal Guides first.',
    problemPlaceholder: 'Describe your problem in your own words...',
    findGuidance: 'Find guidance',
    chooseTopic: 'Choose a topic',
    citizenGuides: 'Citizen Legal Guides',
    publishedGuidance: 'Published guidance',
    browseDirectory: 'Browse directory',
    primarySource: 'Primary Source',
    humanReviewed: 'Human Legal Reviewed',
    sourceLinked: 'Source linked',
    researchHome: 'Research Home',
    cases: 'Cases',
    statutes: 'Statutes',
    amendments: 'Amendments',
    studyHome: 'Study Home',
    askJustor: 'Ask Justor',
    concepts: 'Concepts',
    home: 'Home',
    mobileResearch: 'Research',
    mobileStudy: 'Study',
    mobileAsk: 'Ask',
    mobileStart: 'Start',
    continueCitizen: 'Continue as Citizen',
    continueStudent: 'Continue as Law Student',
    continueProfessional: 'Continue as Legal Professional',
    continueGoogle: 'Continue with Google',
    loginKicker: 'Bangladesh Legal Intelligence',
    loginBrandHeading: 'Continue with authority beside the answer.',
    loginBrandBody: 'Your research is encrypted and stored securely. You control what you share.',
    loginHeading: 'Sign in to Justor',
    loginBody: 'Your research is encrypted and stored securely. You control what you share.',
    returnPublic: 'Return to public website',
    profile: 'User Profile',
    profileHeading: 'Account & Legal Research Settings',
    profileSubtitle: 'Manage your advocate profile, subscription tier, Google Cloud AI quota, and research privacy.',
    accountSettings: 'Account Settings',
    saveSettings: 'Save Changes',
    personalDetails: 'Personal & Chamber Details',
    fullName: 'Full Name',
    emailAddress: 'Email Address',
    chamberName: 'Chamber / Firm Name',
    barAssociation: 'Bar Association',
    practiceAreas: 'Practice Areas',
    subscriptionCloud: 'Membership & Google Cloud AI Infrastructure',
    cloudCredits: 'Google Cloud AI Partner ($2,000 Credits Active)',
    researchPreferences: 'AI Research Preferences',
    dataPrivacy: 'Data Privacy & Local Storage',
    clearAllHistory: 'Clear All Research Threads',
    exportData: 'Export Research History (JSON)',
  },
  bn: {
    // Navigation & Roles
    legalProfessional: 'আইনি পেশাদার',
    lawStudent: 'আইন শিক্ষার্থী',
    citizen: 'সাধারণ নাগরিক',
    student: 'আইন শিক্ষার্থী',
    professional: 'আইনি পেশাদার',
    legalLibrary: 'আইনি লাইব্রেরি',
    library: 'লাইব্রেরি',
    guides: 'গাইড',
    updates: 'আপডেট',
    trust: 'বিশ্বাসযোগ্যতা',
    about: 'আমাদের সম্পর্কে',
    team: 'দল',
    investors: 'বিনিয়োগকারী',
    signIn: 'সাইন ইন',
    signOut: 'সাইন আউট',
    start: 'জাস্টর শুরু করুন',
    startJustor: 'জাস্টর শুরু করুন',
    resources: 'সম্পদ',
    company: 'কোম্পানি',
    product: 'পণ্য',
    contact: 'যোগাযোগ',
    language: 'EN',
    menu: 'মেনু',
    close: 'বন্ধ করুন',
    continue: 'এগিয়ে যান',
    search: 'খুঁজুন',
    cancel: 'বাতিল',

    // Homepage
    controlledBeta: 'নিয়ন্ত্রিত বেটা',
    heroKicker: 'বাংলাদেশের আইনি বুদ্ধিমত্তা',
    heroHeadline: 'কীভাবে জাস্টর ব্যবহার করবেন তা বেছে নিন।',
    heroBody: 'গবেষণা করুন, শিখুন, অথবা ব্যবহারিক আইনি নির্দেশনা খুঁজুন।',
    professionalPromise: 'কর্তৃত্বের সাথে গবেষণা করুন।',
    studentPromise: 'আইন থেকে সরাসরি শিখুন।',
    citizenPromise: 'পরবর্তী পদক্ষেপ জানুন।',
    citizenBody: 'ব্যবহারিক আইনি নির্দেশনা খুঁজুন।',
    studentBody: 'মামলা ও আইন থেকে শিখুন।',
    professionalBody: 'আইন ও কর্তৃত্বপূর্ণ উৎস গবেষণা করুন।',
    libraryHeading: 'আইন দিয়ে শুরু করুন।<br>তারপর AI ব্যবহার করুন।',
    libraryExplore: 'আইনি লাইব্রেরি দেখুন',
    exploreLibrary: 'আইনি লাইব্রেরি দেখুন',
    libraryPlaceholder: 'আইন, ধারা, মামলা, আপডেট খুঁজুন…',
    homepageTagline: 'নির্দেশনা, শিক্ষা ও পেশাদার গবেষণার জন্য বাংলাদেশের আইনি বুদ্ধিমত্তা।',
    verifyHeading: 'শুধু উত্তর নয়।<br>উৎসও যাচাই করুন।',
    verifyBody: 'উদ্ধৃতিগুলো কেবল সাজসজ্জা নয়। সহায়ক কর্তৃত্বপূর্ণ উৎস দেখতে উদ্ধৃতি নির্বাচন করুন।',
    trustHeading: 'গুরুত্বপূর্ণ আইনি তথ্যের সঙ্গে কর্তৃত্বপূর্ণ উৎস থাকা উচিত।',
    trustBody: 'Primary Source মূল কর্তৃপক্ষকে চিহ্নিত করে। Source Checked মানে উৎস ও বক্তব্যের সম্পর্ক যাচাই করা হয়েছে। Human Legal Reviewed কেবল অনুমোদিত নির্দিষ্ট সংস্করণে প্রযোজ্য।',
    trustMethod: 'বিশ্বাসযোগ্যতার পদ্ধতি',
    readTrust: 'বিশ্বাসযোগ্যতার পদ্ধতি পড়ুন',
    productProof: 'লাইভ যাচাইকরণ ইঞ্জিন',

    // Incubation & Early Access
    incubation: 'এনএসইউ স্টার্টআপস নেক্সট কর্তৃক ইনকিউবেটেড',
    incubationStatement: 'নর্থ সাউথ ইউনিভার্সিটির ইনকিউবেশন সমর্থিত।',
    incubationSupport: 'জাস্টর এআই প্রাতিষ্ঠানিক মেন্টরশিপ ও লিগ্যাল টেক ডোমেইন নির্দেশনায় তৈরি।',
    earlyHeading: 'আর্লি এক্সেসের জন্য অনুরোধ করুন।',
    earlyBody: 'বাংলাদেশের আইনি বুদ্ধিমত্তার ভবিষ্যৎ রূপদানে ল চেম্বার, লিগ্যাল ক্লিনিক ও বিশ্ববিদ্যালয়ে যোগ দিন।',
    earlyCta: 'আর্লি এক্সেস অনুরোধ করুন',
    startHeading: 'কীভাবে শুরু করবেন তা বেছে নিন।',
    startBody: 'কাস্টমাইজড আইনি গবেষণা ও কার্যপ্রবাহ পেতে আপনার ভূমিকা নির্বাচন করুন।',

    // Citizen Sectors
    sectorProperty: 'সম্পত্তি ও জমি',
    sectorPropertyDesc: 'বিরোধ, উত্তরাধিকার, কেনাবেচা, ভাড়া',
    sectorFamily: 'পরিবার ও বিবাহ',
    sectorFamilyDesc: 'তালাক, হেফাজত, যৌতুক, ভরণপোষণ',
    sectorCriminal: 'অপরাধ ও পুলিশ',
    sectorCriminalDesc: 'এজাহার, গ্রেপ্তার, জামিন, অভিযোগ',
    sectorEmployment: 'চাকরি ও কর্মসংস্থান',
    sectorEmploymentDesc: 'অবৈধ বরখাস্ত, বকেয়া বেতন, শ্রম অধিকার',
    sectorConsumer: 'ভোক্তা ও চুক্তি',
    sectorConsumerDesc: 'প্রতারণা, ঋণ বিরোধ, চুক্তি সমস্যা',
    sectorRights: 'অধিকার ও দলিল',
    sectorRightsDesc: 'এনআইডি, পাসপোর্ট, জন্ম নিবন্ধন',
    sectorBusiness: 'ব্যবসা ও লাইসেন্স',
    sectorBusinessDesc: 'ব্যবসায়িক অনুমতি, ট্রেড লাইসেন্স',

    // Citizen Guide Page Sections
    guideInvolves: 'এই পরিস্থিতি কী',
    guideWhatToDo: 'এখন কী করবেন',
    guideDocuments: 'কোন কাগজপত্র রাখবেন',
    guideWhereToGo: 'কোথায় যাবেন',
    guideDeadlines: 'গুরুত্বপূর্ণ সময়সীমা',
    guideWhenLawyer: 'কখন আইনজীবী দরকার',
    guideAskAi: 'এখনও বুঝতে পারছেন না? জাস্টর AI-কে জিজ্ঞেস করুন →',
    citizenDisclaimer: 'ℹ️ জাস্টর শুধুমাত্র সাধারণ দিকনির্দেশনা এবং প্রাথমিক ধারণা প্রদান করে। এটি আইনি পরামর্শ নয়। আপনার নির্দিষ্ট পরিস্থিতির জন্য একজন যোগ্য বাংলাদেশী আইনজীবীর সাথে পরামর্শ করুন।',

    // Chat Workspace & Telemetry
    newResearch: 'নতুন গবেষণা',
    recentResearch: 'সাম্প্রতিক গবেষণা',
    askPlaceholder: 'একটি আইনি প্রশ্ন করুন...',
    howAnswerProduced: 'এই উত্তর কীভাবে তৈরি হয়েছে',
    sources: 'উৎস',
    pendingVerification: 'যাচাই অপেক্ষমান',
    sourceChecked: 'উৎস যাচাইকৃত',
    reporterVerified: 'রিপোর্টার যাচাইকৃত',
    unreviewedCorpus: 'পর্যালোচনা করা হয়নি',
    humanLegalReviewed: 'মানব আইনি পর্যালোচনা',
    viewFullProvision: 'সম্পূর্ণ বিধান দেখুন',
    deleteResearchThread: 'গবেষণা মুছুন',
    thisIsHelpful: 'এটি সহায়ক',
    reportAnIssue: 'একটি সমস্যা জানান',
    copyAnswer: 'উত্তর কপি করুন',
    researchWithAuthority: 'কর্তৃত্বের সাথে গবেষণা করুন',
    directAnswer: 'সরাসরি উত্তর',
    keyLegalBasis: 'সংশ্লিষ্ট আইনি ভিত্তি',
    fullAnalysis: 'বিস্তারিত বিশ্লেষণ',
    professionalHelpHeading: 'পেশাদার আইনি পরামর্শ',
    composerPrivacyHint: 'ℹ️ প্রয়োজন না হলে নাম, এনআইডি/পাসপোর্ট নম্বর, ফোন নম্বর এবং মামলার তথ্য লিখবেন না।',
    researchingLoading: 'বাংলাদেশের আইন খোঁজা হচ্ছে...',
    switchExperience: 'অভিজ্ঞতা পরিবর্তন করুন',
    dailyAllowance: 'দৈনিক সীমা',
    signInQuotaPrefix: 'সাইন ইন করলে',
    answersPerDay: 'টি উত্তর প্রতিদিন',
    researchIssue: 'একটি আইনি বিষয় লিখুন',
    findPrecedent: 'নজির খুঁজুন',
    findStatute: 'ধারা খুঁজুন',
    checkAmendment: 'আইন যাচাই করুন',

    // Status Banners
    allSourcesChecked: 'সমস্ত উৎস যাচাইকৃত',
    someSourcesPending: 'কিছু উৎস এখনও যাচাই হয়নি',
    basedOnAvailable: 'উপলব্ধ উৎসের ভিত্তিতে',

    // Error & Empty States
    noResults: 'কোনো রেকর্ড পাওয়া যায়নি',
    noResultsBody: 'কর্পাসে কোনো মিলযুক্ত রেকর্ড পাওয়া যায়নি।',
    noResultsFound: 'কোনো ফলাফল পাওয়া যায়নি',
    noMatchingRecords: 'কর্পাসে কোনো মিলযুক্ত রেকর্ড পাওয়া যায়নি।',
    responseTimeout: 'উত্তর আসতে দেরি হচ্ছে। আবার চেষ্টা করুন।',
    researchUnavailable: 'এই মুহূর্তে গবেষণা পরিষেবা উপলব্ধ নেই।',
    dailyLimitReached: 'আপনার দৈনিক সীমা শেষ হয়েছে।',
    signInToContinue: 'চালিয়ে যেতে সাইন ইন করুন।',
    sourceUrlNotIndexed: 'উৎস URL এখনও সংযুক্ত করা হয়নি। উপরে বিধানের পাঠ দেখুন।',
    guestBannerNudge: 'আপনি গেস্ট হিসেবে ব্রাউজ করছেন। গবেষণা সংরক্ষণ করতে সাইন ইন করুন।',
    unavailableTitle: 'এই অংশে কোনো প্রকাশিত রেকর্ড নেই।',
    unavailableBody: 'প্রকাশের জন্য প্রস্তুত সংযুক্ত রেকর্ড না আসা পর্যন্ত এখানে কিছু দেখানো হবে না।',

    // Feedback Categories & Survey
    feedbackPrompt: 'এই আইনি বিশ্লেষণ কি সঠিক ও সহায়ক ছিল?',
    feedbackHelpful: 'সহায়ক',
    feedbackReportIssue: 'সমস্যা জানান',
    whatWentWrong: 'কী সমস্যা হয়েছে?',
    selectIssueCategory: 'ক্যাটাগরি নির্বাচন করুন...',
    wrongLaw: 'ভুল আইন প্রয়োগ করা হয়েছে',
    wrongCitation: 'ভুল ধারা বা মামলার রেফারেন্স',
    outdatedLaw: 'পুরানো বা বাতিল আইন',
    missingAuthority: 'গুরুত্বপূর্ণ কর্তৃপক্ষ অনুপস্থিত',
    incompleteAnswer: 'অসম্পূর্ণ উত্তর',
    misunderstoodQuestion: 'প্রশ্ন ভুল বোঝা হয়েছে',
    otherIssue: 'অন্যান্য সমস্যা',
    submitFeedback: 'মতামত জমা দিন',
    fbWrongLaw: 'ভুল আইন উদ্ধৃত',
    fbWrongCitation: 'ভুল রেফারেন্স',
    fbOutdatedInfo: 'পুরানো তথ্য',
    fbMissingAuthority: 'গুরুত্বপূর্ণ কর্তৃপক্ষ অনুপস্থিত',
    fbIncompleteAnswer: 'অসম্পূর্ণ উত্তর',
    fbMisunderstood: 'প্রশ্ন ভুল বোঝা হয়েছে',
    fbOther: 'অন্যান্য',
    feedbackRecorded: 'আপনার প্রতিবেদন রেকর্ড করা হয়েছে এবং পর্যালোচনার জন্য রাখা হয়েছে।',

    // Public Library & Guides
    libraryPageHeading: 'আইনি লাইব্রেরি',
    libraryPageBody: 'আইন, ধারা, মামলার নজির এবং আইনি আপডেটসমূহ অনুসন্ধান করুন।',
    publishedRecords: 'প্রকাশিত রেকর্ডসমূহ',
    guidePageHeading: 'নাগরিক আইনি গাইড',
    guidePageBody: 'বাংলাদেশের নাগরিকদের জন্য সহজ ভাষায় আইনি নির্দেশনা, প্রক্রিয়া ও প্রমাণের চেকলিস্ট।',
    guidePlaceholder: 'বিষয় বা সমস্যা লিখে গাইড খুঁজুন...',
    topics: 'বিষয়সমূহ',
    publishedLibrary: 'লাইব্রেরিতে প্রকাশিত',
    browseGuides: 'গাইড ব্রাউজ করুন',
    loadMore: 'আরও লোড করুন',
    updatesHeading: 'আইনি আপডেট ও গেজেট প্রজ্ঞাপন',
    updatesBody: 'সাম্প্রতিক আইনি সংশোধনী, হাইকোর্টের নির্দেশনা এবং গেজেট প্রজ্ঞাপনসমূহ।',
    publicReading: 'পাবলিক রিডিং মোড',

    // Workspaces specific
    professionalKicker: 'পেশাগত আইনি গবেষণা',
    professionalHeading: 'আপনি কী নিয়ে গবেষণা করছেন?',
    professionalSubtitle: 'বাংলাদেশের আইন খুঁজুন, কর্তৃত্বপূর্ণ উৎস দেখুন বা বর্তমান আইনি অবস্থান যাচাই করুন।',
    professionalPlaceholder: 'একটি আইনি বিষয় লিখুন, নজির বা ধারা খুঁজুন, কিংবা সংশোধনী যাচাই করুন...',
    studentKicker: 'আইনের শিক্ষার্থীদের জন্য Justor',
    studentHeading: 'উৎস-সংযুক্ত এআই সহায়তায় মামলা, আইন ও আইনি নীতি শিখুন।',
    studentAllowance: 'বেটা পর্যায়ে প্রতিদিন ৩০টি এআই উত্তর।',
    citizenKicker: 'ব্যবহারিক আইনি নির্দেশনা',
    citizenHeading: 'কী ঘটেছে?',
    citizenSubtitle: 'আপনার সমস্যা লিখুন বা একটি বিষয় বেছে নিন। Justor প্রথমে Citizen Legal Guides-এ খুঁজবে।',
    problemPlaceholder: 'নিজের ভাষায় আপনার সমস্যাটি লিখুন...',
    findGuidance: 'নির্দেশনা খুঁজুন',
    chooseTopic: 'একটি বিষয় বেছে নিন',
    citizenGuides: 'নাগরিক আইনি গাইড',
    publishedGuidance: 'প্রকাশিত নির্দেশনা',
    browseDirectory: 'গাইড তালিকা দেখুন',
    primarySource: 'প্রাথমিক উৎস',
    humanReviewed: 'আইন বিশেষজ্ঞ কর্তৃক পর্যালোচিত',
    sourceLinked: 'উৎস সংযুক্ত',
    researchHome: 'গবেষণা হোম',
    cases: 'মামলা',
    statutes: 'আইনসমূহ',
    amendments: 'সংশোধনী',
    studyHome: 'পড়াশোনার হোম',
    askJustor: 'Justor-কে জিজ্ঞাসা করুন',
    concepts: 'আইনি ধারণা',
    home: 'হোম',
    mobileResearch: 'গবেষণা',
    mobileStudy: 'পড়াশোনা',
    mobileAsk: 'জিজ্ঞাসা',
    mobileStart: 'শুরু',
    continueCitizen: 'নাগরিক হিসেবে এগিয়ে যান',
    continueStudent: 'শিক্ষার্থী হিসেবে এগিয়ে যান',
    continueProfessional: 'আইন পেশাজীবী হিসেবে এগিয়ে যান',
    continueGoogle: 'Google দিয়ে এগিয়ে যান',
    loginKicker: 'বাংলাদেশের আইনি তথ্য ও গবেষণা',
    loginBrandHeading: 'উত্তরের পাশেই কর্তৃত্বপূর্ণ উৎস রাখুন।',
    loginBrandBody: 'আপনার গবেষণা এনক্রিপ্টেড এবং নিরাপদে সংরক্ষিত। আপনি নিয়ন্ত্রণ করেন কী শেয়ার করা হবে।',
    loginHeading: 'জাস্টরে সাইন ইন করুন',
    loginBody: 'আপনার গবেষণা এনক্রিপ্টেড এবং নিরাপদে সংরক্ষিত। আপনি নিয়ন্ত্রণ করেন কী শেয়ার করা হবে।',
    returnPublic: 'পাবলিক ওয়েবসাইটে ফিরুন',
    profile: 'ব্যবহারকারী প্রোফাইল',
    profileHeading: 'অ্যাকাউন্ট ও আইনি গবেষণা সেটিংস',
    profileSubtitle: 'আপনার আইনজীবী প্রোফাইল, সাবস্ক্রিপশন, গুগল ক্লাউড এআই কোটা এবং ডেটা গোপনীয়তা পরিচালনা করুন।',
    accountSettings: 'অ্যাকাউন্ট সেটিংস',
    saveSettings: 'পরিবর্তন সংরক্ষণ করুন',
    personalDetails: 'ব্যক্তিগত ও চেম্বার বিবরণ',
    fullName: 'সম্পূর্ণ নাম',
    emailAddress: 'ইমেইল ঠিকানা',
    chamberName: 'চেম্বার / ফার্মের নাম',
    barAssociation: 'বার অ্যাসোসিয়েশন',
    practiceAreas: 'আইনি অনুশীলনের ক্ষেত্র',
    subscriptionCloud: 'মেম্বারশিপ ও গুগল ক্লাউড অবকাঠামো',
    cloudCredits: 'গুগল ক্লাউড এআই পার্টনার ($২,০০০ ক্রেডিট সক্রিয়)',
    researchPreferences: 'এআই গবেষণা পছন্দসমূহ',
    dataPrivacy: 'ডেটা গোপনীয়তা ও লোকাল স্টোরেজ',
    clearAllHistory: 'সমস্ত গবেষণার ইতিহাস মুছুন',
    exportData: 'গবেষণার ইতিহাস এক্সপোর্ট করুন (JSON)',
  },
} as const;

export type CopyKey = keyof typeof copy.en;

export const ui = (language: Language, key: CopyKey): string => {
  return copy[language]?.[key] ?? copy.en[key] ?? key;
};

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

/**
 * Computed Status Banner System (Section T & W of Guide)
 * Computes exact verification metrics without global/unfounded claims.
 */
export function computeStatusBanner(sources: LegalSource[], locale: Language): string {
  const total = sources.length;
  if (total === 0) {
    return locale === 'bn' ? 'উপলব্ধ আইনি তথ্যের ভিত্তিতে প্রস্তুত' : 'Based on available legal intelligence';
  }

  const checked = sources.filter((s) => {
    const st = (s.verificationStatus || s.status || '').toLowerCase();
    return st.includes('verified') || st.includes('checked') || st.includes('primary');
  }).length;

  const unreviewed = sources.filter((s) => {
    const st = (s.verificationStatus || s.status || '').toLowerCase();
    return st.includes('unreviewed');
  }).length;

  const pending = total - checked - unreviewed;
  const humanReviewed = sources.every((s) => (s.verificationStatus || '').toLowerCase().includes('human'));

  if (humanReviewed && total > 0) {
    return locale === 'bn'
      ? `মানব আইনি পর্যালোচনা — সমস্ত উৎস যাচাইকৃত (${total}টি)`
      : `Human legal reviewed — all sources verified (${total})`;
  }

  if (unreviewed > 0) {
    return locale === 'bn'
      ? `${total}টি কর্তৃপক্ষ: ${checked}টি যাচাইকৃত · ${pending}টি অপেক্ষমান · ${unreviewed}টি পর্যালোচনা করা হয়নি`
      : `${total} authorities: ${checked} source-checked · ${pending} pending · ${unreviewed} unreviewed`;
  }

  return locale === 'bn'
    ? `${total}টি কর্তৃপক্ষ: ${checked}টি যাচাইকৃত · ${pending}টি যাচাই অপেক্ষমান`
    : `${total} authorities: ${checked} source-checked · ${pending} pending verification`;
}
