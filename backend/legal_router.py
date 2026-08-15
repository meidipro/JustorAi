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


class LegalRouter:
    def __init__(
        self,
        llm_call: Callable[[list[dict]], Awaitable[str]],
    ):
        self.llm_call = llm_call

    async def route(self, query: str) -> LegalRoute:
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
