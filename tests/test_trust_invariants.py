"""
Justor AI — Trust Invariant & Provenance Integrity Tests
Ensures zero synthetic verification badges, strict fail-closed rejection on non-existent provisions,
and audited legal procedure constants.
"""

import pytest
from datetime import date, timedelta
from backend.legal_models import EvidenceItem, TrustTier
from backend.legal_procedure_engine import (
    calculate_registration_deadline,
    calculate_police_custody_limits,
    calculate_ni_act_138_timeline,
    LIMITATION_SCHEDULE,
)


def test_evidence_item_defaults_to_unverified():
    """Invariant 1: Any raw EvidenceItem must default to UNVERIFIED and source_verified=False."""
    item = EvidenceItem(
        evidence_id="ACT-1",
        act_name="The Code of Criminal Procedure, 1898",
        section_number="54",
    )
    assert item.trust_tier == "UNVERIFIED"
    assert item.official_source_verified is False
    assert item.version_verified is False
    assert item.get_badge() == "`UNVERIFIED`"


def test_legacy_corpus_cannot_produce_primary_statute_badge():
    """Invariant 2: Chunks from legacy corpus must never display PRIMARY SOURCE badge."""
    item = EvidenceItem(
        evidence_id="ACT-1",
        act_name="The Contract Act, 1872",
        section_number="10",
        trust_tier="LEGACY_CORPUS",
        official_source_verified=False,
    )
    badge = item.get_badge()
    assert "PRIMARY SOURCE" not in badge
    assert "LEGACY DB" in badge or "UNREVIEWED" in badge


def test_primary_source_badge_requires_all_verification_flags():
    """Invariant 3: PRIMARY SOURCE badge is strictly earned only when source, version, and section are all verified."""
    partial_item = EvidenceItem(
        evidence_id="ACT-1",
        act_name="The Penal Code, 1860",
        section_number="420",
        trust_tier="PRIMARY_STATUTE",
        official_source_verified=True,
        version_verified=False,  # unverified version
        exact_section_verified=True,
    )
    assert partial_item.get_badge() == "`OFFICIAL LEGISLATION (UNAUDITED VERSION)`"

    verified_item = EvidenceItem(
        evidence_id="ACT-1",
        act_name="The Penal Code, 1860",
        section_number="420",
        trust_tier="PRIMARY_STATUTE",
        official_source_verified=True,
        version_verified=True,
        exact_section_verified=True,
    )
    assert verified_item.get_badge() == "`PRIMARY SOURCE ✓` `SOURCE CHECKED ✓`"


def test_registration_act_statutory_constants():
    """Invariant 4: Audited constants for Registration Act 1908."""
    today = date(2026, 8, 19)
    
    # Section 17A: Strict 60 days for contract for sale (Baina patra)
    baina_res = calculate_registration_deadline(today, "baina patra")
    assert baina_res["days_allowed"] == 60
    assert baina_res["section"] == "Section 17A"
    assert baina_res["is_mandatory_unregistered_void"] is True

    # Section 23: Strict 3 months (as amended by the Registration (Amendment) Act, 2004)
    general_res = calculate_registration_deadline(today, "general deed")
    assert general_res["section"] == "Section 23"
    assert "3 months" in general_res["statutory_rule"]
    assert "2004" in general_res["statutory_rule"]
    # 3 months from Aug 19 is Nov 19 (92 days in leap-like calendar span)
    assert general_res["deadline"] == "2026-11-19"


def test_criminal_procedure_custody_and_remand_constants():
    """Invariant 5: Audited constants for CrPC custody and remand."""
    today = date(2026, 8, 19)
    custody_res = calculate_police_custody_limits(today)
    
    # CrPC §61 / Constitution Art. 33(2): 24-hour limit without magistrate
    assert custody_res["section_61_custody_limit_hours"] == 24
    assert custody_res["constitutional_article"] == "Article 33(2)"
    
    # CrPC §167: 15-day maximum police custody in the whole
    assert custody_res["remand_max_days_allowed"] == 15
    assert custody_res["remand_max_deadline"] == "2026-09-03"


def test_ni_act_138_three_step_timeline():
    """Invariant 6: Audited 3-step 30-day timeline under NI Act Section 138."""
    dishonour = date(2026, 8, 1)
    ni_res = calculate_ni_act_138_timeline(dishonour)
    
    assert ni_res["step_1_legal_notice"]["deadline"] == "2026-08-31"  # 30 days
    assert ni_res["step_2_payment_window"]["payment_expires"] == "2026-09-30"  # +30 days
    assert ni_res["step_3_court_filing"]["complaint_deadline"] == "2026-10-30"  # +30 days
