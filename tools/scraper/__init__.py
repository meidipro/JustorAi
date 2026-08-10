"""
Justor AI Scrapling Legal Harvester Package
Automated scraping, auto-healing HTML parsing, UTF-16 decoding, and JSON export for bdlaws.minlaw.gov.bd and DLR Case Law.
"""
from .scrapling_config import BDLAWS_BASE_URL, OUTPUT_DIR, SCRAPER_DB_PATH
from .checkpoint_manager import ScraperCheckpointManager
from .json_exporter import export_act_to_json, export_caselaw_to_json
from .bdlaws_harvester import BDLawsHarvester
from .dlr_caselaw_harvester import DLRCaseLawHarvester

__all__ = [
    "BDLAWS_BASE_URL",
    "OUTPUT_DIR",
    "SCRAPER_DB_PATH",
    "ScraperCheckpointManager",
    "export_act_to_json",
    "export_caselaw_to_json",
    "BDLawsHarvester",
    "DLRCaseLawHarvester"
]
