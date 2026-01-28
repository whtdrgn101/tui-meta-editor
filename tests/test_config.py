"""Tests for media_organizer.config module."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from media_organizer.config import AppConfig


class TestAppConfigDefaults:
    """Tests for AppConfig default values."""

    def test_default_root_is_home(self):
        """Test default root is user's home directory."""
        config = AppConfig()
        assert config.default_root == Path.home()

    def test_default_media_extensions(self):
        """Test default media extensions."""
        config = AppConfig()
        assert config.media_extensions == {".mp4", ".mkv", ".m4v", ".avi"}

    def test_default_year(self):
        """Test default year."""
        config = AppConfig()
        assert config.default_year == 2000

    def test_default_season(self):
        """Test default season."""
        config = AppConfig()
        assert config.default_season == 1

    def test_default_episode(self):
        """Test default episode."""
        config = AppConfig()
        assert config.default_episode == 1

    def test_default_episode_padding(self):
        """Test default episode padding is 3 digits."""
        config = AppConfig()
        assert config.episode_padding == 3

    def test_default_mkvpropedit_path(self):
        """Test default mkvpropedit path."""
        config = AppConfig()
        assert config.mkvpropedit_path == "mkvpropedit"

    def test_default_log_level(self):
        """Test default log level."""
        config = AppConfig()
        assert config.log_level == "INFO"


