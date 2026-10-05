from dataclasses import FrozenInstanceError

import pytest

from musicsync.domain.events import DownloadStarted, StorageConnected


def test_download_events_have_independent_job_ids() -> None:
    first = DownloadStarted()
    second = DownloadStarted()

    assert first.job_id != second.job_id
    with pytest.raises(FrozenInstanceError):
        first.job_id = second.job_id  # type: ignore[misc]


def test_storage_event_has_device_identity() -> None:
    event = StorageConnected()

    assert event.device_id.value == "unknown"
    assert event.event_id != event.device_id
