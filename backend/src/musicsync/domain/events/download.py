from __future__ import annotations

from dataclasses import dataclass, field

from musicsync.domain.events.base import DomainEvent
from musicsync.domain.value_objects import JobId, TrackId


@dataclass(frozen=True, slots=True)
class DownloadRequested(DomainEvent):
    job_id: JobId = field(default_factory=JobId.new)


@dataclass(frozen=True, slots=True)
class DownloadStarted(DomainEvent):
    job_id: JobId = field(default_factory=JobId.new)


@dataclass(frozen=True, slots=True)
class TrackDownloaded(DomainEvent):
    job_id: JobId = field(default_factory=JobId.new)
    track_id: TrackId = field(default_factory=TrackId.new)


@dataclass(frozen=True, slots=True)
class TrackProcessed(DomainEvent):
    job_id: JobId = field(default_factory=JobId.new)
    track_id: TrackId = field(default_factory=TrackId.new)


@dataclass(frozen=True, slots=True)
class DuplicateDetected(DomainEvent):
    job_id: JobId = field(default_factory=JobId.new)
    track_id: TrackId = field(default_factory=TrackId.new)


@dataclass(frozen=True, slots=True)
class TrackSkipped(DomainEvent):
    job_id: JobId = field(default_factory=JobId.new)
    track_id: TrackId = field(default_factory=TrackId.new)


@dataclass(frozen=True, slots=True)
class DownloadFailed(DomainEvent):
    job_id: JobId = field(default_factory=JobId.new)
    track_id: TrackId | None = None
    reason: str = ""


@dataclass(frozen=True, slots=True)
class DownloadCompleted(DomainEvent):
    job_id: JobId = field(default_factory=JobId.new)
