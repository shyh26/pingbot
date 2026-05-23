from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from .db import Database
from .models import Job, JobStatus


@dataclass
class Config:
    db: Database
    bot_token: str = ""
    check_interval: int = 60
    base_url: str = ""


_config: Config | None = None


def get_config() -> Config:
    if _config is None:
        raise RuntimeError("pingbot not initialized")
    return _config


def init(db_path: Path, bot_token: str = "", check_interval: int = 60) -> Config:
    global _config
    _config = Config(
        db=Database(db_path),
        bot_token=bot_token,
        check_interval=check_interval,
    )
    return _config


def register_job(name: str, interval_seconds: int, grace_seconds: int = 300,
                 telegram_chat_id: str = "") -> Job:
    cfg = get_config()
    job = Job(
        id=secrets.token_hex(8),
        name=name,
        interval_seconds=interval_seconds,
        grace_seconds=grace_seconds,
        telegram_chat_id=telegram_chat_id,
    )
    cfg.db.upsert_job(job)
    return job


def ping(job_id: str) -> None:
    cfg = get_config()
    cfg.db.update_ping(job_id)


def list_jobs() -> list[Job]:
    return list(get_config().db.get_all_jobs())


def delete_job(job_id: str) -> None:
    get_config().db.delete_job(job_id)
