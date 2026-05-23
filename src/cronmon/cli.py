from __future__ import annotations

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .serve import serve

cli = typer.Typer()
console = Console()


@cli.command()
def start(
    data_dir: Path = typer.Option("./data", help="Data directory for SQLite DB"),
    bot_token: str = typer.Option("", envvar="PINGBOT_BOT_TOKEN", help="Telegram bot token"),
    host: str = typer.Option("127.0.0.1", help="Host to bind"),
    port: int = typer.Option(8520, help="Port to bind"),
    check_interval: int = typer.Option(60, help="Seconds between health checks"),
) -> None:
    """Start the pingbot cron monitor."""
    serve(data_dir, bot_token=bot_token, check_interval=check_interval,
          host=host, port=port)


@cli.command()
def register(
    name: str = typer.Option(..., prompt="Job name"),
    interval_minutes: int = typer.Option(..., prompt="Expected interval (minutes)"),
    grace_minutes: int = typer.Option(5, prompt="Grace period (minutes)"),
    chat_id: str = typer.Option("", prompt="Telegram chat ID (optional)"),
    data_dir: Path = typer.Option("./data"),
) -> None:
    """Register a new cron job."""
    from .logic import init, register_job
    data_dir.mkdir(parents=True, exist_ok=True)
    init(data_dir / "pingbot.db")
    job = register_job(
        name=name,
        interval_seconds=interval_minutes * 60,
        grace_seconds=grace_minutes * 60,
        telegram_chat_id=chat_id,
    )
    console.print(f"[green]✓[/green] Job registered: [bold]{job.id}[/bold]")
    console.print(f"  Ping URL: [cyan]POST /ping/{job.id}[/cyan]")


@cli.command(name="list")
def list_jobs_cmd(data_dir: Path = typer.Option("./data")) -> None:
    """List all registered jobs."""
    from .logic import init, list_jobs
    data_dir.mkdir(parents=True, exist_ok=True)
    init(data_dir / "pingbot.db")

    table = Table(title="Pingbot Jobs")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Interval")
    table.add_column("Status")
    table.add_column("Overdue")

    for job in list_jobs():
        overdue = int(time.time() - job.last_ping - job.interval_seconds)
        table.add_row(
            job.id[:12],
            job.name,
            f"{job.interval_seconds // 60}m",
            job.status.value,
            f"{max(0, overdue)}s",
        )

    console.print(table)


@cli.command()
def delete(
    job_id: str = typer.Argument(..., help="Job ID to delete"),
    data_dir: Path = typer.Option("./data"),
) -> None:
    """Delete a registered job."""
    from .logic import init, delete_job
    data_dir.mkdir(parents=True, exist_ok=True)
    init(data_dir / "pingbot.db")
    delete_job(job_id)
    console.print(f"[green]✓[/green] Deleted: {job_id}")


def main() -> None:
    cli()
