from __future__ import annotations

import json
from .legal_models import EvidencePack, LegalAnswerDraft
from .legal_prompts import LAWYER_PROMPT, STUDENT_PROMPT
from .legal_router import LegalRouter, extract_json
from .legal_repository import LegalRepository
from .evidence_builder import EvidenceBuilder
from .legal_validation import validate_draft
from .legal_critic import LegalCritic
from .legal_clarification import FactSufficiencyGate


class LegalAnswerEngine:
    def __init__(self, repository: LegalRepository, embed_fn, llm_call):
        self.repository = repository
        self.embed_fn = embed_fn
        self.llm_call = llm_call
        self.router = LegalRouter(llm_call=llm_call)
        self.builder = EvidenceBuilder(repository=repository, embed_fn=embed_fn)
        self.critic = LegalCritic(llm_call=llm_call)

    def _system_prompt(self, persona: str) -> str:
        normalized = persona.lower()
        if "lawyer" in normalized or "legal professional" in normalized:
            return LAWYER_PROMPT
        return STUDENT_PROMPT

    def _serialize_pack(self, pack: EvidencePack) -> str:
        return json.dumps(
            pack.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        )

    async def _generate(
        self,
        pack: EvidencePack,
        correction_feedback: str | None = None,
    ) -> LegalAnswerDraft:
        system_prompt = self._system_prompt(pack.persona)
        if correction_feedback:
            system_prompt += (
                "\n\nPREVIOUS DRAFT FAILED VALIDATION.\n\n"
                + correction_feedback
            )

        raw = await self.llm_call(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self._serialize_pack(pack)},
            ]
        )
        parsed = extract_json(raw)
        return LegalAnswerDraft.model_validate(parsed)

    async def _verify_missing_authorities(
        self,
        critic_result: dict,
        pack: EvidencePack,
    ) -> list:
        verified = []
        existing = {
            (x.act_name.lower(), x.section_number.upper())
            for x in pack.authorities
        }

        for candidate in critic_result.get("missing_authorities", []):
            act = candidate.get("act")
            section = candidate.get("section")
            if not act or not section:
                continue

            result = await self.repository.provision_exists(
                act_name=act,
                section_number=section,
                query_date=pack.as_of_date,
            )
            if not result:
                continue

            key = (result.act_name.lower(), result.section_number.upper())
            if key in existing:
                continue
            verified.append(result)

        return verified

    async def answer(self, query: str, persona: str) -> dict:
        # 0. Fact Sufficiency & Interactive Clarification Gate
        clarification = FactSufficiencyGate.evaluate_fact_sufficiency(query, persona)
        if clarification and clarification.get("status") == "needs_clarification":
            return {
                "status": "ok",
                "answer": clarification["clarification_prompt"],
                "reason": "FACT_CLARIFICATION_REQUIRED",
                "authorities": [],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "title": "Legal Intent & Fact Sufficiency",
                        "summary": f"Detected {clarification['intent']} inquiry requiring missing material variables.",
                        "status": "needs_clarification"
                    }
                ]
            }

        # 1. Route.
        try:
            route = await self.router.route(query)
        except Exception as exc:
            return {
                "status": "abstain",
                "answer": "Justor could not reliably classify this legal query.",
                "reason": "ROUTER_FAILURE",
                "debug": str(exc),
            }

        # 2. Build verified Evidence Pack.
        try:
            pack = await self.builder.build(
                query=query,
                persona=persona,
                route=route,
            )
        except Exception as exc:
            return {
                "status": "abstain",
                "answer": "Justor could not build a verified legal evidence set.",
                "reason": "EVIDENCE_BUILD_FAILURE",
                "debug": str(exc),
            }

        if not pack.authorities:
            return {
                "status": "abstain",
                "answer": (
                    "Justor could not verify the controlling legal authority "
                    "from its current primary-source database."
                ),
                "reason": "NO_VERIFIED_EVIDENCE",
            }

        # 3. First generation.
        try:
            draft = await self._generate(pack)
        except Exception as exc:
            return {
                "status": "abstain",
                "answer": "Justor found relevant law, but generation failed.",
                "reason": "GENERATION_FAILURE",
                "debug": str(exc),
            }

        validation = validate_draft(draft, pack)

        # 4. Fast path for perfectly valid drafts
        if validation.passed:
            return self._success(draft, pack, route)

        # 5. Independent legal critic for drafts with validation notices
        critic_result = await self.critic.audit(draft, pack)
        missing = await self._verify_missing_authorities(critic_result, pack)

        # Add only DB-verified critic suggestions.
        if missing:
            next_index = len(pack.authorities) + 1
            for source in missing:
                source.evidence_id = f"ACT-{next_index}"
                source.role = "CONTROLLING"
                pack.authorities.append(source)
                next_index += 1
            validation.passed = False

        critic_pass = bool(critic_result.get("pass", False))

        if validation.passed and critic_pass:
            return self._success(draft, pack, route)

        # 6. One controlled regeneration.
        feedback = json.dumps(
            {
                "deterministic_errors": [
                    e.model_dump() for e in validation.errors
                ],
                "critic_errors": critic_result.get("errors", []),
            },
            ensure_ascii=False,
        )

        try:
            second_draft = await self._generate(
                pack,
                correction_feedback=feedback,
            )
        except Exception:
            second_draft = None

        if second_draft is not None:
            second_validation = validate_draft(second_draft, pack)
            if second_validation.passed:
                # Re-run legal critic on second draft to prevent critic bypass
                second_critic = await self.critic.audit(second_draft, pack)
                if bool(second_critic.get("pass", False)):
                    return self._success(second_draft, pack, route)

        # 7. Fail closed.
        return {
            "status": "abstain",
            "answer": (
                "Justor identified potentially relevant law, but the generated "
                "analysis did not pass its evidence-checked legal verification gates. "
                "Please review the primary authorities directly."
            ),
            "reason": "LEGAL_VERIFICATION_FAILED",
            "authorities": self._authority_cards(pack),
            "reasoning_steps": self._build_reasoning_steps(route, pack, "abstain"),
        }

    def _build_reasoning_steps(self, route, pack: EvidencePack, status: str) -> list[dict]:
        acts_str = ", ".join(list({a.act_name for a in pack.authorities})[:2]) if pack.authorities else "Primary Legislation"
        return [
            {
                "step": 1,
                "title": "Legal Intent & Routing",
                "summary": f"Classified domain: {getattr(route, 'legal_domain', 'General Law')}. Targeted: {acts_str}.",
                "status": "completed"
            },
            {
                "step": 2,
                "title": "Primary Authority Retrieval",
                "summary": f"Retrieved {len(pack.authorities)} provisions with official citations.",
                "status": "completed"
            },
            {
                "step": 3,
                "title": "Rule & Citation Verification",
                "summary": "Verified statutory quotes, temporal validity, trust tiers, and numeric deadlines.",
                "status": "passed" if status == "ok" else "failed_closed"
            },
            {
                "step": 4,
                "title": "Grounded Legal Synthesis",
                "summary": "Generated structured legal analysis anchored strictly to primary sources." if status == "ok" else "Abstained due to verification constraints.",
                "status": "completed" if status == "ok" else "abstained"
            }
        ]

    def _success(self, draft: LegalAnswerDraft, pack: EvidencePack, route=None) -> dict:
        return {
            "status": "ok",
            "answer": self.render_markdown(draft, pack),
            "authorities": self._authority_cards(pack),
            "reasoning_steps": self._build_reasoning_steps(route, pack, "ok"),
        }

    def _authority_cards(self, pack: EvidencePack) -> list[dict]:
        cards = []
        for source in pack.authorities:
            card = {
                "id": source.evidence_id,
                "type": source.item_type,
                "act": source.act_name,
                "section": source.section_number,
                "heading": source.heading,
                "role": source.role,
                "official_url": source.official_url,
                "official_source": source.official_source_verified,
                "exact_section": source.exact_section_verified,
                "current_version": source.version_verified,
                "trust_tier": source.trust_tier,
                "trust_badge": source.get_badge(),
            }
            if source.item_type == "case":
                card["case_title"] = source.case_title
                card["citation"] = source.citation
                card["court"] = source.court
                card["year"] = source.year
                card["ratio_decidendi"] = source.ratio_decidendi
            cards.append(card)
        return cards

    def render_markdown(
        self,
        draft: LegalAnswerDraft,
        pack: EvidencePack,
    ) -> str:
        def paragraph(item):
            tags = " ".join(f"[{x}]" for x in item.evidence_ids)
            return f"{item.text} {tags}".strip()

        output = []
        lawyer = (
            "lawyer" in pack.persona.lower()
            or "legal professional" in pack.persona.lower()
        )

        if lawyer:
            output.append("## ISSUE\n\n" + draft.issue)
            if draft.rules:
                output.append(
                    "## RULE\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.rules)
                )
            if draft.doctrine:
                output.append(
                    "## PRECEDENT & DOCTRINE\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.doctrine)
                )
            if draft.application:
                output.append(
                    "## APPLICATION\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.application)
                )
            output.append("## CONCLUSION\n\n" + paragraph(draft.conclusion))
        else:
            output.append("## The Legal Issue\n\n" + draft.issue)
            if draft.rules:
                output.append(
                    "## Applicable Law\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.rules)
                )
            if draft.doctrine:
                output.append(
                    "## Legal Principle\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.doctrine)
                )
            if draft.application:
                output.append(
                    "## Example / Application\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.application)
                )
            if draft.key_points:
                output.append(
                    "## Key Points\n\n"
                    + "\n".join("- " + paragraph(x) for x in draft.key_points)
                )
            output.append("## Conclusion\n\n" + paragraph(draft.conclusion))

        output.append("## Verified Authorities & Evidence")

        for source in pack.authorities:
            if source.item_type == "case":
                title_line = f"**[{source.evidence_id}]** `{source.case_title or source.act_name}` — {source.citation or ''}"
                if source.court:
                    title_line += f" | {source.court}"
                if source.year:
                    title_line += f" | {source.year}"
                badge_line = source.get_badge()
                output.append(f"- {title_line} — {badge_line}")
            else:
                sec_str = f", Section {source.section_number}" if source.section_number else ""
                heading_str = f": {source.heading}" if source.heading else ""
                badge_line = source.get_badge()
                output.append(
                    f"- **[{source.evidence_id}]** `{source.act_name}`{sec_str}{heading_str} — {badge_line}"
                )

        output.append(
            f"\n*Current-law check performed for query date {pack.as_of_date.isoformat()}.*\n\n"
            "⚖️ *Justor AI summarizes cited legal material to reduce research time. "
            "Practitioners should open and verify primary authorities before relying on the proposition in professional court work.*"
        )
        return "\n\n".join(output)
