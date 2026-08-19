from __future__ import annotations

from datetime import date
from .legal_models import EvidencePack, EvidenceItem, LegalRoute
from .legal_repository import LegalRepository
from .legal_dictionary import expand_query_with_dictionary, normalize_bengali_text
from .legal_relevance import PreGenerationRelevanceGate


from .hierarchical_retriever import HierarchicalRetriever, REPEAL_REPLACEMENT_GRAPH


class EvidenceBuilder:
    def __init__(self, repository: LegalRepository, embed_fn):
        self.repository = repository
        self.embed_fn = embed_fn
        self.hierarchical_retriever = HierarchicalRetriever(repository=repository, embed_fn=embed_fn)

    async def build(
        self,
        query: str,
        persona: str,
        route: LegalRoute,
    ) -> EvidencePack:
        query_date = route.as_of_date or date.today()
        found: list[EvidenceItem] = []
        seen_versions: set[str] = set()
        seen_keys: set[str] = set()

        # ── 1. Bilingual Dictionary & Query Expansion ──
        dict_expansion = expand_query_with_dictionary(query)
        detected_domain = dict_expansion.get("domains", ["General"])[0] if dict_expansion.get("domains") else route.legal_domain

        # Combine router authorities with dictionary candidate Acts
        candidate_acts: list[str] = [a.act for a in route.authorities]
        for d_act in dict_expansion.get("candidate_acts", []):
            if d_act not in candidate_acts:
                candidate_acts.append(d_act)

        # ── 2. Exact Candidate Provision Resolution (Act -> Section Hierarchy) ──
        # Process explicit router authority sections
        for authority in route.authorities:
            # Check repeal status for current query date
            repeal_info = self.hierarchical_retriever.resolve_repeal_replacement(authority.act, query_date)
            target_act = repeal_info["controlling_act"]

            instrument = await self.repository.resolve_instrument(target_act) or await self.repository.resolve_instrument(authority.act)
            for section in authority.sections:
                evidence = None
                if instrument:
                    evidence = await self.repository.resolve_exact_section(
                        instrument_id=instrument["id"],
                        section_number=section,
                        query_date=query_date,
                    )
                if not evidence:
                    evidence = await self.repository.resolve_from_chunks_fallback(
                        act_name=target_act,
                        section_number=section,
                    ) or await self.repository.resolve_from_chunks_fallback(
                        act_name=authority.act,
                        section_number=section,
                    )
                if not evidence or evidence.version_id in seen_versions:
                    continue
                key = f"{evidence.act_name}:{evidence.section_number}"
                if key in seen_keys:
                    continue
                evidence.role = authority.role
                found.append(evidence)
                seen_versions.add(evidence.version_id)
                seen_keys.add(key)

        # Process dictionary suggested sections if not already retrieved
        act_sections_map = dict_expansion.get("act_to_sections", {})
        for act_name in candidate_acts:
            for sec_cand in act_sections_map.get(act_name, []):
                key = f"{act_name}:{sec_cand}"
                if key in seen_keys:
                    continue
                repeal_info = self.hierarchical_retriever.resolve_repeal_replacement(act_name, query_date)
                target_act = repeal_info["controlling_act"]

                instrument = await self.repository.resolve_instrument(target_act) or await self.repository.resolve_instrument(act_name)
                evidence = None
                if instrument:
                    evidence = await self.repository.resolve_exact_section(
                        instrument_id=instrument["id"],
                        section_number=sec_cand,
                        query_date=query_date,
                    )
                if not evidence:
                    evidence = await self.repository.resolve_from_chunks_fallback(
                        act_name=target_act,
                        section_number=sec_cand,
                    )
                if evidence and evidence.version_id not in seen_versions:
                    evidence.role = "SUPPORTING"
                    found.append(evidence)
                    seen_versions.add(evidence.version_id)
                    seen_keys.add(key)

        # ── 3. Hierarchical Hybrid Section Discovery (Inside Candidate Acts) ──
        if len(found) < 2:
            hierarchical_items = await self.hierarchical_retriever.retrieve_hierarchical_sections(
                query=dict_expansion.get("normalized_query", query),
                candidate_acts=candidate_acts,
                query_date=query_date,
                limit_per_act=5,
            )
            for item in hierarchical_items:
                key = f"{item.act_name}:{item.section_number}"
                if item.version_id not in seen_versions and key not in seen_keys:
                    found.append(item)
                    seen_versions.add(item.version_id)
                    seen_keys.add(key)

        # ── 4. Pre-Generation Relevance Gate (3-Tier Filtering) ──
        found = PreGenerationRelevanceGate.filter_evidence_items(
            items=found,
            query=query,
            detected_domain=detected_domain,
            allowed_acts=candidate_acts,
        )

        # ── 5. Special-Over-General Statutory Relationship Graph ──
        if found:
            relationships = await self.repository.get_relationships(
                [x.provision_id for x in found if x.provision_id]
            )

            special_ids = {
                row["source_provision_id"]
                for row in relationships
                if row["relationship_type"] == "SPECIAL_OVER_GENERAL"
            }
            general_ids = {
                row["target_provision_id"]
                for row in relationships
                if row["relationship_type"] == "SPECIAL_OVER_GENERAL"
            }

            for evidence in found:
                if evidence.provision_id in special_ids:
                    evidence.role = "CONTROLLING"
                elif evidence.provision_id in general_ids:
                    evidence.role = "GENERAL"

        # ── 6. Domain-Aligned Case Law / Precedent Retrieval ──
        cases_found: list[EvidenceItem] = []
        q_lower = query.lower()
        has_case_query_intent = any(
            kw in q_lower
            for kw in ["case", "precedent", "judgment", "ruling", "dlr", "ratio", "decision", "versus", "vs.", "vs", "রায়"]
        )
        if (route.needs_case_law or has_case_query_intent) and len(found) > 0:
            cases_found = await self.repository.search_case_law(
                query=query,
                candidate_acts=candidate_acts,
                limit=2,
            )

        rank = {
            "CONTROLLING": 0,
            "SUPPORTING": 1,
            "GENERAL": 2,
            "BACKGROUND": 3,
        }
        found.sort(key=lambda x: rank.get(x.role, 4))

        # Assign unique evidence tags: [ACT-1], [ACT-2], [DLR-1]
        all_items: list[EvidenceItem] = []
        for index, item in enumerate(found, start=1):
            item.evidence_id = f"ACT-{index}"
            item.item_type = "statute"
            all_items.append(item)

        for index, case_item in enumerate(cases_found, start=1):
            case_item.evidence_id = f"DLR-{index}"
            case_item.item_type = "case"
            case_item.role = "SUPPORTING"
            all_items.append(case_item)

        return EvidencePack(
            query=query,
            persona=persona,
            as_of_date=query_date,
            temporal_mode=route.temporal_mode,
            issues=route.issues,
            authorities=all_items,
        )
