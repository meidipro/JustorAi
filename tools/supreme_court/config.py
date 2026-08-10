# tools/supreme_court/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# Directories
PDF_VAULT = BASE_DIR / "sc_pdf_vault"
PDF_VAULT.mkdir(exist_ok=True)

# SQLite checkpoint — survives interruptions
CHECKPOINT_DB = BASE_DIR / "sc_manifest.sqlite"

# Supreme Court URLs
SC_BASE = "https://supremecourt.gov.bd"
SC_HCD_URL = f"{SC_BASE}/web/?div_id=2&lang=&menu=00&page=judgments.php&type_id=5"
SC_AD_URL  = f"{SC_BASE}/web/?div_id=1&lang=&menu=00&page=judgments.php&type_id=5"

# Crawl settings — polite government server throttling
REQUEST_DELAY = 2       # seconds between requests
MAX_RETRIES   = 3
PAGE_SIZE     = 50      # judgments per listing page

# Quality thresholds
MIN_CHARS_PER_PAGE  = 50   # below this → needs OCR
MAX_CORRUPTION_RATE = 0.15  # above this → needs OCR

# Supabase Credentials
SUPABASE_URL = os.environ.get("VITE_SUPABASE_URL", "").strip()
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()

# OpenRouter for BGE-M3
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
EMBEDDING_MODEL    = "baai/bge-m3"
EMBEDDING_DIM      = 1024
