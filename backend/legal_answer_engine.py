from __future__ import annotations

import json
import re
from .legal_models import EvidencePack, LegalAnswerDraft
from .legal_prompts import LAWYER_PROMPT, STUDENT_PROMPT
from .legal_router import LegalRouter, extract_json
from .legal_repository import LegalRepository
from .evidence_builder import EvidenceBuilder
from .legal_validation import validate_draft
from .legal_critic import LegalCritic
from .legal_clarification import FactSufficiencyGate
from .legal_normalize import is_bengali_requested


class LegalAnswerEngine:
    def __init__(self, repository: LegalRepository, embed_fn, llm_call):
        self.repository = repository
        self.embed_fn = embed_fn
        self.llm_call = llm_call
        self.router = LegalRouter(llm_call=llm_call)
        self.builder = EvidenceBuilder(repository=repository, embed_fn=embed_fn)
        self.critic = LegalCritic(llm_call=llm_call)

    def _system_prompt(self, persona: str, language: str = "EN") -> str:
        normalized = persona.lower()
        base_prompt = LAWYER_PROMPT if ("lawyer" in normalized or "legal professional" in normalized) else STUDENT_PROMPT
        if language == "BN":
            base_prompt += (
                "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "🔴 MANDATORY LANGUAGE INSTRUCTION: STRICT BENGALI (বাংলা) 🔴\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "- The user has requested the response in BENGALI (বাংলা).\n"
                "- Write ALL legal explanations, doctrines, examples, and conclusions in natural, fluent BENGALI (বাংলায় লিখুন).\n"
                "- In the JSON response, ALL string values for 'issue', 'rules[].text', 'doctrine[].text', "
                "'application[].text', 'conclusion.text', 'key_points[].text', and 'claims[].text' MUST BE WRITTEN IN BENGALI.\n"
                "- Do NOT write English paragraphs for explanations.\n"
                "- Retain official citations clearly formatted (e.g. 'The Registration Act, 1908-এর Section 17A', 'The Penal Code, 1860-এর Section 302', 'Article 102', 'Order 39 Rule 1').\n"
                "- Strictly tag every claim with its exact evidence tag (e.g. [ACT-1], [DLR-1]).\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
        return base_prompt

    def _serialize_pack(self, pack: EvidencePack) -> str:
        compact_authorities = []
        for a in pack.authorities:
            compact_authorities.append({
                "evidence_id": a.evidence_id,
                "act_name": a.act_name,
                "section_number": a.section_number,
                "heading": a.heading,
                "role": a.role,
                "trust_tier": a.trust_tier,
                "legal_text": a.legal_text[:1000] if a.legal_text else "",
                "case_title": a.case_title,
                "citation": a.citation,
                "ratio_decidendi": a.ratio_decidendi,
            })
        
        payload = {
            "query": pack.query,
            "persona": pack.persona,
            "as_of_date": pack.as_of_date.isoformat(),
            "authorities": compact_authorities,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)

    async def _generate(
        self,
        pack: EvidencePack,
        language: str = "EN",
        correction_feedback: str | None = None,
    ) -> LegalAnswerDraft:
        system_prompt = self._system_prompt(pack.persona, language=language)
        if correction_feedback:
            system_prompt += (
                "\n\nPREVIOUS DRAFT FAILED VALIDATION.\n\n"
                + correction_feedback
            )

        for attempt in range(2):
            raw = await self.llm_call(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": self._serialize_pack(pack)},
                ]
            )
            try:
                parsed = extract_json(raw)
                return LegalAnswerDraft.model_validate(parsed)
            except Exception as exc:
                if attempt == 0:
                    system_prompt += "\n\nCRITICAL INSTRUCTION: Return strictly valid, parseable JSON matching the schema."
                    continue
                clean = re.sub(r',\s*([\]}])', r'\1', raw)
                m = re.search(r'\{.*\}', clean, re.S)
                if m:
                    import ast
                    try:
                        p = ast.literal_eval(m.group(0))
                        return LegalAnswerDraft.model_validate(p)
                    except Exception:
                        pass
                raise exc

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

    async def answer(self, query: str, persona: str, language: str = "EN") -> dict:
        effective_lang = "BN" if is_bengali_requested(query, language) else "EN"
        # 0. Fact Sufficiency & Interactive Clarification Gate
        clarification = FactSufficiencyGate.evaluate_fact_sufficiency(query, persona)
        if clarification and clarification.get("status") == "needs_clarification":
            c_prompt = clarification["clarification_prompt"]
            return {
                "status": "ok",
                "answer": c_prompt,
                "reason": "FACT_CLARIFICATION_REQUIRED",
                "authorities": [],
                "reasoning_steps": [
                    {
                        "step": 1,
                        "title": "আইনি উদ্দেশ্য ও তথ্যের পর্যাপ্ততা" if effective_lang == "BN" else "Legal Intent & Fact Sufficiency",
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
                "answer": "জাসটর এই আইনি প্রশ্নটি সঠিকভাবে শ্রেণিবদ্ধ করতে পারেনি।" if effective_lang == "BN" else "Justor could not reliably classify this legal query.",
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
                "answer": "জাসটর যাচাইকৃত আইনি তথ্যসূত্র সংগ্রহ করতে পারেনি।" if effective_lang == "BN" else "Justor could not build a verified legal evidence set.",
                "reason": "EVIDENCE_BUILD_FAILURE",
                "debug": str(exc),
            }

        if not pack.authorities:
            return {
                "status": "abstain",
                "answer": (
                    "জাসটরের বর্তমান যাচাইকৃত ডাটাবেজে এই নির্দিষ্ট আইনি বিধান বা নজির পাওয়া যায়নি।"
                    if effective_lang == "BN" else
                    "Justor could not verify the controlling legal authority from its current primary-source database."
                ),
                "reason": "NO_VERIFIED_EVIDENCE",
            }

        # 3. First generation.
        try:
            draft = await self._generate(pack, language=effective_lang)
        except Exception as exc:
            return {
                "status": "abstain",
                "answer": "প্রাসঙ্গিক আইন পাওয়া গেছে, কিন্তু উত্তর তৈরিতে সমস্যা হয়েছে।" if effective_lang == "BN" else "Justor found relevant law, but generation failed.",
                "reason": "GENERATION_FAILURE",
                "authorities": self._authority_cards(pack),
                "reasoning_steps": self._build_reasoning_steps(route, pack, "abstain", language=effective_lang),
                "debug": str(exc),
            }

        validation = validate_draft(draft, pack)

        # 4. Fast path for perfectly valid drafts
        if validation.passed:
            return self._success(draft, pack, route, language=effective_lang)

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
            return self._success(draft, pack, route, language=effective_lang)

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
                language=effective_lang,
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
                    return self._success(second_draft, pack, route, language=effective_lang)

        # 7. Fail closed.
        return {
            "status": "abstain",
            "answer": (
                "জাসটর প্রাসঙ্গিক আইন শনাক্ত করেছে, কিন্তু উৎপন্ন বিশ্লেষণ প্রমাণ যাচাইকরণ পরীক্ষায় উত্তীর্ণ হতে পারেনি। অনুগ্রহ করে সরাসরি মূল আইন ও নথিপত্র পর্যালোচনা করুন।"
                if effective_lang == "BN" else
                (
                    "Justor identified potentially relevant law, but the generated "
                    "analysis did not pass its evidence-checked legal verification gates. "
                    "Please review the primary authorities directly."
                )
            ),
            "reason": "LEGAL_VERIFICATION_FAILED",
            "authorities": self._authority_cards(pack),
            "reasoning_steps": self._build_reasoning_steps(route, pack, "abstain", language=effective_lang),
        }

    def _build_reasoning_steps(self, route, pack: EvidencePack, status: str, language: str = "EN") -> list[dict]:
        is_bn = (language == "BN")
        acts_str = ", ".join(list({a.act_name for a in pack.authorities})[:2]) if pack.authorities else ("মূল সংবিধিবদ্ধ আইন" if is_bn else "Primary Legislation")
        domain_str = getattr(route, 'legal_domain', 'সাধারণ আইন' if is_bn else 'General Law')
        if is_bn:
            return [
                {
                    "step": 1,
                    "title": "আইনি উদ্দেশ্য ও অনুসন্ধান শ্রেণিবিভাগ",
                    "summary": f"আইনি ক্ষেত্র: {domain_str}। চিহ্নিত উৎস: {acts_str}।",
                    "status": "completed"
                },
                {
                    "step": 2,
                    "title": "মূল বিধিবদ্ধ আইন ও নজির অনুসন্ধান",
                    "summary": f"{len(pack.authorities)}টি অফিসিয়াল আইনি ধারা ও রায় সংগৃহীত হয়েছে।",
                    "status": "completed"
                },
                {
                    "step": 3,
                    "title": "ধারা ও নজিরের যথার্থতা যাচাই",
                    "summary": "বিধিবদ্ধ আইনের উদ্ধৃতি, সময়সীমা ও নজিরের বৈধতা যাচাই সম্পন্ন।",
                    "status": "passed" if status == "ok" else "failed_closed"
                },
                {
                    "step": 4,
                    "title": "আইনি বিশ্লেষণ ও মতামত প্রণয়ন",
                    "summary": "যাচাইকৃত উৎসের ভিত্তিতে বিশ্লেষণ প্রস্তুত।" if status == "ok" else "যাচাইকরণ বিধিনিষেধের কারণে মতামত বিরত রাখা হয়েছে।",
                    "status": "completed" if status == "ok" else "abstained"
                }
            ]
        return [
            {
                "step": 1,
                "title": "Legal Intent & Routing",
                "summary": f"Classified domain: {domain_str}. Targeted: {acts_str}.",
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

    def _success(self, draft: LegalAnswerDraft, pack: EvidencePack, route=None, language: str = "EN") -> dict:
        return {
            "status": "ok",
            "answer": self.render_markdown(draft, pack, language=language),
            "authorities": self._authority_cards(pack),
            "reasoning_steps": self._build_reasoning_steps(route, pack, "ok", language=language),
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
        language: str = "EN",
    ) -> str:
        def paragraph(item):
            tags = " ".join(f"[{x}]" for x in item.evidence_ids)
            return f"{item.text} {tags}".strip()

        output = []
        lawyer = (
            "lawyer" in pack.persona.lower()
            or "legal professional" in pack.persona.lower()
        )
        is_bn = (language == "BN")

        if lawyer:
            h_issue = "## আইনি প্রশ্ন ও বিরোধ (The Legal Issue)" if is_bn else "## ISSUE"
            h_rule = "## প্রযোজ্য সংবিধিবদ্ধ আইন (Controlling Statutory Law)" if is_bn else "## RULE"
            h_doctrine = "## বিচারিক নজির ও আইনি নীতি (Precedent & Doctrine)" if is_bn else "## PRECEDENT & DOCTRINE"
            h_app = "## ঘটনার আইনি প্রয়োগ ও বিশ্লেষণ (Application)" if is_bn else "## APPLICATION"
            h_concl = "## সিদ্ধান্ত ও আইনি অভিমত (Conclusion)" if is_bn else "## CONCLUSION"

            output.append(f"{h_issue}\n\n" + draft.issue)
            if draft.rules:
                output.append(
                    f"{h_rule}\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.rules)
                )
            if draft.doctrine:
                output.append(
                    f"{h_doctrine}\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.doctrine)
                )
            if draft.application:
                output.append(
                    f"{h_app}\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.application)
                )
            output.append(f"{h_concl}\n\n" + paragraph(draft.conclusion))
        else:
            h_issue = "## মূল আইনি বিষয় (The Legal Issue)" if is_bn else "## The Legal Issue"
            h_law = "## প্রযোজ্য আইন (Applicable Law)" if is_bn else "## Applicable Law"
            h_doctrine = "## আইনি নীতি ও তত্ত্ব (Legal Principle)" if is_bn else "## Legal Principle"
            h_app = "## বাস্তব উদাহরণ ও প্রয়োগ (Example / Application)" if is_bn else "## Example / Application"
            h_kp = "## গুরুত্বপূর্ণ দিকসমূহ (Key Points)" if is_bn else "## Key Points"
            h_concl = "## সিদ্ধান্ত ও করণীয় (Conclusion)" if is_bn else "## Conclusion"

            output.append(f"{h_issue}\n\n" + draft.issue)
            if draft.rules:
                output.append(
                    f"{h_law}\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.rules)
                )
            if draft.doctrine:
                output.append(
                    f"{h_doctrine}\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.doctrine)
                )
            if draft.application:
                output.append(
                    f"{h_app}\n\n"
                    + "\n\n".join(paragraph(x) for x in draft.application)
                )
            if draft.key_points:
                output.append(
                    f"{h_kp}\n\n"
                    + "\n".join("- " + paragraph(x) for x in draft.key_points)
                )
            output.append(f"{h_concl}\n\n" + paragraph(draft.conclusion))

        h_auth = "## যাচাইকৃত আইনি রেফারেন্স ও প্রমাণ (Verified Authorities)" if is_bn else "## Verified Authorities & Evidence"
        output.append(h_auth)

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

        if is_bn:
            output.append(
                f"\n*আইনি তথ্যের সময়সীমা যাচাই: {pack.as_of_date.isoformat()}*\n\n"
                "⚖️ *জাসটর এআই (Justor AI) আইনি গবেষণার সুবিধার্থে অফিসিয়াল আইন ও নজির সারসংক্ষেপ করে। "
                "আদালতে বা পেশাগত কাজে ব্যবহারের পূর্বে সংশ্লিষ্ট মূল গ্যাজেট ও নথিপত্র যাচাই করে নিন।*"
            )
        else:
            output.append(
                f"\n*Current-law check performed for query date {pack.as_of_date.isoformat()}.*\n\n"
                "⚖️ *Justor AI summarizes cited legal material to reduce research time. "
                "Practitioners should open and verify primary authorities before relying on the proposition in professional court work.*"
            )
        return "\n\n".join(output)

    async def answer_stream(self, query: str, persona: str, language: str = "EN"):
        """
        Yields real-time SSE event dictionaries:
        - {"event": "step", "data": {...}}
        - {"event": "authorities", "data": [...]}
        - {"event": "complete", "data": {...}}
        """
        effective_lang = "BN" if is_bengali_requested(query, language) else "EN"
        is_bn = (effective_lang == "BN")

        # 0. Fact Sufficiency Gate
        yield {
            "event": "step",
            "data": {
                "step": 1,
                "title": "আইনি উদ্দেশ্য ও তথ্যের পর্যাপ্ততা" if is_bn else "Legal Intent & Fact Sufficiency",
                "summary": "প্রশ্নের গঠন এবং প্রয়োজনীয় আইনি চলকসমূহ বিশ্লেষণ করা হচ্ছে..." if is_bn else "Analyzing inquiry structure and mandatory material variables...",
                "status": "running"
            }
        }
        clarification = FactSufficiencyGate.evaluate_fact_sufficiency(query, persona)
        if clarification and clarification.get("status") == "needs_clarification":
            c_prompt = clarification["clarification_prompt"]
            step_data = {
                "step": 1,
                "title": "আইনি উদ্দেশ্য ও তথ্যের পর্যাপ্ততা" if is_bn else "Legal Intent & Fact Sufficiency",
                "summary": f"চিহ্নিত অনুসন্ধান: {clarification['intent']}।" if is_bn else f"Detected {clarification['intent']} inquiry requiring missing material variables.",
                "status": "needs_clarification"
            }
            yield {"event": "step", "data": step_data}
            complete_data = {
                "status": "ok",
                "answer": c_prompt,
                "reason": "FACT_CLARIFICATION_REQUIRED",
                "authorities": [],
                "reasoning_steps": [step_data]
            }
            yield {"event": "complete", "data": complete_data}
            return

        # 1. Route
        try:
            route = await self.router.route(query)
            acts_target = ", ".join(getattr(route, "candidate_acts", [])[:2]) or ("মূল সংবিধিবদ্ধ আইন" if is_bn else "General Legislation")
            domain_label = getattr(route, 'legal_domain', 'সাধারণ আইন' if is_bn else 'General Law')
            yield {
                "event": "step",
                "data": {
                    "step": 1,
                    "title": "আইনি উদ্দেশ্য ও অনুসন্ধান শ্রেণিবিভাগ" if is_bn else "Legal Intent & Routing",
                    "summary": f"শ্রেণিভুক্ত ক্ষেত্র: {domain_label}। চিহ্নিত উৎস: {acts_target}।" if is_bn else f"Classified domain: {domain_label}. Targeted: {acts_target}.",
                    "status": "completed"
                }
            }
        except Exception as exc:
            yield {
                "event": "complete",
                "data": {
                    "status": "abstain",
                    "answer": "জাসটর এই আইনি প্রশ্নটি সঠিকভাবে শ্রেণিবদ্ধ করতে পারেনি।" if is_bn else "Justor could not reliably classify this legal query.",
                    "reason": "ROUTER_FAILURE",
                    "debug": str(exc)
                }
            }
            return

        # 2. Build verified Evidence Pack
        yield {
            "event": "step",
            "data": {
                "step": 2,
                "title": "মূল বিধিবদ্ধ আইন ও নজির অনুসন্ধান" if is_bn else "Primary Authority Retrieval",
                "summary": "বাংলাদেশের সংবিধিবদ্ধ আইন ও সুপ্রিম কোর্টের নজির অনুসন্ধান করা হচ্ছে..." if is_bn else "Querying canonical statutes and Supreme Court precedents...",
                "status": "running"
            }
        }
        try:
            pack = await self.builder.build(query=query, persona=persona, route=route)
        except Exception as exc:
            yield {
                "event": "complete",
                "data": {
                    "status": "abstain",
                    "answer": "জাসটর যাচাইকৃত আইনি তথ্যসূত্র সংগ্রহ করতে পারেনি।" if is_bn else "Justor could not build a verified legal evidence set.",
                    "reason": "EVIDENCE_BUILD_FAILURE",
                    "debug": str(exc)
                }
            }
            return

        if not pack.authorities:
            yield {
                "event": "complete",
                "data": {
                    "status": "abstain",
                    "answer": "জাসটরের বর্তমান যাচাইকৃত ডাটাবেজে এই নির্দিষ্ট আইনি বিধান বা নজির পাওয়া যায়নি।" if is_bn else "Justor could not verify the controlling legal authority from its current primary-source database.",
                    "reason": "NO_VERIFIED_EVIDENCE"
                }
            }
            return

        auth_cards = self._authority_cards(pack)
        yield {
            "event": "step",
            "data": {
                "step": 2,
                "title": "মূল বিধিবদ্ধ আইন ও নজির অনুসন্ধান" if is_bn else "Primary Authority Retrieval",
                "summary": f"{len(pack.authorities)}টি অফিসিয়াল আইনি ধারা ও রায় সংগৃহীত হয়েছে।" if is_bn else f"Retrieved {len(pack.authorities)} verified provisions with official citations.",
                "status": "completed"
            }
        }
        yield {"event": "authorities", "data": auth_cards}

        # 3. First generation & validation
        yield {
            "event": "step",
            "data": {
                "step": 3,
                "title": "ধারা ও নজিরের যথার্থতা যাচাই" if is_bn else "Rule & Citation Verification",
                "summary": "বিধিবদ্ধ আইনের উদ্ধৃতি, সময়সীমা ও নজিরের বৈধতা যাচাই চলছে..." if is_bn else "Verifying statutory quotations, numeric tokens, and 7-gate invariants...",
                "status": "running"
            }
        }
        try:
            draft = await self._generate(pack, language=effective_lang)
        except Exception as exc:
            yield {
                "event": "complete",
                "data": {
                    "status": "abstain",
                    "answer": "প্রাসঙ্গিক আইন পাওয়া গেছে, কিন্তু উত্তর তৈরিতে সমস্যা হয়েছে।" if is_bn else "Justor found relevant law, but generation failed.",
                    "reason": "GENERATION_FAILURE",
                    "authorities": auth_cards,
                    "reasoning_steps": self._build_reasoning_steps(route, pack, "abstain", language=effective_lang),
                    "debug": str(exc)
                }
            }
            return

        validation = validate_draft(draft, pack)
        if validation.passed:
            yield {
                "event": "step",
                "data": {
                    "step": 3,
                    "title": "ধারা ও নজিরের যথার্থতা যাচাই" if is_bn else "Rule & Citation Verification",
                    "summary": "১০০% অফিসিয়াল প্রাথমিক আইনের সাথে যাচাই সম্পন্ন।" if is_bn else "100% verified against primary statute text and temporal validity.",
                    "status": "passed"
                }
            }
            final_res = self._success(draft, pack, route, language=effective_lang)
            yield {
                "event": "step",
                "data": {
                    "step": 4,
                    "title": "আইনি বিশ্লেষণ ও মতামত প্রণয়ন" if is_bn else "Grounded Legal Synthesis",
                    "summary": "যাচাইকৃত উৎসের ভিত্তিতে পূর্ণাঙ্গ বিশ্লেষণ প্রস্তুত।" if is_bn else "Generated structured legal analysis anchored strictly to primary sources.",
                    "status": "completed"
                }
            }
            yield {"event": "complete", "data": final_res}
            return

        # Critic and retry
        critic_result = await self.critic.audit(draft, pack)
        missing = await self._verify_missing_authorities(critic_result, pack)
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
            yield {
                "event": "step",
                "data": {
                    "step": 3,
                    "title": "ধারা ও নজিরের যথার্থতা যাচাই" if is_bn else "Rule & Citation Verification",
                    "summary": "দ্বিতীয় পর্যায়ের নিরীক্ষায় যাচাই সফল হয়েছে।" if is_bn else "Audit passed following secondary critic review.",
                    "status": "passed"
                }
            }
            final_res = self._success(draft, pack, route, language=effective_lang)
            yield {
                "event": "step",
                "data": {
                    "step": 4,
                    "title": "আইনি বিশ্লেষণ ও মতামত প্রণয়ন" if is_bn else "Grounded Legal Synthesis",
                    "summary": "যাচাইকৃত উৎসের ভিত্তিতে পূর্ণাঙ্গ বিশ্লেষণ প্রস্তুত।" if is_bn else "Generated structured legal analysis anchored strictly to primary sources.",
                    "status": "completed"
                }
            }
            yield {"event": "complete", "data": final_res}
            return

        # Controlled regeneration
        feedback = json.dumps({
            "deterministic_errors": [e.model_dump() for e in validation.errors],
            "critic_errors": critic_result.get("errors", [])
        }, ensure_ascii=False)

        try:
            second_draft = await self._generate(pack, language=effective_lang, correction_feedback=feedback)
        except Exception:
            second_draft = None

        if second_draft is not None:
            second_validation = validate_draft(second_draft, pack)
            if second_validation.passed:
                second_critic = await self.critic.audit(second_draft, pack)
                if bool(second_critic.get("pass", False)):
                    yield {
                        "event": "step",
                        "data": {
                            "step": 3,
                            "title": "ধারা ও নজিরের যথার্থতা যাচাই" if is_bn else "Rule & Citation Verification",
                            "summary": "সংশোধিত খসড়া যাচাইকরণে উত্তীর্ণ হয়েছে।" if is_bn else "Verified following guided regeneration.",
                            "status": "passed"
                        }
                    }
                    final_res = self._success(second_draft, pack, route, language=effective_lang)
                    yield {
                        "event": "step",
                        "data": {
                            "step": 4,
                            "title": "আইনি বিশ্লেষণ ও মতামত প্রণয়ন" if is_bn else "Grounded Legal Synthesis",
                            "summary": "যাচাইকৃত উৎসের ভিত্তিতে পূর্ণাঙ্গ বিশ্লেষণ প্রস্তুত।" if is_bn else "Generated structured legal analysis anchored strictly to primary sources.",
                            "status": "completed"
                        }
                    }
                    yield {"event": "complete", "data": final_res}
                    return

        # Fail closed
        yield {
            "event": "step",
            "data": {
                "step": 3,
                "title": "ধারা ও নজিরের যথার্থতা যাচাই" if is_bn else "Rule & Citation Verification",
                "summary": "খসড়াটি ১০০% কঠোর যাচাইকরণ মানদণ্ড পূরণ করেনি।" if is_bn else "Draft did not satisfy 100% strict verification criteria. Abstaining.",
                "status": "failed_closed"
            }
        }
        abstain_res = {
            "status": "abstain",
            "answer": (
                "জাসটর প্রাসঙ্গিক আইন শনাক্ত করেছে, কিন্তু উৎপন্ন বিশ্লেষণ প্রমাণ যাচাইকরণ পরীক্ষায় উত্তীর্ণ হতে পারেনি। অনুগ্রহ করে সরাসরি মূল আইন ও নথিপত্র পর্যালোচনা করুন।"
                if is_bn else
                (
                    "Justor identified potentially relevant law, but the generated "
                    "analysis did not pass its evidence-checked legal verification gates. "
                    "Please review the primary authorities directly."
                )
            ),
            "reason": "LEGAL_VERIFICATION_FAILED",
            "authorities": self._authority_cards(pack),
            "reasoning_steps": self._build_reasoning_steps(route, pack, "abstain", language=effective_lang),
        }
        yield {
            "event": "step",
            "data": {
                "step": 4,
                "title": "আইনি বিশ্লেষণ ও মতামত প্রণয়ন" if is_bn else "Grounded Legal Synthesis",
                "summary": "যাচাইকরণ বিধিনিষেধের কারণে মতামত বিরত রাখা হয়েছে।" if is_bn else "Abstained due to verification constraints.",
                "status": "abstained"
            }
        }
        yield {"event": "complete", "data": abstain_res}
