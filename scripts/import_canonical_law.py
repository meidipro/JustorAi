from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from dotenv import load_dotenv
load_dotenv('.env')
from supabase import create_client
from backend.legal_normalize import normalize_act_alias, source_hash

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY", "")).strip()

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ ERROR: VITE_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
    sys.exit(1)

db = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def upsert_instrument(payload: dict) -> str:
    instrument = payload["instrument"]

    response = (
        db.table("legal_instruments")
        .upsert(
            {
                "canonical_title": instrument["canonical_title"],
                "short_title": instrument.get("short_title"),
                "instrument_type": instrument.get(
                    "instrument_type", "principal_act"
                ),
                "act_number": instrument.get("act_number"),
                "year": instrument.get("year"),
                "jurisdiction": "Bangladesh",
                "effective_from": instrument.get("effective_from"),
                "status": instrument.get("status", "active"),
                "official_url": instrument.get("official_url"),
                "official_source_verified": True,
            },
            on_conflict="canonical_title",
        )
        .select("id")
        .execute()
    )

    instrument_id = response.data[0]["id"]

    aliases = {
        instrument["canonical_title"],
        instrument.get("short_title"),
    }

    for alias in aliases:
        if not alias:
            continue
        (
            db.table("legal_instrument_aliases")
            .upsert(
                {
                    "instrument_id": instrument_id,
                    "alias": alias,
                    "normalized_alias": normalize_act_alias(alias),
                },
                on_conflict="normalized_alias",
            )
            .execute()
        )

    return instrument_id


def import_provision(
    instrument_id: str,
    instrument: dict,
    provision: dict,
):
    section = provision["section_number"]
    canonical_key = (
        f"{normalize_act_alias(instrument['canonical_title'])}:"
        f"s{section.lower()}"
    )

    provision_response = (
        db.table("legal_provisions")
        .upsert(
            {
                "instrument_id": instrument_id,
                "section_number": section.upper(),
                "heading": provision.get("heading"),
                "canonical_key": canonical_key,
            },
            on_conflict="canonical_key",
        )
        .select("id")
        .execute()
    )

    provision_id = provision_response.data[0]["id"]
    text = provision["text"]
    digest = source_hash(text)

    current_response = (
        db.table("provision_versions")
        .select("id,source_hash")
        .eq("provision_id", provision_id)
        .eq("is_current", True)
        .limit(1)
        .execute()
    )

    if current_response.data:
        current = current_response.data[0]

        if current["source_hash"] == digest:
            print(f"UNCHANGED §{section}")
            return

        # Changed official text enters review queue.
        (
            db.table("provision_version_candidates")
            .insert(
                {
                    "provision_id": provision_id,
                    "proposed_text": text,
                    "proposed_valid_from": (
                        provision.get("effective_from")
                        or date.today().isoformat()
                    ),
                    "official_url": provision.get("official_url"),
                    "source_hash": digest,
                    "review_status": "PENDING",
                }
            )
            .execute()
        )
        print(f"CHANGE DETECTED §{section} → staged for review")
        return

    # Initial canonical import.
    (
        db.table("provision_versions")
        .insert(
            {
                "provision_id": provision_id,
                "version_number": 1,
                "legal_text": text,
                "valid_from": (
                    provision.get("effective_from")
                    or instrument.get("effective_from")
                    or "1900-01-01"
                ),
                "is_current": True,
                "status": "active",
                "official_url": provision.get("official_url"),
                "source_hash": digest,
                "official_source_verified": True,
                "verified_by": "canonical-import",
            }
        )
        .execute()
    )
    print(f"IMPORTED §{section}")


def main(path: str):
    with open(path, "r", encoding="utf-8") as file:
        payload = json.load(file)

    instrument_id = upsert_instrument(payload)
    instrument = payload["instrument"]

    for provision in payload["provisions"]:
        import_provision(instrument_id, instrument, provision)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    args = parser.parse_args()
    main(args.file)
