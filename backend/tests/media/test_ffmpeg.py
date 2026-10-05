from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from musicsync.domain.ports import ProcessingOptions
from musicsync.domain.value_objects import Duration, MediaFormat, MediaPath, Quality
from musicsync.infrastructure.ffmpeg import FfmpegMediaProcessor
from musicsync.infrastructure.media_errors import MediaConversionError, MediaProbeError


def options(media_format: MediaFormat = MediaFormat.MP3) -> ProcessingOptions:
    return ProcessingOptions(media_format=media_format, quality=Quality(192))


def test_inspect_reads_audio_metadata_and_checksum(tmp_path: Path) -> None:
    source = tmp_path / "audio with spaces.wav"
    source.write_bytes(b"sample audio")
    expected_checksum = hashlib.sha256(source.read_bytes()).hexdigest()

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        assert command[0] == "ffprobe"
        assert command[-1] == str(source)
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps(
                {
                    "format": {"duration": "12.50", "bit_rate": "128000"},
                    "streams": [{"codec_type": "audio", "bit_rate": "96000"}],
                }
            ),
            "",
        )

    inspection = FfmpegMediaProcessor(runner=runner).inspect(MediaPath(str(source)))

    assert inspection.duration == Duration.from_seconds("12.50")
    assert inspection.bitrate_kbps == 96
    assert inspection.checksum == expected_checksum


def test_process_passes_paths_as_individual_arguments_and_returns_destination(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source [authorized].wav"
    destination = tmp_path / "nested output" / "song.mp3"
    source.write_bytes(b"source")
    commands: list[list[str]] = []

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        Path(command[-1]).write_bytes(b"converted")
        return subprocess.CompletedProcess(command, 0, "", "")

    output = FfmpegMediaProcessor(runner=runner).process(
        MediaPath(str(source)), MediaPath(str(destination)), options()
    )

    assert output == MediaPath(str(destination))
    assert destination.read_bytes() == b"converted"
    assert commands == [
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source),
            "-vn",
            "-codec:a",
            "libmp3lame",
            "-b:a",
            "192k",
            str(destination),
        ]
    ]


def test_validate_returns_false_for_media_without_audio(tmp_path: Path) -> None:
    source = tmp_path / "video.mp4"
    source.write_bytes(b"video")

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            command,
            0,
            json.dumps({"format": {"duration": "3"}, "streams": []}),
            "",
        )

    processor = FfmpegMediaProcessor(runner=runner)

    assert processor.validate(MediaPath(str(source))) is False
    with pytest.raises(MediaProbeError, match="audio stream"):
        processor.inspect(MediaPath(str(source)))


def test_process_removes_partial_output_when_ffmpeg_fails(tmp_path: Path) -> None:
    source = tmp_path / "source.wav"
    destination = tmp_path / "output.mp3"
    source.write_bytes(b"source")

    def runner(command: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        Path(command[-1]).write_bytes(b"partial")
        return subprocess.CompletedProcess(command, 1, "", "invalid input")

    with pytest.raises(MediaConversionError, match="invalid input"):
        FfmpegMediaProcessor(runner=runner).process(
            MediaPath(str(source)), MediaPath(str(destination)), options()
        )
    assert not destination.exists()
