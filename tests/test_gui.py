"""Tests for media_organizer.ui.gui module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from media_organizer.config import AppConfig
from media_organizer.models import MediaFile, MediaMetadata


class TestScanWorker:
    """Tests for ScanWorker thread."""

    def test_scan_worker_run_calls_scanner(self, tmp_path):
        """Test ScanWorker.run() calls scanner."""
        from media_organizer.ui.gui import ScanWorker

        mock_scanner = MagicMock()
        mock_scanner.scan_directory.return_value = []

        worker = ScanWorker(mock_scanner, tmp_path)
        worker.finished = MagicMock()

        worker.run()

        mock_scanner.scan_directory.assert_called_once_with(tmp_path)
        worker.finished.emit.assert_called_once()


class TestRenameWorker:
    """Tests for RenameWorker thread."""

    def test_rename_worker_processes_files(self, tmp_path):
        """Test RenameWorker processes each file."""
        from media_organizer.ui.gui import RenameWorker

        mock_renamer = MagicMock()
        mock_renamer.rename_file.return_value = MagicMock(success=True)

        file1 = tmp_path / "file1.mp4"
        file1.touch()
        # Files are now tuples of (row_index, MediaFile)
        files = [(0, MediaFile.from_path(file1))]

        worker = RenameWorker(files, mock_renamer, season=1, episode=1, episodic=True)
        worker.progress = MagicMock()
        worker.finished = MagicMock()

        worker.run()

        mock_renamer.rename_file.assert_called_once()
        worker.finished.emit.assert_called_once()

    def test_rename_worker_increments_episode_on_success(self, tmp_path):
        """Test episode increments after successful rename."""
        from media_organizer.ui.gui import RenameWorker

        mock_renamer = MagicMock()
        mock_renamer.rename_file.return_value = MagicMock(success=True)

        f1 = tmp_path / "f1.mp4"
        f2 = tmp_path / "f2.mp4"
        f1.touch()
        f2.touch()
        # Files are now tuples of (row_index, MediaFile)
        files = [
            (0, MediaFile.from_path(f1)),
            (1, MediaFile.from_path(f2)),
        ]

        worker = RenameWorker(files, mock_renamer, season=1, episode=5, episodic=True)
        worker.progress = MagicMock()
        worker.finished = MagicMock()

        worker.run()

        # Check episodes passed to rename_file
        calls = mock_renamer.rename_file.call_args_list
        assert calls[0][0][2] == 5  # First file: episode 5
        assert calls[1][0][2] == 6  # Second file: episode 6

    def test_rename_worker_no_increment_on_failure(self, tmp_path):
        """Test episode doesn't increment on failed rename."""
        from media_organizer.ui.gui import RenameWorker

        mock_renamer = MagicMock()
        mock_renamer.rename_file.return_value = MagicMock(success=False, error="Failed")

        f1 = tmp_path / "f1.mp4"
        f2 = tmp_path / "f2.mp4"
        f1.touch()
        f2.touch()
        # Files are now tuples of (row_index, MediaFile)
        files = [
            (0, MediaFile.from_path(f1)),
            (1, MediaFile.from_path(f2)),
        ]

        worker = RenameWorker(files, mock_renamer, season=1, episode=5, episodic=True)
        worker.progress = MagicMock()
        worker.finished = MagicMock()

        worker.run()

        # Both should use same episode since first failed
        calls = mock_renamer.rename_file.call_args_list
        assert calls[0][0][2] == 5
        assert calls[1][0][2] == 5


class TestMetadataWorker:
    """Tests for MetadataWorker thread."""

    def test_metadata_worker_updates_each_file(self, tmp_path):
        """Test MetadataWorker updates metadata for each file."""
        from media_organizer.ui.gui import MetadataWorker

        mock_manager = MagicMock()
        mock_manager.update_metadata.return_value = MagicMock(success=True)

        # Files are now tuples of (row_index, MediaFile)
        files = [
            (0, MediaFile.from_path(tmp_path / "f1.mp4")),
            (1, MediaFile.from_path(tmp_path / "f2.mp4")),
        ]

        metadata = MediaMetadata(title="Test", genre="Action")
        worker = MetadataWorker(files, mock_manager, metadata)
        worker.progress = MagicMock()
        worker.finished = MagicMock()

        worker.run()

        assert mock_manager.update_metadata.call_count == 2
        worker.finished.emit.assert_called_once()

    def test_metadata_worker_increments_episode(self, tmp_path):
        """Test MetadataWorker uses incrementing episode numbers."""
        from media_organizer.ui.gui import MetadataWorker

        mock_manager = MagicMock()
        mock_manager.update_metadata.return_value = MagicMock(success=True)

        # Files are now tuples of (row_index, MediaFile)
        files = [
            (0, MediaFile.from_path(tmp_path / "f1.mp4")),
            (1, MediaFile.from_path(tmp_path / "f2.mp4")),
        ]

        metadata = MediaMetadata(title="Test", season=1, episode=1)
        worker = MetadataWorker(files, mock_manager, metadata)
        worker.progress = MagicMock()
        worker.finished = MagicMock()

        worker.run()

        # Check episode numbers in metadata
        calls = mock_manager.update_metadata.call_args_list
        assert calls[0][0][1].episode == 1
        assert calls[1][0][1].episode == 2


class TestRunGui:
    """Tests for run_gui function."""

    def test_run_gui_creates_application(self, tmp_path):
        """Test run_gui creates QApplication."""
        with patch("media_organizer.ui.gui.QApplication") as mock_app_class:
            with patch("media_organizer.ui.gui.MediaOrganizerWindow") as mock_window:
                mock_app = MagicMock()
                mock_app_class.return_value = mock_app

                from media_organizer.ui.gui import run_gui
                run_gui(tmp_path, AppConfig())

                mock_app_class.assert_called_once()
                mock_app.exec.assert_called_once()

    def test_run_gui_creates_window(self, tmp_path):
        """Test run_gui creates MediaOrganizerWindow."""
        with patch("media_organizer.ui.gui.QApplication"):
            with patch("media_organizer.ui.gui.MediaOrganizerWindow") as mock_window_class:
                mock_window = MagicMock()
                mock_window_class.return_value = mock_window

                from media_organizer.ui.gui import run_gui
                run_gui(tmp_path, AppConfig())

                mock_window_class.assert_called_once()
                mock_window.show.assert_called_once()
