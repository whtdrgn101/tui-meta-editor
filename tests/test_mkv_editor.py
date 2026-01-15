"""Tests for media_organizer.editors.mkv_editor module."""

import subprocess
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from media_organizer.editors.mkv_editor import MKVEditor
from media_organizer.models import MediaMetadata


class TestMKVEditorInit:
    """Tests for MKVEditor initialization."""

    def test_default_mkvpropedit_path(self):
        """Test default mkvpropedit path."""
        editor = MKVEditor()
        assert editor._mkvpropedit == "mkvpropedit"

    def test_custom_mkvpropedit_path(self):
        """Test custom mkvpropedit path."""
        editor = MKVEditor("/usr/local/bin/mkvpropedit")
        assert editor._mkvpropedit == "/usr/local/bin/mkvpropedit"

    def test_supported_extensions(self):
        """Test supported extensions are correct."""
        editor = MKVEditor()
        assert editor.supported_extensions == {".mkv"}


class TestMKVEditorRead:
    """Tests for MKVEditor.read method."""

    def test_read_title_found(self, tmp_path):
        """Test reading title from mkvinfo output."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
+ Segment information
| + Title: Test Show Title
| + Duration: 3600
"""

        with patch("subprocess.run", return_value=mock_result):
            editor = MKVEditor()
            metadata = editor.read(file_path)

        assert metadata.title == "Test Show Title"

    def test_read_no_title(self, tmp_path):
        """Test reading when no title present."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
+ Segment information
| + Duration: 3600
"""

        with patch("subprocess.run", return_value=mock_result):
            editor = MKVEditor()
            metadata = editor.read(file_path)

        assert metadata.title == ""

    def test_read_mkvinfo_not_found(self, tmp_path):
        """Test reading when mkvinfo not installed."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        with patch("subprocess.run", side_effect=FileNotFoundError):
            editor = MKVEditor()
            metadata = editor.read(file_path)

        assert metadata == MediaMetadata()

    def test_read_timeout(self, tmp_path):
        """Test reading handles timeout."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("mkvinfo", 30)):
            editor = MKVEditor()
            metadata = editor.read(file_path)

        assert metadata == MediaMetadata()

    def test_read_mkvinfo_failure(self, tmp_path):
        """Test reading when mkvinfo returns error."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            editor = MKVEditor()
            metadata = editor.read(file_path)

        assert metadata.title == ""

    def test_read_exception(self, tmp_path):
        """Test reading handles general exception."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        with patch("subprocess.run", side_effect=Exception("Unknown error")):
            editor = MKVEditor()
            metadata = editor.read(file_path)

        assert metadata == MediaMetadata()


class TestMKVEditorWrite:
    """Tests for MKVEditor.write method."""

    def test_write_success(self, tmp_path):
        """Test successful metadata write."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            editor = MKVEditor()
            metadata = MediaMetadata(title="New Title")
            result = editor.write(file_path, metadata)

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "mkvpropedit" in call_args
        assert str(file_path) in call_args
        assert "title=New Title" in call_args

    def test_write_empty_title_skips(self, tmp_path):
        """Test writing empty title skips mkvpropedit call."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        with patch("subprocess.run") as mock_run:
            editor = MKVEditor()
            metadata = MediaMetadata(title="")
            result = editor.write(file_path, metadata)

        assert result is True
        mock_run.assert_not_called()

    def test_write_mkvpropedit_not_found(self, tmp_path):
        """Test writing when mkvpropedit not installed."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        with patch("subprocess.run", side_effect=FileNotFoundError):
            editor = MKVEditor()
            metadata = MediaMetadata(title="Title")
            result = editor.write(file_path, metadata)

        assert result is False

    def test_write_timeout(self, tmp_path):
        """Test writing handles timeout."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("mkvpropedit", 60)):
            editor = MKVEditor()
            metadata = MediaMetadata(title="Title")
            result = editor.write(file_path, metadata)

        assert result is False

    def test_write_mkvpropedit_failure(self, tmp_path):
        """Test writing when mkvpropedit returns error."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Error: file not found"

        with patch("subprocess.run", return_value=mock_result):
            editor = MKVEditor()
            metadata = MediaMetadata(title="Title")
            result = editor.write(file_path, metadata)

        assert result is False

    def test_write_exception(self, tmp_path):
        """Test writing handles general exception."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        with patch("subprocess.run", side_effect=Exception("Unknown error")):
            editor = MKVEditor()
            metadata = MediaMetadata(title="Title")
            result = editor.write(file_path, metadata)

        assert result is False

    def test_write_uses_custom_path(self, tmp_path):
        """Test writing uses custom mkvpropedit path."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            editor = MKVEditor("/custom/mkvpropedit")
            metadata = MediaMetadata(title="Title")
            editor.write(file_path, metadata)

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "/custom/mkvpropedit"


class TestMKVEditorIsAvailable:
    """Tests for MKVEditor.is_available method."""

    def test_is_available_true(self):
        """Test is_available returns True when mkvpropedit works."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result):
            editor = MKVEditor()
            assert editor.is_available() is True

    def test_is_available_false_not_found(self):
        """Test is_available returns False when mkvpropedit not found."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            editor = MKVEditor()
            assert editor.is_available() is False

    def test_is_available_false_timeout(self):
        """Test is_available returns False on timeout."""
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("mkvpropedit", 10)):
            editor = MKVEditor()
            assert editor.is_available() is False

    def test_is_available_false_nonzero_exit(self):
        """Test is_available returns False on non-zero exit."""
        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch("subprocess.run", return_value=mock_result):
            editor = MKVEditor()
            assert editor.is_available() is False

    def test_is_available_checks_version(self):
        """Test is_available runs --version command."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            editor = MKVEditor()
            editor.is_available()

        call_args = mock_run.call_args[0][0]
        assert "--version" in call_args
