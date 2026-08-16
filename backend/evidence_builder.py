from __future__ import annotations

from datetime import date
from .legal_models import EvidencePack, EvidenceItem, LegalRoute
from .legal_repository import LegalRepository


class EvidenceBuilder:
    def __init__(self, repository: LegalRepository, embed_fn):
        self.repository = repository
        self.embed_fn = embed_fn

    async def build(
        self,
        query: str,
        persona: str,
        route: LegalRoute,
    ) -> EvidencePack:
        query_date = route.as_of_date or date.today()
        found: list[EvidenceItem] = []
        seen_versions: set[str] = set()

        # 1. Exact candidate retrieval first.
        for authority in route.authorities:
            instrument = await self.repository.resolve_instrument(authority.act)
            if instrument:
                for section in authority.sections:
                    evidence = await self.repository.resolve_exact_section(
                        instrument_id=instrument["id"],
                        section_number=section,
                        query_date=query_date,
                    )
                    if not evidence or evidence.version_id in seen_versions:
                        continue
                    evidence.role = authority.role
                    found.append(evidence)
                    seen_versions.add(evidence.version_id)
            else:
                # Fallback to document_chunks
                for section in authority.sections:
                    evidence = await self.repository.resolve_from_chunks_fallback(
                        act_name=authority.act,
                        section_number=section,
                    )
                    if not evidence:
                        continue
                    evidence.role = authority.role
                    found.append(evidence)

        # 2. Hybrid discovery for supporting law (only if exact matches need supplementation)
        if len(found) < 2:
            try:
                embedding = await self.embed_fn(query)
            except Exception:
                embedding = []
        else:
            embedding = []

        if embedding:
            for authority in route.authorities:
                instrument = await self.repository.resolve_instrument(authority.act)
                if not instrument:
                    continue

                results = await self.repository.hybrid_search(
                    query=query,
                    embedding=embedding,
                    query_date=query_date,
                    instrument_id=instrument["id"],
                    match_count=6,
                )

                for row in results:
                    version_id = str(row["provision_version_id"])
                    if version_id in seen_versions:
                        continue

                    found.append(
                        EvidenceItem(
                            evidence_id="",
                            instrument_id=str(row["instrument_id"]),
                            provision_id=str(row["provision_id"]),
                            version_id=version_id,
                            act_name=row["act_name"],
                            section_number=row["section_number"],
                            heading=row.get("heading"),
                            role="SUPPORTING",
                            legal_text=row["legal_text"],
                            official_url=row.get("official_url"),
                            current_for_query_date=True,
                            official_source_verified=True,
                            exact_section_verified=True,
                            version_verified=True,
                        )
                    )
                    seen_versions.add(version_id)

        # 3. Special-over-general relationships.
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

        # 4. Search relevant case law / precedents for Lawyer and Student modes
        cases_found: list[EvidenceItem] = []
        is_legal_persona = any(
            p in persona.lower()
            for p in ["lawyer", "legal professional", "student"]
        )
        if route.needs_case_law or is_legal_persona:
            cand_acts = [a.act for a in route.authorities]
            cases_found = await self.repository.search_case_law(
                query=query,
                candidate_acts=cand_acts,
                limit=2,
            )

        rank = {
            "CONTROLLING": 0,
            "SUPPORTING": 1,
            "GENERAL": 2,
            "BACKGROUND": 3,
        }
        found.sort(key=lambda x: rank.get(x.role, 1))

        # Backend, not LLM, creates collision-free evidence IDs.
        act_idx = 1
        for evidence in found:
            evidence.item_type = "statute"
            evidence.evidence_id = f"ACT-{act_idx}"
            act_idx += 1

        dlr_idx = 1
        for case in cases_found:
            case.evidence_id = f"DLR-{dlr_idx}"
            dlr_idx += 1

        all_authorities = found + cases_found

        return EvidencePack(
            query=query,
            persona=persona,
            as_of_date=query_date,
            temporal_mode=route.temporal_mode,
            issues=route.issues,
            authorities=all_authorities,
        )
