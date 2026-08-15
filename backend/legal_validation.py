from __future__ import annotations

import re
from .legal_models import (
    EvidencePack,
    LegalAnswerDraft,
    ValidationError,
    ValidationResult,
)
from .legal_normalize import normalize_quote, normalize_section

MATERIAL_TYPES = {
    "legal_rule",
    "procedure",
    "deadline",
    "amendment",
    "case_law",
}

SECTION_PATTERN = re.compile(
    r"\b(?:section|sec\.?|s\.)\s*"
    r"([0-9]+[A-Za-z]?(?:\([0-9A-Za-z]+\))*)",
    flags=re.I,
)

NUMBER_WORDS = {
    "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8",
    "nine": "9", "ten": "10", "fifteen": "15", "twenty": "20",
    "thirty": "30", "forty": "40", "forty-five": "45",
    "forty five": "45", "sixty": "60", "ninety": "90",
}


def remove_section_references(text: str) -> str:
    return SECTION_PATTERN.sub("SECTION_REF", text or "")


def extract_numeric_tokens(text: str) -> set[str]:
    text_lower = normalize_quote(remove_section_references(text)).lower()
    tokens = set(re.findall(r"\b\d+(?:\.\d+)?\b", text_lower))
    for word, value in NUMBER_WORDS.items():
        if re.search(rf"\b{re.escape(word)}\b", text_lower):
            tokens.add(value)
    return tokens


def evidence_map(pack: EvidencePack):
    return {item.evidence_id: item for item in pack.authorities}


def validate_evidence_ids(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> list[ValidationError]:
    errors = []
    allowed = set(evidence_map(pack))
    blocks = (
        draft.rules
        + draft.doctrine
        + draft.application
        + draft.key_points
        + ([draft.conclusion] if draft.conclusion else [])
    )

    for paragraph in blocks:
        for evidence_id in paragraph.evidence_ids:
            if evidence_id not in allowed:
                errors.append(
                    ValidationError(
                        code="INVALID_EVIDENCE_ID",
                        severity="critical",
                        message=f"Unknown evidence ID {evidence_id}",
                    )
                )
    return errors


def validate_material_claims(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> list[ValidationError]:
    errors = []
    sources = evidence_map(pack)

    for claim in draft.claims:
        if claim.claim_type not in MATERIAL_TYPES:
            continue

        if not claim.evidence_ids:
            errors.append(
                ValidationError(
                    code="UNSUPPORTED_MATERIAL_CLAIM",
                    severity="critical",
                    claim_id=claim.claim_id,
                    message="Material legal claim has no evidence.",
                )
            )
            continue

        claim_sections = {
            normalize_section(x)
            for x in SECTION_PATTERN.findall(claim.text)
        }

        supplied_sections = set()
        source_texts = []

        for evidence_id in claim.evidence_ids:
            source = sources.get(evidence_id)
            if not source:
                continue
            supplied_sections.add(normalize_section(source.section_number))
            source_texts.append(source.legal_text)

        if claim_sections and not any(
            any(
                cs.startswith(ss) or ss.startswith(cs)
                for ss in supplied_sections
            )
            for cs in claim_sections
        ):
            errors.append(
                ValidationError(
                    code="SECTION_CITATION_MISMATCH",
                    severity="critical",
                    claim_id=claim.claim_id,
                    message=(
                        f"Claim mentions {sorted(claim_sections)} but evidence "
                        f"points to {sorted(supplied_sections)}."
                    ),
                )
            )

        # Only material legal numbers are checked here.
        claim_numbers = extract_numeric_tokens(claim.text)
        evidence_numbers = set()
        for source_text in source_texts:
            evidence_numbers |= extract_numeric_tokens(source_text)

        missing_numbers = claim_numbers - evidence_numbers
        if missing_numbers:
            errors.append(
                ValidationError(
                    code="UNSUPPORTED_NUMBER",
                    severity="critical",
                    claim_id=claim.claim_id,
                    message=(
                        f"Legal numeric claim {sorted(missing_numbers)} "
                        "is not present in cited authority."
                    ),
                )
            )

    return errors


def validate_source_status(pack: EvidencePack) -> list[ValidationError]:
    errors = []
    for source in pack.authorities:
        if not source.exact_section_verified:
            errors.append(
                ValidationError(
                    code="SECTION_NOT_VERIFIED",
                    severity="critical",
                    message=f"{source.evidence_id} exact section not verified.",
                )
            )
        if not source.version_verified:
            errors.append(
                ValidationError(
                    code="VERSION_NOT_VERIFIED",
                    severity="critical",
                    message=f"{source.evidence_id} version not verified.",
                )
            )
    return errors


def validate_quote(quote: str, source_text: str) -> bool:
    return normalize_quote(quote) in normalize_quote(source_text)


def validate_draft(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> ValidationResult:
    errors = []
    errors += validate_source_status(pack)
    errors += validate_evidence_ids(draft, pack)
    errors += validate_material_claims(draft, pack)
    critical = any(error.severity == "critical" for error in errors)
    return ValidationResult(passed=not critical, errors=errors)
