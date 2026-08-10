# tools/supreme_court/extractor.py
import fitz  # PyMuPDF
import sqlite3
import sys
import json
import subprocess
from pathlib import Path
from .config import CHECKPOINT_DB, PDF_VAULT, MIN_CHARS_PER_PAGE, MAX_CORRUPTION_RATE

sys.stdout.reconfigure(encoding='utf-8')


def score_page_quality(text: str) -> dict:
    """Determine if a page needs OCR."""
    char_count = len(text.strip())
    if char_count == 0:
        return {"needs_ocr": True, "reason": "EMPTY", "char_count": 0}

    # Count corruption markers
    corruption_chars = (
        text.count('□') + text.count('â') + text.count('\ufffd')
    )
    corruption_rate = corruption_chars / max(char_count, 1)

    if char_count < MIN_CHARS_PER_PAGE:
        return {"needs_ocr": True, "reason": "TOO_SHORT", "char_count": char_count}
    if corruption_rate > MAX_CORRUPTION_RATE:
        return {"needs_ocr": True, "reason": "HIGH_CORRUPTION",
                "char_count": char_count, "corruption_rate": round(corruption_rate, 3)}

    return {"needs_ocr": False, "char_count": char_count,
            "corruption_rate": round(corruption_rate, 3)}

def run_ocr_on_page(page) -> str:
    """OCR a single page using Tesseract ben+eng if available."""
    try:
        pix = page.get_pixmap(dpi=300)
        img_path = PDF_VAULT / f"_temp_ocr_{page.number}.png"
        pix.save(str(img_path))

        result = subprocess.run(
            ["tesseract", str(img_path), "stdout",
             "-l", "ben+eng", "--oem", "3", "--psm", "3"],
            capture_output=True, text=True, timeout=60
        )
        if img_path.exists():
            img_path.unlink()
        return result.stdout
    except Exception as e:
        return f"OCR_UNAVAILABLE: {e}"

def extract_pdf(manifest_id: str) -> dict:
    """Extract text from one PDF. Returns per-page results."""
    filepath = PDF_VAULT / f"{manifest_id}.pdf"
    if not filepath.exists():
        return {"status": "FILE_NOT_FOUND"}

    try:
        doc = fitz.open(str(filepath))
    except Exception as e:
        return {"status": f"PDF_OPEN_ERROR: {e}"}

    page_count = len(doc)
    pages = []
    ocr_pages = 0

    for page_num, page in enumerate(doc, 1):
        native_text = page.get_text("text", sort=True)
        quality = score_page_quality(native_text)

        ocr_text = None
        if quality["needs_ocr"]:
            print(f"    Page {page_num}: OCR flagged ({quality['reason']})")
            ocr_text = run_ocr_on_page(page)
            if ocr_text and not ocr_text.startswith("OCR_UNAVAILABLE"):
                ocr_pages += 1

        selected_text = ocr_text if quality["needs_ocr"] and ocr_text and not ocr_text.startswith("OCR_UNAVAILABLE") else native_text

        pages.append({
            "page_number":   page_num,
            "native_text":   native_text,
            "ocr_text":      ocr_text,
            "selected_text": selected_text,
            "char_count":    quality["char_count"],
            "needs_ocr":     quality["needs_ocr"],
            "ocr_reason":    quality.get("reason"),
        })

    doc.close()

    full_text = "\n\n".join(
        f"[PAGE {p['page_number']}]\n{p['selected_text']}"
        for p in pages
    )

    print(f"  ✓ Extracted {page_count} pages ({ocr_pages} OCR'd): {manifest_id}")
    return {
        "status": "EXTRACTED",
        "page_count": page_count,
        "ocr_pages": ocr_pages,
        "pages": pages,
        "full_text": full_text
    }

def run_extraction():
    """Phase 3: Extract all downloaded PDFs."""
    conn = sqlite3.connect(CHECKPOINT_DB)
    pending = conn.execute("""
        SELECT manifest_id FROM sc_manifest
        WHERE download_status = 'DOWNLOADED'
        AND extraction_status = 'PENDING'
    """).fetchall()

    print(f"=== Extracting {len(pending)} PDFs ===")
    for (manifest_id,) in pending:
        print(f"\n  {manifest_id}")
        result = extract_pdf(manifest_id)

        output_path = PDF_VAULT / f"{manifest_id}_extracted.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        status = result["status"]
        conn.execute(
            "UPDATE sc_manifest SET extraction_status=?, page_count=? WHERE manifest_id=?",
            (status, result.get("page_count"), manifest_id)
        )
        conn.commit()

    conn.close()
    print("\n=== EXTRACTION COMPLETE ===")

if __name__ == "__main__":
    run_extraction()
