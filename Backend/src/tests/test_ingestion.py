"""
Unit and integration tests for Ingestion Job Lifecycle and n8n Callback processing.
"""

import pytest
import pytest_asyncio
from src.rag.components.data_processor.ingestion import IngestionJobManager
from src.integrations.n8n import N8NIntegrationClient
from src.schemas.ingestion import IngestionCallbackPayload


def test_job_manager_lifecycle():
    mgr = IngestionJobManager()
    job = mgr.create_job(url="https://example.com/test", source_id="src_test_1")

    assert job.status == "QUEUED"
    assert job.url == "https://example.com/test"

    # Advance state
    updated = mgr.update_job(job.job_id, status="FETCHING")
    assert updated.status == "FETCHING"
    assert updated.started_at is not None

    # Complete job
    completed = mgr.update_job(
        job.job_id,
        status="COMPLETED",
        canonical_url="https://example.com/test",
        word_count=500,
        chunk_count=3
    )
    assert completed.status == "COMPLETED"
    assert completed.chunk_count == 3
    assert completed.completed_at is not None


def test_n8n_secret_verification():
    client = N8NIntegrationClient(callback_secret="my-super-secret-token")
    assert client.verify_callback_secret("my-super-secret-token") is True
    assert client.verify_callback_secret("wrong-token") is False
    assert client.verify_callback_secret(None) is False
