"""Tests for media_organizer.__main__ module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from media_organizer.__main__ import main


class TestMainCLI:
    """Tests for the main CLI entry point."""

    def test_main_with_valid_root(self, tmp_path):
        """Test main launches GUI with valid root path."""
        runner = CliRunner()
        with patch("media_organizer.ui.gui.run_gui") as mock_run_gui:
            result = runner.invoke(main, ["--root", str(tmp_path)])
            assert result.exit_code == 0
            mock_run_gui.assert_called_once()

    def test_main_with_debug_flag(self, tmp_path):
        """Test main enables debug logging with --debug."""
        runner = CliRunner()
        with patch("media_organizer.ui.gui.run_gui"):
            with patch("media_organizer.__main__.setup_logging") as mock_setup:
                result = runner.invoke(main, ["--root", str(tmp_path), "--debug"])
                assert result.exit_code == 0
                mock_setup.assert_called_once()
                # Check debug level was passed
                call_kwargs = mock_setup.call_args
                assert call_kwargs[1]["level"] == "DEBUG"

    def test_main_uses_default_root_when_not_specified(self):
        """Test main uses config default root when --root not specified."""
        runner = CliRunner()
        with patch("media_organizer.ui.gui.run_gui") as mock_run_gui:
            with patch("media_organizer.__main__.AppConfig") as mock_config_class:
                mock_config = MagicMock()
                mock_config.default_root = Path("/test/default")
                mock_config.log_level = "INFO"
                mock_config_class.from_env.return_value = mock_config

                result = runner.invoke(main, [])
                assert result.exit_code == 0
                # run_gui should be called with the default root
                call_args = mock_run_gui.call_args[0]
                assert call_args[0] == Path("/test/default")

    def test_main_pyside6_import_error(self, tmp_path):
        """Test main shows helpful message when PySide6 not installed."""
        runner = CliRunner()

        def raise_import_error(*args, **kwargs):
            raise ImportError("No module named 'PySide6'")

        with patch("media_organizer.ui.gui.run_gui", side_effect=raise_import_error):
            result = runner.invoke(main, ["--root", str(tmp_path)])
            # Check error message is shown
            assert "PySide6 is required" in result.output

    def test_main_other_import_error(self, tmp_path):
        """Test main shows import error for non-PySide6 errors."""
        runner = CliRunner()

        def raise_import_error(*args, **kwargs):
            raise ImportError("No module named 'something_else'")

        with patch("media_organizer.ui.gui.run_gui", side_effect=raise_import_error):
            result = runner.invoke(main, ["--root", str(tmp_path)])
            # Check error message is shown
            assert "Import error" in result.output

    def test_main_general_exception(self, tmp_path):
        """Test main handles general exceptions."""
        runner = CliRunner()

        def raise_error(*args, **kwargs):
            raise RuntimeError("Something went wrong")

        with patch("media_organizer.ui.gui.run_gui", side_effect=raise_error):
            result = runner.invoke(main, ["--root", str(tmp_path)])
            # Check error message is shown
            assert "Error:" in result.output
            assert "Something went wrong" in result.output

    def test_main_invalid_root_path(self):
        """Test main fails with non-existent root path."""
        runner = CliRunner()
        result = runner.invoke(main, ["--root", "/nonexistent/path"])
        assert result.exit_code != 0
