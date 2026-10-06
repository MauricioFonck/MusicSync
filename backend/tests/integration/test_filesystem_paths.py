from pathlib import Path

import pytest

from musicsync.domain.value_objects import MediaPath
from musicsync.infrastructure.filesystem import PathSecurityError, SafePathResolver


def test_resolver_accepts_relative_paths_inside_root(tmp_path: Path) -> None:
    resolver = SafePathResolver(tmp_path / "root")

    resolved = resolver.resolve(MediaPath("MUSIC/Artist/song.mp3"))

    assert resolved == (tmp_path / "root" / "MUSIC/Artist/song.mp3").resolve()


@pytest.mark.parametrize(
    "unsafe",
    [
        "../outside.txt",
        "MUSIC/../../outside.txt",
        "/etc/passwd",
        "C:\\Windows\\system.ini",
        "MUSIC\\..\\secret",
    ],
)
def test_resolver_rejects_traversal_and_absolute_paths(tmp_path: Path, unsafe: str) -> None:
    resolver = SafePathResolver(tmp_path / "root")

    with pytest.raises(PathSecurityError):
        resolver.resolve(unsafe)


def test_resolver_rejects_symlinked_components(tmp_path: Path) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    outside.mkdir()
    root.mkdir()
    try:
        (root / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Creating symlinks requires extra privileges on this platform")
    resolver = SafePathResolver(root)

    with pytest.raises(PathSecurityError):
        resolver.resolve("link/file.mp3")


def test_resolver_rejects_excessive_paths(tmp_path: Path) -> None:
    resolver = SafePathResolver(tmp_path / "root", max_path_length=20)

    with pytest.raises(PathSecurityError):
        resolver.resolve("a" * 21)