class TestAppConfigFromEnv:
    """Tests for AppConfig.from_env() method."""

    def test_from_env_no_variables(self):
        """Test from_env with no environment variables set."""
        with patch.dict(os.environ, {}, clear=True):
            config = AppConfig.from_env()
            assert config.default_root == Path.home()
            assert config.default_year == 2000

    def test_from_env_root(self, tmp_path):
        """Test from_env reads MEDIA_ORGANIZER_ROOT."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_ROOT": str(tmp_path)}):
            config = AppConfig.from_env()
            assert config.default_root == tmp_path

    def test_from_env_extensions(self):
        """Test from_env reads MEDIA_ORGANIZER_EXTENSIONS."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_EXTENSIONS": ".mp4,.webm,.flv"}):
            config = AppConfig.from_env()
            assert config.media_extensions == {".mp4", ".webm", ".flv"}

    def test_from_env_extensions_without_dots(self):
        """Test from_env adds dots to extensions without them."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_EXTENSIONS": "mp4,mkv,avi"}):
            config = AppConfig.from_env()
            assert config.media_extensions == {".mp4", ".mkv", ".avi"}

    def test_from_env_year(self):
        """Test from_env reads MEDIA_ORGANIZER_YEAR."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_YEAR": "2024"}):
            config = AppConfig.from_env()
            assert config.default_year == 2024

    def test_from_env_year_invalid(self):
        """Test from_env ignores invalid year."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_YEAR": "invalid"}):
            config = AppConfig.from_env()
            assert config.default_year == 2000  # Default

    def test_from_env_season(self):
        """Test from_env reads MEDIA_ORGANIZER_SEASON."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_SEASON": "5"}):
            config = AppConfig.from_env()
            assert config.default_season == 5

    def test_from_env_season_invalid(self):
        """Test from_env ignores invalid season."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_SEASON": "abc"}):
            config = AppConfig.from_env()
            assert config.default_season == 1  # Default

    def test_from_env_episode(self):
        """Test from_env reads MEDIA_ORGANIZER_EPISODE."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_EPISODE": "10"}):
            config = AppConfig.from_env()
            assert config.default_episode == 10

    def test_from_env_episode_invalid(self):
        """Test from_env ignores invalid episode."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_EPISODE": "not_a_number"}):
            config = AppConfig.from_env()
            assert config.default_episode == 1  # Default

    def test_from_env_episode_padding_2(self):
        """Test from_env reads MEDIA_ORGANIZER_EPISODE_PADDING for 2 digits."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_EPISODE_PADDING": "2"}):
            config = AppConfig.from_env()
            assert config.episode_padding == 2

    def test_from_env_episode_padding_3(self):
        """Test from_env reads MEDIA_ORGANIZER_EPISODE_PADDING for 3 digits."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_EPISODE_PADDING": "3"}):
            config = AppConfig.from_env()
            assert config.episode_padding == 3

    def test_from_env_episode_padding_invalid(self):
        """Test from_env ignores invalid episode padding."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_EPISODE_PADDING": "5"}):
            config = AppConfig.from_env()
            assert config.episode_padding == 3  # Default

    def test_from_env_episode_padding_non_numeric(self):
        """Test from_env ignores non-numeric episode padding."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_EPISODE_PADDING": "abc"}):
            config = AppConfig.from_env()
            assert config.episode_padding == 3  # Default

    def test_from_env_mkvpropedit(self):
        """Test from_env reads MEDIA_ORGANIZER_MKVPROPEDIT."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_MKVPROPEDIT": "/usr/local/bin/mkvpropedit"}):
            config = AppConfig.from_env()
            assert config.mkvpropedit_path == "/usr/local/bin/mkvpropedit"

    def test_from_env_log_level(self):
        """Test from_env reads MEDIA_ORGANIZER_LOG_LEVEL."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_LOG_LEVEL": "debug"}):
            config = AppConfig.from_env()
            assert config.log_level == "DEBUG"

    def test_from_env_log_level_uppercase(self):
        """Test from_env converts log level to uppercase."""
        with patch.dict(os.environ, {"MEDIA_ORGANIZER_LOG_LEVEL": "warning"}):
            config = AppConfig.from_env()
            assert config.log_level == "WARNING"

    def test_from_env_multiple_variables(self, tmp_path):
        """Test from_env with multiple variables set."""
        env_vars = {
            "MEDIA_ORGANIZER_ROOT": str(tmp_path),
            "MEDIA_ORGANIZER_YEAR": "2023",
            "MEDIA_ORGANIZER_SEASON": "3",
            "MEDIA_ORGANIZER_LOG_LEVEL": "error",
        }
        with patch.dict(os.environ, env_vars):
            config = AppConfig.from_env()
            assert config.default_root == tmp_path
            assert config.default_year == 2023
            assert config.default_season == 3
            assert config.log_level == "ERROR"


class TestAppConfigFormatEpisodeName:
    """Tests for AppConfig.format_episode_name() method."""

    def test_format_default_padding_3(self):
        """Test format with default 3-digit padding."""
        config = AppConfig()
        result = config.format_episode_name("Test Show", 1, 5)
        assert result == "Test Show S01 EP005"

    def test_format_padding_2_digits(self):
        """Test format with 2-digit padding."""
        config = AppConfig(episode_padding=2)
        result = config.format_episode_name("My Show", 2, 5)
        assert result == "My Show S02 EP05"

    def test_format_padding_3_digits(self):
        """Test format with 3-digit padding."""
        config = AppConfig(episode_padding=3)
        result = config.format_episode_name("Show", 1, 5)
        assert result == "Show S01 EP005"

    def test_format_padding_2_single_digit_episode(self):
        """Test 2-digit padding with single digit episode."""
        config = AppConfig(episode_padding=2)
        result = config.format_episode_name("Show", 1, 1)
        assert result == "Show S01 EP01"

    def test_format_padding_3_single_digit_episode(self):
        """Test 3-digit padding with single digit episode."""
        config = AppConfig(episode_padding=3)
        result = config.format_episode_name("Show", 1, 1)
        assert result == "Show S01 EP001"

    def test_format_padding_2_large_episode(self):
        """Test 2-digit padding with large episode number."""
        config = AppConfig(episode_padding=2)
        result = config.format_episode_name("Show", 1, 99)
        assert result == "Show S01 EP99"

    def test_format_padding_2_exceeds_padding(self):
        """Test 2-digit padding when episode exceeds padding width."""
        config = AppConfig(episode_padding=2)
        result = config.format_episode_name("Show", 1, 100)
        assert result == "Show S01 EP100"

    def test_format_large_numbers(self):
        """Test format with large season/episode numbers."""
        config = AppConfig()
        result = config.format_episode_name("Long Show", 15, 150)
        assert result == "Long Show S15 EP150"

    def test_format_special_characters_in_title(self):
        """Test format with special characters in title."""
        config = AppConfig()
        result = config.format_episode_name("Show: The Beginning!", 1, 1)
        assert result == "Show: The Beginning! S01 EP001"


class TestAppConfigFormatMovieName:
    """Tests for AppConfig.format_movie_name() method."""

    def test_format_without_year(self):
        """Test format without year returns just title."""
        config = AppConfig()
        result = config.format_movie_name("Test Movie")
        assert result == "Test Movie"

    def test_format_with_none_year(self):
        """Test format with None year returns just title."""
        config = AppConfig()
        result = config.format_movie_name("Test Movie", None)
        assert result == "Test Movie"

    def test_format_with_valid_year(self):
        """Test format with valid year appends in parentheses."""
        config = AppConfig()
        result = config.format_movie_name("Test Movie", 2002)
        assert result == "Test Movie (2002)"

    def test_format_with_zero_year(self):
        """Test format with zero year returns just title."""
        config = AppConfig()
        result = config.format_movie_name("Test Movie", 0)
        assert result == "Test Movie"

    def test_format_with_invalid_year(self):
        """Test format with year < 1000 returns just title."""
        config = AppConfig()
        result = config.format_movie_name("Test Movie", 999)
        assert result == "Test Movie"

    def test_format_with_boundary_year(self):
        """Test format with year = 1000 includes year."""
        config = AppConfig()
        result = config.format_movie_name("Test Movie", 1000)
        assert result == "Test Movie (1000)"

    def test_format_with_special_characters_in_title(self):
        """Test format with special characters in title."""
        config = AppConfig()
        result = config.format_movie_name("Movie: The Beginning!", 2024)
        assert result == "Movie: The Beginning! (2024)"

    def test_format_preserves_title_spacing(self):
        """Test format preserves title spacing."""
        config = AppConfig()
        result = config.format_movie_name("The  Movie  Title", 2024)
        assert result == "The  Movie  Title (2024)"
