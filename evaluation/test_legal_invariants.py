from backend.legal_validation import validate_quote, extract_numeric_tokens
from backend.legal_normalize import normalize_section, split_section_reference, normalize_act_alias
from backend.legal_deadlines import calculate_deadline, evaluate_deadline
from datetime import date

def test_fake_quote_rejected():
    source = "The application shall be made within thirty days."
    fake = "The application may be made within sixty days."
    assert not validate_quote(fake, source)


def test_exact_quote_passes():
    source = "The application shall be made within thirty days."
    quote = "within thirty days"
    assert validate_quote(quote, source)


def test_section_normalization():
    assert normalize_section("Section 17A") == "17A"
    assert normalize_section("sec. 54A") == "54A"
    assert normalize_section("s. 115") == "115"
    assert normalize_section("  Order 39  ") == "ORDER39"


def test_section_splitting():
    root, parts = split_section_reference("17A(2)")
    assert root == "17A"
    assert parts == ["2"]

    root, parts = split_section_reference("55(4)(b)")
    assert root == "55"
    assert parts == ["4", "B"]


def test_act_alias_normalization():
    assert normalize_act_alias("The Registration Act, 1908") == "registrationact1908"
    assert normalize_act_alias("Transfer of Property Act, 1882") == "transferofpropertyact1882"


def test_numeric_token_extraction():
    tokens = extract_numeric_tokens("The application must be filed within thirty days.")
    assert "30" in tokens

    tokens_num = extract_numeric_tokens("Penalty of 500 taka within 60 days.")
    assert "500" in tokens_num
    assert "60" in tokens_num


def test_deadlines():
    start = date(2026, 1, 1)
    target = calculate_deadline(start, 30, "days")
    assert target == date(2026, 1, 31)

    eval_res = evaluate_deadline(start, date(2026, 1, 15), 30, "days")
    assert eval_res["within_period"] is True

    eval_late = evaluate_deadline(start, date(2026, 2, 10), 30, "days")
    assert eval_late["within_period"] is False
    assert eval_late["days_after_deadline"] == 10


def test_registration_act_2026_amendment_60_days():
    # Test L1 scenario: Executed 1 June 2026, Presented 25 July 2026 (54 days)
    execution_date = date(2026, 6, 1)
    presentation_date = date(2026, 7, 25)
    # Registration Act Section 17A(2) after 2026 amendment is 60 days
    eval_res = evaluate_deadline(execution_date, presentation_date, 60, "days")
    assert eval_res["within_period"] is True
    assert eval_res["days_remaining"] == 6


def test_section_heading_mismatch_rejected():
    from backend.legal_models import EvidencePack, EvidenceItem, LegalAnswerDraft, DraftParagraph, DraftClaim
    from backend.legal_validation import validate_heading_entailment

    item_mortgage = EvidenceItem(
        evidence_id="ACT-1",
        act_name="The Transfer of Property Act, 1882",
        section_number="64",
        heading="Renewal of mortgaged lease",
        legal_text="Where the mortgaged property is a lease, and the mortgagee obtains a renewal...",
        exact_section_verified=True,
        version_verified=True,
    )
    pack = EvidencePack(
        query="Explain contract for sale under TPA",
        persona="Lawyer",
        as_of_date=date(2026, 8, 17),
        temporal_mode="CURRENT",
        issues=[],
        authorities=[item_mortgage],
    )
    draft = LegalAnswerDraft(
        issue="Contract for sale",
        rules=[DraftParagraph(text="Under Section 64, a contract for sale of immovable property must be registered.", evidence_ids=["ACT-1"])],
        conclusion=DraftParagraph(text="Contract for sale is governed by Section 64.", evidence_ids=["ACT-1"]),
        claims=[DraftClaim(claim_id="C1", text="Section 64 provides for contract for sale registration.", claim_type="legal_rule", evidence_ids=["ACT-1"])],
    )
    errors = validate_heading_entailment(draft, pack)
    assert len(errors) > 0
    assert any(e.code == "SECTION_HEADING_MISMATCH" for e in errors)


def test_constitutional_articles_distinction():
    from backend.legal_models import EvidencePack, EvidenceItem, LegalAnswerDraft, DraftParagraph, DraftClaim
    from backend.legal_validation import validate_heading_entailment

    item_art111 = EvidenceItem(
        evidence_id="ACT-1",
        act_name="The Constitution of the People's Republic of Bangladesh",
        section_number="111",
        heading="Binding effect of Supreme Court judgments",
        legal_text="The law declared by the Appellate Division shall be binding on the High Court Division...",
        exact_section_verified=True,
        version_verified=True,
    )
    pack = EvidencePack(
        query="Superintendence over subordinate courts",
        persona="Law Student",
        as_of_date=date(2026, 8, 17),
        temporal_mode="CURRENT",
        issues=[],
        authorities=[item_art111],
    )
    draft = LegalAnswerDraft(
        issue="Superintendence of courts",
        rules=[DraftParagraph(text="Article 111 gives the High Court superintendence and control over subordinate courts.", evidence_ids=["ACT-1"])],
        conclusion=DraftParagraph(text="Superintendence is under Article 111.", evidence_ids=["ACT-1"]),
        claims=[DraftClaim(claim_id="C1", text="Article 111 governs superintendence over subordinate courts.", claim_type="legal_rule", evidence_ids=["ACT-1"])],
    )
    errors = validate_heading_entailment(draft, pack)
    assert len(errors) > 0
    assert any(e.code == "CONSTITUTIONAL_ARTICLE_MISMATCH" for e in errors)


def test_contaminated_case_citation_rejected():
    from backend.legal_models import EvidencePack, LegalAnswerDraft, DraftParagraph
    from backend.legal_validation import validate_case_trust_tiers

    pack = EvidencePack(
        query="Arrest without warrant guidelines",
        persona="Lawyer",
        as_of_date=date(2026, 8, 17),
        temporal_mode="CURRENT",
        issues=[],
        authorities=[],
    )
    draft = LegalAnswerDraft(
        issue="Arrest guidelines",
        rules=[DraftParagraph(text="In Dr. Kamal Hossain v Bangladesh, 68 DLR (AD) 298, the court gave arrest guidelines.", evidence_ids=[])],
        conclusion=DraftParagraph(text="Guidelines were settled in 68 DLR (AD) 298.", evidence_ids=[]),
    )
    errors = validate_case_trust_tiers(draft, pack)
    assert len(errors) > 0
    assert any(e.code == "CONTAMINATED_CASE_CITATION" for e in errors)


def test_trust_badge_resolution():
    from backend.legal_models import EvidenceItem

    statute_item = EvidenceItem(
        evidence_id="ACT-1",
        act_name="The Registration Act, 1908",
        section_number="17A",
        item_type="statute",
    )
    assert "PRIMARY SOURCE ✓" in statute_item.get_badge()

    verified_case = EvidenceItem(
        evidence_id="DLR-1",
        act_name="BLAST v Bangladesh",
        item_type="case",
        trust_tier="VERIFIED_JUDGMENT",
    )
    assert "PRIMARY JUDGMENT ✓" in verified_case.get_badge()

    unverified_case = EvidenceItem(
        evidence_id="DLR-2",
        act_name="Md. Nurul Islam v S.M. Shahjahan",
        item_type="case",
        trust_tier="UNVERIFIED_REPORTER_CITATION",
    )
    assert "REPORTER CITATION AVAILABLE ⚠️" in unverified_case.get_badge()

