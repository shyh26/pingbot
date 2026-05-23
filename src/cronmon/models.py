from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum


class JobStatus(StrEnum):
    OK = "ok"
    LATE = "late"
    DEAD = "dead"


@dataclass
class Job:
    id: str
    name: str
    interval_seconds: int
    grace_seconds: int = 300
    last_ping: float = field(default_factory=time.time)
    status: JobStatus = JobStatus.OK
    telegram_chat_id: str = ""
    created_at: float = field(default_factory=time.time)

    @property
    def overdue_seconds(self) -> float:
        return time.time() - self.last_ping - self.interval_seconds

    @property
    def is_late(self) -> bool:
        return self.overdue_seconds > 0 and self.overdue_seconds < self.grace_seconds

    @property
    def is_dead(self) -> bool:
        return self.overdue_seconds >= self.grace_seconds
