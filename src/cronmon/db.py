from __future__ import annotations

import sqlite3
import time
from collections.abc import Sequence
from pathlib import Path

from .models import Job, JobStatus

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    interval_seconds INTEGER NOT NULL,
    grace_seconds INTEGER NOT NULL DEFAULT 300,
    last_ping REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'ok',
    telegram_chat_id TEXT NOT NULL DEFAULT '',
    created_at REAL NOT NULL
);
"""


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def get_job(self, job_id: str) -> Job | None:
        row = self._conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return _row_to_job(row) if row else None

    def get_all_jobs(self) -> Sequence[Job]:
        rows = self._conn.execute("SELECT * FROM jobs").fetchall()
        return [_row_to_job(r) for r in rows]

    def upsert_job(self, job: Job) -> None:
        self._conn.execute(
            """INSERT OR REPLACE INTO jobs
               (id, name, interval_seconds, grace_seconds, last_ping, status, telegram_chat_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (job.id, job.name, job.interval_seconds, job.grace_seconds,
             job.last_ping, job.status.value, job.telegram_chat_id, job.created_at),
        )
        self._conn.commit()

    def update_ping(self, job_id: str) -> None:
        self._conn.execute(
            "UPDATE jobs SET last_ping = ?, status = 'ok' WHERE id = ?",
            (time.time(), job_id),
        )
        self._conn.commit()

    def update_status(self, job_id: str, status: JobStatus) -> None:
        self._conn.execute(
            "UPDATE jobs SET status = ? WHERE id = ?",
            (status.value, job_id),
        )
        self._conn.commit()

    def delete_job(self, job_id: str) -> None:
        self._conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()


def _row_to_job(row: sqlite3.Row) -> Job:
    return Job(
        id=row["id"],
        name=row["name"],
        interval_seconds=row["interval_seconds"],
        grace_seconds=row["grace_seconds"],
        last_ping=row["last_ping"],
        status=JobStatus(row["status"]),
        telegram_chat_id=row["telegram_chat_id"],
        created_at=row["created_at"],
    )
