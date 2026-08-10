# tools/supreme_court/crawler.py
import time
import sqlite3
import sys
import re
import httpx
from bs4 import BeautifulSoup
from .config import SC_HCD_URL, SC_AD_URL, CHECKPOINT_DB, REQUEST_DELAY, SC_BASE

sys.stdout.reconfigure(encoding='utf-8')

def sanitize_id(raw: str) -> str:
    """Sanitize raw text into a safe OS filename string."""
    clean = re.sub(r'[^A-Za-z0-9_\-]', '_', raw)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean[:80] if clean else "CASE"

def init_checkpoint_db():
    conn = sqlite3.connect(CHECKPOINT_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sc_manifest (
            manifest_id TEXT PRIMARY KEY,
            division TEXT NOT NULL,
            case_type TEXT,
            case_number TEXT,
            case_year TEXT,
            parties_raw TEXT,
            short_description_raw TEXT,
            uploaded_date TEXT,
            judgment_date TEXT,       -- extracted from PDF later
            judges TEXT,              -- extracted from PDF later
            pdf_url TEXT,
            translation_url TEXT,
            listing_url TEXT,
            crawl_status TEXT DEFAULT 'DISCOVERED',
            download_status TEXT DEFAULT 'PENDING',
            extraction_status TEXT DEFAULT 'PENDING',
            ingest_status TEXT DEFAULT 'PENDING',
            sha256 TEXT,
            page_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def parse_listing_row(row, division: str, listing_url: str) -> dict | None:
    cells = row.find_all("td")
    if len(cells) < 3:
        return None

    # Find PDF link
    pdf_link = None
    for a in row.find_all("a"):
        href = a.get("href", "")
        if href and ".pdf" in href.lower():
            pdf_link = a
            break
            
    if not pdf_link:
        return None

    href = pdf_link.get("href", "")
    pdf_url = SC_BASE + href if href.startswith("/") else (href if href.startswith("http") else f"{SC_BASE}/web/{href}")

    # Find translation link if any
    translation_url = None
    for a in row.find_all("a"):
        href = a.get("href", "")
        if href and "translate" in href.lower():
            translation_url = SC_BASE + href if href.startswith("/") else href
            break

    # Build stable manifest ID
    case_number = cells[1].text.strip() if len(cells) > 1 else "UNKNOWN"
    case_year   = cells[2].text.strip() if len(cells) > 2 else "UNKNOWN"
    div_code    = "HCD" if "High Court" in division else "AD"
    
    clean_num = sanitize_id(case_number)
    clean_year = sanitize_id(case_year)
    manifest_id = f"BD-SC-{div_code}-{clean_num}-{clean_year}"


    return {
        "manifest_id":          manifest_id,
        "division":             division,
        "case_type":            cells[0].text.strip() if cells else "",
        "case_number":          case_number,
        "case_year":            case_year,
        "parties_raw":          cells[3].text.strip() if len(cells) > 3 else "",
        "short_description_raw": cells[4].text.strip() if len(cells) > 4 else "",
        "uploaded_date":        cells[-1].text.strip() if cells else "",
        "judgment_date":        None,   # extracted from PDF
        "judges":               None,   # extracted from PDF
        "pdf_url":              pdf_url,
        "translation_url":      translation_url,
        "listing_url":          listing_url,
        "crawl_status":         "DISCOVERED",
    }

def crawl_division(division_url: str, division: str, limit: int, conn) -> int:
    """Crawl one division's listing. Returns count of new records added."""
    added = 0
    start = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    with httpx.Client(headers=headers, follow_redirects=True, timeout=30.0) as client:
        while added < limit:
            paginated_url = f"{division_url}&start={start}"
            print(f"  Fetching: {paginated_url}")
            time.sleep(REQUEST_DELAY)

            try:
                resp = client.get(paginated_url)
                if resp.status_code != 200:
                    print(f"  HTTP error {resp.status_code}")
                    break
            except Exception as e:
                print(f"  Network error: {e}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.find_all("tr")

            if not rows or len(rows) <= 1:
                print("  No more rows — listing exhausted.")
                break

            page_added = 0
            for row in rows[1:]:  # skip header row
                if added >= limit:
                    break

                manifest = parse_listing_row(row, division, paginated_url)
                if not manifest:
                    continue

                # Skip if already in checkpoint
                exists = conn.execute(
                    "SELECT 1 FROM sc_manifest WHERE manifest_id = ?",
                    (manifest["manifest_id"],)
                ).fetchone()

                if exists:
                    continue

                conn.execute("""
                    INSERT INTO sc_manifest
                    (manifest_id, division, case_type, case_number, case_year,
                     parties_raw, short_description_raw, uploaded_date,
                     judgment_date, judges, pdf_url, translation_url,
                     listing_url, crawl_status)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    manifest["manifest_id"], manifest["division"],
                    manifest["case_type"], manifest["case_number"],
                    manifest["case_year"], manifest["parties_raw"],
                    manifest["short_description_raw"], manifest["uploaded_date"],
                    manifest["judgment_date"], manifest["judges"],
                    manifest["pdf_url"], manifest["translation_url"],
                    manifest["listing_url"], manifest["crawl_status"]
                ))
                conn.commit()
                added += 1
                page_added += 1
                print(f"    ✓ [{added}/{limit}] {manifest['manifest_id']}")

            if page_added == 0:
                print("  No new records on this page.")
                break

            start += 50

    return added

def run_manifest_crawl(limit_per_division: int = 13):
    """
    Phase 1: Build manifest only. Cap at ~25 total records across AD & HCD.
    """
    conn = init_checkpoint_db()

    print("=== Crawling High Court Division ===")
    hcd_count = crawl_division(SC_HCD_URL, "High Court Division", limit_per_division, conn)

    print("\n=== Crawling Appellate Division ===")
    ad_count  = crawl_division(SC_AD_URL, "Appellate Division", limit_per_division, conn)

    total = hcd_count + ad_count
    print(f"\n=== MANIFEST COMPLETE: {total} new records ===")
    print(f"Database: {CHECKPOINT_DB}")
    conn.close()

if __name__ == "__main__":
    run_manifest_crawl(limit_per_division=13)
