"""
Justor AI — Bilingual Legal Dictionary & Query Normalizer for Bangladesh Law
Maps colonial, Farsi-influenced, and Bengali legal terminology into canonical concepts,
and normalizes Bengali numerals and statutory prefixes for 100% retrieval accuracy.
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

# ─── Comprehensive Bangladesh Legal Dictionary ────────────────────────────────
# Maps local/Farsi/colonial terms to canonical concepts, primary candidate Acts, and sections.
LEGAL_DICTIONARY: list[dict] = [
    # ── Property & Land Law ──
    {
        "term_bn": "বায়না",
        "term_en": "baina",
        "canonical": "Contract for Sale of Immovable Property",
        "aliases": ["বায়না দলিল", "বায়নাপত্র", "bainapatra", "agreement for sale", "contract for sale"],
        "candidate_acts": ["The Registration Act, 1908", "The Transfer of Property Act, 1882", "The Specific Relief Act, 1877"],
        "candidate_sections": ["17A", "54A", "21A"],
        "domain": "Property"
    },
    {
        "term_bn": "নামজারি",
        "term_en": "namjari",
        "canonical": "Mutation of Record of Rights",
        "aliases": ["মিউটেশন", "mutation", "e-namjari", "ই-নামজারি", "খারিজ", "kharij", "জমা খারিজ", "joma kharij"],
        "candidate_acts": ["The State Acquisition and Tenancy Act, 1950", "The Land Reform Act, 2023"],
        "candidate_sections": ["143", "144", "116", "117"],
        "domain": "Property"
    },
    {
        "term_bn": "খতিয়ান",
        "term_en": "khatian",
        "canonical": "Record of Rights (RoR)",
        "aliases": ["পর্চা", "porcha", "CS", "SA", "RS", "BS", "সিটি জরিপ", "record of rights", "ROR"],
        "candidate_acts": ["The State Acquisition and Tenancy Act, 1950", "The Evidence Act, 1872"],
        "candidate_sections": ["144", "144A", "144B", "35"],
        "domain": "Property"
    },
    {
        "term_bn": "হেবা",
        "term_en": "heba",
        "canonical": "Gift under Muslim Law",
        "aliases": ["হেবা দলিল", "দানপত্র", "gift deed", "hiba-bil-ewaz", "হেবা বিল এওয়াজ"],
        "candidate_acts": ["The Registration Act, 1908", "The Transfer of Property Act, 1882"],
        "candidate_sections": ["17(1)", "122", "123"],
        "domain": "Property"
    },
    {
        "term_bn": "অগ্রক্রয়",
        "term_en": "pre-emption",
        "canonical": "Right of Pre-emption",
        "aliases": ["হকশুফা", "shufa", "pre-emption", "preemption", "অগ্রক্রয়"],
        "candidate_acts": ["The State Acquisition and Tenancy Act, 1950", "The Transfer of Property Act, 1882"],
        "candidate_sections": ["96"],
        "domain": "Property"
    },

    # ── Criminal Procedure & Penal Law ──
    {
        "term_bn": "নারাজি",
        "term_en": "naraji",
        "canonical": "Protest Petition against Police Final Report",
        "aliases": ["নারাজি পিটিশন", "naraji petition", "no-objection", "protest petition", "নারাজী"],
        "candidate_acts": ["The Code of Criminal Procedure, 1898"],
        "candidate_sections": ["173", "190", "200"],
        "domain": "Criminal"
    },
    {
        "term_bn": "রিমান্ড",
        "term_en": "remand",
        "canonical": "Police Custody / Detention for Investigation",
        "aliases": ["পুলিশ হেফাজত", "police custody", "remand in custody", "ম্যাজিস্ট্রেট হেফাজত"],
        "candidate_acts": ["The Code of Criminal Procedure, 1898", "The Constitution of the People's Republic of Bangladesh"],
        "candidate_sections": ["61", "167", "33"],
        "domain": "Criminal"
    },
    {
        "term_bn": "জামিন",
        "term_en": "bail",
        "canonical": "Bail / Anticipatory Bail",
        "aliases": ["আগাম জামিন", "anticipatory bail", "interim bail", "অন্তর্র্বতীকালীন জামিন", "bailable offence"],
        "candidate_acts": ["The Code of Criminal Procedure, 1898"],
        "candidate_sections": ["496", "497", "498"],
        "domain": "Criminal"
    },
    {
        "term_bn": "এজাহার",
        "term_en": "ejahar",
        "canonical": "First Information Report (FIR)",
        "aliases": ["এফআইআর", "FIR", "first information report", "থানায় অভিযোগ", "মামলা দায়ের"],
        "candidate_acts": ["The Code of Criminal Procedure, 1898"],
        "candidate_sections": ["154", "156"],
        "domain": "Criminal"
    },
    {
        "term_bn": "সিআর মামলা",
        "term_en": "cr case",
        "canonical": "Complaint Case before Magistrate",
        "aliases": ["নালিশি মামলা", "court complaint", "complaint case", "সি.আর. মামলা"],
        "candidate_acts": ["The Code of Criminal Procedure, 1898"],
        "candidate_sections": ["200", "202", "203", "204"],
        "domain": "Criminal"
    },
    {
        "term_bn": "প্রতারণা",
        "term_en": "cheating",
        "canonical": "Cheating and Dishonestly Inducing Delivery of Property",
        "aliases": ["জালিয়াতি", "চিটিং", "cheating", "fraud", "420 মামলা", "চারশো বিশ"],
        "candidate_acts": ["The Penal Code, 1860"],
        "candidate_sections": ["415", "420", "406"],
        "domain": "Criminal"
    },

    # ── Family & Personal Law ──
    {
        "term_bn": "দেনমোহর",
        "term_en": "denmohor",
        "canonical": "Dower / Mahr",
        "aliases": ["মোহরানা", "mahr", "dower", "prompt dower", "deferred dower", "তলবি মোহরানা"],
        "candidate_acts": ["The Muslim Family Laws Ordinance, 1961", "The Family Courts Act, 2023"],
        "candidate_sections": ["10", "5"],
        "domain": "Family"
    },
    {
        "term_bn": "তালাক",
        "term_en": "talaq",
        "canonical": "Divorce and Dissolution of Marriage",
        "aliases": ["ডিভোর্স", "divorce", "talaq-e-tafweez", "খোলা তালাক", "khula", "সালিশি পরিষদ", "arbitration council"],
        "candidate_acts": ["The Muslim Family Laws Ordinance, 1961", "The Dissolution of Muslim Marriages Act, 1939", "The Family Courts Act, 2023"],
        "candidate_sections": ["7", "8", "2", "5"],
        "domain": "Family"
    },
    {
        "term_bn": "খোরপোষ",
        "term_en": "maintenance",
        "canonical": "Maintenance of Wife and Children",
        "aliases": ["ভরণপোষণ", "maintenance", "iddat maintenance", "সন্তানের ভরণপোষণ"],
        "candidate_acts": ["The Muslim Family Laws Ordinance, 1961", "The Family Courts Act, 2023"],
        "candidate_sections": ["9", "5"],
        "domain": "Family"
    },
    {
        "term_bn": "সন্তানের হেফাজত",
        "term_en": "custody of child",
        "canonical": "Guardianship and Custody of Minors",
        "aliases": ["হেফাজত", "হিজানত", "hizanat", "child custody", "অভিভাবকত্ব", "guardianship"],
        "candidate_acts": ["The Guardians and Wards Act, 1890", "The Family Courts Act, 2023"],
        "candidate_sections": ["17", "25", "5"],
        "domain": "Family"
    },

    # ── Civil Procedure & Commercial / Banking ──
    {
        "term_bn": "নিষেধাজ্ঞা",
        "term_en": "injunction",
        "canonical": "Temporary and Permanent Injunction",
        "aliases": ["অস্থায়ী নিষেধাজ্ঞা", "temporary injunction", "stay order", "স্থিতাবস্থা", "status quo", "স্থায়ী নিষেধাজ্ঞা"],
        "candidate_acts": ["The Code of Civil Procedure, 1908", "The Specific Relief Act, 1877"],
        "candidate_sections": ["Order 39 Rule 1", "Order 39 Rule 2", "52", "53", "54"],
        "domain": "Civil"
    },
    {
        "term_bn": "তামাদি",
        "term_en": "tamadi",
        "canonical": "Law of Limitation / Expiry of Time",
        "aliases": ["তামাদির মেয়াদ", "limitation period", "time barred", "তামাদি মওকুফ", "condonation of delay"],
        "candidate_acts": ["The Limitation Act, 1908"],
        "candidate_sections": ["3", "5", "14", "29"],
        "domain": "Civil"
    },
    {
        "term_bn": "চেক ডিজঅনার",
        "term_en": "cheque dishonour",
        "canonical": "Dishonour of Cheque for Insufficiency of Funds",
        "aliases": ["এন আই এক্ট", "NI Act case", "চেক বাউন্স", "cheque bounce", "138 মামলা"],
        "candidate_acts": ["The Negotiable Instruments Act, 1881"],
        "candidate_sections": ["138", "140", "141"],
        "domain": "Commercial"
    },
    {
        "term_bn": "অর্থ ঋণ",
        "term_en": "artha rin",
        "canonical": "Recovery of Loan by Financial Institutions",
        "aliases": ["অর্থ ঋণ আদালত", "money loan court", "bank loan default", "ঋণখেলাপি", "অকশন সেল"],
        "candidate_acts": ["The Artha Rin Adalat Ain, 2003"],
        "candidate_sections": ["12", "33", "41"],
        "domain": "Banking"
    },
    {
        "term_bn": "ভোক্তা অধিকার",
        "term_en": "consumer rights",
        "canonical": "Consumer Rights Protection and Compensation",
        "aliases": ["জাতীয় ভোক্তা অধিকার", "DNCRP", "ভেজাল পণ্য", "consumer complaint", "অতিরিক্ত দাম"],
        "candidate_acts": ["The Consumer Rights Protection Act, 2009"],
        "candidate_sections": ["40", "45", "53", "71", "76"],
        "domain": "Consumer"
    },
    {
        "term_bn": "শ্রম আইন",
        "term_en": "labour law",
        "canonical": "Labour Rights, Termination, Gratuity and Severance",
        "aliases": ["শ্রমিক ছাঁটাই", "retrenchment", "discharge", "gratuity", "সার্ভিস বেনিফিট", "মাতৃত্বকালীন ছুটি", "maternity benefit"],
        "candidate_acts": ["The Bangladesh Labour Act, 2006"],
        "candidate_sections": ["20", "22", "26", "27", "46", "33"],
        "domain": "Labour"
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
    normalized = normalize_bengali_text(query).lower()
    matches = []
    seen_concepts = set()
    
    for item in LEGAL_DICTIONARY:
        canonical = item["canonical"]
        if canonical in seen_concepts:
            continue
            
        # Match bn term, en term, or any alias
        all_terms = [item["term_bn"], item["term_en"]] + item.get("aliases", [])
        for term in all_terms:
            t_clean = normalize_bengali_text(term).lower()
            if t_clean in normalized or re.search(rf'\b{re.escape(t_clean)}\b', normalized):
                matches.append(item)
                seen_concepts.add(canonical)
                break
                
    return matches


def expand_query_with_dictionary(query: str) -> dict:
    """
    Expands a raw query with normalized concepts, candidate Acts, and suggested sections.
    This acts as a retrieval helper, never as unverified legal authority.
    """
    normalized_q = normalize_bengali_text(query)
    matches = extract_legal_dictionary_matches(normalized_q)
    
    candidate_acts: list[str] = []
    candidate_sections: list[str] = []
    domains: set[str] = set()
    concepts: list[str] = []
    
    for m in matches:
        concepts.append(m["canonical"])
        domains.add(m.get("domain", "General"))
        for act in m.get("candidate_acts", []):
            if act not in candidate_acts:
                candidate_acts.append(act)
        for sec in m.get("candidate_sections", []):
            if sec not in candidate_sections:
                candidate_sections.append(sec)
                
    return {
        "original_query": query,
        "normalized_query": normalized_q,
        "concepts": concepts,
        "domains": list(domains),
        "candidate_acts": candidate_acts,
        "candidate_sections": candidate_sections,
    }
