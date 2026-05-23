import time

import pytest

from cronmon.models import Job, JobStatus


def test_job_is_ok_when_within_interval():
    job = Job(id="1", name="test", interval_seconds=300, last_ping=time.time())
    assert job.status == JobStatus.OK
    assert not job.is_late
    assert not job.is_dead


def test_job_is_late_when_past_interval_but_within_grace():
    job = Job(id="2", name="test", interval_seconds=300, grace_seconds=600,
              last_ping=time.time() - 400)
    assert job.is_late
    assert not job.is_dead


def test_job_is_dead_when_past_grace():
    job = Job(id="3", name="test", interval_seconds=300, grace_seconds=600,
              last_ping=time.time() - 1000)
    assert job.is_dead


def test_job_overdue_seconds():
    job = Job(id="4", name="test", interval_seconds=300,
              last_ping=time.time() - 350)
    assert job.overdue_seconds == pytest.approx(50, abs=2)
