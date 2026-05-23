import tempfile
from pathlib import Path

from cronmon.db import Database
from cronmon.models import Job, JobStatus


def _db(path: Path) -> Database:
    return Database(path)


def test_upsert_and_get_job():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        db = _db(Path(td) / "test.db")
        job = Job(id="abc", name="test-job", interval_seconds=300)
        db.upsert_job(job)
        got = db.get_job("abc")
        assert got is not None
        assert got.name == "test-job"
        assert got.interval_seconds == 300
        db.close()


def test_update_ping_resets_status():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        db = _db(Path(td) / "test.db")
        job = Job(id="abc", name="test", interval_seconds=300)
        db.upsert_job(job)
        db.update_status("abc", JobStatus.DEAD)
        db.update_ping("abc")
        got = db.get_job("abc")
        assert got is not None
        assert got.status == JobStatus.OK
        db.close()


def test_get_all_jobs():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        db = _db(Path(td) / "test.db")
        db.upsert_job(Job(id="a", name="a", interval_seconds=60))
        db.upsert_job(Job(id="b", name="b", interval_seconds=120))
        assert len(list(db.get_all_jobs())) == 2
        db.close()


def test_delete_job():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        db = _db(Path(td) / "test.db")
        db.upsert_job(Job(id="x", name="x", interval_seconds=60))
        db.delete_job("x")
        assert db.get_job("x") is None
        db.close()
