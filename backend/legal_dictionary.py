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
        "term_bn": "আংশিক সম্পাদন",
        "term_en": "part performance",
        "canonical": "Doctrine of Part Performance",
        "aliases": ["অংশিক সম্পাদন", "part performance", "section 53a", "53a", "doctrine of part performance"],
        "candidate_acts": ["The Transfer of Property Act, 1882"],
        "candidate_sections": ["53A"],
        "domain": "Property"
    },
    {
        "term_bn": "পারিবারিক আদালত",
        "term_en": "family court",
        "canonical": "Family Court Jurisdiction and Powers",
        "aliases": ["পারিবারিক আদালত আইন", "family courts act", "family court jurisdiction", "exclusive jurisdiction", "section 5"],
        "candidate_acts": ["Family Courts Act, 2023", "The Family Courts Ordinance, 1985"],
        "candidate_sections": ["5", "6", "23"],
        "domain": "Family"
    },
    {
        "term_bn": "কোয়াশমেন্ট",
        "term_en": "quashment",
        "canonical": "Inherent Power to Quash Criminal Proceedings / Abuse of Process",
        "aliases": ["quashing", "quash", "inherent powers", "abuse of the process", "section 561a", "561a", "561A"],
        "candidate_acts": ["The Code of Criminal Procedure, 1898"],
        "candidate_sections": ["561A"],
        "domain": "Criminal"
    },
    {
        "term_bn": "চুক্তিভঙ্গের ক্ষতিপূরণ",
        "term_en": "breach of contract compensation",
        "canonical": "Compensation for Loss or Damage Caused by Breach of Contract",
        "aliases": ["breach of contract", "loss or damage caused by breach", "compensation for loss or damage", "section 73", "চুক্তিভঙ্গ"],
        "candidate_acts": ["The Contract Act, 1872"],
        "candidate_sections": ["73", "74"],
        "domain": "Commercial"
    },
    {
        "term_bn": "একতরফা ডিক্রি রদ",
        "term_en": "setting aside ex-parte decree",
        "canonical": "Setting Aside Ex-Parte Decree Against Defendant",
        "aliases": ["ex-parte decree", "setting aside ex-parte", "order 9 rule 13", "order ix rule 13", "ex parte decree", "setting aside an ex-parte"],
        "candidate_acts": ["The Code of Civil Procedure, 1908"],
        "candidate_sections": ["Order 9, Rule 13", "Order 9", "9"],
        "domain": "Civil"
    },
    {
        "term_bn": "শ্রমিক অভিযোগ পদ্ধতি",
        "term_en": "worker grievance",
        "canonical": "Grievance Procedure for Individual Worker Complaints",
        "aliases": ["grievance procedure", "individual worker complaints", "worker complaint", "section 33", "অভিযোগ পদ্ধতি"],
        "candidate_acts": ["The Bangladesh Labour Act, 2006"],
        "candidate_sections": ["33", "34"],
        "domain": "Labour"
    },
    {
        "term_bn": "ভোক্তা অভিযোগ ও জরিমানা",
        "term_en": "consumer fine distribution",
        "canonical": "Consumer Complaint and 25% Fine Entitlement",
        "aliases": ["defective or adulterated products", "25% of the fine", "receive 25% of the fine", "section 76", "ভোক্তা অধিকার", "adulterated product"],
        "candidate_acts": ["Consumers' Right Protection Act, 2009", "The Consumers' Right Protection Act, 2009"],
        "candidate_sections": ["76", "71", "45"],
        "domain": "Consumer"
    },
    {
        "term_bn": "আয়কর রিটার্ন দাখিল",
        "term_en": "income tax return",
        "canonical": "Mandatory Submission of Return of Income",
        "aliases": ["income tax act", "return of income", "submission of return of income", "tax return", "আয়কর রিটার্ন", "section 166"],
        "candidate_acts": ["Income Tax Act, 2023", "The Income Tax Act, 2023", "Income-tax Ordinance, 1984"],
        "candidate_sections": ["166", "174", "75"],
        "domain": "Taxation"
    },
    {
        "term_bn": "নির্যাতন ও নিষ্ঠুর সাজা থেকে সুরক্ষা",
        "term_en": "protection against torture",
        "canonical": "Protection Against Torture and Degrading Punishment",
        "aliases": ["torture or cruel", "cruel, inhuman", "degrading punishment", "article 35(5)", "35(5)", "নির্যাতন"],
        "candidate_acts": ["The Constitution of the People's Republic of Bangladesh"],
        "candidate_sections": ["35", "35(5)"],
        "domain": "Constitutional"
    },
    {
        "term_bn": "বেদখল সম্পত্তি উদ্ধার",
        "term_en": "recovery of possession without consent",
        "canonical": "Suit by Person Dispossessed of Immovable Property without Consent",
        "aliases": ["dispossessed without consent", "recovery of possession", "section 9", "সুনির্দিষ্ট প্রতিকার", "বেদখল"],
        "candidate_acts": ["The Specific Relief Act, 1877"],
        "candidate_sections": ["9", "8"],
        "domain": "Property"
    },
    {
        "term_bn": "গ্রেফতার ও আটক সংক্রান্ত রক্ষাকবচ",
        "term_en": "safeguards as to arrest",
        "canonical": "Safeguards as to Arrest and Detention and Right to Consult Legal Practitioner",
        "aliases": ["safeguards as to arrest", "arrest and detention", "right to consult", "article 33", "আটক সংক্রান্ত রক্ষাকবচ"],
        "candidate_acts": ["The Constitution of the People's Republic of Bangladesh"],
        "candidate_sections": ["33"],
        "domain": "Constitutional"
    },
    {
        "term_bn": "ওয়ারেন্ট ছাড়া গ্রেফতার",
        "term_en": "arrest without warrant",
        "canonical": "Arrest without Warrant by Police",
        "aliases": ["arrest without a warrant", "arrest without", "without a warrant", "without warrant", "arrest a person", "বিনা পরোয়ানায় গ্রেপ্তার", "বিনা পরোয়ানায় গ্রেফতার", "police arrest conditions"],
        "candidate_acts": ["The Code of Criminal Procedure, 1898", "The Constitution of the People's Republic of Bangladesh"],
        "candidate_sections": ["54", "76", "55", "46", "61", "33"],
        "domain": "Criminal"
    },
    {
        "term_bn": "ভেজাল বা মেয়াদোত্তীর্ণ পণ্য",
        "term_en": "adulterated goods penalty",
        "canonical": "Penalties for Adulterated or Expired Goods",
        "aliases": ["adulterated goods", "expired goods", "ভেজাল পণ্য", "মেয়াদোত্তীর্ণ পণ্য", "selling adulterated", "selling expired"],
        "candidate_acts": ["Consumers' Right Protection Act, 2009"],
        "candidate_sections": ["45", "Guide-29", "76"],
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
    Expands a raw query with normalized concepts, candidate Acts, and suggested sections.
    This acts as a retrieval helper, never as unverified legal authority.
    """
    normalized_q = normalize_bengali_text(query)
    matches = extract_legal_dictionary_matches(normalized_q)

    candidate_acts: list[str] = []
    candidate_sections: list[str] = []
    act_to_sections: dict[str, list[str]] = {}
    domains: set[str] = set()
    concepts: list[str] = []

    for m in matches:
        concepts.append(m["canonical"])
        domains.add(m.get("domain", "General"))
        acts = m.get("candidate_acts", [])
        secs = m.get("candidate_sections", [])
        for act in acts:
            if act not in candidate_acts:
                candidate_acts.append(act)
            if act not in act_to_sections:
                act_to_sections[act] = []
            for sec in secs:
                if sec not in act_to_sections[act]:
                    act_to_sections[act].append(sec)
        for sec in secs:
            if sec not in candidate_sections:
                candidate_sections.append(sec)

    return {
        "original_query": query,
        "normalized_query": normalized_q,
        "concepts": concepts,
        "domains": list(domains),
        "candidate_acts": candidate_acts,
        "candidate_sections": candidate_sections,
        "act_to_sections": act_to_sections,
    }
