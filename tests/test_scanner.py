"""Tests for media_organizer.core.scanner module."""

import pytest
from pathlib import Path

from media_organizer.core.scanner import MediaScanner
from media_organizer.config import AppConfig


class TestMediaScannerInit:
    """Tests for MediaScanner initialization."""

    def test_default_config(self):
        """Test scanner uses default config when none provided."""
        scanner = MediaScanner()
        assert scanner.media_extensions == {".mp4", ".mkv", ".m4v", ".avi"}

    def test_custom_config(self):
        """Test scanner uses provided config."""
        config = AppConfig(media_extensions={".mp4", ".webm"})
        scanner = MediaScanner(config)
        assert scanner.media_extensions == {".mp4", ".webm"}

    def test_initial_scanned_files_empty(self):
        """Test scanned_files is initially empty."""
        scanner = MediaScanner()
        assert scanner.scanned_files == []


class TestMediaScannerScanDirectory:
    """Tests for MediaScanner.scan_directory method."""

    def test_scan_finds_media_files(self, temp_media_dir, app_config):
        """Test scanning finds media files."""
        scanner = MediaScanner(app_config)
        files = scanner.scan_directory(temp_media_dir)

        # Should find video1.mp4, video2.mkv, video3.m4v (not .txt or .jpg)
        assert len(files) == 3
        names = {f.original_name for f in files}
        assert "video1.mp4" in names
        assert "video2.mkv" in names
        assert "video3.m4v" in names

    def test_scan_excludes_non_media(self, temp_media_dir, app_config):
        """Test scanning excludes non-media files."""
        scanner = MediaScanner(app_config)
        files = scanner.scan_directory(temp_media_dir)

        names = {f.original_name for f in files}
        assert "document.txt" not in names
        assert "image.jpg" not in names

    def test_scan_empty_directory(self, tmp_path, app_config):
        """Test scanning empty directory returns empty list."""
        scanner = MediaScanner(app_config)
        files = scanner.scan_directory(tmp_path)
        assert files == []

    def test_scan_directory_no_media_files(self, tmp_path, app_config):
        """Test scanning directory with no media files."""
        (tmp_path / "doc.txt").touch()
        (tmp_path / "image.png").touch()

        scanner = MediaScanner(app_config)
        files = scanner.scan_directory(tmp_path)
        assert files == []

    def test_scan_nested_directories(self, temp_nested_media_dir, app_config):
        """Test scanning finds files in nested directories."""
        scanner = MediaScanner(app_config)
        files = scanner.scan_directory(temp_nested_media_dir)

        assert len(files) == 3
        names = {f.original_name for f in files}
        assert "root_video.mp4" in names
        assert "sub_video.mkv" in names
        assert "nested_video.mp4" in names

    def test_scan_nonexistent_directory(self, app_config):
        """Test scanning nonexistent directory returns empty list."""
        scanner = MediaScanner(app_config)
        files = scanner.scan_directory("/nonexistent/path")
        assert files == []

    def test_scan_file_instead_of_directory(self, tmp_path, app_config):
        """Test scanning a file instead of directory returns empty list."""
        file_path = tmp_path / "file.mp4"
        file_path.touch()

        scanner = MediaScanner(app_config)
        files = scanner.scan_directory(file_path)
        assert files == []

    def test_scan_with_string_path(self, temp_media_dir, app_config):
        """Test scanning with string path works."""
        scanner = MediaScanner(app_config)
        files = scanner.scan_directory(str(temp_media_dir))
        assert len(files) == 3

    def test_scan_updates_scanned_files(self, temp_media_dir, app_config):
        """Test scanning updates scanned_files property."""
        scanner = MediaScanner(app_config)
        scanner.scan_directory(temp_media_dir)
        assert len(scanner.scanned_files) == 3

    def test_scan_clears_previous_results(self, temp_media_dir, tmp_path, app_config):
        """Test scanning clears previous scan results."""
        scanner = MediaScanner(app_config)

        # First scan
        scanner.scan_directory(temp_media_dir)
        assert len(scanner.scanned_files) == 3

        # Second scan of empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        scanner.scan_directory(empty_dir)
        assert len(scanner.scanned_files) == 0

    def test_scan_returns_files_sorted_alphabetically(self, tmp_path, app_config):
        """Test scan returns files sorted alphabetically by name."""
        # Create files in non-alphabetical order
        (tmp_path / "zebra.mp4").touch()
        (tmp_path / "apple.mp4").touch()
        (tmp_path / "Banana.mp4").touch()  # Capital B to test case-insensitivity
        (tmp_path / "cherry.mp4").touch()

        scanner = MediaScanner(app_config)
        files = scanner.scan_directory(tmp_path)

        names = [f.original_name for f in files]
        # Should be sorted case-insensitively: apple, Banana, cherry, zebra
        assert names == ["apple.mp4", "Banana.mp4", "cherry.mp4", "zebra.mp4"]


