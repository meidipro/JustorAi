"""
Justor AI — Deterministic Legal Procedure & Statutory Deadline Engine
Provides mathematical calculations and rules for limitation periods, pecuniary jurisdictions,
appellate routes, and statutory timelines under Bangladesh legislation.
Never relies on LLM arithmetic for high-stakes legal deadlines.
"""

from __future__ import annotations
from datetime import date, timedelta
from typing import Dict, Any, Optional, List
from dateutil.relativedelta import relativedelta


# ─── Statutory Limitation Schedule (The Limitation Act, 1908) ────────────────
LIMITATION_SCHEDULE: dict[str, dict] = {
    "specific_performance": {
        "article": "113",
        "act": "The Limitation Act, 1908",
        "period_years": 1,
        "description": "Suit for specific performance of a contract",
        "starting_point": "The date fixed for performance, or, if no such date is fixed, when the plaintiff has notice that performance is refused."
    },
    "recovery_immovable_property_title": {
        "article": "142 / 144",
        "act": "The Limitation Act, 1908",
        "period_years": 12,
        "description": "Suit for possession of immovable property based on title or dispossession",
        "starting_point": "The date of dispossession or when the possession of the defendant becomes adverse to the plaintiff."
    },
    "summary_possession_sr_sec9": {
        "article": "3",
        "act": "The Limitation Act, 1908 / Specific Relief Act, 1877",
        "period_months": 6,
        "description": "Suit under Section 9 of the Specific Relief Act for possession of immovable property",
        "starting_point": "The date of the illegal dispossession without consent."
    },
    "pre_emption_sata": {
        "article": "Sec 96",
        "act": "The State Acquisition and Tenancy Act, 1950",
        "period_months": 2,
        "description": "Application for pre-emption by co-sharer tenant",
        "starting_point": "Within 2 months from the date of service of notice or 2 months from the date of knowledge of the transfer."
    },
    "civil_appeal_district_judge": {
        "article": "152",
        "act": "The Limitation Act, 1908",
        "period_days": 30,
        "description": "Appeal under the Code of Civil Procedure to the Court of a District Judge",
        "starting_point": "The date of the decree or order appealed from."
    },
    "civil_appeal_high_court": {
        "article": "156",
        "act": "The Limitation Act, 1908",
        "period_days": 90,
        "description": "Appeal under the Code of Civil Procedure to the High Court Division",
        "starting_point": "The date of the decree or order appealed from."
    },
    "criminal_appeal_sessions_judge": {
        "article": "154",
        "act": "The Limitation Act, 1908",
        "period_days": 30,
        "description": "Appeal under CrPC from an order/sentence of a Magistrate to the Court of Session",
        "starting_point": "The date of the sentence or order appealed from."
    },
    "criminal_appeal_high_court": {
        "article": "155",
        "act": "The Limitation Act, 1908",
        "period_days": 60,
        "description": "Appeal under CrPC to the High Court Division from a Court of Session",
        "starting_point": "The date of the sentence or order appealed from."
    },
    "civil_revision_high_court": {
        "article": "Sec 115",
        "act": "The Code of Civil Procedure, 1908",
        "period_days": 90,
        "description": "Application for revision under Section 115 CPC to the High Court Division",
        "starting_point": "The date of the decree or order sought to be revised."
    }
}


# ─── Pecuniary Jurisdiction & Civil Court Hierarchy (Civil Courts Act, 1887 amended 2021) ───
def determine_civil_court_jurisdiction(suit_value_bdt: float) -> dict:
    """
    Determines the appropriate trial court and appellate forum under the Civil Courts (Amendment) Act, 2021.
    """
    if suit_value_bdt <= 1500000:
        trial_court = "Court of Assistant Judge"
        jurisdiction_note = "Suits valued up to BDT 15,00,000 (15 Lakh)."
    elif suit_value_bdt <= 2500000:
        trial_court = "Court of Senior Assistant Judge"
        jurisdiction_note = "Suits valued above BDT 15,00,000 up to BDT 25,00,000 (25 Lakh)."
    else:
        trial_court = "Court of Joint District Judge"
        jurisdiction_note = "Suits valued above BDT 25,00,000 (unlimited pecuniary jurisdiction)."

    # Appellate forum rules
    if suit_value_bdt <= 50000000:
        appeal_forum = "Court of District Judge"
        appeal_note = "Appeals against decree/order valued up to BDT 5,00,00,000 (5 Crore) lie before the District Judge."
        limitation_days = 30
    else:
        appeal_forum = "High Court Division of the Supreme Court"
        appeal_note = "Appeals against decree/order valued above BDT 5,00,00,000 lie directly to the High Court Division."
        limitation_days = 90

    return {
        "suit_value_bdt": suit_value_bdt,
        "trial_court": trial_court,
        "jurisdiction_note": jurisdiction_note,
        "appellate_forum": appeal_forum,
        "appeal_limitation_days": limitation_days,
        "appellate_note": appeal_note,
        "governing_statute": "The Civil Courts (Amendment) Act, 2021 (Act No. 5 of 2021)"
    }


