"""
JustorAI — Bulk Law Data Ingestion Script
==========================================
Use this script to upload your local law PDFs into the Supabase knowledge base.
The server processes PDFs in the background - this script polls for completion.

Usage:
    python backend/ingest.py --dir "./law_docs" --url "http://localhost:10000"
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path


def upload_and_wait(api_url: str, pdf_path: Path) -> dict:
    """Upload a PDF and poll until processing is complete."""
    # 1. Submit the upload (returns immediately with a job_id)
    with open(pdf_path, "rb") as f:
        resp = requests.post(
            f"{api_url}/upload",
            data={"title": pdf_path.stem.replace("_", " ").replace("-", " ").title()},
            files={"file": (pdf_path.name, f, "application/pdf")},
            timeout=60,
        )
    resp.raise_for_status()
    job = resp.json()
    job_id = job.get("job_id")
    if not job_id:
        return job  # Unexpected response

    # 2. Poll status until done or error
    poll_url = f"{api_url}/upload/status/{job_id}"
    dots = 0
    while True:
        time.sleep(3)
        status_resp = requests.get(poll_url, timeout=10)
        status_resp.raise_for_status()
        status = status_resp.json()

        state = status.get("status", "unknown")
        if state == "done":
            return status
        elif state == "error":
            raise RuntimeError(status.get("error", "Unknown error"))
        else:
            # Still processing — show progress
            done = status.get("chunks_done", 0)
            total = status.get("total_chunks", "?")
            dots = (dots + 1) % 4
            print(f"\r  processing {'.' * (dots+1):<4} {done}/{total} chunks", end="", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Bulk ingest law PDFs into JustorAI knowledge base.")
    parser.add_argument("--dir", required=True, help="Folder containing PDF files")
    parser.add_argument("--url", default="http://localhost:10000", help="API base URL")
    args = parser.parse_args()

    pdf_dir = Path(args.dir)
    if not pdf_dir.is_dir():
        print(f"ERROR: '{pdf_dir}' is not a directory.")
        sys.exit(1)

    pdfs = sorted(pdf_dir.glob("**/*.pdf"))
    if not pdfs:
        print(f"No PDF files found in '{pdf_dir}'.")
        sys.exit(0)

    print(f"Found {len(pdfs)} PDF(s). Uploading to {args.url} ...\n")

    success, failed = 0, 0
    for pdf in pdfs:
        print(f"  -> {pdf.name} ... ", end="", flush=True)
        try:
            result = upload_and_wait(args.url, pdf)
            chunks = result.get("total_chunks", "?")
            doc_id = result.get("document_id", "?")
            print(f"\r  -> {pdf.name} ... OK  ({chunks} chunks, id: {doc_id})")
            success += 1
        except Exception as e:
            print(f"\r  -> {pdf.name} ... FAILED  {e}")
            failed += 1

    print(f"\nDone. {success} uploaded, {failed} failed.")


if __name__ == "__main__":
    main()
