"""Configuration management for Media Organizer."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    """Application configuration settings."""

    default_root: Path = field(default_factory=lambda: Path.home())
    media_extensions: set[str] = field(
        default_factory=lambda: {".mp4", ".mkv", ".m4v", ".avi"}
    )
    default_year: int = 2000
    default_season: int = 1
    default_episode: int = 1
    episode_padding: int = 3  # 2 or 3 digits for episode number (EP01 vs EP001)
    mkvpropedit_path: str = "mkvpropedit"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables.

        Environment variables:
            MEDIA_ORGANIZER_ROOT: Default root directory for file browser
            MEDIA_ORGANIZER_EXTENSIONS: Comma-separated list of extensions
            MEDIA_ORGANIZER_YEAR: Default year for metadata
            MEDIA_ORGANIZER_SEASON: Default season number
            MEDIA_ORGANIZER_EPISODE: Default episode number
            MEDIA_ORGANIZER_EPISODE_PADDING: Episode number padding (2 or 3 digits)
            MEDIA_ORGANIZER_MKVPROPEDIT: Path to mkvpropedit executable
            MEDIA_ORGANIZER_LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR)

        Returns:
            AppConfig instance with values from environment or defaults.
        """
        config = cls()

        if root := os.environ.get("MEDIA_ORGANIZER_ROOT"):
            config.default_root = Path(root)

        if extensions := os.environ.get("MEDIA_ORGANIZER_EXTENSIONS"):
            config.media_extensions = {
                ext.strip() if ext.strip().startswith(".") else f".{ext.strip()}"
                for ext in extensions.split(",")
            }

        if year := os.environ.get("MEDIA_ORGANIZER_YEAR"):
            try:
                config.default_year = int(year)
            except ValueError:
                pass

        if season := os.environ.get("MEDIA_ORGANIZER_SEASON"):
            try:
                config.default_season = int(season)
            except ValueError:
                pass

        if episode := os.environ.get("MEDIA_ORGANIZER_EPISODE"):
            try:
                config.default_episode = int(episode)
            except ValueError:
                pass

        if episode_padding := os.environ.get("MEDIA_ORGANIZER_EPISODE_PADDING"):
            try:
                padding = int(episode_padding)
                if padding in (2, 3):
                    config.episode_padding = padding
            except ValueError:
                pass

        if mkvpropedit := os.environ.get("MEDIA_ORGANIZER_MKVPROPEDIT"):
            config.mkvpropedit_path = mkvpropedit

        if log_level := os.environ.get("MEDIA_ORGANIZER_LOG_LEVEL"):
            config.log_level = log_level.upper()

        return config

    def format_episode_name(self, title: str, season: int, episode: int) -> str:
        """Format an episode name using the configured padding.

        Args:
            title: The show title.
            season: Season number.
            episode: Episode number.

        Returns:
            Formatted episode name string (e.g., "Show S01 EP001" or "Show S01 EP01").
        """
        format_str = f"{{title}} S{{season:02d}} EP{{episode:0{self.episode_padding}d}}"
        return format_str.format(title=title, season=season, episode=episode)

    def format_movie_name(self, title: str, year: int | None = None) -> str:
        """Format a movie name with optional year.

        Args:
            title: The movie title.
            year: Optional year to append in parentheses.

        Returns:
            Formatted movie name string (e.g., "Movie Title (2002)" or "Movie Title").
        """
        if year and year >= 1000:
            return f"{title} ({year})"
        return title
