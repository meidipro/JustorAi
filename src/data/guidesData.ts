// src/data/guidesData.ts

export interface LegalGuide {
  id: string;
  slug: string;
  category: 'property' | 'consumer' | 'family' | 'tax' | 'employment' | 'digital' | 'civic';
  categoryNameBn: string;
  categoryNameEn: string;
  titleBn: string;
  titleEn: string;
  subtitleEn: string;
  lastReviewed: string;
  applicableLaw: string;
  directAnswer: string;
  highlights: {
    appliesTo: string;
    deadline: string;
    authority: string;
  };
  lawSummary: string;
  steps: { title: string; desc: string }[];
  documentsRequired: string[];
  feesTimeline: string;
  exampleScenario: {
    title: string;
    situation: string;
    legalOutcome: string;
  };
  commonMistakes: string[];
  primarySources: {
    id: string;
    name: string;
    sections: string;
    url: string;
    status: 'PRIMARY SOURCE ✓' | 'SOURCE CHECKED ✓';
  }[];
}

export const LEGAL_GUIDES: LegalGuide[] = [
  {
    id: '01',
    slug: 'land-registration',
    category: 'property',
    categoryNameBn: 'জমি ও সম্পত্তি',
    categoryNameEn: 'Property & Land',
    titleBn: 'জমি নিবন্ধন কীভাবে করবেন: ধাপে ধাপে সরকারি নিয়ম ও প্রক্রিয়া',
    titleEn: 'How to Register Land in Bangladesh',
    subtitleEn: 'Step-by-Step Guide to Land Registration, Stamp Duty & 2026 Amendments',
    lastReviewed: '14 August 2026',
    applicableLaw: 'The Registration Act, 1908 (including 2026 Amendment Act No. 14); Transfer of Property Act, 1882; Stamp Act, 1899',
    directAnswer: 'In Bangladesh, transferring immovable property valued above 100 BDT or executing an agreement for sale requires mandatory written registration under Section 17 of the Registration Act, 1908 and Section 54 of the Transfer of Property Act, 1882. Registration must be completed at the Sub-Registry office within the local jurisdiction where the land is situated within statutory time limits.',
    highlights: {
      appliesTo: 'Land buyers, sellers, deed writers (দলিল লেখক), and property heirs.',
      deadline: 'Presentation within 3 months under Section 23 of Registration Act.',
      authority: 'Sub-Registry Office (Directorate of Registration, Ministry of Law).'
    },
    lawSummary: 'Under Section 17(1) of the Registration Act, 1908, all non-testamentary instruments transferring or creating any right, title, or interest in immovable property must be registered. Under Section 54 of the Transfer of Property Act, 1882, an oral contract creates no legal interest. Under Section 49 of the Registration Act, an unregistered document cannot affect any immovable property or be received as evidence of title in court.',
    steps: [
      { title: '1. Title & Ownership Verification', desc: 'Verify the seller’s CS, SA, RS, and City/BS Khatians, updated Namjari (Mutation), and Land Development Tax (Khajna) receipts.' },
      { title: '2. Deed Drafting & Valuation', desc: 'Draft the registered deed (Saf-Kabala / Baina-Nama) on official non-judicial stamp papers and calculate official Mouza rates.' },
      { title: '3. Fee Payment & Challan', desc: 'Deposit Stamp Duty (1.5%), Registration Fee (1%), Local Govt Tax (2-3%), and AIT (if applicable) through Sonali Bank e-Challan.' },
      { title: '4. Sub-Registry Presentation', desc: 'Both buyer and seller appear before the Sub-Registrar with NID cards, photos, and witnesses for biometrics and signature.' },
      { title: '5. Endorsement & I-Form Receipt', desc: 'Sub-Registrar checks Section 52A compliance, endorses the deed, and issues the official Form 52 delivery receipt.' }
    ],
    documentsRequired: [
      'Original registered title deed (মূল সাফ-কবলা দলিল) of seller',
      'Certified RS and City/BS Porcha (খতিয়ান)',
      'DCR & Namjari Khatian in seller\'s name with 117/143 note',
      'Current Land Development Tax (দাখিলা) receipt',
      'NID cards and passport-size photographs of buyer, seller, and identifier'
    ],
    feesTimeline: 'Approx. 8-10.5% of declared deed value. Estimated completion: 1 working day for presentation, 15-45 days for certified original copy.',
    exampleScenario: {
      title: 'Buying Land with Baina (Agreement for Sale)',
      situation: 'Rahim paid 10 Lakh BDT advance on an unregistered agreement to buy land in Savar. The seller later refused to execute the sale.',
      legalOutcome: 'Under Section 21A of Specific Relief Act and Section 17A of Registration Act, civil courts cannot entertain a suit for specific performance on an unregistered contract. Rahim can only file a money recovery suit.'
    },
    commonMistakes: [
      'Signing an unregistered Baina-Nama on plain non-judicial stamp paper.',
      'Relying only on RS Khatian without checking modern BS/City Survey or Namjari.',
      'Purchasing from an heir whose name is not recorded in the revenue mutation.'
    ],
    primarySources: [
      { id: 'ACT-REG-1908', name: 'The Registration Act, 1908', sections: 'Sections 17, 17A, 23, 49, 52A', url: 'http://bdlaws.minlaw.gov.bd/act-83.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'ACT-TPA-1882', name: 'The Transfer of Property Act, 1882', sections: 'Sections 54, 54A', url: 'http://bdlaws.minlaw.gov.bd/act-48.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'ACT-SRA-1877', name: 'The Specific Relief Act, 1877', sections: 'Section 21A', url: 'http://bdlaws.minlaw.gov.bd/act-32.html', status: 'PRIMARY SOURCE ✓' }
    ]
  },
  {
    id: '02',
    slug: 'mutation-namjari',
    category: 'property',
    categoryNameBn: 'জমি ও সম্পত্তি',
    categoryNameEn: 'Property & Land',
    titleBn: 'ই-নামজারি (Mutation) করার নিয়ম, খরচ ও সময়সীমা',
    titleEn: 'How to Complete Land Mutation (e-Namjari) in Bangladesh',
    subtitleEn: 'Complete Guide to Ministry of Land e-Mutation, DCR & Khatian Generation',
    lastReviewed: '14 August 2026',
    applicableLaw: 'The State Acquisition and Tenancy Act, 1950 (Sections 116, 117, 143, 144); Land Management Manual, 1990; Ministry of Land e-Mutation Circulars',
    directAnswer: 'Land Mutation (নামজারি / খারিজ) is the official administrative procedure to record a new owner’s name in the government land revenue register (Jamabandi / Khatian) following a purchase, inheritance, gift, or court decree. Applications in Bangladesh are submitted exclusively online through the official portal (mutation.land.gov.bd) for a statutory government fee of exactly 1,170 BDT.',
    highlights: {
      appliesTo: 'Anyone who recently purchased, inherited, or received land via gift deed.',
      deadline: 'Standard statutory disposal within 28 working days.',
      authority: 'Assistant Commissioner (Land) / AC Land Office (উপজেলা ভূমি অফিস).'
    },
    lawSummary: 'Under Sections 117 and 143 of the State Acquisition and Tenancy Act, 1950, revenue authorities must maintain an updated record of rent-paying tenants. Mutation does not create original title, but proves possession and tenancy status. Under Section 52A of the Registration Act, 1908, no subsequent sale can be registered without an updated Namjari Khatian in the seller’s name.',
    steps: [
      { title: '1. Online Application', desc: 'Visit mutation.land.gov.bd, enter NID and mobile number, and fill in Mouza, JL number, RS/BS Khatian, and plot number.' },
      { title: '2. Upload Certified Deeds', desc: 'Attach PDF copies of the registered deed (দলিল), previous chain deeds (ভায়া দলিল), updated Khajna receipt, and layout sketch.' },
      { title: '3. Payment of Court & Notice Fees', desc: 'Pay 70 BDT initial application & notice fee via mobile banking (bKash/Nagad/Rocket).' },
      { title: '4. Union Land Office Verification', desc: 'Union Land Officer (Tehsildar) inspects physical possession and submits verification report to AC Land.' },
      { title: '5. Hearing & DCR / Khatian Download', desc: 'Attend AC Land hearing if summoned. Upon approval, pay remaining 1,100 BDT to instantly download the QR-coded Namjari Khatian & DCR.' }
    ],
    documentsRequired: [
      'Copy of registered sale deed / gift deed / court decree',
      'Chain of title deeds (ভায়া দলিল) spanning past 25 years',
      'Latest certified RS and BS/City Survey Khatians',
      'Warish Certificate (if applying through inheritance)',
      'Current fiscal year Land Development Tax (দাখিলা) receipt'
    ],
    feesTimeline: 'Statutory Fee: 1,170 BDT total (Application 20 + Notice 50 + DCR 1,000 + Khatian 100). Processing: 28 working days.',
    exampleScenario: {
      title: 'Delayed Mutation After Buying Land',
      situation: 'Sumon bought land 2 years ago with a registered deed but never did Namjari. He now wants to take a bank loan against the land.',
      legalOutcome: 'Banks and sub-registry offices require the mutation Khatian. Sumon must complete e-Namjari before any mortgage or resale can be processed.'
    },
    commonMistakes: [
      'Paying unauthorized middleman fees (the legal government fee is strictly 1,170 BDT online).',
      'Not keeping track of the tracking number (ট্র্যাকিং আইডি) sent via SMS.',
      'Failing to verify that the Mouza number and JL number match the physical location.'
    ],
    primarySources: [
      { id: 'ACT-SAT-1950', name: 'The State Acquisition and Tenancy Act, 1950', sections: 'Sections 117, 143, 144', url: 'http://bdlaws.minlaw.gov.bd/act-241.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'CIRCULAR-MINLAND', name: 'Ministry of Land Official e-Mutation System', sections: 'Standard Operating Procedures 2021/2024', url: 'https://mutation.land.gov.bd', status: 'SOURCE CHECKED ✓' }
    ]
  },
  {
    id: '03',
    slug: 'khatian-types',
    category: 'property',
    categoryNameBn: 'জমি ও সম্পত্তি',
    categoryNameEn: 'Property & Land',
    titleBn: 'সিএস, এসএ, আরএস ও বিএস খতিয়ানের পার্থক্য ও চেনার উপায়',
    titleEn: 'CS, SA, RS and BS Khatians: How to Identify and Verify Them',
    subtitleEn: 'A Complete Guide to Land Survey Records (Porcha) in Bangladesh',
    lastReviewed: '14 August 2026',
    applicableLaw: 'The Bengal Tenancy Act, 1885; The State Acquisition and Tenancy Act, 1950 (Sections 17, 18, 144); Evidence Act, 1872',
    directAnswer: 'A Khatian (খতিয়ান / পর্চা) is the official Record of Rights (RoR) that specifies the land owner, plot boundary, area, and revenue status during a specific cadastral survey. In Bangladesh, chronological surveys include: CS (Cadastral Survey 1888–1940), SA (State Acquisition 1956–1963), RS (Revisional Survey 1965–1990), and BS / City Survey (Bangladesh Survey 1998–Present).',
    highlights: {
      appliesTo: 'Anyone investigating title, inheriting land, or purchasing immovable property.',
      deadline: 'Permanent historical records; obtainable via e-Porcha portal.',
      authority: 'Directorate of Land Records and Surveys (DLRS) & DC Record Room.'
    },
    lawSummary: 'Under Section 144 of the State Acquisition and Tenancy Act, 1950 and Section 35 of the Evidence Act, 1872, entries in an official Khatian carry a statutory presumption of correctness regarding possession. While CS proves the historical root of ownership, the latest final published survey (RS or BS/City) governs current fiscal and cadastral identification.',
    steps: [
      { title: '1. Identify Survey Type', desc: 'Inspect the top header: CS (usually 2 pages, columns 1-17), SA (written on badam-color paper), RS (compact layout), BS (modern 2-page format).' },
      { title: '2. Check Chain of Continuity', desc: 'Trace ownership: CS Landlord/Tenant $\\rightarrow$ SA Tenant $\\rightarrow$ RS Recorded Owner $\\rightarrow$ BS Recorded Owner.' },
      { title: '3. Verify Against Registered Deeds', desc: 'Ensure that deed transfers match the plot numbers and boundary descriptions recorded in the respective survey.' },
      { title: '4. Download Certified Digital Copy', desc: 'Order certified e-Porcha copies with digital stamps via eporcha.gov.bd for legal proceedings.' }
    ],
    documentsRequired: [
      'District, Upazila, and Mouza name with JL Number',
      'Khatian Number or Plot (Dag) Number',
      'Name of the historical or recorded owner'
    ],
    feesTimeline: 'Digital online copy: 100 BDT via eporcha.gov.bd. Certified physical copy: 150-200 BDT via Deputy Commissioner (DC) Record Room.',
    exampleScenario: {
      title: 'Discrepancy Between SA and RS Khatians',
      situation: 'Karim’s grandfather had 50 decimals in SA Khatian, but in RS Khatian only 30 decimals were recorded under his name.',
      legalOutcome: 'Under Section 144B of SAT Act, Karim must verify if the 20 decimals were transferred by registered deed, or file a Title Suit in Civil Court for declaration of title and correction of record.'
    },
    commonMistakes: [
      'Relying solely on CS Khatian without checking subsequent RS or BS surveys.',
      'Confusing Land Revenue Mutation Khatian (খারিজ খতিয়ান) with Cadastral Survey Khatian (জরিপ খতিয়ান).',
      'Accepting non-certified photocopies without QR code verification.'
    ],
    primarySources: [
      { id: 'ACT-SAT-1950', name: 'The State Acquisition and Tenancy Act, 1950', sections: 'Sections 17, 18, 144', url: 'http://bdlaws.minlaw.gov.bd/act-241.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'PORTAL-EPORCHA', name: 'Official e-Porcha Verification Portal', sections: 'DLRS National Land Records System', url: 'https://eporcha.gov.bd', status: 'SOURCE CHECKED ✓' }
    ]
  },
  {
    id: '04',
    slug: 'deed-verification',
    category: 'property',
    categoryNameBn: 'জমি ও সম্পত্তি',
    categoryNameEn: 'Property & Land',
    titleBn: 'জমি কেনার আগে দলিলের সত্যতা যাচাই করার নিয়ম',
    titleEn: 'How to Verify a Property Deed (Dalil) in Bangladesh',
    subtitleEn: 'Pre-Purchase Due Diligence Checklist for Safe Land Transactions',
    lastReviewed: '14 August 2026',
    applicableLaw: 'The Registration Act, 1908 (Sections 52, 57); The Transfer of Property Act, 1882; The Evidence Act, 1872',
    directAnswer: 'Before purchasing property in Bangladesh, a buyer must conduct formal title verification by checking original registered deeds (মূল দলিল) and previous chain deeds (ভায়া দলিল) spanning at least 25 years. Authenticity must be cross-checked at the local Sub-Registry office by applying for an official Search & Non-Encumbrance Certificate under Section 57 of the Registration Act, 1908.',
    highlights: {
      appliesTo: 'Prospective property buyers, banks, and legal advisors.',
      deadline: 'Must be completed prior to paying advance or signing Baina-Nama.',
      authority: 'Sub-Registry Office & District Registrar Office.'
    },
    lawSummary: 'Under Section 57 of the Registration Act, 1908, the public has a statutory right to inspect Book No. 1 and Book No. 2 at the Sub-Registry office upon payment of prescribed search fees. Under the Transfer of Property Act, 1882, the doctrine of caveat emptor (buyer beware) applies; failure to investigate registered encumbrances deprives a buyer of bonafide purchaser protection.',
    steps: [
      { title: '1. Original Deed Inspection', desc: 'Inspect the volume number, page number, deed number, registration year, and seal of the Sub-Registry on the original deed.' },
      { title: '2. 25-Year Search (तलाশি)', desc: 'Submit a formal search application (तलाশি) at the Sub-Registry office covering all previous transactions for the specific plot.' },
      { title: '3. Non-Encumbrance Certificate (NEC)', desc: 'Obtain a formal Non-Encumbrance Certificate (দায়মুক্ত সনদ) to verify the property has no mortgage or prior registered lease.' },
      { title: '4. Mutation & Khajna Match', desc: 'Verify that the seller’s name appears on the latest DCR, Namjari Khatian, and Land Development Tax receipt.' },
      { title: '5. Physical Spot Inspection', desc: 'Visit the physical land plot to verify actual possession, boundaries, and ensure no co-sharer or third party claims.' }
    ],
    documentsRequired: [
      'Copy of Seller\'s Title Deed (সাফ-কবলা দলিল)',
      'All historical chain deeds (ভায়া দলিল)',
      'Mutation Khatian (নামজারি খতিয়ান) & DCR',
      'Up-to-date Land Development Tax (দাখিলা) receipts',
      'Mouza Map (নকশা) showing plot demarcation'
    ],
    feesTimeline: 'Sub-Registry Search fee: approx. 100-300 BDT per year searched. Certified copy of deed: approx. 300-800 BDT depending on page volume.',
    exampleScenario: {
      title: 'Fake Deed Produced by Fraudulent Seller',
      situation: 'A seller presented a clean deed photocopy. The buyer conducted a Section 57 search and found the volume page was completely blank in Sub-Registry Book 1.',
      legalOutcome: 'The deed was counterfeit. Under Section 463/468 of Penal Code, the seller committed forgery. The buyer saved his funds by verifying Book 1 records before payment.'
    },
    commonMistakes: [
      'Relying on notarized photocopies instead of inspecting the original Sub-Registry volume.',
      'Failing to trace the chain of deeds (ভায়া দলিল) back to an authentic survey record.',
      'Not conducting a physical boundary inspection on the actual ground.'
    ],
    primarySources: [
      { id: 'ACT-REG-1908', name: 'The Registration Act, 1908', sections: 'Sections 52, 57', url: 'http://bdlaws.minlaw.gov.bd/act-83.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'ACT-TPA-1882', name: 'The Transfer of Property Act, 1882', sections: 'Section 54', url: 'http://bdlaws.minlaw.gov.bd/act-48.html', status: 'PRIMARY SOURCE ✓' }
    ]
  },
  {
    id: '05',
    slug: 'consumer-complaint-dncrp',
    category: 'consumer',
    categoryNameBn: 'ভোক্তা অধিকার',
    categoryNameEn: 'Consumer Rights',
    titleBn: 'ভোক্তা অধিকারে কীভাবে অভিযোগ করবেন ও ২৫% জরিমানা পুরস্কার পাবেন',
    titleEn: 'How to File a Consumer Complaint with DNCRP in Bangladesh',
    subtitleEn: 'Complete Guide to Consumer Rights Protection Act, 2009 & 25% Compensation',
    lastReviewed: '14 August 2026',
    applicableLaw: 'The Consumer Rights Protection Act, 2009 (Act No. 26 of 2009, Sections 60, 71, 76)',
    directAnswer: 'Under Section 60 of the Consumer Rights Protection Act, 2009, any consumer who suffers from adulteration, false advertisement, overpricing, short-weight, or defective goods/services can file a formal complaint with the Directorate of National Consumer Rights Protection (DNCRP) within 30 days of the occurrence. If the complaint is proven and a fine is imposed, the complainant receives exactly 25% of the total realized fine as a statutory reward under Section 76(1).',
    highlights: {
      appliesTo: 'Any individual consumer purchasing goods, medicines, food, electronics, or services.',
      deadline: 'Strictly within 30 days of the cause of action under Section 60.',
      authority: 'Directorate of National Consumer Rights Protection (DNCRP / জাতীয় ভোক্তা-অধিকার সংরক্ষণ অধিদপ্তর).'
    },
    lawSummary: 'The Consumer Rights Protection Act, 2009 provides comprehensive penal and administrative remedies for consumer exploitation. Under Section 71, offenses can be compounded administratively. Under Section 76(1), when a fine is realized through administrative proceedings, 25% of the fine is immediately disbursed to the complainant.',
    steps: [
      { title: '1. Preserve Purchase Evidence', desc: 'Keep the original cash memo / invoice, receipt, product packaging, photos of the MRP/price tag, and screenshots for online orders.' },
      { title: '2. Draft the Complaint', desc: 'Write the complaint specifying complainant details, seller/business details, date, time, statutory offense under CRPA 2009, and prayer for remedy.' },
      { title: '3. Submit to DNCRP', desc: 'Submit via email (nccc@dncrp.gov.bd), the official DNCRP app, or physical submission to the District DNCRP Office.' },
      { title: '4. Attend Administrative Hearing', desc: 'DNCRP summons both complainant and business owner for hearing and evidence verification.' },
      { title: '5. Receive 25% Reward', desc: 'Upon finding of guilt and realization of administrative fine, collect the 25% cheque / bank transfer.' }
    ],
    documentsRequired: [
      'Original Cash Memo, Invoice, or online order confirmation',
      'Clear photos of the product packaging, batch number, MRP, and expiry date',
      'Copy of Complainant\'s National ID (NID) Card',
      'Brief written statement detailing the date, price paid, and violation'
    ],
    feesTimeline: 'Government filing fee: 0 BDT (Completely Free). Average resolution timeline: 15 to 30 days.',
    exampleScenario: {
      title: 'Overcharging on Packaged Medicine',
      situation: 'Farhan was charged 150 BDT for eye drops having an official printed MRP of 100 BDT. Farhan kept the cash memo and filed a DNCRP complaint.',
      legalOutcome: 'DNCRP held a hearing, found the pharmacy guilty under Section 40 of CRPA 2009, and imposed a 20,000 BDT fine. Farhan received 5,000 BDT (25%) on the spot.'
    },
    commonMistakes: [
      'Filing after the 30-day statutory limitation period under Section 60.',
      'Throwing away the original cash memo or invoice.',
      'Failing to record the exact business address and trade license name of the shop.'
    ],
    primarySources: [
      { id: 'ACT-CRPA-2009', name: 'The Consumer Rights Protection Act, 2009', sections: 'Sections 40, 45, 60, 71, 76', url: 'http://bdlaws.minlaw.gov.bd/act-1014.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'PORTAL-DNCRP', name: 'Directorate of National Consumer Rights Protection Official System', sections: 'Consumer Complaint Redressal Guidelines', url: 'https://dncrp.gov.bd', status: 'SOURCE CHECKED ✓' }
    ]
  },
  {
    id: '06',
    slug: 'income-tax-return-filing',
    category: 'tax',
    categoryNameBn: 'কর ও অর্থ',
    categoryNameEn: 'Tax & Finance',
    titleBn: 'আয়কর রিটার্ন (e-Return) দাখিল করার নিয়ম ও কর নির্ধারণ',
    titleEn: 'How to File Income Tax e-Return in Bangladesh (2026–27)',
    subtitleEn: 'Step-by-Step Guide to Income Tax Act, 2023, Tax Slabs & NBR e-Return Portal',
    lastReviewed: '15 August 2026',
    applicableLaw: 'The Income Tax Act, 2023 (Act No. 12 of 2023, Sections 166, 171, 264); NBR e-Return Rules & Annual Finance Acts',
    directAnswer: 'Under Section 166 of the Income Tax Act, 2023, every individual having taxable income above the statutory exemption threshold (350,000 BDT for general individuals; 400,000 BDT for female/senior citizens) or holding a mandatory proof of submission (PSR) category must file an annual income tax return. The National Board of Revenue (NBR) operates mandatory online filing via etaxnbr.gov.bd.',
    highlights: {
      appliesTo: 'Salaried employees, business owners, professionals, and car/property owners.',
      deadline: 'Tax Day: Usually 30th November of the assessment year.',
      authority: 'National Board of Revenue (NBR / জাতীয় রাজস্ব বোর্ড).'
    },
    lawSummary: 'The Income Tax Act, 2023 repealed the legacy 1984 Ordinance. Under Section 264, Proof of Submission of Return (PSR) is mandatory for 43+ civic services including obtaining bank loans over 5 Lakh BDT, trade license renewal, purchasing motor vehicles, and utility connections. Failure to submit within the deadline attracts statutory penalty and interest under Section 174.',
    steps: [
      { title: '1. Register on e-Tax Portal', desc: 'Visit etaxnbr.gov.bd, enter your 12-digit e-TIN and biometric mobile number registered in your NID.' },
      { title: '2. Enter Income Sources', desc: 'Fill in heads of income: Salary, House Property, Agriculture, Business, Capital Gains, and Financial Assets.' },
      { title: '3. Claim Tax Rebate for Investment', desc: 'Enter allowable investments (Life Insurance, DPS, Treasury Bonds, Sanchayapatra) to claim rebate under Part 3 of Sixth Schedule.' },
      { title: '4. Asset & Liability Statement (IT-10B)', desc: 'Declare gross wealth, lifestyle expenses, bank balance as of 30th June, and sources of funds.' },
      { title: '5. Pay Tax & Download Acknowledgement', desc: 'Pay net tax liability via online debit card/e-Banking/MFS and download the instant PSR Tax Certificate.' }
    ],
    documentsRequired: [
      '12-digit e-TIN Certificate and NID Card',
      'Salary Certificate & Bank Statement (1st July to 30th June)',
      'Investment certificates (Sanchayapatra, DPS, Insurance, Stocks)',
      'Property title deeds and rental agreements (if earning rental income)',
      'Proof of Advance Income Tax (AIT) deductions (challans, car fitness tokens)'
    ],
    feesTimeline: 'NBR e-Return Portal fee: 0 BDT (Free). Filing window: July 1 to November 30 (Tax Day).',
    exampleScenario: {
      title: 'Applying for Bank Loan without Tax Return',
      situation: 'Fahim applied for an 8 Lakh BDT SME loan. The bank refused to disburse the funds without PSR.',
      legalOutcome: 'Under Section 264 of Income Tax Act 2023, banks are strictly prohibited from sanctioning loans above 5 Lakh BDT without verified Proof of Submission of Return (PSR).'
    },
    commonMistakes: [
      'Submitting return manually when online e-Return is mandatory for your circle.',
      'Omitting bank interest or dividend income from financial statements.',
      'Failing to declare newly acquired property in the IT-10B Statement of Assets and Liabilities.'
    ],
    primarySources: [
      { id: 'ACT-ITA-2023', name: 'The Income Tax Act, 2023', sections: 'Sections 166, 171, 174, 264', url: 'http://bdlaws.minlaw.gov.bd/act-1445.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'PORTAL-NBR', name: 'National Board of Revenue Official e-Return Portal', sections: 'Online Tax Return Submission Guidelines', url: 'https://etaxnbr.gov.bd', status: 'SOURCE CHECKED ✓' }
    ]
  },
  {
    id: '07',
    slug: 'labour-law-termination-severance',
    category: 'employment',
    categoryNameBn: 'চাকরি ও শ্রম আইন',
    categoryNameEn: 'Employment & Labour',
    titleBn: 'চাকরি থেকে অব্যাহতি, নোটিশ পে ও গ্র্যাচুইটি পাওয়ার সরকারি নিয়ম',
    titleEn: 'Employee Termination, Notice Pay & Severance under Bangladesh Labour Act',
    subtitleEn: 'Legal Rights on Dismissal, Retrenchment, Resignation & Gratuity Calculation',
    lastReviewed: '15 August 2026',
    applicableLaw: 'The Bangladesh Labour Act, 2006 (Act No. 42 of 2006, Sections 20, 26, 27, 28) & Bangladesh Labour Rules, 2015',
    directAnswer: 'Under Section 26 of the Bangladesh Labour Act, 2006, an employer can terminate a permanent worker by giving 120 days’ written notice (for monthly rated workers) or by paying basic wages in lieu of notice. The terminated employee is statutorily entitled to 30 days’ wages for every completed year of service as severance compensation, plus accrued gratuity, provident fund, and unavailed earned leave encashment.',
    highlights: {
      appliesTo: 'Workers, employees, factories, corporate establishments, and HR managers.',
      deadline: 'Service benefits must be cleared within 30 working days under Section 30.',
      authority: 'Department of Inspection for Factories and Establishments (DIFE) & Labour Court.'
    },
    lawSummary: 'The Bangladesh Labour Act, 2006 strictly regulates termination of employment. Unlawful termination without following statutory notice and severance benefits under Section 26 gives the worker a statutory right to file a Grievance Petition under Section 33 before the employer, followed by a formal case before the Labour Court (শ্রম আদালত).',
    steps: [
      { title: '1. Check Employment Status', desc: 'Determine whether you are classified as a permanent worker, probationer, or contractual employee under Section 4.' },
      { title: '2. Review Termination Letter', desc: 'Verify whether the employer provided statutory 120 days’ notice or 120 days’ basic wage in lieu of notice under Section 26.' },
      { title: '3. Calculate Statutory Dues', desc: 'Calculate: (a) Notice pay, (b) Compensation (30 days basic wage per completed year), (c) Gratuity/PF, (d) Unavailed earned leave.' },
      { title: '4. Submit Section 33 Grievance', desc: 'If benefits are unpaid, submit a formal written Grievance Petition to the employer by registered post within 30 days.' },
      { title: '5. File Labour Court Case', desc: 'If employer does not respond within 15 days or rejects grievance, file a case before the Chairman, Labour Court within 30 days.' }
    ],
    documentsRequired: [
      'Appointment Letter, ID Card, and Service Book',
      'Pay slips, bank salary statements for past 12 months',
      'Termination letter, discharge letter, or resignation acceptance copy',
      'Copy of written Section 33 Grievance Petition with postal receipt'
    ],
    feesTimeline: 'Labour Court filing fee: Free / nominal. Employer must disburse all dues within 30 working days under Section 30.',
    exampleScenario: {
      title: 'Sudden Termination After 5 Years Service',
      situation: 'Tanvir worked 5 years as a senior officer. The company abruptly terminated him with 1 month salary without notice pay or compensation.',
      legalOutcome: 'Under Section 26, the company owes Tanvir 120 days notice pay plus 150 days (5 x 30 days) basic wage severance compensation plus earned leave encashment.'
    },
    commonMistakes: [
      'Signing a "Full and Final Settlement" voucher on blank stamp paper before receiving money.',
      'Missing the strict 30-day statutory deadline to submit the Section 33 Grievance Notice.',
      'Confusing gross salary with basic salary for statutory compensation calculations.'
    ],
    primarySources: [
      { id: 'ACT-BLA-2006', name: 'The Bangladesh Labour Act, 2006', sections: 'Sections 20, 26, 27, 28, 30, 33', url: 'http://bdlaws.minlaw.gov.bd/act-952.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'RULES-BLR-2015', name: 'Bangladesh Labour Rules, 2015', sections: 'Rules 22, 23, 27', url: 'http://dife.gov.bd', status: 'SOURCE CHECKED ✓' }
    ]
  },
  {
    id: '08',
    slug: 'family-court-denmohor-maintenance',
    category: 'family',
    categoryNameBn: 'পারিবারিক আইন',
    categoryNameEn: 'Family & Succession',
    titleBn: 'দেনমোহর ও সন্তানের ভরণপোষণ আদায়ের আইনি প্রক্রিয়া',
    titleEn: 'How to Claim Denmohor (Dower) & Child Maintenance in Family Court',
    subtitleEn: 'Complete Procedure under Family Courts Act, 2023 & Muslim Family Laws Ordinance',
    lastReviewed: '15 August 2026',
    applicableLaw: 'The Family Courts Act, 2023 (Act No. 8 of 2023); Muslim Family Laws Ordinance, 1961 (Section 9); Muslim Personal Law (Shariat) Application Act, 1937',
    directAnswer: 'In Bangladesh, Denmohor (dower) is the absolute, unconditional legal debt of the husband to the wife agreed upon in the Nikahnama (Kabin-nama). A wife can sue for prompt dower at any time during marriage, and for deferred dower upon divorce or death. Under Section 5 of the Family Courts Act, 2023, exclusive jurisdiction lies with the Family Court (পারিবারিক আদালত) to decree dower and child maintenance.',
    highlights: {
      appliesTo: 'Divorced, separated, or abandoned wives and minor children.',
      deadline: 'Prompt dower: 3 years from refusal; Deferred dower: 3 years from divorce.',
      authority: 'Family Court (Judge: Assistant Judge / Senior Assistant Judge).'
    },
    lawSummary: 'Under Section 5 of the Family Courts Act, 2023 (replacing 1985 Ordinance), Family Courts have exclusive jurisdiction over: (1) Dissolution of marriage, (2) Restitution of conjugal rights, (3) Dower, (4) Maintenance, and (5) Guardianship and custody of children. Dower cannot be waived by unilateral verbal statement without free consent.',
    steps: [
      { title: '1. Gather Marriage & Divorce Proof', desc: 'Obtain certified copy of the registered Nikahnama (Kabin-nama) and Talaknama (if divorce occurred).' },
      { title: '2. Draft the Family Court Plaint', desc: 'Engage an advocate to file a plaint in the Family Court within local jurisdiction where the wife resides or where marriage was solemnized.' },
      { title: '3. Pre-Trial Reconciliation Hearing', desc: 'Under Section 10 of Family Courts Act, the Judge conducts mandatory pre-trial conciliation between parties.' },
      { title: '4. Evidence & Judgment', desc: 'If reconciliation fails, court frames issues, takes oral/documentary evidence, and passes judgment and decree for dower and maintenance.' },
      { title: '5. Execution (Jari Case)', desc: 'If husband fails to pay within court deadline, file an Execution Case; court can attach husband\'s salary/property or issue civil arrest warrant.' }
    ],
    documentsRequired: [
      'Certified copy of registered Nikahnama (কবিননামা / নিকাহনামা)',
      'Notice of Talaq & Postal receipts (if divorce was initiated)',
      'Birth certificates and school fee receipts of minor children',
      'Complainant\'s National ID Card and address proof'
    ],
    feesTimeline: 'Family Court court fee: strictly 50 BDT fixed fee. Execution timeline: 6 to 18 months.',
    exampleScenario: {
      title: 'Husband Refusing Dower Claiming Wife Initiated Divorce',
      situation: 'Rima divorced her husband through delegated divorce (Talaq-e-Tawfeez). The husband refused to pay 5 Lakh BDT Denmohor claiming she forfeited it.',
      legalOutcome: 'Under Bangladesh law, exercising Talaq-e-Tawfeez does not forfeit dower. Rima is fully entitled to recover 100% of her dower and child maintenance in Family Court.'
    },
    commonMistakes: [
      'Assuming that a wife forfeits Denmohor if she asks for divorce (dower is an absolute statutory debt unless explicitly settled in Khula).',
      'Failing to claim interim child maintenance (অন্তর্র্বতীকালীন ভরণপোষণ) during suit pendency.',
      'Missing the 3-year limitation window under Article 103/104 of the Limitation Act, 1908.'
    ],
    primarySources: [
      { id: 'ACT-FCA-2023', name: 'The Family Courts Act, 2023', sections: 'Sections 4, 5, 10, 14, 16', url: 'http://bdlaws.minlaw.gov.bd/act-1440.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'ACT-MFLO-1961', name: 'The Muslim Family Laws Ordinance, 1961', sections: 'Sections 9, 10', url: 'http://bdlaws.minlaw.gov.bd/act-305.html', status: 'PRIMARY SOURCE ✓' }
    ]
  },
  {
    id: '09',
    slug: 'inheritance-property-shares',
    category: 'family',
    categoryNameBn: 'পারিবারিক আইন',
    categoryNameEn: 'Family & Succession',
    titleBn: 'মুসলিম উত্তরাধিকার আইন: সম্পত্তি বণ্টন ও অংশ নির্ধারণের নিয়ম',
    titleEn: 'Muslim Inheritance & Property Distribution Rules in Bangladesh',
    subtitleEn: 'Comprehensive Guide to Quranic Shares, Residuaries & Section 4 MFLO',
    lastReviewed: '15 August 2026',
    applicableLaw: 'The Muslim Personal Law (Shariat) Application Act, 1937; The Muslim Family Laws Ordinance, 1961 (Section 4); Succession Act, 1925',
    directAnswer: 'Under Muslim succession law in Bangladesh (Hanafi principles), inheritance opens immediately upon the death of the property owner. After paying funeral expenses, debts, and valid bequests (wasiyat up to 1/3), the estate is distributed among primary heirs (Sharers and Residuaries). Surviving sons take twice the share of surviving daughters, and under Section 4 of MFLO 1961, children of predeceased sons or daughters receive their parent’s full share per stirpes.',
    highlights: {
      appliesTo: 'Heirs, family members, property buyers, and civil advocates.',
      deadline: 'No limitation period to claim inheritance; co-sharers hold jointly until partition.',
      authority: 'Civil Court (Partition Suit / বাটোয়ারা মামলা) & Local City/Union Parishad.'
    },
    lawSummary: 'Inheritance in Bangladesh is governed by personal religious law. Sharers (Zawil-Furooz) receive fixed statutory Quranic fractions (e.g., Wife gets 1/8 if children exist, 1/4 if no children; Mother gets 1/6; Father gets 1/6). The remaining estate passes to Residuaries (Asaba), where brothers and sisters share in 2:1 ratio. Partition is enforced through a Partition Suit under the Partition Act, 1893.',
    steps: [
      { title: '1. Obtain Warish Certificate', desc: 'Obtain an official legal heir certificate (ওয়ারিশান সনদ) from the relevant Union Parishad Chairman, City Corporation Mayor, or Ward Councilor.' },
      { title: '2. Determine Sharers & Residuaries', desc: 'Identify living heirs: Surviving spouse, parents, sons, daughters, and orphaned grandchildren under Section 4 MFLO.' },
      { title: '3. Calculate Exact Fractional Shares', desc: 'Calculate exact decimals: Wife (1/8 or 12.5%), Mother (1/6 or 16.66%), remaining 70.84% split among sons and daughters (2:1).' },
      { title: '4. Mutual Partition Deed (আপস বণ্টন দলিল)', desc: 'Execute an amicable registered partition deed (বণ্টননামা দলিল) among all heirs specifying physical boundaries.' },
      { title: '5. Court Partition Suit (If disputed)', desc: 'If co-sharers refuse mutual partition, file a Partition Suit (বাটোয়ারা মামলা) in the Civil Court of the Assistant Judge / Sub-Judge.' }
    ],
    documentsRequired: [
      'Official Warish Certificate (ওয়ারিশান সনদ) with NID numbers',
      'Death Certificate of the deceased propositus',
      'Title deeds (সাফ-কবলা দলিল) and CS/SA/RS/BS Khatians of the deceased',
      'Updated Land Development Tax receipts'
    ],
    feesTimeline: 'Mutual Partition Deed registration fee: nominal fixed rate (approx. 500-1000 BDT). Civil Partition Suit: fixed court fee 300 BDT.',
    exampleScenario: {
      title: 'Inheritance of Orphaned Grandchildren',
      situation: 'Jamal died leaving his elderly father. Two years later, his father died leaving 10 bighas land and another living son. The surviving son claimed Jamal’s children get zero.',
      legalOutcome: 'Under Section 4 of Muslim Family Laws Ordinance 1961, Jamal’s children step into their deceased father’s shoes and inherit the exact 50% share Jamal would have received.'
    },
    commonMistakes: [
      'Depriving married daughters of their rightful registered inheritance.',
      'Selling unpartitioned joint land without demarcation, leading to criminal trespass cases.',
      'Relying on an unverified village panchayat distribution without a registered partition deed.'
    ],
    primarySources: [
      { id: 'ACT-MFLO-1961', name: 'The Muslim Family Laws Ordinance, 1961', sections: 'Section 4', url: 'http://bdlaws.minlaw.gov.bd/act-305.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'ACT-PART-1893', name: 'The Partition Act, 1893', sections: 'Sections 2, 4', url: 'http://bdlaws.minlaw.gov.bd/act-63.html', status: 'PRIMARY SOURCE ✓' }
    ]
  },
  {
    id: '10',
    slug: 'cyber-crime-online-harassment',
    category: 'digital',
    categoryNameBn: 'সাইবার ও ডিজিটাল আইন',
    categoryNameEn: 'Cyber & Digital Law',
    titleBn: 'সাইবার ক্রাইম, অনলাইন প্রতারণা ও ব্ল্যাকমেইলের আইনি প্রতিকার',
    titleEn: 'How to File a Cyber Crime & Online Harassment Complaint in Bangladesh',
    subtitleEn: 'Legal Remedies for Blackmail, Fake IDs, Financial Fraud & Cyber Security Act, 2023',
    lastReviewed: '15 August 2026',
    applicableLaw: 'The Cyber Security Act, 2023 (Act No. 27 of 2023, Sections 24, 25, 26, 29); The Penal Code, 1860 (Sections 419, 500, 506, 509)',
    directAnswer: 'If you are a victim of cyber bullying, online blackmail, unauthorized sharing of private photos, identity theft (fake ID), or online financial fraud in Bangladesh, you have a statutory right to immediate police assistance. Complaints can be filed at any local Thana (General Diary / FIR), via CID Cyber Police Centre (CPC), or through the specialized Police Cyber Support for Women (PCSW).',
    highlights: {
      appliesTo: 'Victims of online harassment, defamation, extortion, hacked social media, and digital fraud.',
      deadline: 'Immediate action recommended; preserve digital evidence before deletion.',
      authority: 'CID Cyber Police Centre, Cyber Support for Women (PCSW) & Cyber Tribunal.'
    },
    lawSummary: 'The Cyber Security Act, 2023 provides penal sanctions for unlawful access to computer systems, identity theft (Section 24), online cheating/fraud (Section 26), and publication of offensive/defamatory information. Offenses involving extortion, blackmail, or sexual harassment are non-bailable and investigated by specialized cyber forensic units.',
    steps: [
      { title: '1. Preserve Digital Evidence', desc: 'Take high-resolution screenshots of posts, messages, URLs, phone numbers, and transaction IDs (bKash/Nagad/Bank). Do not delete chats.' },
      { title: '2. Collect Account URL & IP Proof', desc: 'Copy the full URL link of the offending Facebook/Instagram profile or WhatsApp account.' },
      { title: '3. Contact Specialized Cyber Units', desc: 'For women/children: Contact Police Cyber Support for Women (01320000888 / pcsw@police.gov.bd). For financial fraud: CID Cyber Centre (01769691522).' },
      { title: '4. File a General Diary (GD) or FIR', desc: 'Visit your local Thana with printed digital evidence and NID to file a formal General Diary (GD) or First Information Report (FIR).' },
      { title: '5. Cyber Tribunal Prosecution', desc: 'Upon police investigation and forensic submission, the case is tried before the Divisional Cyber Tribunal (সাইবার ট্রাইব্যুনাল).' }
    ],
    documentsRequired: [
      'Clear printed screenshots of abusive messages, emails, or fake posts',
      'Exact URL link of the offending social media profile / group',
      'Transaction statements and TrxID (for online financial scam)',
      'Complainant\'s National ID Card and phone number'
    ],
    feesTimeline: 'Police Cyber Support & GD Filing: 0 BDT (Completely Free). Emergency response: 24 to 72 hours for profile takedown.',
    exampleScenario: {
      title: 'Blackmail with Compromised Private Photographs',
      situation: 'An anonymous Facebook account demanded 50,000 BDT threatening to circulate edited private photos of a student.',
      legalOutcome: 'Under Section 24/26 of Cyber Security Act and Section 506/509 of Penal Code, this constitutes non-bailable criminal extortion. CID Cyber Unit can trace the IP, arrest the perpetrator, and issue takedown requests to Meta.'
    },
    commonMistakes: [
      'Deleting the chat or blocking the blackmailer immediately before taking verifiable URL and timestamp screenshots.',
      'Paying money to extortionists (paying almost never stops blackmail and encourages further demands).',
      'Not including the full alphanumeric profile URL of the fake account.'
    ],
    primarySources: [
      { id: 'ACT-CSA-2023', name: 'The Cyber Security Act, 2023', sections: 'Sections 24, 25, 26, 29', url: 'http://bdlaws.minlaw.gov.bd/act-1449.html', status: 'PRIMARY SOURCE ✓' },
      { id: 'POLICE-PCSW', name: 'Bangladesh Police Cyber Support for Women (PCSW)', sections: 'Official Cyber Incident Reporting Framework', url: 'https://police.gov.bd', status: 'SOURCE CHECKED ✓' }
    ]
  }
];
