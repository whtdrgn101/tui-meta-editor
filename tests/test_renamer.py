"""Tests for media_organizer.core.renamer module."""

import pytest
from pathlib import Path

from media_organizer.core.renamer import MediaRenamer
from media_organizer.config import AppConfig


class TestMediaRenamerInit:
    """Tests for MediaRenamer initialization."""

    def test_init_with_title(self):
        """Test renamer initializes with title."""
        renamer = MediaRenamer("Test Show")
        assert renamer.title == "Test Show"

    def test_init_with_config(self):
        """Test renamer uses provided config."""
        config = AppConfig(episode_padding=2)
        renamer = MediaRenamer("Show", config)
        assert renamer.generate_episode_name(1, 5) == "Show S01 EP05"

    def test_title_property_setter(self):
        """Test title can be changed via property."""
        renamer = MediaRenamer("Original")
        renamer.title = "Updated"
        assert renamer.title == "Updated"


class TestMediaRenamerGenerateEpisodeName:
    """Tests for MediaRenamer.generate_episode_name method."""

    def test_default_format(self, app_config):
        """Test generating episode name with default format."""
        renamer = MediaRenamer("Test Show", app_config)
        result = renamer.generate_episode_name(1, 5)
        assert result == "Test Show S01 EP005"

    def test_season_padding(self, app_config):
        """Test season number is zero-padded."""
        renamer = MediaRenamer("Show", app_config)
        assert "S01" in renamer.generate_episode_name(1, 1)
        assert "S09" in renamer.generate_episode_name(9, 1)
        assert "S10" in renamer.generate_episode_name(10, 1)

    def test_episode_padding_3_digits(self, app_config):
        """Test episode number is zero-padded to 3 digits with default config."""
        renamer = MediaRenamer("Show", app_config)
        assert "EP001" in renamer.generate_episode_name(1, 1)
        assert "EP099" in renamer.generate_episode_name(1, 99)
        assert "EP100" in renamer.generate_episode_name(1, 100)

    def test_episode_padding_2_digits(self):
        """Test episode number is zero-padded to 2 digits."""
        config = AppConfig(episode_padding=2)
        renamer = MediaRenamer("Show", config)
        assert "EP01" in renamer.generate_episode_name(1, 1)
        assert "EP99" in renamer.generate_episode_name(1, 99)
        assert "EP100" in renamer.generate_episode_name(1, 100)


