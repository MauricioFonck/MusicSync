from musicsync.domain.ports import (
    DownloaderPort,
    DownloadJobRepository,
    MediaFileRepository,
    MediaProcessorPort,
    StorageDevicePort,
    TrackRepository,
)


def test_domain_ports_are_protocols() -> None:
    for port in (
        DownloadJobRepository,
        DownloaderPort,
        MediaFileRepository,
        MediaProcessorPort,
        StorageDevicePort,
        TrackRepository,
    ):
        assert getattr(port, "_is_protocol", False)
