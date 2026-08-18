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
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("Model did not return JSON")
    candidate = match.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        # Fallback: remove non-printable control chars and retry
        clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', candidate)
        return json.loads(clean)



def fast_exact_route(query: str) -> Optional[LegalRoute]:
    """
    Fast 0ms deterministic candidate hint generator using bilingual legal dictionary & rules.
    Provides candidate search areas only; does not embed legal rules or conclusions.
    The primary database independently establishes and verifies all legal rules.
    """
    from .legal_models import CandidateAuthority, LegalIssue
    from .legal_dictionary import expand_query_with_dictionary, normalize_bengali_text

    norm_q = normalize_bengali_text(query).lower()
    dict_match = expand_query_with_dictionary(query)

    # 1. If dictionary matched explicit Bangladesh Acts & sections, build route in 0ms
    if dict_match.get("candidate_acts"):
        candidate_acts = dict_match["candidate_acts"]
        candidate_secs = dict_match.get("candidate_sections", [])
        domain = dict_match.get("domains", ["General Law"])[0] if dict_match.get("domains") else "General Law"

        authorities = []
        for i, act in enumerate(candidate_acts):
            authorities.append(
                CandidateAuthority(
                    act=act,
                    sections=candidate_secs,
                    role="CONTROLLING" if i == 0 else "SUPPORTING",
                    reason="canonical dictionary candidate"
                )
            )

        issues_list = [
            LegalIssue(issue=f"{c} statutory provisions", confidence=0.95)
            for c in dict_match.get("concepts", ["Statutory legal provisions"])
        ]

        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain=domain,
            issues=issues_list or [LegalIssue(issue="Statutory legal provisions", confidence=0.95)],
            authorities=authorities,
            needs_case_law=True,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    # 2. Rule-based regex fallback for explicit Section/Article queries
    sec_match = re.search(r'(?:section|sec\.?|ধারা)\s*([0-9A-Za-z]+)', norm_q, re.IGNORECASE)
    art_match = re.search(r'(?:article|art\.?|অনুচ্ছেদ)\s*([0-9A-Za-z]+)', norm_q, re.IGNORECASE)
    ord_match = re.search(r'(?:order|আদেশ)\s*([0-9IVXLCDM]+)', norm_q, re.IGNORECASE)

    if art_match:
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Constitutional Law",
            issues=[LegalIssue(issue="Constitutional Article interpretation", confidence=0.95)],
            authorities=[
                CandidateAuthority(
                    act="The Constitution of the People's Republic of Bangladesh",
                    sections=[f"Article {art_match.group(1)}", art_match.group(1)],
                    role="CONTROLLING",
                    reason="explicit constitutional article"
                )
            ],
            needs_case_law=True,
            temporal_mode="CURRENT",
            as_of_date=date.today(),
        )

    if ord_match:
        return LegalRoute(
            jurisdiction="Bangladesh",
            legal_domain="Civil Procedure",
            issues=[LegalIssue(issue="Civil Procedure Code Order provisions", confidence=0.95)],
            authorities=[
                CandidateAuthority(
                    act="The Code of Civil Procedure, 1908",
                    sections=[f"Order {ord_match.group(1)}", ord_match.group(1)],
                    role="CONTROLLING",
                    reason="explicit CPC order"
                )
            ],
            needs_case_law=True,
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
