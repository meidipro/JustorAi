import sqlite3
import time
import logging
from pathlib import Path
from .scrapling_config import SCRAPER_DB_PATH

logger = logging.getLogger(__name__)

class ScraperCheckpointManager:
    """
    SQLite-backed state persistence for legal web scraper.
    Allows resilient resume, retry handling, and data integrity checks.
    """

    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else SCRAPER_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=30.0)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scrap_tasks (
                    url TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    act_id TEXT,
                    status TEXT NOT NULL, -- PENDING, COMPLETED, FAILED
                    retries INTEGER DEFAULT 0,
                    error_message TEXT,
                    items_scraped INTEGER DEFAULT 0,
                    last_updated REAL NOT NULL
                );
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_type_status ON scrap_tasks(task_type, status);
            """)
            conn.commit()

    def register_task(self, url: str, task_type: str = "bdlaws_act", act_id: str = None):
        """Registers a new URL task if not already present."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO scrap_tasks (url, task_type, act_id, status, last_updated)
                VALUES (?, ?, ?, 'PENDING', ?)
            """, (url, task_type, act_id, time.time()))
            conn.commit()

    def register_tasks_batch(self, tasks: list):
        """Batch registers tasks: list of (url, task_type, act_id)."""
        now = time.time()
        records = [(t[0], t[1], t[2], 'PENDING', now) for t in tasks]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR IGNORE INTO scrap_tasks (url, task_type, act_id, status, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, records)
            conn.commit()

    def is_completed(self, url: str) -> bool:
        """Returns True if task was successfully completed."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM scrap_tasks WHERE url = ?", (url,))
            row = cursor.fetchone()
            return row is not None and row[0] == "COMPLETED"

    def mark_completed(self, url: str, items_scraped: int = 0):
        """Marks task as completed."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scrap_tasks
                SET status = 'COMPLETED', items_scraped = ?, last_updated = ?
                WHERE url = ?
            """, (items_scraped, time.time(), url))
            conn.commit()

    def mark_failed(self, url: str, error_message: str):
        """Marks task as failed and increments retry counter."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE scrap_tasks
                SET status = 'FAILED', retries = retries + 1, error_message = ?, last_updated = ?
                WHERE url = ?
            """, (str(error_message), time.time(), url))
            conn.commit()

    def get_pending_tasks(self, task_type: str = "bdlaws_act", max_retries: int = 3):
        """Retrieves all pending or failed (under retry limit) tasks."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT url, act_id FROM scrap_tasks
                WHERE task_type = ? AND (status = 'PENDING' OR (status = 'FAILED' AND retries < ?))
            """, (task_type, max_retries))
            return cursor.fetchall()

    def get_summary(self):
        """Returns statistical summary of task statuses."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM scrap_tasks GROUP BY status")
            return dict(cursor.fetchall())
