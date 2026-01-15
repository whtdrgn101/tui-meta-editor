"""Shared pytest fixtures for Media Organizer tests."""

import pytest
from pathlib import Path

from media_organizer.config import AppConfig
from media_organizer.models import MediaFile, MediaMetadata


@pytest.fixture
def app_config():
    """Default test configuration."""
    return AppConfig(
        default_year=2024,
        default_season=1,
        default_episode=1,
        episode_padding=3,
    )


@pytest.fixture
def sample_metadata():
    """Sample MediaMetadata for tests."""
    return MediaMetadata(
        title="Test Show",
        season=1,
        episode=5,
        genre="Action",
        year=2024,
    )


@pytest.fixture
def temp_media_dir(tmp_path):
    """Create temp directory with sample media files."""
    (tmp_path / "video1.mp4").touch()
    (tmp_path / "video2.mkv").touch()
    (tmp_path / "video3.m4v").touch()
    (tmp_path / "document.txt").touch()
    (tmp_path / "image.jpg").touch()
    return tmp_path


@pytest.fixture
def temp_nested_media_dir(tmp_path):
    """Create temp directory with nested structure and media files."""
    # Root level
    (tmp_path / "root_video.mp4").touch()

    # Subdirectory
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "sub_video.mkv").touch()

    # Nested subdirectory
    nested = subdir / "nested"
    nested.mkdir()
    (nested / "nested_video.mp4").touch()

    return tmp_path


@pytest.fixture
def mock_mp4_instance(mocker):
    """Create a mock MP4 instance with tag data."""
    instance = mocker.MagicMock()
    instance.get.return_value = None
    instance.__contains__ = lambda self, key: False
    return instance


@pytest.fixture
def mock_mp4_class(mocker, mock_mp4_instance):
    """Mock the mutagen MP4 class."""
    mock_class = mocker.patch("media_organizer.editors.mp4_editor.MP4")
    mock_class.return_value = mock_mp4_instance
    return mock_class


@pytest.fixture
def mock_subprocess_run(mocker):
    """Mock subprocess.run for MKV operations."""
    return mocker.patch("subprocess.run")