# ─── Statutory Registration Presentation Timelines (The Registration Act, 1908) ───
def calculate_registration_deadline(execution_date: date, instrument_type: str = "baina") -> dict:
    """
    Calculates presentation deadline for registration under Section 17A or Section 23 of Registration Act.
    """
    itype = instrument_type.lower()
    if "baina" in itype or "contract for sale" in itype or "agreement for sale" in itype:
        # Section 17A: Strict 60 days
        deadline = execution_date + timedelta(days=60)
        section = "Section 17A"
        rule = "A contract for sale of immovable property must be presented for registration within 60 days from execution."
        is_mandatory_unregistered_void = True
    else:
        # Section 23: General 3 months (amended by the Registration (Amendment) Act, 2004)
        deadline = execution_date + relativedelta(months=3)
        section = "Section 23"
        rule = "General documents must be presented for registration within 3 months from execution date (Registration Act §23 as amended in 2004)."
        is_mandatory_unregistered_void = False

    return {
        "execution_date": execution_date.isoformat(),
        "deadline": deadline.isoformat(),
        "section": section,
        "act": "The Registration Act, 1908",
        "statutory_rule": rule,
        "days_allowed": (deadline - execution_date).days,
        "is_mandatory_unregistered_void": is_mandatory_unregistered_void
    }


# ─── Criminal Procedure Detention & Remand Limits (CrPC 1898 & Constitution) ──
def calculate_police_custody_limits(arrest_date: date, journey_hours: int = 0) -> dict:
    """
    Calculates statutory limits on police detention without magistrate and maximum remand under CrPC.
    - CrPC §61 / Constitution Art. 33: 24-hour limit without magistrate order (excluding journey).
    - CrPC §167: Maximum 15 days total police custody in the whole case.
    """
    remand_max_days = 15
    remand_deadline = arrest_date + timedelta(days=remand_max_days)

    return {
        "section_61_custody_limit_hours": 24,
        "excluded_journey_hours": journey_hours,
        "constitutional_article": "Article 33(2)",
        "crpc_section": "Section 61",
        "remand_max_days_allowed": 15,
        "remand_max_deadline": remand_deadline.isoformat(),
        "statutory_rule": "No police officer shall detain in custody a person arrested without warrant for a longer period than 24 hours exclusive of the time necessary for the journey from the place of arrest to the Magistrate's Court (CrPC §61, Const. Art. 33(2)). The aggregate period of remand to police custody shall not exceed 15 days in the whole (CrPC §167)."
    }


# ─── Negotiable Instruments Act, 1881 (Section 138 Cheque Dishonour Timeline) ──
def calculate_ni_act_138_timeline(dishonour_date: date, notice_served_date: Optional[date] = None) -> dict:
    """
    Calculates the 3 mandatory statutory steps for Cheque Dishonour under Section 138 NI Act:
    1. Legal Demand Notice: within 30 days of dishonour memo.
    2. Payment Window: 30 days from receipt of notice by drawer.
    3. Court Complaint Filing: within 30 days after expiry of payment window.
    """
    notice_deadline = dishonour_date + timedelta(days=30)
    
    n_served = notice_served_date or notice_deadline
    payment_expiry = n_served + timedelta(days=30)
    complaint_deadline = payment_expiry + timedelta(days=30)

    return {
        "step_1_legal_notice": {
            "requirement": "Send legal demand notice in writing within 30 days of receiving the cheque return memo.",
            "deadline": notice_deadline.isoformat(),
            "section": "Section 138(1)(b) NI Act"
        },
        "step_2_payment_window": {
            "requirement": "Drawer is given 30 days from receipt of notice to make payment.",
            "payment_expires": payment_expiry.isoformat(),
            "section": "Section 138(1)(c) NI Act"
        },
        "step_3_court_filing": {
            "requirement": "Formal complaint must be filed before the Magistrate within 30 days after cause of action arises.",
            "complaint_deadline": complaint_deadline.isoformat(),
            "section": "Section 141 NI Act"
        },
        "governing_statute": "The Negotiable Instruments Act, 1881"
    }


