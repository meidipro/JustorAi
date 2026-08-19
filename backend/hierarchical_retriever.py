"""
Justor AI — Hierarchical Act -> Section Legal RAG Orchestrator
Implements two-stage multilingual retrieval:
Stage 1: Act-level candidate filtering to prevent cross-statute pollution.
Stage 2: Constrained Section-level search within candidate Act IDs.
Combines exact citation matching, BGE-M3 dense embeddings, Postgres Full-Text Search, and RRF.
"""

from __future__ import annotations
from datetime import date
from typing import Dict, List, Optional, Any, Callable
from .legal_models import EvidenceItem, LegalRoute
from .legal_repository import LegalRepository
from .legal_dictionary import expand_query_with_dictionary, normalize_bengali_text


# ─── Repeal & Replacement Event Graph ─────────────────────────────────────────
REPEAL_REPLACEMENT_GRAPH: dict[str, dict] = {
    "the family courts ordinance, 1985": {
        "repealed_by": "Family Courts Act, 2023",
        "act_number": "Act No. 26 of 2023",
        "repeal_date": "2023-09-18",
        "status": "REPEALED",
        "canonical_active_act": "Family Courts Act, 2023",
        "warning_banner": "The Family Courts Ordinance, 1985 was repealed and replaced by the Family Courts Act, 2023 (Act No. 26 of 2023)."
    },
    "the income-tax ordinance, 1984": {
        "repealed_by": "Income Tax Act, 2023",
        "act_number": "Act No. 12 of 2023",
        "repeal_date": "2023-06-22",
        "status": "REPEALED",
        "canonical_active_act": "Income Tax Act, 2023",
        "warning_banner": "The Income-tax Ordinance, 1984 was repealed and replaced by the Income Tax Act, 2023 (Act No. 12 of 2023)."
    }
}


class HierarchicalRetriever:
    """Orchestrates two-stage Act -> Section hierarchical legal retrieval."""

    def __init__(self, repository: LegalRepository, embed_fn: Callable):
        self.repository = repository
        self.embed_fn = embed_fn

    def resolve_repeal_replacement(self, act_name: str, query_date: date) -> dict:
        """
        Checks whether the queried Act has been repealed/replaced by a newer statute
        as of the query date.
        """
        clean_act = act_name.lower().strip()
        record = REPEAL_REPLACEMENT_GRAPH.get(clean_act)
        if not record:
            return {"is_repealed": False, "controlling_act": act_name, "warning": None}

        repeal_dt = date.fromisoformat(record["repeal_date"])
        if query_date >= repeal_dt:
            return {
                "is_repealed": True,
                "original_act": act_name,
                "controlling_act": record["canonical_active_act"],
                "repealed_by": record["repealed_by"],
                "act_number": record["act_number"],
                "warning": record["warning_banner"]
            }

        return {"is_repealed": False, "controlling_act": act_name, "warning": None}

    async def retrieve_hierarchical_sections(
        self,
        query: str,
        candidate_acts: list[str],
        query_date: date,
        limit_per_act: int = 5,
    ) -> list[EvidenceItem]:
        """
        Stage 2: Constrained Section Search within the selected candidate Acts.
        Prevents provisions from unrelated statutes from mixing together.
        """
        if not candidate_acts:
            return []

        try:
            embedding = await self.embed_fn(query)
        except Exception:
            embedding = []

        found_items: list[EvidenceItem] = []
        seen_versions: set[str] = set()
        seen_keys: set[str] = set()

        for act_name in candidate_acts[:3]:
            # Check repeal status for current query date
            repeal_info = self.resolve_repeal_replacement(act_name, query_date)
            target_act = repeal_info["controlling_act"]

            instrument = await self.repository.resolve_instrument(target_act)
            if not instrument:
                # Fallback to original act name if target not directly aliased
                instrument = await self.repository.resolve_instrument(act_name)

            if instrument and embedding:
                results = await self.repository.hybrid_search(
                    query=query,
                    embedding=embedding,
                    query_date=query_date,
                    instrument_id=instrument["id"],
                    match_count=limit_per_act,
                )

                for row in results:
                    version_id = str(row.get("provision_version_id", ""))
                    key = f"{row.get('act_name')}:{row.get('section_number')}"
                    if version_id in seen_versions or key in seen_keys:
                        continue

                    is_official = bool(row.get("official_source_verified", False))
                    found_items.append(
                        EvidenceItem(
                            evidence_id="",
                            instrument_id=str(row.get("instrument_id", "")),
                            provision_id=str(row.get("provision_id", "")),
                            version_id=version_id,
                            act_name=row.get("act_name", target_act),
                            section_number=str(row.get("section_number", "")),
                            heading=row.get("heading"),
                            role="SUPPORTING",
                            legal_text=row.get("legal_text", ""),
                            official_url=row.get("official_url"),
                            current_for_query_date=True,
                            official_source_verified=is_official,
                            exact_section_verified=True,
                            version_verified=True,
                            trust_tier="PRIMARY_STATUTE" if is_official else "UNVERIFIED",
                        )
                    )
                    seen_versions.add(version_id)
                    seen_keys.add(key)

        return found_items
