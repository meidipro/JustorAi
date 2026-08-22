#!/usr/bin/env python3
"""
scripts/test_tlre_resolution.py
Validates TLRE resolution across core litigation provisions.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from backend.backend import resolve_provision_text

test_queries = [
    ("The Negotiable Instruments Act, 1881", "138"),
    ("CPC", "Order XXXIX Rule 1"),
    ("Specific Relief Act", "21A"),
    ("Registration Act", "17A"),
    ("CrPC", "54"),
    ("Constitution", "111"),
]

passed = 0
for act, sec in test_queries:
    r = resolve_provision_text(act, sec)
    if r:
        passed += 1
        name = r.get("short_title") or r.get("act_title")
        heading = r.get("heading") or ""
        status = r.get("verification_status")
        print(f"  ✓ {name} {r.get('section')} — {heading} [{status}]")
    else:
        print(f"  ❌ FAILED: {act} {sec}")

print(f"\nTLRE Resolution Test: {passed}/{len(test_queries)} passed.")
if passed == len(test_queries):
    print("✅ All TLRE statutory resolutions verified successfully!")
