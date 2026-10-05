import hashlib
from pathlib import Path

from musicsync.infrastructure.filesystem import Sha256ChecksumService


def test_sha256_checksum_matches_reference_for_large_file(tmp_path: Path) -> None:
    payload = (b"music-sync\x00" * 250_000) + b"end"
    source = tmp_path / "audio.bin"
    source.write_bytes(payload)

    expected = hashlib.sha256(payload).hexdigest()
    checksum = Sha256ChecksumService(chunk_size=4096).calculate(source)

    assert checksum.value == expected
