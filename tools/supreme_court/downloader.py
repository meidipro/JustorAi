# tools/supreme_court/downloader.py
import hashlib
import sqlite3
import sys
import re
import time
import httpx
from pathlib import Path
from .config import CHECKPOINT_DB, PDF_VAULT, REQUEST_DELAY

sys.stdout.reconfigure(encoding='utf-8')

def safe_filename(manifest_id: str) -> str:
    """Sanitize manifest_id to clean safe OS filename string."""
    clean = re.sub(r'[^A-Za-z0-9_\-]', '_', manifest_id)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean[:120] if clean else "judgment"

def download_and_validate(manifest_id: str, pdf_url: str, conn) -> dict:
    """Download one PDF, validate it, record SHA-256."""
    fname = safe_filename(manifest_id) + ".pdf"
    filepath = PDF_VAULT / fname


    # Skip if already downloaded
    if filepath.exists():
        print(f"  Already exists: {filename}")
        return {"status": "ALREADY_EXISTS", "filepath": str(filepath)}

    time.sleep(REQUEST_DELAY)

    try:
        response = httpx.get(
            pdf_url,
            headers={"User-Agent": "JustorAI/1.0 (+https://justorai.com)"},
            follow_redirects=True,
            timeout=60.0
        )
    except Exception as e:
        conn.execute(
            "UPDATE sc_manifest SET download_status=? WHERE manifest_id=?",
            (f"ERROR: {e}", manifest_id)
        )
        conn.commit()
        return {"status": "DOWNLOAD_ERROR", "error": str(e)}

    # Validate HTTP status
    if response.status_code != 200:
        conn.execute(
            "UPDATE sc_manifest SET download_status=? WHERE manifest_id=?",
            (f"HTTP_{response.status_code}", manifest_id)
        )
        conn.commit()
        return {"status": f"HTTP_{response.status_code}"}

    # Validate it's actually a PDF
    if response.content[:4] != b'%PDF':
        conn.execute(
            "UPDATE sc_manifest SET download_status=? WHERE manifest_id=?",
            ("NOT_A_PDF", manifest_id)
        )
        conn.commit()
        return {"status": "NOT_A_PDF"}

    # Save file
    filepath.write_bytes(response.content)

    # SHA-256 for integrity
    sha256 = hashlib.sha256(response.content).hexdigest()

    # Check for duplicate hash
    duplicate = conn.execute(
        "SELECT manifest_id FROM sc_manifest WHERE sha256=? AND manifest_id!=?",
        (sha256, manifest_id)
    ).fetchone()

    if duplicate:
        print(f"  WARNING: Duplicate PDF detected — same as {duplicate[0]}")

    conn.execute("""
        UPDATE sc_manifest
        SET download_status='DOWNLOADED', sha256=?
        WHERE manifest_id=?
    """, (sha256, manifest_id))
    conn.commit()

    print(f"  ✓ Downloaded: {fname} ({len(response.content)//1024}KB, SHA-256: {sha256[:12]}...)")
    return {"status": "DOWNLOADED", "filepath": str(filepath), "sha256": sha256}


def run_downloads():
    """Phase 2: Download all DISCOVERED manifests."""
    conn = sqlite3.connect(CHECKPOINT_DB)
    pending = conn.execute("""
        SELECT manifest_id, pdf_url FROM sc_manifest
        WHERE download_status = 'PENDING'
        ORDER BY manifest_id
    """).fetchall()

    print(f"=== Downloading {len(pending)} PDFs ===")
    for manifest_id, pdf_url in pending:
        print(f"\n  {manifest_id}")
        download_and_validate(manifest_id, pdf_url, conn)

    conn.close()
    print("\n=== DOWNLOADS COMPLETE ===")

if __name__ == "__main__":
    run_downloads()