class TestMediaRenamerGenerateNewName:
    """Tests for MediaRenamer.generate_new_name method."""

    def test_episodic_name(self, tmp_path, app_config):
        """Test generating episodic filename."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer("Test Show", app_config)
        directory, new_name = renamer.generate_new_name(file_path, 1, 5, episodic=True)

        assert directory == tmp_path
        assert new_name == "Test Show S01 EP005.mp4"

    def test_non_episodic_name(self, tmp_path, app_config):
        """Test generating non-episodic filename (just title)."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer("Movie Title", app_config)
        directory, new_name = renamer.generate_new_name(file_path, 1, 1, episodic=False)

        assert directory == tmp_path
        assert new_name == "Movie Title.mp4"

    def test_preserves_extension(self, tmp_path, app_config):
        """Test original file extension is preserved."""
        for ext in [".mp4", ".mkv", ".m4v", ".avi"]:
            file_path = tmp_path / f"original{ext}"
            file_path.touch()

            renamer = MediaRenamer("Show", app_config)
            _, new_name = renamer.generate_new_name(file_path, 1, 1)

            assert new_name.endswith(ext)

    def test_with_string_path(self, tmp_path, app_config):
        """Test works with string path."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer("Show", app_config)
        directory, new_name = renamer.generate_new_name(str(file_path), 1, 1)

        assert directory == tmp_path


class TestMediaRenamerRenameFile:
    """Tests for MediaRenamer.rename_file method."""

    def test_rename_success(self, tmp_path, app_config):
        """Test successful file rename."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer("Test Show", app_config)
        result = renamer.rename_file(file_path, 1, 5)

        assert result.success is True
        assert result.new_path == tmp_path / "Test Show S01 EP005.mp4"
        assert result.new_path.exists()
        assert not file_path.exists()

    def test_rename_non_episodic(self, tmp_path, app_config):
        """Test rename with episodic=False."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer("Movie", app_config)
        result = renamer.rename_file(file_path, 1, 1, episodic=False)

        assert result.success is True
        assert result.new_path == tmp_path / "Movie.mp4"

    def test_rename_nonexistent_file(self, tmp_path, app_config):
        """Test rename fails for nonexistent file."""
        file_path = tmp_path / "nonexistent.mp4"

        renamer = MediaRenamer("Show", app_config)
        result = renamer.rename_file(file_path, 1, 1)

        assert result.success is False
        assert "does not exist" in result.error

    def test_rename_target_exists(self, tmp_path, app_config):
        """Test rename fails when target file already exists."""
        # Create source file
        source = tmp_path / "original.mp4"
        source.touch()

        # Create target file (what the rename would produce)
        target = tmp_path / "Show S01 EP001.mp4"
        target.touch()

        renamer = MediaRenamer("Show", app_config)
        result = renamer.rename_file(source, 1, 1)

        assert result.success is False
        assert "already exists" in result.error
        # Original should still exist
        assert source.exists()

    def test_rename_same_name(self, tmp_path, app_config):
        """Test rename when file already has target name (idempotent)."""
        file_path = tmp_path / "Show S01 EP001.mp4"
        file_path.touch()

        renamer = MediaRenamer("Show", app_config)
        result = renamer.rename_file(file_path, 1, 1)

        # Should succeed (same source and target is allowed)
        assert result.success is True
        assert file_path.exists()

    def test_rename_with_string_path(self, tmp_path, app_config):
        """Test rename works with string path."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer("Show", app_config)
        result = renamer.rename_file(str(file_path), 1, 1)

        assert result.success is True

    def test_rename_multiple_files_increments(self, tmp_path, app_config):
        """Test renaming multiple files with incrementing episodes."""
        files = []
        for i in range(3):
            f = tmp_path / f"file{i}.mp4"
            f.touch()
            files.append(f)

        renamer = MediaRenamer("Show", app_config)

        for i, file_path in enumerate(files, start=1):
            result = renamer.rename_file(file_path, 1, i)
            assert result.success is True

        # Verify all files exist with correct names
        assert (tmp_path / "Show S01 EP001.mp4").exists()
        assert (tmp_path / "Show S01 EP002.mp4").exists()
        assert (tmp_path / "Show S01 EP003.mp4").exists()

    def test_rename_preserves_directory(self, tmp_path, app_config):
        """Test rename keeps file in same directory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        file_path = subdir / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer("Show", app_config)
        result = renamer.rename_file(file_path, 1, 1)

        assert result.success is True
        assert result.new_path.parent == subdir

    def test_rename_permission_error(self, tmp_path, app_config, mocker):
        """Test rename handles PermissionError."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        mocker.patch("os.rename", side_effect=PermissionError("Access denied"))

        renamer = MediaRenamer("Show", app_config)
        result = renamer.rename_file(file_path, 1, 1)

        assert result.success is False
        assert "Permission denied" in result.error

    def test_rename_os_error(self, tmp_path, app_config, mocker):
        """Test rename handles OSError."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        mocker.patch("os.rename", side_effect=OSError("Disk full"))

        renamer = MediaRenamer("Show", app_config)
        result = renamer.rename_file(file_path, 1, 1)

        assert result.success is False
        assert "OS error" in result.error

    def test_rename_with_2_digit_padding(self, tmp_path):
        """Test rename produces 2-digit episode padding."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        config = AppConfig(episode_padding=2)
        renamer = MediaRenamer("Test Show", config)
        result = renamer.rename_file(file_path, 1, 5)

        assert result.success is True
        assert result.new_path == tmp_path / "Test Show S01 EP05.mp4"
        assert result.new_path.exists()

    def test_rename_with_3_digit_padding(self, tmp_path):
        """Test rename produces 3-digit episode padding."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        config = AppConfig(episode_padding=3)
        renamer = MediaRenamer("Test Show", config)
        result = renamer.rename_file(file_path, 1, 5)

        assert result.success is True
        assert result.new_path == tmp_path / "Test Show S01 EP005.mp4"
        assert result.new_path.exists()

    def test_rename_multiple_with_2_digit_padding(self, tmp_path):
        """Test batch rename with 2-digit padding."""
        files = []
        for i in range(3):
            f = tmp_path / f"file{i}.mp4"
            f.touch()
            files.append(f)

        config = AppConfig(episode_padding=2)
        renamer = MediaRenamer("Show", config)

        for i, file_path in enumerate(files, start=1):
            result = renamer.rename_file(file_path, 1, i)
            assert result.success is True

        # Verify all files exist with correct 2-digit padding
        assert (tmp_path / "Show S01 EP01.mp4").exists()
        assert (tmp_path / "Show S01 EP02.mp4").exists()
        assert (tmp_path / "Show S01 EP03.mp4").exists()


class TestMediaRenamerYearInFilename:
    """Tests for MediaRenamer year in filename feature."""

    def test_init_with_year_parameters(self):
        """Test renamer initializes with year parameters."""
        renamer = MediaRenamer(
            "Test Movie",
            year=2002,
            include_year_in_filename=True,
        )
        assert renamer.year == 2002
        assert renamer.include_year_in_filename is True

    def test_year_property_setter(self):
        """Test year can be changed via property."""
        renamer = MediaRenamer("Movie")
        renamer.year = 2024
        assert renamer.year == 2024

    def test_include_year_property_setter(self):
        """Test include_year_in_filename can be changed via property."""
        renamer = MediaRenamer("Movie")
        renamer.include_year_in_filename = True
        assert renamer.include_year_in_filename is True

    def test_generate_new_name_non_episodic_with_year(self, tmp_path, app_config):
        """Test generating non-episodic filename with year."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer(
            "Movie Title",
            config=app_config,
            year=2002,
            include_year_in_filename=True,
        )
        directory, new_name = renamer.generate_new_name(file_path, 1, 1, episodic=False)

        assert directory == tmp_path
        assert new_name == "Movie Title (2002).mp4"

    def test_generate_new_name_non_episodic_without_year_flag(self, tmp_path, app_config):
        """Test generating non-episodic filename without year flag."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer(
            "Movie Title",
            config=app_config,
            year=2002,
            include_year_in_filename=False,  # Year provided but flag is False
        )
        directory, new_name = renamer.generate_new_name(file_path, 1, 1, episodic=False)

        assert new_name == "Movie Title.mp4"

    def test_generate_new_name_episodic_ignores_year(self, tmp_path, app_config):
        """Test generating episodic filename ignores year setting."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer(
            "Show Title",
            config=app_config,
            year=2002,
            include_year_in_filename=True,
        )
        directory, new_name = renamer.generate_new_name(file_path, 1, 5, episodic=True)

        # Episodic should still use episode format, not year
        assert new_name == "Show Title S01 EP005.mp4"
        assert "(2002)" not in new_name

    def test_rename_non_episodic_with_year(self, tmp_path, app_config):
        """Test successful rename with year in filename."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer(
            "Test Movie",
            config=app_config,
            year=2002,
            include_year_in_filename=True,
        )
        result = renamer.rename_file(file_path, 1, 1, episodic=False)

        assert result.success is True
        assert result.new_path == tmp_path / "Test Movie (2002).mp4"
        assert result.new_path.exists()
        assert not file_path.exists()

    def test_rename_with_m4v_extension_and_year(self, tmp_path, app_config):
        """Test rename preserves m4v extension with year."""
        file_path = tmp_path / "original.m4v"
        file_path.touch()

        renamer = MediaRenamer(
            "Test Movie",
            config=app_config,
            year=2024,
            include_year_in_filename=True,
        )
        result = renamer.rename_file(file_path, 1, 1, episodic=False)

        assert result.success is True
        assert result.new_path.suffix == ".m4v"
        assert result.new_path.name == "Test Movie (2024).m4v"

    def test_rename_multiple_movies_same_year(self, tmp_path, app_config):
        """Test renaming multiple movies with same year fails for second."""
        file1 = tmp_path / "movie1.mp4"
        file2 = tmp_path / "movie2.mp4"
        file1.touch()
        file2.touch()

        renamer = MediaRenamer(
            "Same Movie",
            config=app_config,
            year=2002,
            include_year_in_filename=True,
        )

        result1 = renamer.rename_file(file1, 1, 1, episodic=False)
        assert result1.success is True

        result2 = renamer.rename_file(file2, 1, 1, episodic=False)
        assert result2.success is False
        assert "already exists" in result2.error

    def test_rename_with_year_already_in_filename(self, tmp_path, app_config):
        """Test renaming when target already has year (idempotent)."""
        file_path = tmp_path / "Test Movie (2002).mp4"
        file_path.touch()

        renamer = MediaRenamer(
            "Test Movie",
            config=app_config,
            year=2002,
            include_year_in_filename=True,
        )
        result = renamer.rename_file(file_path, 1, 1, episodic=False)

        # Should succeed (same source and target)
        assert result.success is True
        assert file_path.exists()

    def test_rename_with_mkv_extension_and_year(self, tmp_path, app_config):
        """Test rename preserves mkv extension with year."""
        file_path = tmp_path / "original.mkv"
        file_path.touch()

        renamer = MediaRenamer(
            "Test Movie",
            config=app_config,
            year=1999,
            include_year_in_filename=True,
        )
        result = renamer.rename_file(file_path, 1, 1, episodic=False)

        assert result.success is True
        assert result.new_path.suffix == ".mkv"
        assert result.new_path.name == "Test Movie (1999).mkv"

    def test_rename_with_invalid_year_no_year_in_filename(self, tmp_path, app_config):
        """Test rename with invalid year produces filename without year."""
        file_path = tmp_path / "original.mp4"
        file_path.touch()

        renamer = MediaRenamer(
            "Test Movie",
            config=app_config,
            year=999,  # Invalid - less than 1000
            include_year_in_filename=True,
        )
        result = renamer.rename_file(file_path, 1, 1, episodic=False)

        assert result.success is True
        assert result.new_path.name == "Test Movie.mp4"
        assert "(999)" not in result.new_path.name
