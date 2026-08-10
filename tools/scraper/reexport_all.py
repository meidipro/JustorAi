import sqlite3
import re
import logging
from pathlib import Path
from tools.scraper.checkpoint_manager import ScraperCheckpointManager
from tools.scraper.bdlaws_harvester import BDLawsHarvester
from tools.scraper.scrapling_config import SCRAPER_DB_PATH, OUTPUT_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Reexporter")

def reexport_all():
    """
    Clears failed/unnamed duplicates and re-fetches or re-exports all completed act URLs
    with distinct act_<id>_...json filenames.
    """
    checkpoint_mgr = ScraperCheckpointManager()
    
    with sqlite3.connect(SCRAPER_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT url, act_id FROM scrap_tasks WHERE task_type = 'bdlaws_act' AND status = 'COMPLETED'")
        rows = cursor.fetchall()

    logger.info(f"Re-exporting {len(rows)} completed Bangladesh Acts into distinct act_<id>_...json files...")

    # Reset tasks to PENDING so harvester writes distinct files
    with sqlite3.connect(SCRAPER_DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE scrap_tasks SET status = 'PENDING' WHERE task_type = 'bdlaws_act' AND status = 'COMPLETED'")
        conn.commit()

    harvester = BDLawsHarvester(checkpoint_mgr)
    harvester.run_full_harvest(max_workers=15)

if __name__ == "__main__":
    reexport_all()
