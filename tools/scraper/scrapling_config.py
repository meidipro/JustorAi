import os
from pathlib import Path

# Base directory for Justor AI workspace
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "Scrap BDLAW Json"
SCRAPER_DB_PATH = BASE_DIR / "tools" / "scraper" / "scraper_state.db"

# Create output directory if it does not exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Target URLs
BDLAWS_BASE_URL = "http://bdlaws.minlaw.gov.bd"
BDLAWS_INDEX_URL = f"{BDLAWS_BASE_URL}/laws-of-bangladesh-alphabetical-index.html"
BDLAWS_CHRONO_INDEX_URL = f"{BDLAWS_BASE_URL}/laws-of-bangladesh-chronological-index.html"

# Default HTTP headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
}

# Concurrency & Retries
MAX_CONCURRENT_REQUESTS = 10
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2.0
