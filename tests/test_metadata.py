"""Tests for media_organizer.core.metadata module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from media_organizer.core.metadata import MetadataManager
from media_organizer.config import AppConfig
from media_organizer.models import MediaMetadata, MetadataUpdateResult


class MockEditor:
    """Mock editor for testing MetadataManager."""

    def __init__(self, read_result=None, write_result=True):
        self.read_result = read_result or MediaMetadata()
        self.write_result = write_result
        self.read_called_with = None
        self.write_called_with = None

    @property
    def supported_extensions(self):
        return {".test"}

    def read(self, file_path):
        self.read_called_with = file_path
        return self.read_result

    def write(self, file_path, metadata):
        self.write_called_with = (file_path, metadata)
        return self.write_result


class TestMetadataManagerInit:
    """Tests for MetadataManager initialization."""

    def test_default_editors(self):
        """Test default editors are created."""
        manager = MetadataManager()
        extensions = manager.get_supported_extensions()
        assert ".mp4" in extensions
        assert ".m4v" in extensions
        assert ".mkv" in extensions

    def test_custom_editors(self):
        """Test custom editors can be provided."""
        mock_editor = MockEditor()
        manager = MetadataManager(editors={".custom": mock_editor})
        extensions = manager.get_supported_extensions()
        assert ".custom" in extensions
        assert ".mp4" not in extensions

    def test_custom_config(self):
        """Test custom config is used."""
        config = AppConfig(mkvpropedit_path="/custom/path")
        manager = MetadataManager(config=config)
        assert manager._config.mkvpropedit_path == "/custom/path"


class TestMetadataManagerReadMetadata:
    """Tests for MetadataManager.read_metadata method."""

    def test_read_with_matching_editor(self, tmp_path):
        """Test reading with matching editor."""
        expected_metadata = MediaMetadata(title="Test", season=1, episode=5)
        mock_editor = MockEditor(read_result=expected_metadata)

        manager = MetadataManager(editors={".mp4": mock_editor})
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        metadata = manager.read_metadata(file_path)

        assert metadata == expected_metadata
        assert mock_editor.read_called_with == file_path

    def test_read_unsupported_extension(self, tmp_path):
        """Test reading unsupported extension returns empty metadata."""
        mock_editor = MockEditor()
        manager = MetadataManager(editors={".mp4": mock_editor})

        file_path = tmp_path / "test.unknown"
        file_path.touch()

        metadata = manager.read_metadata(file_path)

        assert metadata == MediaMetadata()
        assert mock_editor.read_called_with is None

    def test_read_with_string_path(self, tmp_path):
        """Test reading with string path."""
        mock_editor = MockEditor(read_result=MediaMetadata(title="Test"))
        manager = MetadataManager(editors={".mp4": mock_editor})

        file_path = tmp_path / "test.mp4"
        file_path.touch()

        metadata = manager.read_metadata(str(file_path))

        assert metadata.title == "Test"


class TestMetadataManagerUpdateMetadata:
    """Tests for MetadataManager.update_metadata method."""

    def test_update_success(self, tmp_path, app_config):
        """Test successful metadata update."""
        mock_editor = MockEditor(write_result=True)
        manager = MetadataManager(editors={".mp4": mock_editor}, config=app_config)

        file_path = tmp_path / "test.mp4"
        file_path.touch()

        metadata = MediaMetadata(title="Show", genre="Action", year=2024)
        result = manager.update_metadata(file_path, metadata)

        assert result.success is True
        assert mock_editor.write_called_with is not None

    def test_update_failure(self, tmp_path, app_config):
        """Test failed metadata update."""
        mock_editor = MockEditor(write_result=False)
        manager = MetadataManager(editors={".mp4": mock_editor}, config=app_config)

        file_path = tmp_path / "test.mp4"
        file_path.touch()

        metadata = MediaMetadata(title="Show")
        result = manager.update_metadata(file_path, metadata)

        assert result.success is False
        assert result.error == "Editor write failed"

    def test_update_unsupported_extension(self, tmp_path, app_config):
        """Test update with unsupported extension."""
        mock_editor = MockEditor()
        manager = MetadataManager(editors={".mp4": mock_editor}, config=app_config)

        file_path = tmp_path / "test.unknown"
        file_path.touch()

        metadata = MediaMetadata(title="Show")
        result = manager.update_metadata(file_path, metadata)

        assert result.success is False
        assert "Unsupported file type" in result.error

    def test_update_with_dict(self, tmp_path, app_config):
        """Test update with dict instead of MediaMetadata."""
        mock_editor = MockEditor(write_result=True)
        manager = MetadataManager(editors={".mp4": mock_editor}, config=app_config)

        file_path = tmp_path / "test.mp4"
        file_path.touch()

        # Pass dict instead of MediaMetadata
        metadata_dict = {"title": "Show", "genre": "Comedy", "year": 2023}
        result = manager.update_metadata(file_path, metadata_dict)

        assert result.success is True

    def test_update_formats_title_with_episode(self, tmp_path, app_config):
        """Test title is formatted when season/episode provided."""
        mock_editor = MockEditor(write_result=True)
        manager = MetadataManager(editors={".mp4": mock_editor}, config=app_config)

        file_path = tmp_path / "test.mp4"
        file_path.touch()

        metadata = MediaMetadata(title="Show", season=1, episode=5)
        manager.update_metadata(file_path, metadata)

        # Check that the written metadata has formatted title
        written_path, written_metadata = mock_editor.write_called_with
        assert "S01" in written_metadata.title
        assert "EP005" in written_metadata.title

    def test_update_no_format_without_episode(self, tmp_path, app_config):
        """Test title not formatted when season/episode are 0."""
        mock_editor = MockEditor(write_result=True)
        manager = MetadataManager(editors={".mp4": mock_editor}, config=app_config)

        file_path = tmp_path / "test.mp4"
        file_path.touch()

        metadata = MediaMetadata(title="Show", season=0, episode=0)
        manager.update_metadata(file_path, metadata)

        written_path, written_metadata = mock_editor.write_called_with
        assert written_metadata.title == "Show"

    def test_update_exception_handling(self, tmp_path, app_config):
        """Test update handles exceptions."""
        mock_editor = MagicMock()
        mock_editor.write.side_effect = Exception("Write error")

        manager = MetadataManager(editors={".mp4": mock_editor}, config=app_config)

        file_path = tmp_path / "test.mp4"
        file_path.touch()

        metadata = MediaMetadata(title="Show")
        result = manager.update_metadata(file_path, metadata)

        assert result.success is False
        assert "Write error" in result.error

    def test_update_with_string_path(self, tmp_path, app_config):
        """Test update with string path."""
        mock_editor = MockEditor(write_result=True)
        manager = MetadataManager(editors={".mp4": mock_editor}, config=app_config)

        file_path = tmp_path / "test.mp4"
        file_path.touch()

        metadata = MediaMetadata(title="Show")
        result = manager.update_metadata(str(file_path), metadata)

        assert result.success is True


class TestMetadataManagerGetSupportedExtensions:
    """Tests for MetadataManager.get_supported_extensions method."""

    def test_returns_set(self):
        """Test returns a set of extensions."""
        manager = MetadataManager()
        extensions = manager.get_supported_extensions()
        assert isinstance(extensions, set)

    def test_contains_expected_extensions(self):
        """Test contains expected extensions."""
        manager = MetadataManager()
        extensions = manager.get_supported_extensions()
        assert ".mp4" in extensions
        assert ".mkv" in extensions

    def test_custom_editors_extensions(self):
        """Test returns extensions from custom editors."""
        mock_editor1 = MockEditor()
        mock_editor2 = MockEditor()

        manager = MetadataManager(editors={".custom1": mock_editor1, ".custom2": mock_editor2})
        extensions = manager.get_supported_extensions()

        assert extensions == {".custom1", ".custom2"}


class TestMetadataManagerEditorSelection:
    """Tests for editor selection logic."""

    def test_selects_correct_editor_mp4(self, tmp_path):
        """Test correct editor is selected for .mp4."""
        mp4_editor = MockEditor(read_result=MediaMetadata(title="MP4"))
        mkv_editor = MockEditor(read_result=MediaMetadata(title="MKV"))

        manager = MetadataManager(editors={".mp4": mp4_editor, ".mkv": mkv_editor})

        file_path = tmp_path / "test.mp4"
        file_path.touch()

        metadata = manager.read_metadata(file_path)

        assert metadata.title == "MP4"
        assert mp4_editor.read_called_with is not None
        assert mkv_editor.read_called_with is None

    def test_selects_correct_editor_mkv(self, tmp_path):
        """Test correct editor is selected for .mkv."""
        mp4_editor = MockEditor(read_result=MediaMetadata(title="MP4"))
        mkv_editor = MockEditor(read_result=MediaMetadata(title="MKV"))

        manager = MetadataManager(editors={".mp4": mp4_editor, ".mkv": mkv_editor})

        file_path = tmp_path / "test.mkv"
        file_path.touch()

        metadata = manager.read_metadata(file_path)

        assert metadata.title == "MKV"

    def test_case_insensitive_extension(self, tmp_path):
        """Test extension matching is case insensitive."""
        mock_editor = MockEditor(read_result=MediaMetadata(title="Test"))

        manager = MetadataManager(editors={".mp4": mock_editor})

        file_path = tmp_path / "test.MP4"
        file_path.touch()

        metadata = manager.read_metadata(file_path)

        assert metadata.title == "Test"
