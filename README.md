# pingbot

Dead-simple cron job monitor with Telegram alerts. Set up in 5 minutes.

## What it does

pingbot watches your cron jobs, backup scripts, and scheduled tasks. When something doesn't check in on time, you get a Telegram message. When it recovers, you get another one.

## Quick start

```bash
pip install pingbot
pingbot start --token YOUR_BOT_TOKEN
```

Then configure your cron jobs to ping:
```bash
curl -X POST https://your-pingbot.example.com/ping/my-daily-backup
```

## Features

- **Telegram alerts** — Get notified when jobs go late or die
- **Auto-recovery notices** — Know when things are back to normal
- **Simple HTTP API** — Any language, any platform. Just curl it
- **SQLite backend** — Zero dependencies, no database server needed
- **CLI management** — Register, list, delete jobs from the terminal

## How it works

```
Cron job ──ping──> pingbot API ──check loop──> Status DB
                                                    │
                                           Late/Dead? ──> Telegram alert
```

1. Jobs ping `/ping/{job_id}` on their schedule
2. A background monitor checks all jobs every N seconds
3. If a job hasn't pinged within its grace period, status goes LATE
4. If it's been dead too long, status goes DEAD
5. Status changes trigger Telegram messages

## CLI

```bash
# Start the server
pingbot start --token 123456:ABC-DEF

# Register a new job
pingbot register --name "Daily Backup" --interval 86400 --grace 3600

# List all jobs
pingbot list

# Delete a job
pingbot delete my-job-id
```

## API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ping/{job_id}` | Check in (returning "pong") |
| GET | `/health` | Health check |
| GET | `/jobs` | List all jobs and statuses |

## Configuration

| Env var | Description |
|---------|-------------|
| `PINGBOT_BOT_TOKEN` | Telegram bot token |

## Tech stack

Python, FastAPI, SQLite, httpx, Typer, Rich

## More tools

- [envyzer](https://github.com/shyh26/envyzer) — .env file validator and diff tool
- [shipnotes](https://github.com/shyh26/shipnotes) — changelog generator from git history
- [tokenalyzer](https://github.com/shyh26/tokenalyzer) — AI coding token usage & cost analyzer
