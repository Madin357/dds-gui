"""SQLite extractor — reads from mock institution source databases."""

import sqlite3
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SQLiteExtractor:
    def __init__(self, connection_config: dict):
        self.db_path = connection_config.get("db_path", "")

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def extract_all(self, table_name: str) -> list[dict]:
        """Full extraction — all rows from the table."""
        conn = self._connect()
        try:
            cursor = conn.execute(f"SELECT * FROM {table_name}")
            rows = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Extracted {len(rows)} rows from {table_name} (full)")
            return rows
        finally:
            conn.close()

    def extract_incremental(self, table_name: str, since: str) -> list[dict]:
        """Incremental extraction — rows updated since the given timestamp."""
        conn = self._connect()
        try:
            cursor = conn.execute(
                f"SELECT * FROM {table_name} WHERE updated_at > ?",
                (since,),
            )
            rows = [dict(row) for row in cursor.fetchall()]
            logger.info(f"Extracted {len(rows)} rows from {table_name} (incremental since {since})")
            return rows
        finally:
            conn.close()

    def get_row_count(self, table_name: str) -> int:
        conn = self._connect()
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        finally:
            conn.close()
