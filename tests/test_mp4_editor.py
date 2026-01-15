"""Tests for media_organizer.editors.mp4_editor module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from media_organizer.editors.mp4_editor import MP4Editor
from media_organizer.models import MediaMetadata


class TestMP4EditorInit:
    """Tests for MP4Editor initialization."""

    def test_supported_extensions(self):
        """Test supported extensions are correct."""
        editor = MP4Editor()
        assert editor.supported_extensions == {".mp4", ".m4v"}


class TestMP4EditorRead:
    """Tests for MP4Editor.read method."""

    def test_read_all_metadata(self, tmp_path):
        """Test reading all metadata fields."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()
        mock_mp4.__contains__ = lambda self, key: key in {
            "\xa9nam", "tvsn", "tves", "\xa9gen", "\xa9day"
        }
        mock_mp4.get.side_effect = lambda key, default: {
            "\xa9nam": ["Test Title"],
            "tvsn": [2],
            "tves": [10],
            "\xa9gen": ["Action"],
            "\xa9day": ["2024"],
        }.get(key, default)

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            metadata = editor.read(file_path)

        assert metadata.title == "Test Title"
        assert metadata.season == 2
        assert metadata.episode == 10
        assert metadata.genre == "Action"
        assert metadata.year == 2024

    def test_read_missing_metadata(self, tmp_path):
        """Test reading file with no metadata."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()
        mock_mp4.__contains__ = lambda self, key: False
        mock_mp4.get.return_value = None

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            metadata = editor.read(file_path)

        assert metadata.title == ""
        assert metadata.season == 0
        assert metadata.episode == 0
        assert metadata.genre == ""
        assert metadata.year == 0

    def test_read_partial_metadata(self, tmp_path):
        """Test reading file with only some metadata."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()
        mock_mp4.__contains__ = lambda self, key: key == "\xa9nam"
        mock_mp4.get.side_effect = lambda key, default: {
            "\xa9nam": ["Only Title"],
        }.get(key, default)

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            metadata = editor.read(file_path)

        assert metadata.title == "Only Title"
        assert metadata.season == 0

    def test_read_year_with_full_date(self, tmp_path):
        """Test reading year from full date format."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()
        mock_mp4.__contains__ = lambda self, key: key == "\xa9day"
        mock_mp4.get.side_effect = lambda key, default: {
            "\xa9day": ["2024-06-15"],
        }.get(key, default)

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            metadata = editor.read(file_path)

        assert metadata.year == 2024

    def test_read_year_invalid_format(self, tmp_path):
        """Test reading year with invalid format defaults to 0."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()
        mock_mp4.__contains__ = lambda self, key: key == "\xa9day"
        mock_mp4.get.side_effect = lambda key, default: {
            "\xa9day": ["invalid"],
        }.get(key, default)

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            metadata = editor.read(file_path)

        assert metadata.year == 0

    def test_read_empty_lists(self, tmp_path):
        """Test reading when metadata lists are empty."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()
        mock_mp4.__contains__ = lambda self, key: key == "\xa9nam"
        mock_mp4.get.side_effect = lambda key, default: {
            "\xa9nam": [],
        }.get(key, default)

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            metadata = editor.read(file_path)

        assert metadata.title == ""

    def test_read_exception_returns_empty(self, tmp_path):
        """Test read returns empty metadata on exception."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        with patch("mutagen.mp4.MP4", side_effect=Exception("Error")):
            editor = MP4Editor()
            metadata = editor.read(file_path)

        assert metadata == MediaMetadata()


class TestMP4EditorWrite:
    """Tests for MP4Editor.write method."""

    def test_write_all_metadata(self, tmp_path):
        """Test writing all metadata fields."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            metadata = MediaMetadata(
                title="New Title",
                season=3,
                episode=15,
                genre="Comedy",
                year=2023,
            )
            result = editor.write(file_path, metadata)

        assert result is True
        mock_mp4.__setitem__.assert_any_call("\xa9nam", "New Title")
        mock_mp4.__setitem__.assert_any_call("tvsn", [3])
        mock_mp4.__setitem__.assert_any_call("tves", [15])
        mock_mp4.__setitem__.assert_any_call("\xa9gen", "Comedy")
        mock_mp4.__setitem__.assert_any_call("\xa9day", ["2023"])
        mock_mp4.save.assert_called_once()

    def test_write_partial_metadata(self, tmp_path):
        """Test writing only title (other fields 0/empty)."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            metadata = MediaMetadata(title="Only Title")
            result = editor.write(file_path, metadata)

        assert result is True
        mock_mp4.__setitem__.assert_called_once_with("\xa9nam", "Only Title")

    def test_write_skips_zero_values(self, tmp_path):
        """Test that zero/empty values are skipped."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            metadata = MediaMetadata(title="Title", season=0, episode=0, genre="", year=0)
            editor.write(file_path, metadata)

        # Should only set title
        assert mock_mp4.__setitem__.call_count == 1

    def test_write_exception_returns_false(self, tmp_path):
        """Test write returns False on exception."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        with patch("mutagen.mp4.MP4", side_effect=Exception("Error")):
            editor = MP4Editor()
            metadata = MediaMetadata(title="Title")
            result = editor.write(file_path, metadata)

        assert result is False

    def test_write_save_called(self, tmp_path):
        """Test that save() is called after writing."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            editor.write(file_path, MediaMetadata(title="Test"))

        mock_mp4.save.assert_called_once()


class TestMP4EditorContextManager:
    """Tests for MP4Editor._open_mp4 context manager."""

    def test_context_manager_yields_mp4(self, tmp_path):
        """Test context manager yields MP4 object."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()

        mock_mp4 = MagicMock()

        with patch("mutagen.mp4.MP4", return_value=mock_mp4):
            editor = MP4Editor()
            with editor._open_mp4(file_path) as mp4:
                assert mp4 is mock_mp4
