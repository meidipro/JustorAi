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


# ==============================================================================
# 7-GATE DETERMINISTIC LEGAL VERIFICATION ENGINE (G1 - G7)
# ==============================================================================

def validate_authority_identity(pack: EvidencePack) -> list[ValidationError]:
    """Gate 1 (G1): Authority Identity.
    Verifies that every authority has an identified canonical Bangladesh instrument and title.
    """
    errors = []
    for source in pack.authorities:
        if not source.act_name or source.act_name.strip() == "":
            errors.append(
                ValidationError(
                    code="G1_INVALID_AUTHORITY_IDENTITY",
                    severity="critical",
                    message=f"Gate 1 Failure: Authority [{source.evidence_id}] has no valid canonical Act title.",
                )
            )
    return errors


def validate_provision_identity(pack: EvidencePack) -> list[ValidationError]:
    """Gate 2 (G2): Exact Provision Identity.
    Verifies that exact section/article/order numbers are well-formed and resolved.
    """
    errors = []
    for source in pack.authorities:
        if source.item_type == "statute":
            sec = str(source.section_number).strip()
            clean_sec = re.sub(r'^(?:Section|Sec\.?|Article|Art\.?)\s*', '', sec, flags=re.IGNORECASE).strip()
            is_order_rule = bool(re.match(r'^Order\s+[0-9IVXLCDM]+(?:\s*,?\s*Rule\s+[0-9]+)?$', sec, re.IGNORECASE))
            is_valid_sec = bool(re.match(r'^[0-9IVXLCDM]+[A-Za-z]?(?:\([0-9A-Za-z]+\))*$', clean_sec))
            if not (is_order_rule or is_valid_sec or sec.lower().startswith("order") or sec.lower().startswith("article")):
                errors.append(
                    ValidationError(
                        code="G2_INVALID_PROVISION_IDENTITY",
                        severity="critical",
                        message=f"Gate 2 Failure: [{source.evidence_id}] '{source.act_name}' has invalid or missing section number '{sec}'.",
                    )
                )
    return errors


def validate_version_validity(pack: EvidencePack) -> list[ValidationError]:
    """Gate 3 (G3): Current / Version Validity.
    Verifies version validity, temporal query date ranges, and requires official_source_verified
    for controlling authorities in Lawyer Mode.
    """
    errors = []
    is_lawyer = pack.persona in ["Legal Professional", "Lawyer"]

    for source in pack.authorities:
        if source.item_type == "statute":
            if not source.version_verified and source.trust_tier != "LEGACY_CORPUS":
                errors.append(
                    ValidationError(
                        code="G3_VERSION_NOT_VERIFIED",
                        severity="critical",
                        message=f"Gate 3 Failure: [{source.evidence_id}] version validity not verified for date {pack.as_of_date}.",
                    )
                )
            
            # Enforce temporal validity bounds if present
            if source.valid_from and pack.as_of_date < source.valid_from:
                errors.append(
                    ValidationError(
                        code="G3_TEMPORAL_PRE_ENACTMENT",
                        severity="critical",
                        message=f"Gate 3 Failure: [{source.evidence_id}] not valid on {pack.as_of_date} (valid from {source.valid_from}).",
                    )
                )
            if source.valid_to and pack.as_of_date > source.valid_to:
                errors.append(
                    ValidationError(
                        code="G3_TEMPORAL_POST_EXPIRY",
                        severity="critical",
                        message=f"Gate 3 Failure: [{source.evidence_id}] expired before {pack.as_of_date} (valid to {source.valid_to}).",
                    )
                )

            # Strict provenance for controlling authorities in Lawyer mode
            if is_lawyer and source.role == "CONTROLLING":
                if source.trust_tier == "LEGACY_CORPUS":
                    errors.append(
                        ValidationError(
                            code="G3_UNVERIFIED_LEGACY_CONTROLLING",
                            severity="critical",
                            message=f"Gate 3 Failure: [{source.evidence_id}] '{source.act_name}' is unreviewed legacy corpus and cannot serve as controlling law for Legal Professional mode.",
                        )
                    )
                elif not source.official_source_verified:
                    errors.append(
                        ValidationError(
                            code="G3_OFFICIAL_SOURCE_NOT_VERIFIED",
                            severity="critical",
                            message=f"Gate 3 Failure: [{source.evidence_id}] '{source.act_name}' official source not verified.",
                        )
                    )
    return errors


def validate_claim_entailment(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> list[ValidationError]:
    """Gate 4 (G4): Claim -> Authority Entailment.
    Verifies that section headings and topics entail the claims asserted, preventing corrupt mappings.
    """
    errors = []
    sources = evidence_map(pack)

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
                                code="G4_SECTION_HEADING_MISMATCH",
                                severity="critical",
                                message=f"Gate 4 Failure: [{ev_id}] '{source.act_name} §{source.section_number}' ({source.heading}) does not entail topic. {rule['error_message']}",
                            )
                        )

                if "forbidden_articles" in rule:
                    if any(fa in source_sec for fa in rule["forbidden_articles"]) or any(fa in block_text for fa in rule["forbidden_articles"]):
                        errors.append(
                            ValidationError(
                                code="G4_CONSTITUTIONAL_ARTICLE_MISMATCH",
                                severity="critical",
                                message=f"Gate 4 Failure: [{ev_id}] '{source.act_name} §{source.section_number}'. {rule['error_message']}",
                            )
                        )

    return errors


