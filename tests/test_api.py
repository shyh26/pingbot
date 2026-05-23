import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import cronmon.logic
from cronmon.api import app


@pytest.fixture(autouse=True)
def _isolate():
    cronmon.logic._config = None


@pytest.fixture
def client():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
        db_path = Path(td) / "test.db"
        cronmon.logic.init(db_path)
        with TestClient(app) as c:
            yield c
        cronmon.logic.get_config().db.close()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.text == "ok"


def test_ping_creates_ack(client):
    job = cronmon.logic.register_job("test-job", 300)
    r = client.post(f"/ping/{job.id}")
    assert r.status_code == 200
    assert r.text == "ok"


def test_ping_unknown_job(client):
    r = client.post("/ping/nonexistent")
    assert r.status_code == 200


def test_list_jobs(client):
    cronmon.logic.register_job("job-a", 60)
    cronmon.logic.register_job("job-b", 120)
    r = client.get("/jobs")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
