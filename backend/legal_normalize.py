from __future__ import annotations

import hashlib
import re
import unicodedata


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_act_alias(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower()
    value = value.replace("&", "and")
    value = re.sub(r"\bthe\b", "", value)
    value = re.sub(r"[^a-z0-9]+", "", value)
    return value


def normalize_section(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = value.strip()
    value = re.sub(r"^(section|sec\.?|s\.?)\s*", "", value, flags=re.I)
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
