from __future__ import annotations

import asyncio
import contextlib
import time

from .logic import get_config
from .models import JobStatus
from .notify import send_alert, send_recovery


async def run_check_loop() -> None:
    """Background loop that checks all jobs and sends alerts."""
    cfg = get_config()
    while True:
        await asyncio.sleep(cfg.check_interval)
        for job in cfg.db.get_all_jobs():
            prev = job.status
            if job.is_dead:
                job.status = JobStatus.DEAD
            elif job.is_late:
                job.status = JobStatus.LATE
            else:
                job.status = JobStatus.OK

            if job.status != prev:
                cfg.db.update_status(job.id, job.status)
                if cfg.bot_token and job.telegram_chat_id:
                    if job.status == JobStatus.OK:
                        with contextlib.suppress(Exception):
                            await send_recovery(job, cfg.bot_token)
                    else:
                        with contextlib.suppress(Exception):
                            await send_alert(job, cfg.bot_token)
