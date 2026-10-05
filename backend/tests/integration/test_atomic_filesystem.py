from pathlib import Path

import pytest

from musicsync.domain.value_objects import JobId, MediaPath
from musicsync.infrastructure.filesystem import (
    DestinationExistsError,
    LocalFilesystemService,
    PathSecurityError,
)


def test_temp_checksum_atomic_move_and_cleanup(tmp_path: Path) -> None:
    service = LocalFilesystemService(tmp_path / "storage", tmp_path / "temp")
    job_id = JobId.new()
    temp_directory = service.create_temp_directory(job_id)
    temp_file = service.temporary.resolver.resolve(f"{temp_directory}/audio.bin")
    temp_file.write_bytes(b"authorized audio")

    checksum = service.checksum(MediaPath(f"{temp_directory}/audio.bin"))
    destination = service.atomic_move(
        MediaPath(f"{temp_directory}/audio.bin"),
        MediaPath("MUSIC/Artist/Album/song.mp3"),
    )

    final_path = tmp_path / "storage" / str(destination)
    assert final_path.read_bytes() == b"authorized audio"
    assert checksum.value
    assert not temp_file.exists()
    service.cleanup_temp_directory(temp_directory)
    assert not (tmp_path / "temp" / str(temp_directory)).exists()


def test_atomic_move_rejects_collision_without_creating_variant(tmp_path: Path) -> None:
    service = LocalFilesystemService(tmp_path / "storage", tmp_path / "temp")
    temp_directory = service.create_temp_directory(JobId.new())
    temp_file = service.temporary.resolver.resolve(f"{temp_directory}/audio.bin")
    temp_file.write_bytes(b"new")
    destination = tmp_path / "storage" / "MUSIC/song.mp3"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"existing")

    with pytest.raises(DestinationExistsError):
        service.atomic_move(
            MediaPath(f"{temp_directory}/audio.bin"),
            MediaPath("MUSIC/song.mp3"),
        )

    assert destination.read_bytes() == b"existing"
    assert not (destination.parent / "song (1).mp3").exists()


def test_cleanup_rejects_arbitrary_directory(tmp_path: Path) -> None:
    service = LocalFilesystemService(tmp_path / "storage", tmp_path / "temp")

    with pytest.raises(PathSecurityError):
        service.cleanup_temp_directory(MediaPath("other-directory"))
