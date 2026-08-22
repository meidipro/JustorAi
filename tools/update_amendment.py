#!/usr/bin/env python3
"""
tools/update_amendment.py
Justor TLRE — Manual Amendment Management CLI

Matches Justor Legal Evidence V2 Schema (Project 1: Statutes):
  - legal_instruments (canonical_title, short_title, year, status, official_source_verified)
  - legal_provisions (instrument_id, section_number, heading, canonical_key)
  - provision_versions (provision_id, version_number, legal_text, valid_from, valid_to, is_current, status, official_source_verified, verified_by)
  - amendment_events (amending_instrument_id, target_provision_id, operation, effective_from, old_text, new_text, verified_by)

Usage:
  python tools/update_amendment.py list-acts
  python tools/update_amendment.py list-pending
  python tools/update_amendment.py add
  python tools/update_amendment.py verify <amendment_id>
  python tools/update_amendment.py coverage
  python tools/update_amendment.py add-provision
"""

import os
import sys
import uuid
import hashlib
from datetime import date, datetime
from dotenv import load_dotenv
from supabase import create_client, Client

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

# ── Auth ──────────────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in your environment.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

OPERATIONS = ["SUBSTITUTE", "OMIT", "INSERT", "REPEAL", "ADD_PROVISO", "RENUMBER", "OTHER"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def divider():
    print("\n" + "─" * 72 + "\n")

def prompt(label: str, required: bool = True) -> str:
    while True:
        val = input(f"  {label}: ").strip()
        if val or not required:
            return val
        print("  [required — please enter a value]")

def prompt_date(label: str, required: bool = True) -> str | None:
    while True:
        val = input(f"  {label} (YYYY-MM-DD): ").strip()
        if not val and not required:
            return None
        try:
            date.fromisoformat(val)
            return val
        except ValueError:
            print("  [invalid date — use YYYY-MM-DD format]")

def prompt_choice(label: str, choices: list[str]) -> str:
    print(f"  {label}:")
    for i, c in enumerate(choices, 1):
        print(f"    {i}. {c}")
    while True:
        val = input("  Enter number: ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        print("  [invalid choice]")

def prompt_multiline(label: str) -> str:
    print(f"  {label} (type END on a new line when done):")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)

def sha256_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_list_acts():
    """List all Acts in the legal_instruments table."""
    res = supabase.table("legal_instruments").select("id, canonical_title, short_title, status, year, official_source_verified").order("year").execute()
    divider()
    print(f"{'ID (first 8)':<12} {'Year':<6} {'Short':<12} {'Canonical Title':<50} {'Status'}")
    print("-" * 92)
    for row in res.data:
        short = row.get("short_title") or ""
        yr = str(row.get("year") or "")
        v_mark = "✓" if row.get("official_source_verified") else ""
        print(f"{row['id'][:8]:<12} {yr:<6} {short:<12} {row['canonical_title'][:48]:<50} {row['status']} {v_mark}")
    divider()
    print(f"Total Acts: {len(res.data)}")
    divider()


def cmd_list_pending():
    """Show all amendment_events that are draft / awaiting verification."""
    res = (
        supabase.table("amendment_events")
        .select("id, operation, effective_from, gazette_number, created_at, target_provision_id, official_gazette_verified")
        .order("created_at")
        .execute()
    )
    divider()
    pending = [r for r in res.data if not r.get("official_gazette_verified")]
    if not pending:
        print("No pending amendments. Everything in TLRE is verified.")
        divider()
        return

    print(f"{'ID (first 8)':<12} {'Operation':<14} {'Effective':<12} {'Gazette Ref'}")
    print("-" * 72)
    for row in pending:
        print(
            f"{row['id'][:8]:<12} "
            f"{row['operation']:<14} "
            f"{str(row.get('effective_from', '')):<12} "
            f"{row.get('gazette_number', '') or ''}"
        )
    divider()
    print(f"Total pending verification: {len(pending)}")
    divider()


def cmd_add():
    """Interactive form to add a new amendment event (saved as DRAFT)."""
    divider()
    print("ADD NEW AMENDMENT — saved for two-person human verification protocol.\n")

    # Select Act
    acts = supabase.table("legal_instruments").select("id, canonical_title, short_title").order("canonical_title").execute()
    print("  Available Acts:")
    for i, a in enumerate(acts.data, 1):
        print(f"    {i:>2}. {a['canonical_title']}")
    while True:
        val = input("  Select Act (number): ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(acts.data):
                act = acts.data[idx]
                break
        except ValueError:
            pass
        print("  [invalid]")

    # Select or create provision
    provisions = (
        supabase.table("legal_provisions")
        .select("id, section_number, heading, canonical_key")
        .eq("instrument_id", act["id"])
        .order("section_number")
        .execute()
    )
    print(f"\n  Provisions in {act.get('short_title') or act['canonical_title']}:")
    for i, p in enumerate(provisions.data, 1):
        heading = f" — {p['heading']}" if p.get("heading") else ""
        print(f"    {i:>2}. Section/Ref {p['section_number']}{heading}")
    print(f"    {len(provisions.data)+1:>2}. [Add new provision]")

    while True:
        val = input("  Select provision (number): ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(provisions.data):
                provision = provisions.data[idx]
                break
            elif idx == len(provisions.data):
                provision = None
                break
        except ValueError:
            pass
        print("  [invalid]")

    if provision is None:
        # Create new provision
        print("\n  Creating new legal_provision:")
        pref = prompt("Section / Provision number (e.g. '138' or 'Order XXXIX Rule 1')")
        heading = prompt("Heading (e.g. 'Dishonour of Cheque')", required=False)
        canon_key = f"{act['id']}_{pref}".replace(" ", "_")
        new_prov = supabase.table("legal_provisions").insert({
            "instrument_id": act["id"],
            "section_number": pref,
            "heading": heading or None,
            "canonical_key": canon_key
        }).execute()
        provision = new_prov.data[0]
        print(f"  Created provision: {provision['section_number']} (ID: {provision['id'][:8]})")

    # Operation type
    print()
    operation = prompt_choice("Operation type", OPERATIONS)

    # Old text
    print()
    if operation in ["SUBSTITUTE", "OMIT", "REPEAL"]:
        print("  OLD TEXT (the provision text BEFORE this amendment):")
        old_text = prompt_multiline("Paste old text")
    else:
        old_text = None

    # New text
    if operation in ["SUBSTITUTE", "INSERT", "ADD_PROVISO", "RENUMBER"]:
        print("\n  NEW TEXT (the provision text AFTER this amendment):")
        new_text = prompt_multiline("Paste new text")
    else:
        new_text = None

    # Dates
    print()
    effective_date = prompt_date("Effective date (when this takes legal effect)", required=True)
    gazette_ref = prompt("Gazette reference (e.g. 'Bangladesh Gazette Ext., 15 Mar 2026, p.4')", required=False)
    notes = prompt("Reviewer notes (optional)", required=False)

    # Confirm
    divider()
    print("SUMMARY — please confirm before saving:")
    print(f"  Act:          {act['canonical_title']}")
    print(f"  Provision:    {provision['section_number']}")
    print(f"  Operation:    {operation}")
    print(f"  Effective:    {effective_date}")
    print(f"  Gazette ref:  {gazette_ref or '(not entered)'}")
    if old_text:
        print(f"  Old text:     {old_text[:80]}{'...' if len(old_text)>80 else ''}")
    if new_text:
        print(f"  New text:     {new_text[:80]}{'...' if len(new_text)>80 else ''}")

    confirm = input("\n  Save as DRAFT? [y/n]: ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    # Insert amendment_event
    supabase.table("amendment_events").insert({
        "amending_instrument_id": act["id"],
        "target_provision_id": provision["id"],
        "operation": operation,
        "old_text": old_text,
        "new_text": new_text,
        "effective_from": effective_date,
        "gazette_number": gazette_ref or None,
        "explanation": notes or None,
        "official_gazette_verified": False
    }).execute()

    divider()
    print("  ✓ Amendment saved as DRAFT.")
    print("  A second reviewer must run `python tools/update_amendment.py verify <id>` to publish it.")
    divider()


def cmd_verify(amendment_id_prefix: str):
    """Show a draft amendment in full and allow the reviewer to mark it VERIFIED."""
    res = (
        supabase.table("amendment_events")
        .select("*, legal_provisions(section_number, instrument_id, legal_instruments(canonical_title))")
        .ilike("id", f"{amendment_id_prefix}%")
        .execute()
    )

    if not res.data:
        print(f"ERROR: No amendment found with ID starting with '{amendment_id_prefix}'.")
        return

    row = res.data[0]
    divider()
    print("VERIFY AMENDMENT")
    print(f"  ID:           {row['id']}")
    print(f"  Operation:    {row['operation']}")
    print(f"  Effective:    {row.get('effective_from')}")
    print(f"  Gazette ref:  {row.get('gazette_number', '(not entered)')}")
    print(f"  Notes:        {row.get('explanation', '(none)')}")
    print(f"  Verified?:    {row.get('official_gazette_verified', False)}")

    if row.get("old_text"):
        print("\n  OLD TEXT:")
        print("  " + row["old_text"].replace("\n", "\n  "))
    if row.get("new_text"):
        print("\n  NEW TEXT:")
        print("  " + row["new_text"].replace("\n", "\n  "))

    divider()
    print("  Have you read the original gazette notification and confirmed this is correct?")
    confirm = input("  Mark as VERIFIED and apply? [y/n]: ").strip().lower()
    if confirm != "y":
        print("  Cancelled. Amendment remains unverified.")
        return

    reviewer = input("  Your email (recorded as verifier): ").strip()

    # Mark amendment as verified
    supabase.table("amendment_events").update({
        "official_gazette_verified": True,
        "verified_by": reviewer,
        "verified_at": datetime.utcnow().isoformat()
    }).eq("id", row["id"]).execute()

    # Apply to provision_versions
    # 1. Close previous version
    prev = (
        supabase.table("provision_versions")
        .select("id, version_number")
        .eq("provision_id", row["target_provision_id"])
        .eq("is_current", True)
        .execute()
    )
    next_ver = 1
    prev_id = None
    if prev.data:
        prev_id = prev.data[0]["id"]
        next_ver = (prev.data[0].get("version_number") or 1) + 1
        supabase.table("provision_versions").update({
            "is_current": False,
            "valid_to": row["effective_from"]
        }).eq("id", prev_id).execute()

    # 2. Insert new version
    if row["operation"] not in ["REPEAL", "OMIT"] and row.get("new_text"):
        txt = row["new_text"]
        supabase.table("provision_versions").insert({
            "provision_id": row["target_provision_id"],
            "version_number": next_ver,
            "legal_text": txt,
            "valid_from": row["effective_from"],
            "valid_to": None,
            "is_current": True,
            "status": "active",
            "created_by_instrument_id": row.get("amending_instrument_id"),
            "supersedes_version_id": prev_id,
            "source_hash": sha256_hash(txt),
            "official_source_verified": True,
            "verified_by": reviewer,
            "verified_at": datetime.utcnow().isoformat()
        }).execute()

    divider()
    print("  ✓ Amendment VERIFIED and applied to provision_versions.")
    print(f"  Effective from: {row.get('effective_from')}")
    print("  The TLRE resolver will now return the updated text for queries on or after this date.")
    divider()


def cmd_coverage():
    """Show which Acts have provisions in the TLRE vs total provisions needed."""
    acts = supabase.table("legal_instruments").select("id, canonical_title, short_title, status").eq("status", "active").execute()
    divider()
    print(f"{'Act':<42} {'Provisions':<12} {'Verified Versions'}")
    print("-" * 74)
    for act in acts.data:
        provs = supabase.table("legal_provisions").select("id").eq("instrument_id", act["id"]).execute()
        prov_ids = [p["id"] for p in provs.data]
        if prov_ids:
            verified = supabase.table("provision_versions").select("id").eq("official_source_verified", True).in_("provision_id", prov_ids).execute()
            v = len(set(r["id"] for r in verified.data))
        else:
            v = 0
        total = len(prov_ids)
        bar = "●" * v + "○" * max(0, total - v) if total <= 20 else f"{v}/{total}"
        name = act.get("short_title") or act["canonical_title"]
        print(f"{name[:40]:<42} {total:<12} {bar}")
    divider()


def cmd_add_provision():
    """Add a provision to an Act (without an amendment event — for initial data entry)."""
    acts = supabase.table("legal_instruments").select("id, canonical_title, short_title").order("canonical_title").execute()
    print("\n  Available Acts:")
    for i, a in enumerate(acts.data, 1):
        print(f"    {i:>2}. {a['canonical_title']}")
    while True:
        val = input("  Select Act (number): ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(acts.data):
                act = acts.data[idx]
                break
        except ValueError:
            pass
        print("  [invalid]")

    divider()
    print(f"  Adding provision to: {act['canonical_title']}\n")
    pref = prompt("Section / Rule number (e.g. '138' or 'Order XXXIX Rule 1')")
    heading = prompt("Heading (e.g. 'Dishonour of Cheque')", required=False)
    print("\n  CURRENT TEXT (as currently in force — type END on new line when done):")
    text = prompt_multiline("Paste text")
    effective = prompt_date("In force from (original commencement date)")
    reviewer = input("  Your email: ").strip()

    confirm = input("  Save? [y/n]: ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    canon_key = f"{act['id']}_{pref}".replace(" ", "_")
    new_prov = supabase.table("legal_provisions").insert({
        "instrument_id": act["id"],
        "section_number": pref,
        "heading": heading or None,
        "canonical_key": canon_key
    }).execute()
    provision = new_prov.data[0]

    # Create initial version
    supabase.table("provision_versions").insert({
        "provision_id": provision["id"],
        "version_number": 1,
        "legal_text": text,
        "valid_from": effective,
        "valid_to": None,
        "is_current": True,
        "status": "active",
        "created_by_instrument_id": act["id"],
        "source_hash": sha256_hash(text),
        "official_source_verified": True,
        "verified_by": reviewer,
        "verified_at": datetime.utcnow().isoformat()
    }).execute()

    divider()
    print(f"  ✓ Provision '{pref}' added and marked VERIFIED.")
    divider()


COMMANDS = {
    "list-acts":      (cmd_list_acts,     "List all Acts in the database"),
    "list-pending":   (cmd_list_pending,  "Show draft amendments awaiting verification"),
    "add":            (cmd_add,           "Add a new amendment (saved as DRAFT)"),
    "verify":         (cmd_verify,        "Verify a DRAFT amendment and apply it (requires amendment ID prefix)"),
    "coverage":       (cmd_coverage,      "Show TLRE coverage by Act"),
    "add-provision":  (cmd_add_provision, "Add a provision + initial text (no amendment event)"),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("\nJustor TLRE — Amendment Management CLI\n")
        print("Usage: python tools/update_amendment.py <command>\n")
        print("Commands:")
        for cmd, (_, desc) in COMMANDS.items():
            print(f"  {cmd:<16} {desc}")
        print()
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "verify":
        if not args:
            print("ERROR: provide the amendment ID prefix. Run list-pending to see IDs.")
            sys.exit(1)
        COMMANDS[cmd][0](args[0])
    else:
        COMMANDS[cmd][0]()
