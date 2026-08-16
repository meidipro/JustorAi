from __future__ import annotations

import json
import re
from datetime import date
from typing import Awaitable, Callable
from .legal_models import LegalRoute

ROUTER_PROMPT = """
You are the legal routing layer for Justor AI.

Jurisdiction is Bangladesh.
Your job is NOT to answer the legal question.

Identify:
1. legal issue(s)
2. likely primary statute(s)
3. likely section(s)
4. supporting statutes
5. whether case law is necessary
6. temporal intent

Authority roles:
CONTROLLING
SUPPORTING
GENERAL
BACKGROUND

Temporal modes:
CURRENT
AS_OF_DATE
HISTORICAL
COMPARE_VERSIONS
AMENDMENT_HISTORY

Rules:
- Do not invent section numbers.
- Candidate sections are suggestions only.
- The database independently verifies them.
- Prefer specific provisions over general provisions.
- Consider cross-statute relationships.
- Do not use Indian law.

Return JSON only:

{
  "jurisdiction": "Bangladesh",
  "legal_domain": "...",
  "issues": [
    {"issue": "...", "confidence": 0.95}
  ],
  "authorities": [
    {
      "act": "...",
      "sections": ["..."],
      "role": "CONTROLLING",
      "reason": "..."
    }
  ],
  "needs_case_law": false,
  "temporal_mode": "CURRENT",
  "as_of_date": null
}
"""


def extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("Model did not return JSON")
    return json.loads(match.group(0))


def fast_exact_route(query: str) -> Optional[LegalRoute]:
    q = query.lower()
    from .legal_models import CandidateAuthority, LegalIssue

    # 1. Contract for sale / Baina / Section 54A / Section 17A
    if any(k in q for k in ["contract for sale", "baina", "bayanama", "54a", "17a", "agreement for sale"]):
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Property & Land Law",
            issues=[LegalIssue(issue="Validity and enforceability of contract for sale of immovable property", confidence=0.98)],
            authorities=[
                CandidateAuthority(act="The Registration Act, 1908", sections=["17A", "23", "49"], role="CONTROLLING", reason="Mandatory registration & presentation timelines"),
                CandidateAuthority(act="The Transfer of Property Act, 1882", sections=["54", "54A"], role="CONTROLLING", reason="Statutory requirement for registered contract for sale"),
                CandidateAuthority(act="The Specific Relief Act, 1877", sections=["21A"], role="SUPPORTING", reason="Bar on specific performance of unregistered contract"),
            ],
            needs_case_law=True,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    # 2. Land Registration / Section 23 / 3-month deadline
    if any(k in q for k in ["land registration", "register land", "section 23", "registration act"]):
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Property & Land Law",
            issues=[LegalIssue(issue="Statutory land registration procedure and presentation timelines", confidence=0.95)],
            authorities=[
                CandidateAuthority(act="The Registration Act, 1908", sections=["17", "23", "49"], role="CONTROLLING", reason="Mandatory registration & 3-month timeline"),
                CandidateAuthority(act="The Transfer of Property Act, 1882", sections=["54"], role="SUPPORTING", reason="Transfer of ownership definition"),
            ],
            needs_case_law=False,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    # 3. Mutation / Namjari / Khatian
    if any(k in q for k in ["mutation", "namjari", "khatian", "porcha", "dcr", "kharaj"]):
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Land Revenue Law",
            issues=[LegalIssue(issue="Land mutation and revenue record update procedure", confidence=0.95)],
            authorities=[
                CandidateAuthority(act="State Acquisition and Tenancy Act, 1950", sections=["116", "117", "143"], role="CONTROLLING", reason="Record of rights and mutation statutory provisions"),
            ],
            needs_case_law=False,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    # 4. Denmohor / Dower / Maintenance / Family Court
    if any(k in q for k in ["denmohor", "dower", "mehr", "maintenance", "family court"]):
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Family & Personal Law",
            issues=[LegalIssue(issue="Dower and maintenance recovery rights", confidence=0.95)],
            authorities=[
                CandidateAuthority(act="The Muslim Family Laws Ordinance, 1961", sections=["9", "10"], role="CONTROLLING", reason="Statutory dower and maintenance provisions"),
                CandidateAuthority(act="The Family Courts Act, 2023", sections=["4", "5"], role="SUPPORTING", reason="Exclusive family court jurisdiction"),
            ],
            needs_case_law=False,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    # 5. Talaq / Divorce
    if any(k in q for k in ["talaq", "divorce", "dissolution of marriage", "khula", "tawfeez"]):
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Family & Personal Law",
            issues=[LegalIssue(issue="Statutory procedure for talaq and judicial dissolution", confidence=0.95)],
            authorities=[
                CandidateAuthority(act="The Muslim Family Laws Ordinance, 1961", sections=["7"], role="CONTROLLING", reason="Statutory talaq notice and 90-day reconciliation"),
                CandidateAuthority(act="The Dissolution of Muslim Marriages Act, 1939", sections=["2"], role="SUPPORTING", reason="Grounds for decree of dissolution of marriage"),
            ],
            needs_case_law=False,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    # 6. Consumer rights / Defective product / DNCRP
    if any(k in q for k in ["defective product", "consumer", "dncrp", "fake product", "damaged goods"]):
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Consumer Protection Law",
            issues=[LegalIssue(issue="Consumer rights remedy for defective goods and compensation", confidence=0.95)],
            authorities=[
                CandidateAuthority(act="The Sale of Goods Act, 1930", sections=["14", "16"], role="CONTROLLING", reason="Implied conditions and warranties as to quality"),
                CandidateAuthority(act="Consumers' Right Protection Act, 2009", sections=["45", "76"], role="SUPPORTING", reason="DNCRP complaints and 25% compensation reward"),
            ],
            needs_case_law=False,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    return None


class LegalRouter:
    def __init__(
        self,
        llm_call: Callable[[list[dict]], Awaitable[str]],
    ):
        self.llm_call = llm_call

    async def route(self, query: str) -> LegalRoute:
        # Fast 0ms rule-based path
        fast_res = fast_exact_route(query)
        if fast_res:
            return fast_res

        # LLM fallback path
        raw = await self.llm_call(
            [
                {"role": "system", "content": ROUTER_PROMPT},
                {"role": "user", "content": query},
            ]
        )
        parsed = extract_json(raw)
        route = LegalRoute.model_validate(parsed)
        if route.temporal_mode == "CURRENT" and route.as_of_date is None:
            route.as_of_date = date.today()
        return route
