from __future__ import annotations

from pathlib import Path

from .api import app
from .logic import init


def serve(data_dir: Path, bot_token: str = "", check_interval: int = 60,
          host: str = "127.0.0.1", port: int = 8520) -> None:
    import uvicorn

    data_dir.mkdir(parents=True, exist_ok=True)
    init(data_dir / "pingbot.db", bot_token=bot_token, check_interval=check_interval)
    uvicorn.run(app, host=host, port=port)
