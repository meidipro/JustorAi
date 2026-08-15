from __future__ import annotations

import json
from .legal_models import EvidencePack, LegalAnswerDraft
from .legal_prompts import LAWYER_PROMPT, STUDENT_PROMPT
from .legal_router import LegalRouter, extract_json
from .legal_repository import LegalRepository
from .evidence_builder import EvidenceBuilder
from .legal_validation import validate_draft
from .legal_critic import LegalCritic


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

        # 4. Independent legal critic.
        critic_result = await self.critic.audit(draft, pack)
        missing = await self._verify_missing_authorities(critic_result, pack)

        # 5. Add only DB-verified critic suggestions.
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
            return self._success(draft, pack)

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
            second_critic = await self.critic.audit(second_draft, pack)

            if second_validation.passed and second_critic.get("pass") is True:
                return self._success(second_draft, pack)

        # 7. Fail closed.
        return {
            "status": "abstain",
            "answer": (
                "Justor identified potentially relevant law, but the generated "
                "analysis did not pass its legal evidence verification checks. "
                "Please review the primary authorities directly."
            ),
            "reason": "LEGAL_VERIFICATION_FAILED",
            "authorities": self._authority_cards(pack),
        }

    def _success(self, draft: LegalAnswerDraft, pack: EvidencePack) -> dict:
        return {
            "status": "ok",
            "answer": self.render_markdown(draft, pack),
            "authorities": self._authority_cards(pack),
        }

    def _authority_cards(self, pack: EvidencePack) -> list[dict]:
        return [
            {
                "id": source.evidence_id,
                "act": source.act_name,
                "section": source.section_number,
                "heading": source.heading,
                "role": source.role,
                "official_url": source.official_url,
                "official_source": source.official_source_verified,
                "exact_section": source.exact_section_verified,
                "current_version": source.version_verified,
            }
            for source in pack.authorities
        ]

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

        output.append("## Verified Authorities")

        for source in pack.authorities:
            badges = []
            if source.official_source_verified:
                badges.append("✓ Official Source")
            if source.exact_section_verified:
                badges.append("✓ Exact Section")
            if source.version_verified:
                badges.append("✓ Current Version")

            output.append(
                f"**[{source.evidence_id}] {source.act_name} — "
                f"Section {source.section_number}**  \n"
                f"{' · '.join(badges)}  \n"
                f"{source.official_url or ''}"
            )

        output.append(
            f"\n*Current-law check performed for {pack.as_of_date.isoformat()}.*"
        )
        return "\n\n".join(output)
