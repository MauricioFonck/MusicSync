from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path, PurePosixPath

from musicsync.domain.entities import DownloadItem, DownloadJob, MediaFile, StorageDevice, Track
from musicsync.domain.ports import (
    DownloaderPort,
    FileSystemPort,
    MediaProcessorPort,
    ProcessingOptions,
)
from musicsync.domain.services import StoragePathService
from musicsync.domain.value_objects import DownloadStatus, MediaPath

from .download_orchestrator import DownloadOrchestrator

# Temp files live on the destination device so the final move is a same-volume rename.
TEMP_DIRNAME = ".musicsync-tmp"

FilesystemFactory = Callable[[Path, Path], FileSystemPort]
JobListener = Callable[[DownloadJob], None]
MediaRecorder = Callable[[Track, MediaFile], None]


class SyncPipeline:
    """Download, transcode, validate, checksum and atomically place tracks on a device."""

    def __init__(
        self,
        downloader: DownloaderPort,
        media: MediaProcessorPort,
        filesystem_for: FilesystemFactory,
        options: ProcessingOptions,
        *,
        orchestrator: DownloadOrchestrator | None = None,
        on_change: JobListener | None = None,
        record: MediaRecorder | None = None,
    ) -> None:
        self._downloader = downloader
        self._media = media
        self._filesystem_for = filesystem_for
        self._options = options
        self._orchestrator = orchestrator or DownloadOrchestrator()
        self._paths = StoragePathService()
        self._on_change = on_change or (lambda job: None)
        self._record = record or (lambda track, media_file: None)

    def run(self, job: DownloadJob, device: StorageDevice | None) -> DownloadJob:
        if job.status in {DownloadStatus.CANCELLED, DownloadStatus.COMPLETED}:
            return job
        if device is None or not device.is_available:
            for item in job.items:
                if item.status is not DownloadStatus.COMPLETED:
                    item.mark_failed("Storage device is not available")
            job.finish()
            self._on_change(job)
            return job

        root = Path(device.mount_point)
        filesystem = self._filesystem_for(root, root / TEMP_DIRNAME)
        try:
            tracks = self._downloader.analyze(job.source_url).tracks
        except Exception as exc:
            for item in job.items:
                if item.status is not DownloadStatus.COMPLETED:
                    item.mark_failed(str(exc) or "Source analysis failed")
            job.finish()
            self._on_change(job)
            return job
        self._skip_already_synced(job, tracks, root)
        temp_dir = filesystem.create_temp_directory(job.id)
        temp_path = root / TEMP_DIRNAME / temp_dir.value
        try:
            self._orchestrator.run(
                job,
                self._downloader,
                lambda index: str(temp_path / f"{index}.source"),
                finalize=lambda item, track, downloaded: self._finalize(
                    job, item, track, downloaded, filesystem, root, temp_dir
                ),
                tracks=tracks,
            )
        finally:
            filesystem.cleanup_temp_directory(temp_dir)
            self._on_change(job)
        return job

    def _skip_already_synced(self, job: DownloadJob, tracks: tuple[Track, ...], root: Path) -> None:
        by_id = {track.id: track for track in tracks}
        for item in job.items:
            track = by_id.get(item.track_id)
            if item.status is DownloadStatus.COMPLETED or track is None:
                continue
            destination = self._destination(track)
            if (root / destination.value).is_file():
                item.status = DownloadStatus.COMPLETED
                item.error = None
                item.output_path = destination
                item.update_progress(100)

    def _finalize(
        self,
        job: DownloadJob,
        item: DownloadItem,
        track: Track,
        downloaded: str,
        filesystem: FileSystemPort,
        root: Path,
        temp_dir: MediaPath,
    ) -> None:
        item.status = DownloadStatus.PROCESSING
        item.update_progress(max(item.progress, 50))
        self._on_change(job)

        extension = self._options.media_format.value
        # Item ids are "<job>-<index>"; keep only the index so temp paths stay short.
        name = item.id.rsplit("-", 1)[-1]
        relative_processed = MediaPath(f"{temp_dir.value}/{name}.{extension}")
        processed = MediaPath(str(root / TEMP_DIRNAME / relative_processed.value))
        options = replace(self._options, metadata=self._metadata(track))
        self._media.process(MediaPath(downloaded), processed, options)
        Path(downloaded).unlink(missing_ok=True)
        inspection = self._media.inspect(processed)
        checksum = filesystem.checksum(relative_processed)

        final = filesystem.atomic_move(relative_processed, self._destination(track))
        item.mark_completed(final, checksum)
        self._record(
            track,
            MediaFile(
                id=str(uuid.uuid4()),
                track_id=track.id,
                path=final,
                filename=PurePosixPath(final.value).name,
                extension=extension,
                size=(root / final.value).stat().st_size,
                duration=inspection.duration,
                bitrate=inspection.bitrate_kbps,
                checksum=checksum,
            ),
        )
        self._on_change(job)

    def _destination(self, track: Track) -> MediaPath:
        return self._paths.build_track_path(track, self._options.media_format)

    @staticmethod
    def _metadata(track: Track) -> tuple[tuple[str, str], ...]:
        values = {
            "title": track.title,
            "artist": track.artist,
            "album": track.album,
            "album_artist": track.album_artist,
            "track": str(track.track_number) if track.track_number else None,
            "disc": str(track.disc_number) if track.disc_number else None,
            "genre": track.genre,
            "date": str(track.release_date.year) if track.release_date else None,
        }
        return tuple((key, value) for key, value in values.items() if value)
