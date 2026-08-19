"""
Justor AI — Bilingual Legal Dictionary & Query Normalizer for Bangladesh Law
Maps colonial, Farsi-influenced, and Bengali legal terminology into canonical concepts,
with strict per-Act structured authority bindings to eliminate Cartesian Act×Section contamination.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple, Set

# ─── Bengali to ASCII Numeral Translation Map ────────────────────────────────
BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

# ─── Statutory Prefix Normalizations ──────────────────────────────────────────
STATUTORY_PREFIX_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'(?:ধারা|দফা|সেকশন)\s*([0-9A-Za-z]+)', re.IGNORECASE), r'Section \1'),
    (re.compile(r'(?:অনুচ্ছেদ|আর্টিকেল)\s*([0-9A-Za-z]+)', re.IGNORECASE), r'Article \1'),
    (re.compile(r'(?:আদেশ|অর্ডার)\s*([0-9IVXLCDM]+)', re.IGNORECASE), r'Order \1'),
    (re.compile(r'(?:বিধি|নিয়ম|নিয়ম|রুল)\s*([0-9A-Za-z]+)', re.IGNORECASE), r'Rule \1'),
    (re.compile(r'(?:উপধারা|সাবসেকশন)\s*([0-9A-Za-z]+)', re.IGNORECASE), r'(\1)'),
]

# ─── Comprehensive Bangladesh Legal Dictionary (Structured Schema) ───────────
# Each entry binds specific sections to its respective Act only.
LEGAL_DICTIONARY: list[dict] = [
    # ── Property & Land Law ──
    {
        "term_bn": "বায়না",
        "term_en": "baina",
        "canonical": "Contract for Sale of Immovable Property",
        "aliases": ["বায়না দলিল", "বায়নাপত্র", "bainapatra", "agreement for sale", "contract for sale", "baina"],
        "authorities": [
            {"act": "The Registration Act, 1908", "sections": ["17A"], "role": "CONTROLLING"},
            {"act": "The Transfer of Property Act, 1882", "sections": ["54A"], "role": "CONTROLLING"},
            {"act": "The Specific Relief Act, 1877", "sections": ["21A"], "role": "SUPPORTING"}
        ],
        "domain": "Property"
    },
    {
        "term_bn": "নামজারি",
        "term_en": "namjari",
        "canonical": "Mutation of Record of Rights",
        "aliases": ["মিউটেশন", "mutation", "e-namjari", "ই-নামজারি", "খারিজ", "kharij", "জমা খারিজ", "joma kharij"],
        "authorities": [
            {"act": "The State Acquisition and Tenancy Act, 1950", "sections": ["143", "144", "116", "117"], "role": "CONTROLLING"}
        ],
        "domain": "Property"
    },
    {
        "term_bn": "খতিয়ান",
        "term_en": "khatian",
        "canonical": "Record of Rights (RoR)",
        "aliases": ["পর্চা", "porcha", "CS", "SA", "RS", "BS", "সিটি জরিপ", "record of rights", "ROR"],
        "authorities": [
            {"act": "The State Acquisition and Tenancy Act, 1950", "sections": ["144", "144A", "144B"], "role": "CONTROLLING"},
            {"act": "The Evidence Act, 1872", "sections": ["35"], "role": "SUPPORTING"}
        ],
        "domain": "Property"
    },
    {
        "term_bn": "হেবা",
        "term_en": "heba",
        "canonical": "Gift under Muslim Law",
        "aliases": ["হেবা দলিল", "দানপত্র", "gift deed", "hiba-bil-ewaz", "হেবা বিল এওয়াজ"],
        "authorities": [
            {"act": "The Registration Act, 1908", "sections": ["17(1)"], "role": "CONTROLLING"},
            {"act": "The Transfer of Property Act, 1882", "sections": ["122", "123"], "role": "SUPPORTING"}
        ],
        "domain": "Property"
    },
    {
        "term_bn": "অগ্রক্রয়",
        "term_en": "pre-emption",
        "canonical": "Right of Pre-emption",
        "aliases": ["হকশুফা", "shufa", "pre-emption", "preemption", "অগ্রক্রয়"],
        "authorities": [
            {"act": "The State Acquisition and Tenancy Act, 1950", "sections": ["96"], "role": "CONTROLLING"}
        ],
        "domain": "Property"
    },

    # ── Criminal Procedure & Penal Law ──
    {
        "term_bn": "নারাজি",
        "term_en": "naraji",
        "canonical": "Protest Petition against Police Final Report",
        "aliases": ["নারাজি পিটিশন", "naraji petition", "no-objection", "protest petition", "নারাজী"],
        "authorities": [
            {"act": "The Code of Criminal Procedure, 1898", "sections": ["173", "190", "200"], "role": "CONTROLLING"}
        ],
        "domain": "Criminal"
    },
    {
        "term_bn": "রিমান্ড",
        "term_en": "remand",
        "canonical": "Police Custody / Detention for Investigation",
        "aliases": ["পুলিশ হেফাজত", "police custody", "remand in custody", "ম্যাজিস্ট্রেট হেফাজত"],
        "authorities": [
            {"act": "The Code of Criminal Procedure, 1898", "sections": ["61", "167"], "role": "CONTROLLING"},
            {"act": "The Constitution of the People's Republic of Bangladesh", "sections": ["33"], "role": "SUPPORTING"}
        ],
        "domain": "Criminal"
    },
    {
        "term_bn": "জামিন",
        "term_en": "bail",
        "canonical": "Bail / Anticipatory Bail",
        "aliases": ["আগাম জামিন", "anticipatory bail", "interim bail", "অন্তর্র্বতীকালীন জামিন", "bailable offence"],
        "authorities": [
            {"act": "The Code of Criminal Procedure, 1898", "sections": ["496", "497", "498"], "role": "CONTROLLING"}
        ],
        "domain": "Criminal"
    },
    {
        "term_bn": "কোয়াশমেন্ট",
        "term_en": "quashment",
        "canonical": "Quashing of Criminal Proceedings (Section 561A CrPC)",
        "aliases": ["quashing", "quash", "561A", "section 561A", "বাতিল", "খারিজ মামলা", "inherent power"],
        "authorities": [
            {"act": "The Code of Criminal Procedure, 1898", "sections": ["561A", "561"], "role": "CONTROLLING"}
        ],
        "domain": "Criminal"
    },
    {
        "term_bn": "এজাহার",
        "term_en": "FIR",
        "canonical": "First Information Report (FIR)",
        "aliases": ["এফআইআর", "first information report", "প্রাথমিক তথ্য বিবরণী", "থানায় মামলা", "lodging an fir"],
        "authorities": [
            {"act": "The Code of Criminal Procedure, 1898", "sections": ["154", "156"], "role": "CONTROLLING"}
        ],
        "domain": "Criminal"
    },
    {
        "term_bn": "১৪৪ ধারা",
        "term_en": "section 144",
        "canonical": "Prohibitory Injunction / Urgent Restraint Order",
        "aliases": ["নিষেধাজ্ঞা", "curfew", "১৪৪ ধারা জারি", "জরুরি আদেশ", "prohibitory order"],
        "authorities": [
            {"act": "The Code of Criminal Procedure, 1898", "sections": ["144"], "role": "CONTROLLING"}
        ],
        "domain": "Criminal"
    },

    # ── Civil Procedure & Remedies ──
    {
        "term_bn": "নিষেধাজ্ঞা",
        "term_en": "injunction",
        "canonical": "Temporary and Permanent Injunction",
        "aliases": ["অস্থায়ী নিষেধাজ্ঞা", "temporary injunction", "status quo", "স্টে অর্ডার", "অর্ডার ৩৯"],
        "authorities": [
            {"act": "The Code of Civil Procedure, 1908", "sections": ["Order 39", "Order 39 Rule 1", "Order 39 Rule 2", "39"], "role": "CONTROLLING"},
            {"act": "The Specific Relief Act, 1877", "sections": ["52", "53", "54"], "role": "SUPPORTING"}
        ],
        "domain": "Civil"
    },
    {
        "term_bn": "আরজি খারিজ",
        "term_en": "rejection of plaint",
        "canonical": "Rejection of Plaint (Order 7 Rule 11 CPC)",
        "aliases": ["rejection of plaint", "order 7 rule 11", "৭ আদেশ ১১ নিয়ম", "মামলা খারিজ", "cause of action"],
        "authorities": [
            {"act": "The Code of Civil Procedure, 1908", "sections": ["Order 7 Rule 11", "7", "Order 7"], "role": "CONTROLLING"}
        ],
        "domain": "Civil"
    },
    {
        "term_bn": "একতরফা ডিক্রি বাতিল",
        "term_en": "setting aside ex-parte decree",
        "canonical": "Setting Aside Ex-Parte Decree (Order 9 Rule 13 CPC)",
        "aliases": ["setting aside ex-parte", "ex-parte decree", "একতরফা ডিক্রি", "order 9 rule 13", "৯ আদেশ ১৩ নিয়ম"],
        "authorities": [
            {"act": "The Code of Civil Procedure, 1908", "sections": ["Order 9 Rule 13", "9", "Order 9"], "role": "CONTROLLING"}
        ],
        "domain": "Civil"
    },

    # ── Family Law & Dower ──
    {
        "term_bn": "দেনমোহর",
        "term_en": "dower",
        "canonical": "Mahr / Dower Recovery and Payment",
        "aliases": ["mohorana", "দেনমোহরানা", "mohor", "prompt dower", "deferred dower", "দাবি দেনমোহর"],
        "authorities": [
            {"act": "The Muslim Family Laws Ordinance, 1961", "sections": ["10"], "role": "CONTROLLING"},
            {"act": "Family Courts Act, 2023", "sections": ["5"], "role": "SUPPORTING"}
        ],
        "domain": "Family"
    },
    {
        "term_bn": "খোরপোশ",
        "term_en": "maintenance",
        "canonical": "Maintenance of Wife and Children (Nafaqah)",
        "aliases": ["ভরণপোষণ", "maintenance", "nafaqah", "খোরপোষ", "স্ত্রী ও সন্তানের ভরণপোষণ"],
        "authorities": [
            {"act": "The Muslim Family Laws Ordinance, 1961", "sections": ["9"], "role": "CONTROLLING"},
            {"act": "Family Courts Act, 2023", "sections": ["5"], "role": "SUPPORTING"}
        ],
        "domain": "Family"
    },
    {
        "term_bn": "তালাক",
        "term_en": "talaq",
        "canonical": "Divorce and Notice Procedure under MFLO",
        "aliases": ["divorce", "তালাক নোটিশ", "notice of talaq", "dissolution of marriage", "তালাকনামা"],
        "authorities": [
            {"act": "The Muslim Family Laws Ordinance, 1961", "sections": ["7", "8"], "role": "CONTROLLING"},
            {"act": "The Dissolution of Muslim Marriages Act, 1939", "sections": ["2"], "role": "SUPPORTING"}
        ],
        "domain": "Family"
    },
    {
        "term_bn": "বহুবিবাহ",
        "term_en": "polygamy",
        "canonical": "Polygamy / Permission for Second Marriage",
        "aliases": ["দ্বিতীয় বিবাহ", "second marriage", "permission for polygamy", "সালিশি পরিষদ"],
        "authorities": [
            {"act": "The Muslim Family Laws Ordinance, 1961", "sections": ["6"], "role": "CONTROLLING"}
        ],
        "domain": "Family"
    },
    {
        "term_bn": "পারিবারিক আদালতের এখতিয়ার",
        "term_en": "family court jurisdiction",
        "canonical": "Exclusive Jurisdiction of Family Court",
        "aliases": ["family courts act", "family court", "পারিবারিক আদালত", "jurisdiction of family court", "section 5"],
        "authorities": [
            {"act": "Family Courts Act, 2023", "sections": ["5"], "role": "CONTROLLING"},
            {"act": "The Family Courts Ordinance, 1985", "sections": ["5", "6", "23"], "role": "LEGACY_CORPUS"}
        ],
        "domain": "Family"
    },

    # ── Commercial, Labour & Contract Law ──
    {
        "term_bn": "চেক ডিজঅনার",
        "term_en": "cheque dishonour",
        "canonical": "Dishonour of Cheque (Section 138 NI Act)",
        "aliases": ["চেক প্রতারণা", "cheque bounce", "bounced cheque", "138 ধারার মামলা", "এনআই এ্যাক্ট"],
        "authorities": [
            {"act": "The Negotiable Instruments Act, 1881", "sections": ["138", "140", "141"], "role": "CONTROLLING"}
        ],
        "domain": "Commercial"
    },
    {
        "term_bn": "চুক্তি ভঙ্গ ও ক্ষতিপূরণ",
        "term_en": "breach of contract compensation",
        "canonical": "Compensation for Loss or Damage Caused by Breach of Contract",
        "aliases": ["breach of contract", "loss or damage", "compensation for loss", "চুক্তি ভঙ্গ", "section 73"],
        "authorities": [
            {"act": "The Contract Act, 1872", "sections": ["73", "74"], "role": "CONTROLLING"}
        ],
        "domain": "Contract"
    },
    {
        "term_bn": "অংশ সম্পাদন নীতি",
        "term_en": "doctrine of part performance",
        "canonical": "Doctrine of Part Performance (Section 53A TPA)",
        "aliases": ["part performance", "doctrine of part", "53A", "অংশ সম্পাদন", "section 53A"],
        "authorities": [
            {"act": "The Transfer of Property Act, 1882", "sections": ["53A", "53"], "role": "CONTROLLING"}
        ],
        "domain": "Property"
    },
    {
        "term_bn": "শ্রমিক ছাঁটাই",
        "term_en": "retrenchment of workers",
        "canonical": "Retrenchment and Compensation under Labour Act",
        "aliases": ["retrenchment", "ছাঁটাই", "retrenchment of workers", "section 20", "শ্রম আইন"],
        "authorities": [
            {"act": "The Bangladesh Labour Act, 2006", "sections": ["20"], "role": "CONTROLLING"}
        ],
        "domain": "Labour"
    },
    {
        "term_bn": "চাকরি অবসান বা বরখাস্ত",
        "term_en": "termination of employment",
        "canonical": "Termination of Employment by Employer",
        "aliases": ["termination of employment", "notice or wages in lieu", "বিনা নোটিশে বরখাস্ত", "section 26"],
        "authorities": [
            {"act": "The Bangladesh Labour Act, 2006", "sections": ["26"], "role": "CONTROLLING"}
        ],
        "domain": "Labour"
    },
    {
        "term_bn": "শ্রমিকের পদত্যাগ",
        "term_en": "resignation by worker",
        "canonical": "Resignation by Worker and Service Benefits",
        "aliases": ["resignation by a worker", "service benefits", "পদত্যাগ", "section 27"],
        "authorities": [
            {"act": "The Bangladesh Labour Act, 2006", "sections": ["27"], "role": "CONTROLLING"}
        ],
        "domain": "Labour"
    },
    {
        "term_bn": "শ্রমিক অভিযোগ পদ্ধতি",
        "term_en": "worker grievance",
        "canonical": "Grievance Procedure for Individual Worker Complaints",
        "aliases": ["grievance procedure", "individual worker complaints", "worker complaint", "section 33", "অভিযোগ পদ্ধতি"],
        "authorities": [
            {"act": "The Bangladesh Labour Act, 2006", "sections": ["33", "34"], "role": "CONTROLLING"}
        ],
        "domain": "Labour"
    },
    {
        "term_bn": "ভোক্তা অভিযোগ ও জরিমানা",
        "term_en": "consumer fine distribution",
        "canonical": "Consumer Complaint and 25% Fine Entitlement",
        "aliases": ["defective or adulterated products", "25% of the fine", "receive 25% of the fine", "section 76", "ভোক্তা অধিকার", "adulterated product"],
        "authorities": [
            {"act": "Consumers' Right Protection Act, 2009", "sections": ["76", "Guide-29", "45"], "role": "CONTROLLING"}
        ],
        "domain": "Consumer"
    },
    {
        "term_bn": "আয়কর রিটার্ন দাখিল",
        "term_en": "income tax return",
        "canonical": "Mandatory Submission of Return of Income",
        "aliases": ["income tax act", "return of income", "submission of return of income", "tax return", "আয়কর রিটার্ন", "section 166"],
        "authorities": [
            {"act": "Income Tax Act, 2023", "sections": ["166", "174", "Guide-21"], "role": "CONTROLLING"},
            {"act": "The Income-tax Ordinance, 1984", "sections": ["166", "174"], "role": "LEGACY_CORPUS"}
        ],
        "domain": "Taxation"
    },
    {
        "term_bn": "নির্যাতন ও নিষ্ঠুর সাজা থেকে সুরক্ষা",
        "term_en": "protection against torture",
        "canonical": "Protection Against Torture and Degrading Punishment",
        "aliases": ["torture or cruel", "cruel, inhuman", "degrading punishment", "article 35(5)", "35(5)", "নির্যাতন"],
        "authorities": [
            {"act": "The Constitution of the People's Republic of Bangladesh", "sections": ["35", "35(5)"], "role": "CONTROLLING"}
        ],
        "domain": "Constitutional"
    },
    {
        "term_bn": "বেদখল সম্পত্তি উদ্ধার",
        "term_en": "recovery of possession without consent",
        "canonical": "Suit by Person Dispossessed of Immovable Property without Consent",
        "aliases": ["dispossessed without consent", "recovery of possession", "section 9", "সুনির্দিষ্ট প্রতিকার", "বেদখল"],
        "authorities": [
            {"act": "The Specific Relief Act, 1877", "sections": ["9", "8"], "role": "CONTROLLING"}
        ],
        "domain": "Property"
    },
    {
        "term_bn": "ওয়ারেন্ট ছাড়া গ্রেফতার",
        "term_en": "arrest without warrant",
        "canonical": "Arrest without Warrant by Police",
        "aliases": ["arrest without a warrant", "arrest without", "without a warrant", "without warrant", "arrest a person", "বিনা পরোয়ানায় গ্রেপ্তার", "বিনা পরোয়ানায় গ্রেফতার", "police arrest conditions"],
        "authorities": [
            {"act": "The Code of Criminal Procedure, 1898", "sections": ["54", "76", "55", "46", "61"], "role": "CONTROLLING"},
            {"act": "The Constitution of the People's Republic of Bangladesh", "sections": ["33"], "role": "SUPPORTING"}
        ],
        "domain": "Criminal"
    },
    {
        "term_bn": "ভেজাল বা মেয়াদোত্তীর্ণ পণ্য",
        "term_en": "adulterated goods penalty",
        "canonical": "Penalties for Adulterated or Expired Goods",
        "aliases": ["adulterated goods", "expired goods", "ভেজাল পণ্য", "মেয়াদোত্তীর্ণ পণ্য", "selling adulterated", "selling expired"],
        "authorities": [
            {"act": "Consumers' Right Protection Act, 2009", "sections": ["45", "Guide-29", "76"], "role": "CONTROLLING"}
        ],
        "domain": "Consumer"
    }
]


def normalize_bengali_text(text: str) -> str:
    """Converts Bengali numerals to ASCII and standardizes statutory prefixes."""
    if not text:
        return ""
    
    # 1. Translate Bengali digits to English
    normalized = text.translate(BN_DIGITS)
    
    # 2. Normalize statutory keywords (e.g. ধারা ১৭ক -> Section 17A)
    for pattern, replacement in STATUTORY_PREFIX_PATTERNS:
        normalized = pattern.sub(replacement, normalized)
        
    # 3. Normalize Bengali sub-letters (১৭ক -> 17A, ৫৪ক -> 54A, ২১ক -> 21A)
    bn_suffix_map = {
        "ক": "A", "খ": "B", "গ": "C", "ঘ": "D", "ঙ": "E",
        "চ": "F", "ছ": "G", "জ": "H", "ঝ": "I", "ঞ": "J"
    }
    for bn_letter, en_letter in bn_suffix_map.items():
        normalized = re.sub(rf'([0-9]+)\s*{bn_letter}\b', rf'\1{en_letter}', normalized)
        
    return normalized.strip()


def extract_legal_dictionary_matches(query: str) -> list[dict]:
    """Scans the query for terms in the bilingual legal dictionary and returns candidate targets."""
    normalized = normalize_bengali_text(query)
    q_lower = normalized.lower()
    matches = []
    seen_concepts = set()

    scored_matches: list[tuple[int, dict]] = []

    for item in LEGAL_DICTIONARY:
        canonical = item["canonical"]
        if canonical in seen_concepts:
            continue

        # Match bn term, en term, or any alias
        all_terms = [item["term_bn"], item["term_en"]] + item.get("aliases", [])
        for term in all_terms:
            t_clean = normalize_bengali_text(term).strip()
            if not t_clean:
                continue
            
            is_matched = False
            match_len = len(t_clean)

            if len(t_clean) <= 3 and t_clean.isascii():
                # Strict case-sensitive or word boundary check for short acronyms like CS, SA, RS, FIR
                if re.search(rf'\b{re.escape(t_clean)}\b', normalized, re.IGNORECASE):
                    is_matched = True
            elif t_clean.isascii():
                # English words require word boundaries
                if re.search(rf'\b{re.escape(t_clean.lower())}\b', q_lower):
                    is_matched = True
            else:
                # Bengali phrases require exact substring match
                if t_clean in normalized:
                    is_matched = True

            if is_matched:
                scored_matches.append((match_len, item))
                seen_concepts.add(canonical)
                break

    # Sort by longest/most specific match first, take at most top 2 concepts
    scored_matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in scored_matches[:2]]


def expand_query_with_dictionary(query: str) -> dict:
    """
    Expands a raw query with normalized concepts, candidate Acts, and structured per-Act sections.
    Guarantees non-Cartesian binding between Acts and specific sections.
    """
    normalized_q = normalize_bengali_text(query)
    matches = extract_legal_dictionary_matches(normalized_q)

    candidate_acts: list[str] = []
    candidate_sections: list[str] = []
    act_to_sections: dict[str, list[str]] = {}
    structured_authorities: list[dict] = []
    domains: set[str] = set()
    concepts: list[str] = []

    for m in matches:
        concepts.append(m["canonical"])
        domains.add(m.get("domain", "General"))
        authorities = m.get("authorities", [])
        for auth in authorities:
            act = auth["act"]
            secs = auth.get("sections", [])
            role = auth.get("role", "SUPPORTING")

            if act not in candidate_acts:
                candidate_acts.append(act)
            if act not in act_to_sections:
                act_to_sections[act] = []
            for s in secs:
                if s not in act_to_sections[act]:
                    act_to_sections[act].append(s)
                if s not in candidate_sections:
                    candidate_sections.append(s)

            structured_authorities.append({
                "act": act,
                "sections": secs,
                "role": role,
                "concept": m["canonical"]
            })

    return {
        "original_query": query,
        "normalized_query": normalized_q,
        "concepts": concepts,
        "domains": list(domains),
        "candidate_acts": candidate_acts,
        "candidate_sections": candidate_sections,
        "act_to_sections": act_to_sections,
        "structured_authorities": structured_authorities,
    }
