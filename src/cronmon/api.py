from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from .logic import get_config, ping


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    from .monitor import run_check_loop
    task = asyncio.create_task(run_check_loop())
    yield
    task.cancel()


app = FastAPI(title="pingbot", version="0.1.0", lifespan=lifespan)


@app.post("/ping/{job_id}", response_class=PlainTextResponse)
async def handle_ping(job_id: str) -> str:
    ping(job_id)
    return "ok"


@app.get("/health", response_class=PlainTextResponse)
async def health() -> str:
    return "ok"


@app.get("/jobs")
async def list_jobs():
    from .logic import list_jobs as _list
    return [{"id": j.id, "name": j.name, "status": j.status.value,
             "last_ping": j.last_ping, "interval": j.interval_seconds} for j in _list()]
