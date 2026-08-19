"""
Justor AI — Sprint 4 Deterministic Procedure Engine Tests
"""

import pytest
from datetime import date
from backend.legal_procedure_engine import (
    evaluate_procedural_intent,
    determine_civil_court_jurisdiction,
    calculate_limitation_period,
    calculate_registration_deadline,
    calculate_police_custody_limits,
    calculate_ni_act_138_timeline,
)


def test_evaluate_procedural_intent_baina():
    """Verify procedural intent detection for Baina contract registration."""
    res = evaluate_procedural_intent("baina registration er deadline koto?")
    assert res is not None
    assert res["calculator_type"] == "REGISTRATION_DEADLINE"
    assert res["calculation"]["days_allowed"] == 60
    assert res["calculation"]["section"] == "Section 17A"


def test_evaluate_procedural_intent_ni_act():
    """Verify procedural intent detection for Section 138 cheque dishonour."""
    res = evaluate_procedural_intent("138 ধারা অনুযায়ী চেক ডিজঅনার নোটিশ দেওয়ার সময়সীমা কত?")
    assert res is not None
    assert res["calculator_type"] == "NI_ACT_138_TIMELINE"
    assert "step_1_legal_notice" in res["calculation"]
    assert "step_2_payment_window" in res["calculation"]
    assert "step_3_court_filing" in res["calculation"]


def test_evaluate_procedural_intent_remand():
    """Verify procedural intent detection for police remand limits."""
    res = evaluate_procedural_intent("পুলিশ কত ঘণ্টা পর্যন্ত রিমান্ড বা হেফাজতে রাখতে পারে?")
    assert res is not None
    assert res["calculator_type"] == "POLICE_CUSTODY_LIMITS"
    assert res["calculation"]["section_61_custody_limit_hours"] == 24
    assert res["calculation"]["remand_max_days_allowed"] == 15


def test_pecuniary_civil_court_jurisdiction():
    """Verify civil court hierarchy under Civil Courts (Amendment) Act 2021."""
    # Under 15 Lakh -> Assistant Judge
    tier_1 = determine_civil_court_jurisdiction(1200000)
    assert tier_1["trial_court"] == "Court of Assistant Judge"
    assert tier_1["appellate_forum"] == "Court of District Judge"

    # 15 to 25 Lakh -> Senior Assistant Judge
    tier_2 = determine_civil_court_jurisdiction(2000000)
    assert tier_2["trial_court"] == "Court of Senior Assistant Judge"
    assert tier_2["appellate_forum"] == "Court of District Judge"

    # Over 25 Lakh -> Joint District Judge
    tier_3 = determine_civil_court_jurisdiction(3500000)
    assert tier_3["trial_court"] == "Court of Joint District Judge"
    assert tier_3["appellate_forum"] == "Court of District Judge"

    # Over 5 Crore appeal -> High Court Division
    tier_4 = determine_civil_court_jurisdiction(60000000)
    assert tier_4["trial_court"] == "Court of Joint District Judge"
    assert tier_4["appellate_forum"] == "High Court Division of the Supreme Court"
    assert tier_4["appeal_limitation_days"] == 90


def test_limitation_calculation_with_exclusion():
    """Verify limitation calculation under Limitation Act 1908 including Section 12 exclusions."""
    start = date(2026, 1, 1)
    # Suit under Section 9 Specific Relief Act has 6 months limitation
    res = calculate_limitation_period("summary_possession_sr_sec9", start, excluded_days=10)
    assert res is not None
    assert res["statutory_deadline"] == "2026-07-01"
    assert res["final_deadline_with_exclusions"] == "2026-07-11"
    assert res["excluded_days"] == 10
