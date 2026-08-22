#!/usr/bin/env python3
"""
scripts/seed_top10_acts.py
Seeds Tier 1 & core Bangladesh statutes into legal_instruments & legal_instrument_aliases.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("VITE_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("VITE_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL / KEY missing.")
    sys.exit(1)

db = create_client(SUPABASE_URL, SUPABASE_KEY)

CORE_ACTS = [
    {
        "canonical_title": "The Code of Civil Procedure, 1908",
        "short_title": "CPC",
        "act_number": "V of 1908",
        "year": 1908,
        "instrument_type": "principal_act",
        "effective_from": "1909-01-01",
        "status": "active",
        "aliases": ["CPC", "Code of Civil Procedure", "দেওয়ানী কার্যবিধি", "দেওয়ানী কার্যবিধি", "সিপিসি"]
    },
    {
        "canonical_title": "The Code of Criminal Procedure, 1898",
        "short_title": "CrPC",
        "act_number": "V of 1898",
        "year": 1898,
        "instrument_type": "principal_act",
        "effective_from": "1898-07-01",
        "status": "active",
        "aliases": ["CrPC", "Code of Criminal Procedure", "ফৌজদারি কার্যবিধি", "ফৌজদারী কার্যবিধি", "সিআরপিসি"]
    },
    {
        "canonical_title": "The Negotiable Instruments Act, 1881",
        "short_title": "NI Act",
        "act_number": "XXVI of 1881",
        "year": 1881,
        "instrument_type": "principal_act",
        "effective_from": "1882-03-01",
        "status": "active",
        "aliases": ["NI Act", "Negotiable Instruments Act", "হস্তান্তরযোগ্য দলিল আইন", "এনআই অ্যাক্ট", "এনআই এ্যাক্ট"]
    },
    {
        "canonical_title": "Negotiable Instruments (Amendment) Act, 2026",
        "short_title": "NI Amend 2026",
        "act_number": "I of 2026",
        "year": 2026,
        "instrument_type": "amendment_act",
        "effective_from": "2026-01-01",
        "status": "active",
        "aliases": ["NI Amendment 2026", "এনআই সংশোধনী ২০২৬"]
    },
    {
        "canonical_title": "The Specific Relief Act, 1877",
        "short_title": "SRA",
        "act_number": "I of 1877",
        "year": 1877,
        "instrument_type": "principal_act",
        "effective_from": "1877-05-01",
        "status": "active",
        "aliases": ["SRA", "Specific Relief Act", "সুনির্দিষ্ট প্রতিকার আইন"]
    },
    {
        "canonical_title": "The Contract Act, 1872",
        "short_title": "Contract Act",
        "act_number": "IX of 1872",
        "year": 1872,
        "instrument_type": "principal_act",
        "effective_from": "1872-09-01",
        "status": "active",
        "aliases": ["Contract Act", "চুক্তি আইন"]
    },
    {
        "canonical_title": "The Evidence Act, 1872",
        "short_title": "Evidence Act",
        "act_number": "I of 1872",
        "year": 1872,
        "instrument_type": "principal_act",
        "effective_from": "1872-09-01",
        "status": "active",
        "aliases": ["Evidence Act", "সাক্ষ্য আইন"]
    },
    {
        "canonical_title": "The Penal Code, 1860",
        "short_title": "Penal Code",
        "act_number": "XLV of 1860",
        "year": 1860,
        "instrument_type": "principal_act",
        "effective_from": "1862-01-01",
        "status": "active",
        "aliases": ["Penal Code", "দণ্ডবিধি", "দন্ডবিধি", "দণ্ডবিধি ১৮৬০"]
    },
    {
        "canonical_title": "The Transfer of Property Act, 1882",
        "short_title": "TPA",
        "act_number": "IV of 1882",
        "year": 1882,
        "instrument_type": "principal_act",
        "effective_from": "1882-07-01",
        "status": "active",
        "aliases": ["TPA", "Transfer of Property Act", "সম্পত্তি হস্তান্তর আইন"]
    },
    {
        "canonical_title": "The Registration Act, 1908",
        "short_title": "Registration Act",
        "act_number": "XVI of 1908",
        "year": 1908,
        "instrument_type": "principal_act",
        "effective_from": "1909-01-01",
        "status": "active",
        "aliases": ["Registration Act", "রেজিস্ট্রেশন আইন", "নিবন্ধন আইন"]
    },
    {
        "canonical_title": "The Limitation Act, 1908",
        "short_title": "Limitation Act",
        "act_number": "IX of 1908",
        "year": 1908,
        "instrument_type": "principal_act",
        "effective_from": "1909-01-01",
        "status": "active",
        "aliases": ["Limitation Act", "তামাদি আইন", "তামাদী আইন"]
    },
    {
        "canonical_title": "The Constitution of the People's Republic of Bangladesh",
        "short_title": "Constitution",
        "act_number": "Constitutional Instrument",
        "year": 1972,
        "instrument_type": "constitution",
        "effective_from": "1972-12-16",
        "status": "active",
        "aliases": ["Constitution", "গণপ্রজাতন্ত্রী বাংলাদেশের সংবিধান", "বাংলাদেশ সংবিধান", "সংবিধান", "Article 111", "অনুচ্ছেদ ১১১"]
    },
    {
        "canonical_title": "Family Courts Act, 2023",
        "short_title": "Family Courts Act 2023",
        "act_number": "Act No. 38 of 2023",
        "year": 2023,
        "instrument_type": "principal_act",
        "effective_from": "2023-09-18",
        "status": "active",
        "aliases": [
            "Family Courts Act",
            "পারিবারিক আদালত আইন",
            "পারিবারিক আদালত আইন ২০২৩",
            "Family Courts Ordinance 1985 (Repealed by Act 38 of 2023)",
            "পারিবারিক আদালত অধ্যাদেশ ১৯৮৫"
        ]
    },
    {
        "canonical_title": "Children Act, 2013",
        "short_title": "Children Act 2013",
        "act_number": "Act No. 24 of 2013",
        "year": 2013,
        "instrument_type": "principal_act",
        "effective_from": "2013-06-20",
        "status": "active",
        "aliases": ["Children Act", "শিশু আইন", "শিশু আইন ২০১৩", "Juvenile Justice"]
    },
    {
        "canonical_title": "The Muslim Family Laws Ordinance, 1961",
        "short_title": "MFLO",
        "act_number": "VIII of 1961",
        "year": 1961,
        "instrument_type": "ordinance",
        "effective_from": "1961-07-15",
        "status": "active",
        "aliases": ["MFLO", "Muslim Family Laws Ordinance", "মুসলিম পারিবারিক আইন অধ্যাদেশ"]
    },
    {
        "canonical_title": "The Bangladesh Labour Act, 2006",
        "short_title": "Labour Act",
        "act_number": "XLII of 2006",
        "year": 2006,
        "instrument_type": "principal_act",
        "effective_from": "2006-10-11",
        "status": "active",
        "aliases": ["Labour Act", "বাংলাদেশ শ্রম আইন", "শ্রম আইন ২০০৬"]
    },
    {
        "canonical_title": "Consumers' Right Protection Act, 2009",
        "short_title": "CRPA",
        "act_number": "XXVI of 2009",
        "year": 2009,
        "instrument_type": "principal_act",
        "effective_from": "2009-04-06",
        "status": "active",
        "aliases": ["CRPA", "Consumers Right Protection Act", "ভোক্তা অধিকার সংরক্ষণ আইন"]
    },
    {
        "canonical_title": "Income Tax Act, 2023",
        "short_title": "Income Tax Act",
        "act_number": None,
        "year": 2023,
        "instrument_type": "principal_act",
        "effective_from": "2023-07-01",
        "status": "active",
        "aliases": ["Income Tax Act", "আয়কর আইন", "আয়কর আইন ২০২৩"]
    },
    {
        "canonical_title": "The State Acquisition and Tenancy Act, 1950",
        "short_title": "SAT Act",
        "act_number": "XXVIII of 1951",
        "year": 1950,
        "instrument_type": "principal_act",
        "effective_from": "1951-05-16",
        "status": "active",
        "aliases": ["SAT Act", "State Acquisition and Tenancy Act", "রাষ্ট্রীয় অধিগ্রহণ ও প্রজাস্বত্ব আইন", "প্রজাস্বত্ব আইন"]
    }
]

def normalize_alias(s: str) -> str:
    import re
    return re.sub(r'[^a-zA-Z0-9\u0980-\u09FF]', '', s.lower())

def main():
    print(f"Seeding {len(CORE_ACTS)} core statutes into legal_instruments...")
    for item in CORE_ACTS:
        res = db.table("legal_instruments").upsert(
            {
                "canonical_title": item["canonical_title"],
                "short_title": item["short_title"],
                "act_number": item.get("act_number"),
                "year": item["year"],
                "instrument_type": item["instrument_type"],
                "effective_from": item["effective_from"],
                "status": item["status"],
                "official_source_verified": True,
            },
            on_conflict="canonical_title"
        ).execute()
        inst_id = res.data[0]["id"]
        print(f"  ✓ {item['canonical_title']} (ID: {inst_id[:8]})")

        # Seed aliases
        all_aliases = set(item.get("aliases", [])) | {item["canonical_title"], item["short_title"]}
        for al in all_aliases:
            if not al:
                continue
            norm = normalize_alias(al)
            try:
                db.table("legal_instrument_aliases").upsert(
                    {
                        "instrument_id": inst_id,
                        "alias": al,
                        "normalized_alias": norm
                    },
                    on_conflict="normalized_alias"
                ).execute()
            except Exception as e:
                pass

    print("\n✅ All core instruments seeded successfully.")

if __name__ == "__main__":
    main()