class TestMediaScannerFilterByExtension:
    """Tests for MediaScanner.filter_by_extension method."""

    def test_filter_with_dot(self, temp_media_dir, app_config):
        """Test filtering with extension including dot."""
        scanner = MediaScanner(app_config)
        scanner.scan_directory(temp_media_dir)

        mp4_files = scanner.filter_by_extension(".mp4")
        assert len(mp4_files) == 1
        assert mp4_files[0].original_name == "video1.mp4"

    def test_filter_without_dot(self, temp_media_dir, app_config):
        """Test filtering with extension without dot."""
        scanner = MediaScanner(app_config)
        scanner.scan_directory(temp_media_dir)

        mkv_files = scanner.filter_by_extension("mkv")
        assert len(mkv_files) == 1
        assert mkv_files[0].original_name == "video2.mkv"

    def test_filter_no_matches(self, temp_media_dir, app_config):
        """Test filtering returns empty when no matches."""
        scanner = MediaScanner(app_config)
        scanner.scan_directory(temp_media_dir)

        avi_files = scanner.filter_by_extension(".avi")
        assert avi_files == []

    def test_filter_case_insensitive(self, tmp_path, app_config):
        """Test filtering is case insensitive."""
        (tmp_path / "video.MP4").touch()

        scanner = MediaScanner(app_config)
        scanner.scan_directory(tmp_path)

        files = scanner.filter_by_extension(".mp4")
        assert len(files) == 1


class TestMediaScannerErrorHandling:
    """Tests for MediaScanner error handling."""

    def test_scan_handles_permission_error(self, tmp_path, app_config, mocker):
        """Test scanning handles PermissionError gracefully."""
        scanner = MediaScanner(app_config)

        # Mock os.walk to raise PermissionError
        mocker.patch("os.walk", side_effect=PermissionError("Access denied"))

        files = scanner.scan_directory(tmp_path)
        assert files == []

    def test_scan_handles_os_error(self, tmp_path, app_config, mocker):
        """Test scanning handles OSError gracefully."""
        scanner = MediaScanner(app_config)

        # Mock os.walk to raise OSError
        mocker.patch("os.walk", side_effect=OSError("I/O error"))

        files = scanner.scan_directory(tmp_path)
        assert files == []


class TestMediaScannerUtilityMethods:
    """Tests for MediaScanner utility methods."""

    def test_get_file_count(self, temp_media_dir, app_config):
        """Test get_file_count returns correct count."""
        scanner = MediaScanner(app_config)
        scanner.scan_directory(temp_media_dir)
        assert scanner.get_file_count() == 3

    def test_get_file_count_empty(self, app_config):
        """Test get_file_count returns 0 when no files scanned."""
        scanner = MediaScanner(app_config)
        assert scanner.get_file_count() == 0

    def test_clear(self, temp_media_dir, app_config):
        """Test clear removes all scanned files."""
        scanner = MediaScanner(app_config)
        scanner.scan_directory(temp_media_dir)
        assert len(scanner.scanned_files) == 3

        scanner.clear()
        assert scanner.scanned_files == []
        assert scanner.get_file_count() == 0