def validate_numbers_and_deadlines(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> list[ValidationError]:
    """Gate 5 (G5): Numbers, Dates & Deadlines.
    Verifies that statutory numbers, percentages, and deadlines asserted in claims match authority text.
    """
    errors = []
    sources = evidence_map(pack)

    for claim in draft.claims:
        if claim.claim_type not in MATERIAL_TYPES:
            continue

        source_texts = []
        for evidence_id in claim.evidence_ids:
            source = sources.get(evidence_id)
            if source:
                source_texts.append(source.legal_text)

        claim_numbers = extract_numeric_tokens(claim.text)
        evidence_numbers = set()
        for source_text in source_texts:
            evidence_numbers |= extract_numeric_tokens(source_text)

        missing_numbers = claim_numbers - evidence_numbers
        if missing_numbers:
            errors.append(
                ValidationError(
                    code="G5_UNSUPPORTED_NUMBER_OR_DEADLINE",
                    severity="critical",
                    claim_id=claim.claim_id,
                    message=(
                        f"Gate 5 Failure: Legal numeric/deadline claim {sorted(missing_numbers)} "
                        "is not present in cited authority."
                    ),
                )
            )

    return errors


def validate_case_provenance(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> list[ValidationError]:
    """Gate 6 (G6): Judgment & Case Provenance.
    Enforces that case law citations meet verified judgment tiers and blocks contaminated citations.
    """
    errors = []
    sources = evidence_map(pack)

    CONTAMINATED_CITATIONS = {
        "68 DLR (AD) 298": "Mohammad Eusof Babu vs State (NI Act matter) — cannot be cited as Dr. Kamal Hossain or arrest guidelines.",
    }

    all_text = " ".join(
        p.text for p in (
            draft.rules + draft.doctrine + draft.application + draft.key_points + ([draft.conclusion] if draft.conclusion else [])
        )
    )

    # 1. Contaminated citation checks
    for cit, reason in CONTAMINATED_CITATIONS.items():
        if cit.lower() in all_text.lower():
            if "kamal hossain" in all_text.lower() or "arrest" in all_text.lower() or "remand" in all_text.lower():
                errors.append(
                    ValidationError(
                        code="G6_CONTAMINATED_CASE_CITATION",
                        severity="critical",
                        message=f"Gate 6 Failure: {reason}",
                    )
                )

    # 2. General case law trust tier enforcement
    for source in pack.authorities:
        if source.item_type == "case":
            if source.trust_tier == "UNVERIFIED_REPORTER_CITATION" and source.role == "CONTROLLING":
                errors.append(
                    ValidationError(
                        code="G6_UNVERIFIED_REPORTER_CITATION_CONTROLLING",
                        severity="critical",
                        message=f"Gate 6 Failure: Case [{source.citation}] is an unverified reporter citation and cannot serve as controlling precedent.",
                    )
                )

    return errors


def validate_material_claim_coverage(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> list[ValidationError]:
    """Gate 7 (G7): Complete Material Claim Coverage & Evidence ID Integrity.
    Verifies that every material claim has at least one valid supporting evidence ID.
    """
    errors = []
    sources = evidence_map(pack)
    allowed = set(sources)

    blocks = (
        draft.rules
        + draft.doctrine
        + draft.application
        + draft.key_points
        + ([draft.conclusion] if draft.conclusion else [])
    )

    # Verify all evidence IDs in text exist in pack
    for paragraph in blocks:
        for evidence_id in paragraph.evidence_ids:
            if evidence_id not in allowed:
                errors.append(
                    ValidationError(
                        code="G7_INVALID_EVIDENCE_ID",
                        severity="critical",
                        message=f"Gate 7 Failure: Unknown evidence ID {evidence_id}",
                    )
                )

    # Verify every material claim has evidence
    for claim in draft.claims:
        if claim.claim_type in MATERIAL_TYPES and not claim.evidence_ids:
            errors.append(
                ValidationError(
                    code="G7_UNSUPPORTED_MATERIAL_CLAIM",
                    severity="critical",
                    claim_id=claim.claim_id,
                    message=f"Gate 7 Failure: Material legal claim '{claim.claim_id}' has no supporting evidence tag.",
                )
            )

    return errors


def validate_quote(quote: str, source_text: str) -> bool:
    return normalize_quote(quote) in normalize_quote(source_text)


def validate_draft(
    draft: LegalAnswerDraft,
    pack: EvidencePack,
) -> ValidationResult:
    """Executes the 7 Independent Deterministic Legal Verification Gates."""
    errors: list[ValidationError] = []
    
    # Gate 1: Authority Identity
    errors += validate_authority_identity(pack)
    # Gate 2: Exact Provision Identity
    errors += validate_provision_identity(pack)
    # Gate 3: Current / Version Validity
    errors += validate_version_validity(pack)
    # Gate 4: Claim -> Authority Entailment
    errors += validate_claim_entailment(draft, pack)
    # Gate 5: Numbers, Dates & Deadlines
    errors += validate_numbers_and_deadlines(draft, pack)
    # Gate 6: Judgment & Case Provenance
    errors += validate_case_provenance(draft, pack)
    # Gate 7: Complete Material Claim Coverage
    errors += validate_material_claim_coverage(draft, pack)

    critical = any(error.severity == "critical" for error in errors)
    return ValidationResult(passed=not critical, errors=errors)