# ─── General Limitation Calculator ────────────────────────────────────────────
def calculate_limitation_period(
    action_key: str,
    event_date: date,
    excluded_days: int = 0
) -> Optional[dict]:
    """
    Calculates limitation expiry date from the Limitation Act schedule with optional Section 12 excluded days.
    """
    rule = LIMITATION_SCHEDULE.get(action_key)
    if not rule:
        return None

    if "period_years" in rule:
        base_deadline = event_date + relativedelta(years=rule["period_years"])
    elif "period_months" in rule:
        base_deadline = event_date + relativedelta(months=rule["period_months"])
    elif "period_days" in rule:
        base_deadline = event_date + timedelta(days=rule["period_days"])
    else:
        return None

    final_deadline = base_deadline + timedelta(days=excluded_days)

    return {
        "action_key": action_key,
        "description": rule["description"],
        "article": rule["article"],
        "act": rule["act"],
        "event_date": event_date.isoformat(),
        "statutory_deadline": base_deadline.isoformat(),
        "final_deadline_with_exclusions": final_deadline.isoformat(),
        "excluded_days": excluded_days,
        "starting_point_rule": rule["starting_point"]
    }


def evaluate_procedural_intent(query: str, as_of_date: Optional[date] = None) -> Optional[dict]:
    """
    Evaluates whether a query requires deterministic procedural calculation
    (e.g., registration deadline, NI Act timeline, remand caps, or limitation period).
    """
    q_lower = query.lower()
    dt = as_of_date or date.today()

    # 1. Baina / Contract for Sale registration (Registration Act §17A)
    if any(k in q_lower for k in ["baina", "বায়না", "contract for sale", "agreement for sale"]) and any(k in q_lower for k in ["registration", "রেজিস্ট্রি", "deadline", "time", "period", "কত দিন", "কতদিন"]):
        return {
            "calculator_type": "REGISTRATION_DEADLINE",
            "calculation": calculate_registration_deadline(dt, "baina"),
        }

    # 2. General document registration (Registration Act §23)
    if "section 23" in q_lower or "২৩ ধারা" in q_lower or ("registration" in q_lower and "general" in q_lower):
        return {
            "calculator_type": "REGISTRATION_DEADLINE",
            "calculation": calculate_registration_deadline(dt, "general"),
        }

    # 3. Police Custody & Remand (CrPC §61, §167, Const. Art. 33)
    if any(k in q_lower for k in ["remand", "রিমান্ড", "police custody", "পুলিশ হেফাজত", "হেফাজত"]) and any(k in q_lower for k in ["limit", "period", "কত দিন", "hour", "hours", "২৪ ঘণ্টা", "24 hour", "ঘণ্টা", "ঘন্টা", "সময়", "সময়", "কত"]):
        return {
            "calculator_type": "POLICE_CUSTODY_LIMITS",
            "calculation": calculate_police_custody_limits(dt),
        }

    # 4. Cheque Dishonour (NI Act §138)
    if any(k in q_lower for k in ["138", "dishonour", "cheque", "চেক", "bounce", "ডিজঅনার"]):
        return {
            "calculator_type": "NI_ACT_138_TIMELINE",
            "calculation": calculate_ni_act_138_timeline(dt),
        }

    # 5. Recovery of Possession (SRA §9 / Limitation Act Art. 3)
    if "section 9" in q_lower and any(k in q_lower for k in ["specific relief", "dispossession", "possession", "সুনির্দিষ্ট প্রতিকার", "বেদখল"]):
        return {
            "calculator_type": "LIMITATION_PERIOD",
            "calculation": calculate_limitation_period("summary_possession_sr_sec9", dt),
        }

    return None
