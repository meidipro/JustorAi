#!/usr/bin/env python3
"""
scripts/scrape_supreme_court_cases.py
Scrapes 200+ Supreme Court judgments and orders from the official Supreme Court of Bangladesh portal:
URL: https://supremecourt.gov.bd/web/?page=judgments.php&menu=00&div_id=2&type_id=5&lang=
"""

import os
import sys
import json
import csv
import re
import time
from urllib.parse import urljoin
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()

BASE_URL = "https://supremecourt.gov.bd/web/"
TARGET_PATH = "judgments.php"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

JSON_OUTPUT = os.path.join(OUTPUT_DIR, "scraped_supreme_court_cases_200.json")
CSV_OUTPUT = os.path.join(OUTPUT_DIR, "scraped_supreme_court_cases_200.csv")

def create_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
        "Connection": "keep-alive"
    })
    # Warm up session with base site cookie handshake
    try:
        s.get("https://supremecourt.gov.bd/web/?lang=", verify=False, timeout=20)
    except Exception as e:
        print(f"Warning on initial session warmup: {e}")
    return s

def scrape_judgments(target_count: int = 250) -> list:
    session = create_session()
    cases = []
    seen_urls = set()
    start_offset = 0
    page_num = 1

    print(f"Starting scrape from Supreme Court portal (target: {target_count}+ cases)...")

    while len(cases) < target_count and start_offset <= 600:
        url = f"https://supremecourt.gov.bd/web/?page=judgments.php&menu=00&div_id=2&type_id=5&lang=&start={start_offset}"
        print(f"Fetching Page {page_num} (start={start_offset})...")
        try:
            r = session.get(url, verify=False, timeout=25)
            if r.status_code != 200:
                print(f"  Warning: status {r.status_code} received on start={start_offset}")
                break

            soup = BeautifulSoup(r.text, "html.parser")
            all_a = soup.find_all("a", href=True)
            pdf_links = [a for a in all_a if "pdf" in a["href"].lower() and "translation" not in a["href"].lower()]

            if not pdf_links:
                print(f"  No more PDF links found on page {page_num}.")
                break

            page_added = 0
            for a in pdf_links:
                href = a["href"].strip()
                full_pdf_url = urljoin(BASE_URL, href)
                if full_pdf_url in seen_urls:
                    continue
                seen_urls.add(full_pdf_url)

                raw_title = a.get_text(strip=True)
                cleaned_title = re.sub(r"\s*\([^)]*\)$", "", raw_title).strip() or raw_title

                # Extract upload date if available from surrounding text
                upload_date = None
                p_text = ""
                if a.parent:
                    p_text += a.parent.get_text(" ", strip=True) + " "
                    if a.parent.parent:
                        p_text += a.parent.parent.get_text(" ", strip=True)
                
                upload_match = re.search(r"Uploaded\s*on\s*:\s*([\d\w-]+)", p_text, re.IGNORECASE)
                if upload_match:
                    upload_date = upload_match.group(1).strip()

                # Parse Case Type, Number, Year
                m = re.match(r"^(.*?)\s*(\d+\s*/\s*\d{4})", cleaned_title)
                if m:
                    case_type = m.group(1).strip()
                    case_no = m.group(2).strip().replace(" ", "")
                    year_val = case_no.split("/")[-1]
                    year = int(year_val) if year_val.isdigit() else None
                else:
                    case_type = cleaned_title
                    case_no = None
                    year = None

                filename = href.split("/")[-1]
                trans_url = f"https://supremecourt.gov.bd/translation/process.php?file={filename}"

                case_record = {
                    "id": f"SC_HCD_{len(cases) + 1:04d}",
                    "case_title": cleaned_title,
                    "case_type": case_type,
                    "case_number": case_no,
                    "year": year,
                    "division": "High Court Division",
                    "court_name": "Supreme Court of Bangladesh",
                    "pdf_url": full_pdf_url,
                    "translation_url": trans_url,
                    "filename": filename,
                    "upload_date": upload_date,
                    "scraped_at": datetime.now().isoformat()
                }

                cases.append(case_record)
                page_added += 1

            print(f"  Page {page_num} complete: added {page_added} cases (Total unique: {len(cases)})")
            start_offset += 50
            page_num += 1
            time.sleep(0.5)

        except Exception as ex:
            print(f"Error fetching page {page_num}: {ex}")
            break

    return cases

def save_datasets(cases: list):
    # 1. Save JSON
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved {len(cases)} cases to JSON: {JSON_OUTPUT}")

    # 2. Save CSV
    if cases:
        fieldnames = list(cases[0].keys())
        with open(CSV_OUTPUT, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cases)
        print(f"✓ Saved {len(cases)} cases to CSV: {CSV_OUTPUT}")

def print_summary(cases: list):
    print("\n" + "="*60)
    print(f" SUPREME COURT OF BANGLADESH SCRAPING REPORT")
    print("="*60)
    print(f" Total Cases Scraped: {len(cases)}")
    
    # Type breakdown
    types = {}
    for c in cases:
        t = c["case_type"] or "Unknown"
        types[t] = types.get(t, 0) + 1

    print("\n Top Case Categories:")
    for t, count in sorted(types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  • {t}: {count} cases")

    # Year breakdown
    years = {}
    for c in cases:
        y = c["year"] or "Unknown"
        years[y] = years.get(y, 0) + 1

    print("\n Year Distribution (Recent):")
    for y in sorted([k for k in years.keys() if isinstance(k, int)], reverse=True)[:8]:
        print(f"  • Year {y}: {years[y]} cases")
    print("="*60 + "\n")

if __name__ == "__main__":
    cases = scrape_judgments(target_count=220)
    save_datasets(cases)
    print_summary(cases)
