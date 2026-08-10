import urllib.request
import urllib.error
import re
import os
import time
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup

from .scrapling_config import (
    BDLAWS_BASE_URL,
    BDLAWS_INDEX_URL,
    DEFAULT_HEADERS,
    MAX_CONCURRENT_REQUESTS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    OUTPUT_DIR
)
from .checkpoint_manager import ScraperCheckpointManager
from .json_exporter import export_act_to_json, clean_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("BDLawsHarvester")

class BDLawsHarvester:
    """
    Ultimate Scrapling-Powered Web Harvester for http://bdlaws.minlaw.gov.bd/
    Handles UTF-16 BE BOM encoding, paired element DOM selectors (txt-head & txt-details),
    footnote/amendment parsing, and high-throughput multithreaded extraction.
    """

    def __init__(self, checkpoint_mgr: ScraperCheckpointManager = None):
        self.checkpoint_mgr = checkpoint_mgr or ScraperCheckpointManager()

    def fetch_url_with_utf16_autodetect(self, url: str) -> str:
        """
        Fetches URL and handles bdlaws-specific UTF-16 BOM encoding (\xfe\xff).
        Implements stealth headers and automatic backoff retries.
        """
        retries = 0
        last_error = None

        while retries < MAX_RETRIES:
            try:
                req = urllib.request.Request(url, headers=DEFAULT_HEADERS)
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as response:
                    raw_data = response.read()

                # Attempt UTF-16 BE decoding first (standard for bdlaws)
                if raw_data.startswith(b'\xfe\xff') or raw_data.startswith(b'\xff\xfe'):
                    try:
                        return raw_data.decode('utf-16')
                    except Exception:
                        pass
                
                # Fallback decodings
                for encoding in ['utf-16', 'utf-8-sig', 'utf-8', 'iso-8859-1']:
                    try:
                        return raw_data.decode(encoding)
                    except Exception:
                        continue
                
                return raw_data.decode('utf-8', errors='ignore')

            except urllib.error.URLError as e:
                last_error = e
                retries += 1
                logger.warning(f"Fetch failed for {url} (Attempt {retries}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY * retries)
            except Exception as e:
                last_error = e
                retries += 1
                logger.warning(f"Unexpected error fetching {url} (Attempt {retries}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY * retries)

        raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts. Last error: {last_error}")

    def discover_all_act_ids(self) -> list:
        """
        Crawls the master index page (/laws-of-bangladesh-alphabetical-index.html)
        to extract all Act IDs (e.g. 1 to 1600+).
        Returns list of tuples: [(act_id, act_url, title), ...]
        """
        logger.info(f"Crawling master index: {BDLAWS_INDEX_URL}...")
        html_content = self.fetch_url_with_utf16_autodetect(BDLAWS_INDEX_URL)
        
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a', href=True)

        act_map = {}
        pattern = re.compile(r'/act-(\d+)\.html')

        for a in links:
            href = a['href']
            match = pattern.search(href)
            if match:
                act_id = match.group(1)
                title = clean_text(a.get_text())
                if act_id not in act_map:
                    details_url = f"{BDLAWS_BASE_URL}/act-details-{act_id}.html"
                    act_map[act_id] = (act_id, details_url, title)

        results = list(act_map.values())
        logger.info(f"Discovered total {len(results)} unique Bangladesh Acts.")
        return results

    def parse_act_details_html(self, html_content: str, provenance_url: str) -> dict:
        """
        Scrapling-inspired 1-to-1 paired DOM parser for act-details-<id>.html pages.
        Extracts Act Name, paired marginal headings (txt-head) and section contents (txt-details).
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract Act Title
        act_title = ""
        title_tag = soup.find('title')
        if title_tag and title_tag.get_text().strip():
            act_title = clean_text(title_tag.get_text())
        else:
            header_h3 = soup.find('h3') or soup.find('h4') or soup.find('h2')
            if header_h3:
                act_title = clean_text(header_h3.get_text())

        if not act_title or act_title.lower() == "bdlaws":
            act_title = "Unknown Bangladesh Act"

        # Global Footnotes / Amendment annotations extraction
        footnote_spans = soup.find_all('span', class_='footnote')
        amendment_notes_global = []
        for span in footnote_spans:
            title_attr = span.get('title')
            if title_attr and clean_text(title_attr):
                cleaned_note = clean_text(title_attr)
                if len(cleaned_note) > 5 and cleaned_note not in amendment_notes_global:
                    amendment_notes_global.append(cleaned_note)

        # Paired extraction of txt-head (Section Titles) and txt-details (Section Bodies)
        heads = soup.find_all('div', class_='txt-head')
        details = soup.find_all('div', class_='txt-details')

        parsed_sections = []

        if heads and details and len(heads) == len(details):
            for i in range(len(heads)):
                sec_head = clean_text(heads[i].get_text())
                sec_detail_soup = details[i]

                # Find section footnotes
                sec_footnotes = []
                for fn in sec_detail_soup.find_all('span', class_='footnote'):
                    fn_title = fn.get('title')
                    if fn_title:
                        fn_cleaned = clean_text(fn_title)
                        if fn_cleaned and fn_cleaned not in sec_footnotes:
                            sec_footnotes.append(fn_cleaned)

                detail_text = clean_text(sec_detail_soup.get_text())

                # Extract Section Number from start of detail_text (e.g., "1. ", "2. ", "3A. ")
                num_match = re.match(r'^\s*(\d+[A-Z]?|\u09e6-\u09ef+[A-Z]?)\.\s*', detail_text)
                if num_match:
                    sec_num = num_match.group(1)
                else:
                    sec_num = str(i + 1)

                parsed_sections.append({
                    "Section_Number": sec_num,
                    "Section_Title": sec_head,
                    "Content": detail_text,
                    "Status": "Active" if "repealed" not in detail_text.lower() else "Repealed",
                    "Jurisdiction": "Bangladesh",
                    "Amendment_Notes": sec_footnotes if sec_footnotes else amendment_notes_global,
                    "Repealed_Clauses": []
                })
        else:
            # Fallback regex parsing if DOM tags differ
            for btn in soup.find_all(['header', 'footer', 'nav', 'script', 'style']):
                btn.decompose()
            full_text = clean_text(soup.get_text())
            section_pattern = re.compile(r'(?:\n|\r|^)\s*(\d{1,4}|\u09e6-\u09ef{1,4})\.\s+([^\n]+)')
            matches = list(section_pattern.finditer(full_text))

            if matches:
                for idx, match in enumerate(matches):
                    sec_num = match.group(1).strip()
                    start_pos = match.start()
                    end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(full_text)
                    block = full_text[start_pos:end_pos].strip()
                    lines = block.splitlines()
                    sec_head = lines[0][:100] if lines else f"Section {sec_num}"

                    parsed_sections.append({
                        "Section_Number": sec_num,
                        "Section_Title": sec_head,
                        "Content": block,
                        "Status": "Active",
                        "Jurisdiction": "Bangladesh",
                        "Amendment_Notes": amendment_notes_global,
                        "Repealed_Clauses": []
                    })
            else:
                parsed_sections.append({
                    "Section_Number": "1",
                    "Section_Title": act_title,
                    "Content": full_text[:10000],
                    "Status": "Active",
                    "Jurisdiction": "Bangladesh",
                    "Amendment_Notes": amendment_notes_global,
                    "Repealed_Clauses": []
                })

        return {
            "act_name": act_title,
            "sections": parsed_sections,
            "provenance_url": provenance_url
        }

    def scrape_single_act(self, act_id: str, provenance_url: str = None) -> Path:
        """
        Scrapes, parses, and exports a single Act by ID.
        """
        if not provenance_url:
            provenance_url = f"{BDLAWS_BASE_URL}/act-details-{act_id}.html"

        logger.info(f"Processing Act ID {act_id} ({provenance_url})...")
        html_content = self.fetch_url_with_utf16_autodetect(provenance_url)
        parsed_data = self.parse_act_details_html(html_content, provenance_url)

        output_path = export_act_to_json(
            act_name=parsed_data["act_name"],
            sections=parsed_data["sections"],
            provenance_url=parsed_data["provenance_url"]
        )

        self.checkpoint_mgr.mark_completed(provenance_url, items_scraped=len(parsed_data["sections"]))
        return output_path

    def run_full_harvest(self, limit: int = None, max_workers: int = MAX_CONCURRENT_REQUESTS):
        """
        Crawls all Bangladesh Acts concurrently using thread pool workers.
        Integrates checkpoint manager for zero duplicate requests.
        """
        act_tuples = self.discover_all_act_ids()
        
        if limit:
            act_tuples = act_tuples[:limit]

        # Register tasks in checkpoint DB
        tasks_to_register = [(url, "bdlaws_act", act_id) for act_id, url, _ in act_tuples]
        self.checkpoint_mgr.register_tasks_batch(tasks_to_register)

        pending_tasks = self.checkpoint_mgr.get_pending_tasks(task_type="bdlaws_act")
        logger.info(f"Starting batch harvesting for {len(pending_tasks)} pending Acts (Workers: {max_workers})...")

        completed_count = 0
        failed_count = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {
                executor.submit(self.scrape_single_act, act_id, url): (act_id, url)
                for url, act_id in pending_tasks
            }

            for future in as_completed(future_to_task):
                act_id, url = future_to_task[future]
                try:
                    out_path = future.result()
                    completed_count += 1
                    logger.info(f"[{completed_count}/{len(pending_tasks)}] Scraped Act {act_id} -> {out_path.name}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error scraping Act {act_id} ({url}): {e}")
                    self.checkpoint_mgr.mark_failed(url, str(e))

        summary = self.checkpoint_mgr.get_summary()
        logger.info(f"Harvest completed. Total: {len(pending_tasks)} | Success: {completed_count} | Failed: {failed_count}")
        logger.info(f"Checkpoint summary: {summary}")

def main():
    parser = argparse.ArgumentParser(description="BDLaws Scrapling-Powered Web Harvester")
    parser.add_argument("--act-id", type=str, help="Scrape a single Act by ID (e.g. 180)")
    parser.add_argument("--limit", type=int, help="Limit number of Acts to harvest (e.g. 5)")
    parser.add_argument("--workers", type=int, default=MAX_CONCURRENT_REQUESTS, help="Concurrent worker threads")
    args = parser.parse_args()

    harvester = BDLawsHarvester()

    if args.act_id:
        out = harvester.scrape_single_act(args.act_id)
        print(f"Single Act scrape finished: {out}")
    else:
        harvester.run_full_harvest(limit=args.limit, max_workers=args.workers)

if __name__ == "__main__":
    main()
