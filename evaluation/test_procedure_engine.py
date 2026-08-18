"""
Unit tests verifying the Deterministic Legal Procedure & Statutory Deadline Engine
"""

import unittest
from datetime import date
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.legal_procedure_engine import (
    determine_civil_court_jurisdiction,
    calculate_registration_deadline,
    calculate_ni_act_138_timeline,
    calculate_limitation_period,
    LIMITATION_SCHEDULE,
)


class TestProcedureEngine(unittest.TestCase):

    def test_pecuniary_jurisdiction_2021_amendment(self):
        # 10 Lakh BDT -> Assistant Judge, Appeal to District Judge
        res_10l = determine_civil_court_jurisdiction(1000000)
        self.assertEqual(res_10l["trial_court"], "Court of Assistant Judge")
        self.assertEqual(res_10l["appellate_forum"], "Court of District Judge")
        self.assertEqual(res_10l["appeal_limitation_days"], 30)

        # 20 Lakh BDT -> Senior Assistant Judge
        res_20l = determine_civil_court_jurisdiction(2000000)
        self.assertEqual(res_20l["trial_court"], "Court of Senior Assistant Judge")
        self.assertEqual(res_20l["appellate_forum"], "Court of District Judge")

        # 3 Crore BDT -> Joint District Judge, Appeal to District Judge (under 5 Crore)
        res_3cr = determine_civil_court_jurisdiction(30000000)
        self.assertEqual(res_3cr["trial_court"], "Court of Joint District Judge")
        self.assertEqual(res_3cr["appellate_forum"], "Court of District Judge")

        # 6 Crore BDT -> Joint District Judge, Appeal directly to High Court Division
        res_6cr = determine_civil_court_jurisdiction(60000000)
        self.assertEqual(res_6cr["trial_court"], "Court of Joint District Judge")
        self.assertEqual(res_6cr["appellate_forum"], "High Court Division of the Supreme Court")
        self.assertEqual(res_6cr["appeal_limitation_days"], 90)

    def test_registration_act_timelines(self):
        # Section 17A Baina Patra (60 days)
        exec_date = date(2026, 1, 1)
        res_baina = calculate_registration_deadline(exec_date, "baina contract for sale")
        self.assertEqual(res_baina["section"], "Section 17A")
        self.assertEqual(res_baina["deadline"], "2026-03-02")
        self.assertTrue(res_baina["is_mandatory_unregistered_void"])

        # Section 23 General Document (4 months)
        res_gen = calculate_registration_deadline(exec_date, "general deed of partition")
        self.assertEqual(res_gen["section"], "Section 23")
        self.assertEqual(res_gen["deadline"], "2026-05-01")

    def test_ni_act_138_timeline(self):
        # Cheque dishonoured 2026-02-01
        dishonour = date(2026, 2, 1)
        res_ni = calculate_ni_act_138_timeline(dishonour)
        self.assertEqual(res_ni["step_1_legal_notice"]["deadline"], "2026-03-03")
        self.assertEqual(res_ni["step_2_payment_window"]["payment_expires"], "2026-04-02")
        self.assertEqual(res_ni["step_3_court_filing"]["complaint_deadline"], "2026-05-02")

    def test_limitation_act_calculations(self):
        start = date(2026, 1, 15)

        # Article 113 Specific Performance (1 year)
        res_sp = calculate_limitation_period("specific_performance", start)
        self.assertEqual(res_sp["article"], "113")
        self.assertEqual(res_sp["statutory_deadline"], "2027-01-15")

        # Article 152 CPC Appeal to District Judge (30 days)
        res_app = calculate_limitation_period("civil_appeal_district_judge", start, excluded_days=5)
        self.assertEqual(res_app["statutory_deadline"], "2026-02-14")
        self.assertEqual(res_app["final_deadline_with_exclusions"], "2026-02-19")

        # Article 142 Immovable Property (12 years)
        res_prop = calculate_limitation_period("recovery_immovable_property_title", start)
        self.assertEqual(res_prop["statutory_deadline"], "2038-01-15")


if __name__ == "__main__":
    unittest.main()
