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


def validate_heading_entailment(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> list[ValidationError]:
    """Gate 3: Validate that section headings and topics entail the claims asserted.
    Prevents corrupt section mappings (e.g. TPA §64 being cited for contract for sale).
    """
    errors = []
    sources = evidence_map(pack)
    
    # Topic conflict matrix for known critical statutory confusions
    CONFUSION_RULES = [
        {
            "topic_keywords": ["contract for sale", "agreement for sale", "baina", "sale deed", "unregistered contract"],
            "forbidden_headings": ["mortgage", "mortgaged", "lease", "usufructuary", "renewal"],
            "expected_sections": ["54", "54a", "17a", "21a"],
            "act_patterns": ["transfer of property", "tpa", "registration", "specific relief"],
            "error_message": "Contract for sale cannot be attributed to a mortgage or lease provision (e.g. Section 62/63/64)."
        },
        {
            "topic_keywords": ["superintendence", "control over subordinate courts"],
            "forbidden_articles": ["111"],
            "expected_articles": ["109"],
            "act_patterns": ["constitution"],
            "error_message": "High Court Division superintendence is governed by Article 109, not Article 111 (binding precedent)."
        },
        {
            "topic_keywords": ["binding effect", "doctrine of precedent", "binding on subordinate"],
            "forbidden_articles": ["109"],
            "expected_articles": ["111"],
            "act_patterns": ["constitution"],
            "error_message": "Doctrine of binding precedent is governed by Article 111, not Article 109 (superintendence)."
        },
        {
            "topic_keywords": ["self-incrimination", "witness against himself"],
            "forbidden_articles": ["35(3)", "35(5)"],
            "expected_articles": ["35(4)"],
            "act_patterns": ["constitution"],
            "error_message": "Privilege against self-incrimination is Article 35(4), not Article 35(3) or 35(5)."
        },
        {
            "topic_keywords": ["torture", "cruel, inhuman", "custodial violence"],
            "forbidden_articles": ["35(3)", "35(4)"],
            "expected_articles": ["35(5)"],
            "act_patterns": ["constitution"],
            "error_message": "Protection against torture is Article 35(5), not Article 35(3) or 35(4)."
        }
    ]

    all_blocks = (
        draft.rules
        + draft.doctrine
        + draft.application
        + draft.key_points
        + ([draft.conclusion] if draft.conclusion else [])
    )

    for block in all_blocks:
        block_text = block.text.lower()
        for ev_id in block.evidence_ids:
            source = sources.get(ev_id)
            if not source:
                continue
            
            source_heading = (source.heading or "").lower()
            source_sec = (source.section_number or "").lower()
            act_name = source.act_name.lower()

            for rule in CONFUSION_RULES:
                matches_act = any(pat in act_name for pat in rule["act_patterns"])
                if not matches_act:
                    continue

                has_topic = any(kw in block_text for kw in rule["topic_keywords"])
                if not has_topic:
                    continue

                if "forbidden_headings" in rule:
                    if any(fh in source_heading for fh in rule["forbidden_headings"]):
                        errors.append(
                            ValidationError(
                                code="SECTION_HEADING_MISMATCH",
                                severity="critical",
                                message=f"Gate 3 Failure: [{ev_id}] '{source.act_name} §{source.section_number}' ({source.heading}) does not entail topic. {rule['error_message']}",
                            )
                        )

                if "forbidden_articles" in rule:
                    if any(fa in source_sec for fa in rule["forbidden_articles"]) or any(fa in block_text for fa in rule["forbidden_articles"]):
                        errors.append(
                            ValidationError(
                                code="CONSTITUTIONAL_ARTICLE_MISMATCH",
                                severity="critical",
                                message=f"Gate 3 Failure: [{ev_id}] '{source.act_name} §{source.section_number}'. {rule['error_message']}",
                            )
                        )

    return errors


def validate_case_trust_tiers(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> list[ValidationError]:
    """Gate 6: Validate that case citations in draft match verified case models."""
    errors = []
    sources = evidence_map(pack)

    # Detect known contaminated citations
    CONTAMINATED_CITATIONS = {
        "68 DLR (AD) 298": "Mohammad Eusof Babu vs State (NI Act matter) — cannot be cited as Dr. Kamal Hossain or arrest guidelines.",
    }

    all_text = " ".join(
        p.text for p in (
            draft.rules + draft.doctrine + draft.application + draft.key_points + ([draft.conclusion] if draft.conclusion else [])
        )
    )

    for cit, reason in CONTAMINATED_CITATIONS.items():
        if cit.lower() in all_text.lower():
            if "kamal hossain" in all_text.lower() or "arrest" in all_text.lower() or "remand" in all_text.lower():
                errors.append(
                    ValidationError(
                        code="CONTAMINATED_CASE_CITATION",
                        severity="critical",
                        message=f"Gate 6 Failure: {reason}",
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
    errors += validate_heading_entailment(draft, pack)
    errors += validate_case_trust_tiers(draft, pack)
    critical = any(error.severity == "critical" for error in errors)
    return ValidationResult(passed=not critical, errors=errors)
