"""
Unit tests verifying Justor V3 x MINA enhancements:
1. Bilingual legal dictionary & Bengali numeral normalizer
2. Pre-generation relevance gate (domain filtering & cross-contamination blocking)
3. Fact sufficiency & interactive clarification gate
"""

import unittest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.legal_dictionary import (
    normalize_bengali_text,
    extract_legal_dictionary_matches,
    expand_query_with_dictionary,
)
from backend.legal_relevance import PreGenerationRelevanceGate
from backend.legal_clarification import FactSufficiencyGate
from backend.legal_models import EvidenceItem


class TestMinaEnhancements(unittest.TestCase):

    def test_bengali_numeral_and_prefix_normalization(self):
        # Bengali digit + prefix conversion
        raw = "ধারা ১৭ক অনুযায়ী বায়না দলিলের তামাদি কত?"
        norm = normalize_bengali_text(raw)
        self.assertIn("Section 17A", norm)
        self.assertNotIn("১৭ক", norm)

        raw_cpc = "আদেশ ৩৯ নিয়ম ১ অনুযায়ী নিষেধাজ্ঞা"
        norm_cpc = normalize_bengali_text(raw_cpc)
        self.assertIn("Order 39 Rule 1", norm_cpc)

        raw_art = "অনুচ্ছেদ ১১১ সুপ্রিম কোর্ট"
        norm_art = normalize_bengali_text(raw_art)
        self.assertIn("Article 111", norm_art)

    def test_legal_dictionary_expansion(self):
        # Query with local / colonial / Farsi terminology
        res = expand_query_with_dictionary("নারাজি পিটিশন দাখিল করার নিয়ম কি?")
        self.assertIn("The Code of Criminal Procedure, 1898", res["candidate_acts"])
        self.assertIn("173", res["candidate_sections"])
        self.assertIn("Criminal", res["domains"])

        res_baina = expand_query_with_dictionary("বায়নাপত্র রেজিস্ট্রি করার সময়সীমা")
        self.assertIn("The Registration Act, 1908", res_baina["candidate_acts"])
        self.assertIn("17A", res_baina["candidate_sections"])

        res_denmohor = expand_query_with_dictionary("তলবি মোহরানা বা দেনমোহর পরিশোধের বিধান")
        self.assertIn("The Muslim Family Laws Ordinance, 1961", res_denmohor["candidate_acts"])
        self.assertIn("10", res_denmohor["candidate_sections"])

    def test_pre_generation_relevance_gate_domain_filtering(self):
        # Civil injunction context: should REJECT unrelated criminal CrPC provisions
        civil_item = EvidenceItem(
            evidence_id="ACT-1",
            act_name="The Code of Civil Procedure, 1908",
            section_number="Order 39 Rule 1",
            legal_text="Where in any suit it is proved by affidavit or otherwise that any property in dispute is in danger of being wasted...",
            role="CONTROLLING"
        )
        criminal_item = EvidenceItem(
            evidence_id="ACT-2",
            act_name="The Code of Criminal Procedure, 1898",
            section_number="498",
            legal_text="The High Court Division or Court of Session may in any case direct that any person be admitted to bail...",
            role="SUPPORTING"
        )

        filtered = PreGenerationRelevanceGate.filter_evidence_items(
            items=[civil_item, criminal_item],
            query="How to obtain a temporary injunction?",
            detected_domain="Civil"
        )

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].act_name, "The Code of Civil Procedure, 1908")

    def test_fact_sufficiency_clarification_gate(self):
        # Ambiguous appeal question missing court level
        ambiguous = "Can I appeal this judgment?"
        clarification = FactSufficiencyGate.evaluate_fact_sufficiency(ambiguous, "Law Student")
        self.assertIsNotNone(clarification)
        self.assertEqual(clarification["status"], "needs_clarification")
        self.assertIn("Which court passed the decision?", clarification["clarification_prompt"])

        # Sufficient appeal question
        specific = "Appeal from an original decree passed by Joint District Judge to High Court Division under Section 96 CPC"
        self.assertIsNone(FactSufficiencyGate.evaluate_fact_sufficiency(specific, "Law Student"))


if __name__ == "__main__":
    unittest.main()
