"""
Justor AI — Unicode, Bengali Digit & Orthographic Normalizer
Provides NFKC Unicode normalization, Bengali digit translation, statutory reference parsing,
and language state detection (BN / EN / MIXED).
"""

from __future__ import annotations
import hashlib
import re
import unicodedata
from typing import Dict, List, Tuple, Literal

# ─── Bengali Digit Map ───────────────────────────────────────────────────────
BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

# ─── Bengali Orthographic Normalization Pairs ─────────────────────────────────
ORTHOGRAPHIC_VARIANTS: list[tuple[re.Pattern, str]] = [
    # য় (\u09af\u09bc) vs য় (\u09df) -> standardize to \u09df
    (re.compile(r'\u09af\u09bc', re.UNICODE), '\u09df'),
    
    # ী vs ি variants in legal terminology
    (re.compile(r'ফৌজদারী', re.UNICODE), 'ফৌজদারি'),
    (re.compile(r'তামাদী', re.UNICODE), 'তামাদি'),
    (re.compile(r'নারাজী', re.UNICODE), 'নারাজি'),
    (re.compile(r'নামজারী', re.UNICODE), 'নামজারি'),
    (re.compile(r'অগ্রক্রয়', re.UNICODE), 'অগ্রক্রয়'),
]

BANGLISH_INDICATORS = {
    "onujayi", "anujayi", "koto", "korar", "pore", "er", "ki", "hobe",
    "shomoy", "shomoyshima", "kotodin", "baina", "namjari", "kharij",
    "talaq", "denmohor", "jamin", "remand", "porcha", "khatian"
}

# ─── Statutory Prefix Normalizations ──────────────────────────────────────────
STATUTORY_PREFIX_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r'(?:ধারা|দফা|সেকশন)\s*([0-9A-Za-z]+)', re.IGNORECASE), r'Section \1'),
    (re.compile(r'(?:অনুচ্ছেদ|আর্টিকেল)\s*([0-9A-Za-z]+)', re.IGNORECASE), r'Article \1'),
    (re.compile(r'(?:আদেশ|অর্ডার)\s*([0-9IVXLCDM]+)', re.IGNORECASE), r'Order \1'),
    (re.compile(r'(?:বিধি|নিয়ম|নিয়ম|রুল)\s*([0-9A-Za-z]+)', re.IGNORECASE), r'Rule \1'),
    (re.compile(r'(?:উপধারা|সাবসেকশন)\s*([0-9A-Za-z]+)', re.IGNORECASE), r'(\1)'),
]

# Bengali subsection letters (১৭ক -> 17A, ৫৪ক -> 54A, ২১ক -> 21A, ৫৬১ক -> 561A)
BN_SUBSECTION_LETTERS = {
    "ক": "A", "খ": "B", "গ": "C", "ঘ": "D", "ঙ": "E",
    "চ": "F", "ছ": "G", "জ": "H", "ঝ": "I", "ঞ": "J"
}


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def detect_language(text: str) -> Literal["BN", "EN", "MIXED"]:
    """
    Detects whether text is pure Bengali, pure English, or mixed/Banglish.
    """
    if not text:
        return "EN"
    
    has_bengali = bool(re.search(r'[\u0980-\u09FF]', text))
    has_latin = bool(re.search(r'[A-Za-z]', text))

    if has_bengali and has_latin:
        return "MIXED"
    elif has_bengali:
        return "BN"

    # Check for Banglish words in pure Latin script text
    words = set(re.findall(r'\b[a-zA-Z]+\b', text.lower()))
    if words.intersection(BANGLISH_INDICATORS):
        return "MIXED"

    return "EN"


def normalize_bengali_text(text: str) -> str:
    """
    Standardizes Bengali text:
    1. NFKC Unicode normalization.
    2. Bengali numerals (০-৯) -> ASCII digits (0-9).
    3. Orthographic spelling variants.
    4. Statutory prefixes (ধারা -> Section, অনুচ্ছেদ -> Article, আদেশ -> Order).
    5. Bengali subsection letters (১৭ক -> 17A).
    """
    if not text:
        return ""

    # 1. NFKC normalization
    normalized = unicodedata.normalize("NFKC", text)

    # 2. Bengali to ASCII digits
    normalized = normalized.translate(BN_DIGITS)

    # 3. Orthographic spelling consistency
    for pattern, replacement in ORTHOGRAPHIC_VARIANTS:
        normalized = pattern.sub(replacement, normalized)

    # 4. Statutory prefixes
    for pattern, replacement in STATUTORY_PREFIX_PATTERNS:
        normalized = pattern.sub(replacement, normalized)

    # 5. Subsection letters
    for bn_letter, en_letter in BN_SUBSECTION_LETTERS.items():
        normalized = re.sub(rf'([0-9]+)\s*{bn_letter}\b', rf'\1{en_letter}', normalized)

    return normalize_whitespace(normalized)


def normalize_act_alias(value: str) -> str:
    value = normalize_bengali_text(value).lower()
    value = value.replace("&", "and")
    value = re.sub(r"\bthe\b", "", value)
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def normalize_section(value: str) -> str:
    value = normalize_bengali_text(value).strip()
    value = re.sub(r"^(section|sec\.?|s\.?|ধারা)\s*", "", value, flags=re.I)
    return value.replace(" ", "").upper()


def split_section_reference(value: str) -> tuple[str, list[str]]:
    """
    17A      -> ("17A", [])
    17A(2)   -> ("17A", ["2"])
    55(4)(b) -> ("55", ["4", "b"])
    """
    normalized = normalize_section(value)
    match = re.match(r"^([0-9]+[A-Z]?)(.*)$", normalized)
    if not match:
        return normalized, []
    root = match.group(1)
    tail = match.group(2)
    parts = re.findall(r"\(([^)]+)\)", tail)
    return root, parts


def normalize_quote(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = (
        value.replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )
    return normalize_whitespace(value)


def source_hash(value: str) -> str:
    normalized = normalize_quote(value)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
