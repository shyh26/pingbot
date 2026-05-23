from __future__ import annotations

import httpx

from .models import Job, JobStatus

ALERT_EMOJI: dict[JobStatus, str] = {
    JobStatus.LATE: "⚠️",
    JobStatus.DEAD: "🔴",
}


async def send_alert(job: Job, bot_token: str) -> None:
    emoji = ALERT_EMOJI.get(job.status, "")
    overdue = int(job.overdue_seconds)
    mins = overdue // 60

    text = (
        f"{emoji} *{job.name}* is {job.status.value.upper()}\n"
        f"Expected every {_fmt_seconds(job.interval_seconds)}\n"
        f"Last ping: {mins} min ago\n"
        f"Job ID: `{job.id}`"
    )

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": job.telegram_chat_id,
                "text": text,
                "parse_mode": "Markdown",
            },
        )


async def send_recovery(job: Job, bot_token: str) -> None:
    text = f"✅ *{job.name}* is back to normal\nJob ID: `{job.id}`"
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": job.telegram_chat_id, "text": text, "parse_mode": "Markdown"},
        )


def _fmt_seconds(s: int) -> str:
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m"
    return f"{s // 3600}h"
