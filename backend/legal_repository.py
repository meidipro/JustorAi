from __future__ import annotations

import asyncio
from datetime import date
from typing import Any
from supabase import Client

from .legal_models import EvidenceItem
from .legal_normalize import normalize_act_alias, split_section_reference


class LegalRepository:
    def __init__(self, supabase: Client):
        self.db = supabase

    async def _run(self, fn):
        return await asyncio.to_thread(fn)

    async def resolve_instrument(self, act_name: str) -> dict[str, Any] | None:
        normalized = normalize_act_alias(act_name)

        def query():
            return (
                self.db.table("legal_instrument_aliases")
                .select(
                    """
                    instrument_id,
                    legal_instruments(
                        id,
                        canonical_title,
                        status,
                        jurisdiction,
                        official_url,
                        official_source_verified
                    )
                    """
                )
                .eq("normalized_alias", normalized)
                .limit(1)
                .execute()
            )

        try:
            response = await self._run(query)
            if not response.data:
                return None
            return response.data[0].get("legal_instruments")
        except Exception:
            return None

    async def _resolve_provision_record(
        self,
        instrument_id: str,
        section_reference: str,
    ) -> dict[str, Any] | None:
        root, parts = split_section_reference(section_reference)

        # Prefer child/subsection when the canonical store contains it.
        if parts:
            first_subsection = parts[0]

            def child_query():
                return (
                    self.db.table("legal_provisions")
                    .select(
                        """
                        id,
                        section_number,
                        subsection,
                        clause,
                        heading,
                        instrument_id
                        """
                    )
                    .eq("instrument_id", instrument_id)
                    .eq("section_number", root)
                    .eq("subsection", first_subsection)
                    .limit(1)
                    .execute()
                )

            try:
                child_response = await self._run(child_query)
                if child_response.data:
                    return child_response.data[0]
            except Exception:
                pass

        # Fallback to the complete/root section.
        def parent_query():
            return (
                self.db.table("legal_provisions")
                .select(
                    """
                    id,
                    section_number,
                    subsection,
                    clause,
                    heading,
                    instrument_id
                    """
                )
                .eq("instrument_id", instrument_id)
                .eq("section_number", root)
                .is_("subsection", "null")
                .limit(1)
                .execute()
            )

        try:
            parent_response = await self._run(parent_query)
            if not parent_response.data:
                return None
            return parent_response.data[0]
        except Exception:
            return None

    async def resolve_exact_section(
        self,
        instrument_id: str,
        section_number: str,
        query_date: date,
    ) -> EvidenceItem | None:
        provision = await self._resolve_provision_record(
            instrument_id,
            section_number,
        )
        if not provision:
            return None

        provision_id = provision["id"]

        def version_query():
            return (
                self.db.table("provision_versions")
                .select(
                    """
                    id,
                    legal_text,
                    valid_from,
                    valid_to,
                    status,
                    official_url,
                    official_source_verified
                    """
                )
                .eq("provision_id", provision_id)
                .lte("valid_from", query_date.isoformat())
                .or_(
                    "valid_to.is.null,"
                    f"valid_to.gt.{query_date.isoformat()}"
                )
                .eq("status", "active")
                .order("version_number", desc=True)
                .limit(1)
                .execute()
            )

        try:
            version_response = await self._run(version_query)
            if not version_response.data:
                return None
            version = version_response.data[0]

            def instrument_query():
                return (
                    self.db.table("legal_instruments")
                    .select("canonical_title,official_source_verified")
                    .eq("id", instrument_id)
                    .limit(1)
                    .execute()
                )

            instrument_response = await self._run(instrument_query)
            instrument = instrument_response.data[0] if instrument_response.data else {}

            rendered_section = provision["section_number"]
            if provision.get("subsection"):
                rendered_section += f"({provision['subsection']})"

            return EvidenceItem(
                evidence_id="",
                instrument_id=instrument_id,
                provision_id=provision_id,
                version_id=version["id"],
                act_name=instrument.get("canonical_title", ""),
                section_number=rendered_section,
                heading=provision.get("heading"),
                role="SUPPORTING",
                legal_text=version["legal_text"],
                official_url=version.get("official_url"),
                valid_from=version.get("valid_from"),
                valid_to=version.get("valid_to"),
                current_for_query_date=True,
                official_source_verified=bool(
                    version.get("official_source_verified")
                ),
                exact_section_verified=True,
                version_verified=True,
            )
        except Exception:
            return None

    async def hybrid_search(
        self,
        query: str,
        embedding: list[float],
        query_date: date,
        instrument_id: str | None = None,
        match_count: int = 10,
    ) -> list[dict[str, Any]]:
        def rpc():
            return (
                self.db.rpc(
                    "hybrid_search_law_v2",
                    {
                        "p_query_text": query,
                        "p_query_embedding": embedding,
                        "p_query_date": query_date.isoformat(),
                        "p_instrument_id": instrument_id,
                        "p_match_count": match_count,
                    },
                ).execute()
            )

        try:
            response = await self._run(rpc)
            return response.data or []
        except Exception:
            return []

    async def get_relationships(
        self,
        provision_ids: list[str],
    ) -> list[dict[str, Any]]:
        if not provision_ids:
            return []

        def query():
            return (
                self.db.table("provision_relationships")
                .select(
                    """
                    source_provision_id,
                    target_provision_id,
                    relationship_type,
                    explanation,
                    verified
                    """
                )
                .in_("source_provision_id", provision_ids)
                .eq("verified", True)
                .execute()
            )

        try:
            response = await self._run(query)
            return response.data or []
        except Exception:
            return []

    async def provision_exists(
        self,
        act_name: str,
        section_number: str,
        query_date: date,
    ) -> EvidenceItem | None:
        instrument = await self.resolve_instrument(act_name)
        if not instrument:
            return None
        return await self.resolve_exact_section(
            instrument_id=instrument["id"],
            section_number=section_number,
            query_date=query_date,
        )
