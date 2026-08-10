# Justor AI Ultimate Legal Scraper Suite

An enterprise-grade, Scrapling-backed legal web harvester and parser designed for Bangladesh Laws (`bdlaws.minlaw.gov.bd`) and Dhaka Law Reports (DLR / Supreme Court Case Law).

---

## Key Features

1. **UTF-16 BE Decoding with BOM (`\xfe\xff`)**: Solves standard web scraper encoding bugs on `bdlaws.minlaw.gov.bd`.
2. **Auto-Healing Selectors**: Resilient parsing of Act titles, section numbers, titles, contents, sub-sections, and footnoted amendment notes.
3. **Resilient SQLite Checkpointing (`checkpoint_manager.py`)**: Zero duplicate requests, instant session pause and resume capability.
4. **Multithreaded Concurrent Engine**: Concurrently scrapes 1,100+ Bangladesh Code laws in high-throughput batches.
5. **DLR & Supreme Court Case Law Parser**: Extracts citations (`52 DLR (AD) 112`), court/bench, headnotes, ratio decidendi, and act cross-references.
6. **Justor AI Standard JSON Exporter (`json_exporter.py`)**: Directly exports cleaned, normalized JSON files ready for vector embedding ingestion into Supabase / PostgreSQL.

---

## Directory Structure

```
tools/scraper/
├── __init__.py
├── scrapling_config.py      # Config & Constants
├── checkpoint_manager.py     # SQLite State Tracker
├── json_exporter.py          # Justor AI Schema Formatter & Exporter
├── bdlaws_harvester.py       # BDLaws Crawler & Parser
└── dlr_caselaw_harvester.py  # DLR & Case Law Parser
```

---

## CLI Usage

### 1. Scrape Single Bangladesh Act by ID
```bash
.venv\Scripts\python.exe -m tools.scraper.bdlaws_harvester --act-id 180
```

### 2. Scrape Batch of Acts with Concurrency
```bash
.venv\Scripts\python.exe -m tools.scraper.bdlaws_harvester --limit 10 --workers 5
```

### 3. Full Harvest (All ~1,100+ Bangladesh Acts)
```bash
.venv\Scripts\python.exe -m tools.scraper.bdlaws_harvester --workers 10
```

### 4. Parse DLR Case Law
```bash
.venv\Scripts\python.exe -m tools.scraper.dlr_caselaw_harvester
```

---

## Output Location

Scraped JSON files are saved to `knowledge/scraped/`.
Run `python ingest_new_json_folder.py` to ingest the scraped JSON files directly into Justor AI's vector database.
