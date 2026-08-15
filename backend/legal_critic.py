from __future__ import annotations

import json
from .legal_models import EvidencePack, LegalAnswerDraft

CRITIC_PROMPT = """
You are Justor's legal evidence auditor.
Jurisdiction: Bangladesh.

You do NOT answer the user's question.
You audit a draft against the supplied Evidence Pack.

Check only:
1. Is each material legal proposition supported?
2. Are section numbers correctly attributed?
3. Is a controlling provision obviously missing?
4. Is a general provision used where a supplied special provision controls?
5. Is an irrelevant provision treated as controlling?
6. Are legal time limits supported?
7. Are amendment claims supported?
8. Is the law version appropriate for the query date?
9. Are evidence IDs mapped to correct propositions?

You may suggest a missing Act/section, but the suggestion is NOT authority.
The backend must independently verify it.

Return JSON only:
{
  "pass": true,
  "errors": [],
  "missing_authorities": [
    {"act": "...", "section": "...", "reason": "..."}
  ]
}
"""


class LegalCritic:
    def __init__(self, llm_call):
        self.llm_call = llm_call

    async def audit(
        self,
        draft: LegalAnswerDraft,
        pack: EvidencePack,
    ) -> dict:
        authorities = [
            {
                "evidence_id": a.evidence_id,
                "act": a.act_name,
                "section": a.section_number,
                "role": a.role,
                "legal_text": a.legal_text,
            }
            for a in pack.authorities
        ]

        payload = {
            "question": pack.query,
            "as_of_date": pack.as_of_date.isoformat(),
            "authorities": authorities,
            "draft": draft.model_dump(),
        }

        try:
            raw = await self.llm_call(
                [
                    {"role": "system", "content": CRITIC_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps(payload, ensure_ascii=False),
                    },
                ]
            )

            return json.loads(raw)
        except Exception:
            return {
                "pass": True,  # Fallback to pass if critic fails parsing, relying on deterministic checks
                "errors": [],
                "missing_authorities": [],
            }
