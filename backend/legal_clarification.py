"""
Justor AI — Legal Fact Sufficiency & Clarification Engine
Identifies missing material variables in high-stakes legal inquiries (Appeals, Limitations,
Registration periods, Bail, Succession) and generates structured clarification requests.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple


class FactSufficiencyGate:
    """
    Evaluates whether an inquiry contains sufficient material facts to give a sound legal answer,
    or if it requires an interactive clarification to prevent premature assumptions.
    """

    @classmethod
    def evaluate_fact_sufficiency(cls, query: str, persona: str) -> Optional[dict]:
        """
        Returns None if facts are sufficient to proceed with retrieval & answer.
        Returns a dict with clarifying question if critical variables are missing.
        """
        q_lower = query.lower()

        # ── 1. Appeal Inquiries: Require originating court level & decree/order type ──
        if re.search(r'\b(?:can i appeal|how to appeal|right of appeal|আপিল করার নিয়ম|আপিল করা যাবে কি)\b', q_lower):
            has_court = any(w in q_lower for w in [
                "assistant judge", "senior assistant judge", "joint district", "district judge",
                "high court", "magistrate", "sessions", "সহকারী জজ", "যুগ্ম জেলা জজ", "জেলা জজ", "হাইকোর্ট"
            ])
            has_order_type = any(w in q_lower for w in ["decree", "order", "judgment", "sentence", "ডিক্রি", "আদেশ", "রায়"])
            
            if not has_court or not has_order_type:
                return {
                    "status": "needs_clarification",
                    "intent": "Appeal Route Determination",
                    "missing_facts": [
                        "Originating Court level (e.g. Assistant Judge, District Judge, Magistrate)",
                        "Nature of the decision (Decree, Interlocutory Order, or Final Judgment)"
                    ],
                    "clarification_prompt": (
                        "To determine the exact appeal forum and limitation deadline under the Code of Civil Procedure or CrPC, please clarify:\n\n"
                        "1. **Which court passed the decision?** (e.g., Assistant Judge, Joint District Judge, or Magistrate Court)\n"
                        "2. **Is the decision a final Decree, Judgment, or an interim Order?**"
                    )
                }

        # ── 2. Limitation Inquiries: Require triggering event or date ──
        if re.search(r'\b(?:is my case time-barred|is it time barred|তামাদি হয়ে গেছে কি|মামলার সময় শেষ)\b', q_lower):
            has_date_or_event = any(w in q_lower for w in [
                "years", "months", "days", "date", "since", "from", "বছর", "মাস", "দিন", "তারিখ", "আগে"
            ])
            if not has_date_or_event:
                return {
                    "status": "needs_clarification",
                    "intent": "Limitation Calculation",
                    "missing_facts": ["Date when the cause of action or dispute arose"],
                    "clarification_prompt": (
                        "To calculate the statutory limitation period under the Limitation Act, 1908, please specify:\n\n"
                        "1. **What is the nature of the suit or relief sought?** (e.g., recovery of money, recovery of land possession, specific performance)\n"
                        "2. **When did the cause of action arise or when was the agreement/event breached?**"
                    )
                }

        return None
