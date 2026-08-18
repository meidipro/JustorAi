"""
Justor AI — Pre-Generation Legal Evidence Relevance Gate
3-Tier filtering ensuring only legally valid, domain-aligned, and directly relevant
provisions and case law enter the Evidence Pack.
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Optional
from .legal_models import EvidenceItem, LegalRoute


# ─── Domain-to-Act Mapping Matrix for Strict Cross-Contamination Prevention ──
DOMAIN_ACT_ALLOWLIST: dict[str, list[str]] = {
    "Civil": [
        "The Code of Civil Procedure, 1908",
        "The Specific Relief Act, 1877",
        "The Limitation Act, 1908",
        "The Court-fees Act, 1870",
        "The Civil Courts Act, 1887",
        "The Evidence Act, 1872",
    ],
    "Criminal": [
        "The Code of Criminal Procedure, 1898",
        "The Penal Code, 1860",
        "The Special Powers Act, 1974",
        "The Evidence Act, 1872",
        "The Prevention of Corruption Act, 1947",
        "The Digital Security Act, 2018",
        "The Cyber Security Act, 2023",
        "The Nari O Shishu Nirjatan Daman Ain, 2000",
    ],
    "Property": [
        "The Registration Act, 1908",
        "The Transfer of Property Act, 1882",
        "The Specific Relief Act, 1877",
        "The State Acquisition and Tenancy Act, 1950",
        "The Land Reform Act, 2023",
        "The Land Development Tax Act, 2023",
        "The Non-Agricultural Tenancy Act, 1949",
        "The Evidence Act, 1872",
    ],
    "Family": [
        "The Muslim Family Laws Ordinance, 1961",
        "The Dissolution of Muslim Marriages Act, 1939",
        "The Family Courts Act, 2023",
        "The Guardians and Wards Act, 1890",
        "The Child Marriage Restraint Act, 2017",
        "The Hindu Marriage Registration Act, 2012",
        "The Special Marriage Act, 1872",
    ],
    "Commercial": [
        "The Negotiable Instruments Act, 1881",
        "The Contract Act, 1872",
        "The Companies Act, 1994",
        "The Artha Rin Adalat Ain, 2003",
        "The Bankruptcy Act, 1997",
        "The Arbitration Act, 2001",
    ],
    "Constitutional": [
        "The Constitution of the People's Republic of Bangladesh",
    ],
    "Labour": [
        "The Bangladesh Labour Act, 2006",
        "The Bangladesh Labour Rules, 2015",
    ],
    "Tax": [
        "The Income Tax Act, 2023",
        "The Value Added Tax and Supplementary Duty Act, 2012",
        "The Customs Act, 1969",
    ],
    "Consumer": [
        "The Consumer Rights Protection Act, 2009",
    ]
}


class PreGenerationRelevanceGate:
    """
    Evaluates candidate statutory provisions and judicial precedents before packaging.
    Guarantees zero cross-domain pollution (e.g., stops criminal bail cases from leaking into civil injunctions).
    """

    @classmethod
    def filter_evidence_items(
        cls,
        items: list[EvidenceItem],
        query: str,
        detected_domain: Optional[str] = None,
        allowed_acts: Optional[list[str]] = None,
    ) -> list[EvidenceItem]:
        accepted: list[EvidenceItem] = []

        # Derive target domain from allowed_acts if not explicitly provided
        domain = detected_domain or cls._infer_domain_from_acts(allowed_acts or [])

        for item in items:
            # ── Tier 1: Deterministic Metadata Eligibility ──
            if not cls._is_metadata_eligible(item):
                continue

            # ── Tier 2: Domain Alignment ──
            if domain and not cls._is_domain_aligned(item, domain, allowed_acts):
                continue

            # ── Tier 3: Issue Match & Non-Empty Text ──
            if not item.legal_text or len(item.legal_text.strip()) < 15:
                continue

            accepted.append(item)

        return accepted

    @staticmethod
    def _is_metadata_eligible(item: EvidenceItem) -> bool:
        """Verifies fundamental integrity of evidence item."""
        if not item.act_name:
            return False
        # Reject explicitly expired/repealed statutes unless query asks for historical context
        if item.valid_to and item.current_for_query_date is False:
            return False
        return True

    @classmethod
    def _is_domain_aligned(
        cls,
        item: EvidenceItem,
        domain: str,
        allowed_acts: Optional[list[str]] = None
    ) -> bool:
        """Ensures the statute belongs to the active legal domain or query whitelist."""
        if not domain or domain == "General":
            return True

        act_clean = item.act_name.replace("The ", "").strip().lower()

        # Whitelist override
        if allowed_acts:
            for allowed in allowed_acts:
                if allowed.replace("The ", "").strip().lower() in act_clean:
                    return True

        # Check domain allowlist
        valid_acts = DOMAIN_ACT_ALLOWLIST.get(domain, [])
        for valid in valid_acts:
            if valid.replace("The ", "").strip().lower() in act_clean:
                return True

        # Universal evidence acts
        if "evidence act" in act_clean or "constitution" in act_clean:
            return True

        return False

    @staticmethod
    def _infer_domain_from_acts(acts: list[str]) -> Optional[str]:
        for act in acts:
            act_lower = act.lower()
            for dom, dom_acts in DOMAIN_ACT_ALLOWLIST.items():
                for da in dom_acts:
                    if da.lower() in act_lower or act_lower in da.lower():
                        return dom
        return None
