"""POST /transcribe and sarvam.task_engine.whisper_fallback.transcribe.

Genuine absence-path tests (Task 19, D5): this dev environment has no `whisper`
(openai-whisper) installed by design -- see sarvam/task_engine/whisper_fallback.py.
These tests assert the real, unmonkeypatched 503 outcome, matching the pattern already
used by test_orchestrator.py's mlagents-learn absence-path test.
"""
import io

import pytest
from fastapi.testclient import TestClient

from orchestrator import db, jobs
from orchestrator.service import app
from sarvam.task_engine import whisper_fallback


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("TWINFORGE_DATA", str(tmp_path / "data"))
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "twinforge.db"))
    monkeypatch.delenv("SARVAM_API_KEY", raising=False)
    return TestClient(app)


def test_whisper_fallback_raises_runtime_error_when_whisper_is_absent():
    with pytest.raises(ModuleNotFoundError):
        import whisper  # noqa: F401 -- confirms the absence this test relies on

    with pytest.raises(RuntimeError, match="no offline transcription backend available"):
        whisper_fallback.transcribe("/does/not/matter.wav")


def test_transcribe_endpoint_returns_503_when_whisper_is_absent(client):
    """Real, unmonkeypatched path -- must actually 503, not skip."""
    response = client.post(
        "/transcribe",
        files={"file": ("clip.wav", io.BytesIO(b"not really audio"), "audio/wav")},
        params={"lang": "hi"},
    )

    assert response.status_code == 503
    body = response.json()["detail"]
    assert body["error"] == "no transcription backend available"
    assert "no offline transcription backend available" in body["detail"]


def test_transcribe_failure_marks_the_job_failed_not_stuck_running(client, monkeypatch):
    """Earlier task's lesson: an error response must not leave a job stuck 'running'."""
    seen_job_ids = []
    real_create_job = jobs.create_job

    def _create_job(stage):
        seen_job_ids.append(real_create_job(stage))
        return seen_job_ids[-1]

    monkeypatch.setattr(jobs, "create_job", _create_job)

    response = client.post(
        "/transcribe", files={"file": ("clip.wav", io.BytesIO(b"nope"), "audio/wav")})

    assert response.status_code == 503
    assert len(seen_job_ids) == 1
    job = jobs.get_job(seen_job_ids[0])
    assert job["status"] == "failed"
    assert job["status"] != "running"
