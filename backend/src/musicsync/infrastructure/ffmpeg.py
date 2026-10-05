from __future__ import annotations

import hashlib
import json
import subprocess
from collections.abc import Callable, Sequence
from contextlib import suppress
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from musicsync.domain.ports import MediaInspection, MediaProcessorPort, ProcessingOptions
from musicsync.domain.value_objects import Duration, MediaFormat, MediaPath

from .media_errors import (
    MediaConversionError,
    MediaProbeError,
    MediaToolNotFoundError,
    MediaValidationError,
)

CommandRunner = Callable[..., subprocess.CompletedProcess[str]]


class FfmpegMediaProcessor(MediaProcessorPort):
    """Process and inspect audio through FFmpeg without invoking a shell.

    Paths are passed as individual subprocess arguments. User-controlled values
    therefore cannot become shell syntax, even when they contain spaces or
    special characters.
    """

    def __init__(
        self,
        *,
        ffmpeg_binary: str = "ffmpeg",
        ffprobe_binary: str = "ffprobe",
        runner: CommandRunner | None = None,
    ) -> None:
        self._ffmpeg_binary = ffmpeg_binary
        self._ffprobe_binary = ffprobe_binary
        self._runner = runner or subprocess.run

    def process(
        self,
        source: MediaPath,
        destination: MediaPath,
        options: ProcessingOptions,
    ) -> MediaPath:
        source_path = Path(source.value)
        destination_path = Path(destination.value)
        if not source_path.is_file():
            raise MediaValidationError(f"Source media file does not exist: {source.value}")
        if destination_path == source_path:
            raise MediaConversionError("Source and destination media paths must differ")
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        command = [
            self._ffmpeg_binary,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(source_path),
            "-vn",
            *self._codec_arguments(options),
            str(destination_path),
        ]
        result = self._run(command)
        if result.returncode != 0:
            self._remove_partial_output(destination_path)
            detail = (result.stderr or "").strip() or "unknown FFmpeg error"
            raise MediaConversionError(f"FFmpeg conversion failed: {detail}")
        if not destination_path.is_file() or destination_path.stat().st_size == 0:
            raise MediaConversionError("FFmpeg completed without producing a valid output file")
        return MediaPath(str(destination_path))

    def inspect(self, path: MediaPath) -> MediaInspection:
        media_path = Path(path.value)
        if not media_path.is_file():
            raise MediaProbeError(f"Media file does not exist: {path.value}")
        command = [
            self._ffprobe_binary,
            "-v",
            "error",
            "-show_entries",
            "format=duration,bit_rate:stream=codec_type,bit_rate",
            "-of",
            "json",
            str(media_path),
        ]
        result = self._run(command)
        if result.returncode != 0:
            detail = (result.stderr or "").strip() or "unknown FFprobe error"
            raise MediaProbeError(f"FFprobe inspection failed: {detail}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise MediaProbeError("FFprobe returned invalid JSON") from exc

        streams = payload.get("streams", [])
        audio_streams = [stream for stream in streams if stream.get("codec_type") == "audio"]
        if not audio_streams:
            raise MediaProbeError("Media file does not contain an audio stream")
        duration = self._duration(payload)
        bitrate = self._bitrate(audio_streams, payload.get("format", {}))
        return MediaInspection(
            duration=Duration.from_seconds(duration),
            bitrate_kbps=bitrate,
            checksum=self._checksum(media_path),
        )

    def validate(self, path: MediaPath) -> bool:
        try:
            self.inspect(path)
        except (MediaProbeError, MediaToolNotFoundError):
            return False
        return True

    def _run(self, command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        try:
            return self._runner(
                list(command),
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise MediaToolNotFoundError(f"Media tool is not available: {command[0]}") from exc
        except OSError as exc:
            raise MediaToolNotFoundError(f"Could not execute media tool: {command[0]}") from exc

    @staticmethod
    def _codec_arguments(options: ProcessingOptions) -> list[str]:
        if options.media_format is MediaFormat.MP3:
            return ["-codec:a", "libmp3lame", "-b:a", f"{options.quality.bitrate_kbps}k"]
        if options.media_format is MediaFormat.FLAC:
            return ["-codec:a", "flac"]
        if options.media_format is MediaFormat.WAV:
            return ["-codec:a", "pcm_s16le"]
        raise MediaConversionError(f"Unsupported media format: {options.media_format}")

    @staticmethod
    def _duration(payload: dict[str, Any]) -> Decimal:
        raw_duration = payload.get("format", {}).get("duration")
        if raw_duration is None:
            raise MediaProbeError("FFprobe did not return media duration")
        try:
            duration = Decimal(str(raw_duration))
        except (InvalidOperation, ValueError) as exc:
            raise MediaProbeError("FFprobe returned an invalid media duration") from exc
        if duration < 0:
            raise MediaProbeError("FFprobe returned a negative media duration")
        return duration

    @staticmethod
    def _bitrate(streams: list[dict[str, Any]], media_format: dict[str, Any]) -> int | None:
        raw_bitrate = streams[0].get("bit_rate") or media_format.get("bit_rate")
        if raw_bitrate is None:
            return None
        try:
            bits_per_second = int(raw_bitrate)
        except (TypeError, ValueError):
            return None
        return max(1, round(bits_per_second / 1000))

    @staticmethod
    def _checksum(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as media_file:
            for chunk in iter(lambda: media_file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _remove_partial_output(path: Path) -> None:
        with suppress(OSError):
            path.unlink(missing_ok=True)
