"""Media file renamer for consistent file naming."""

import logging
import os
from pathlib import Path
from typing import Optional

from ..config import AppConfig
from ..models import RenameResult


class MediaRenamer:
    """Renamer for media files using consistent naming patterns."""

    def __init__(
        self,
        title: str,
        config: Optional[AppConfig] = None,
        year: Optional[int] = None,
        include_year_in_filename: bool = False,
    ) -> None:
        """Initialize the renamer.

        Args:
            title: The show/movie title to use in filenames.
            config: Application configuration. If None, uses defaults.
            year: The year to include in movie filenames (optional).
            include_year_in_filename: If True, append year to non-episodic names.
        """
        self._title = title
        self._config = config or AppConfig()
        self._year = year
        self._include_year = include_year_in_filename
        self._logger = logging.getLogger(__name__)

    @property
    def title(self) -> str:
        """Return the current title."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Set the title."""
        self._title = value

    @property
    def year(self) -> Optional[int]:
        """Return the current year."""
        return self._year

    @year.setter
    def year(self, value: Optional[int]) -> None:
        """Set the year."""
        self._year = value

    @property
    def include_year_in_filename(self) -> bool:
        """Return whether to include year in filename."""
        return self._include_year

    @include_year_in_filename.setter
    def include_year_in_filename(self, value: bool) -> None:
        """Set whether to include year in filename."""
        self._include_year = value

    def generate_episode_name(self, season: int, episode: int) -> str:
        """Generate an episode name using the configured format.

        Args:
            season: Season number.
            episode: Episode number.

        Returns:
            Formatted episode name string.
        """
        return self._config.format_episode_name(
            title=self._title,
            season=season,
            episode=episode,
        )

    def generate_new_name(
        self,
        file_path: str | Path,
        season: int,
        episode: int,
        episodic: bool = True,
    ) -> tuple[Path, str]:
        """Generate a new filename for a media file.

        Args:
            file_path: Path to the original file.
            season: Season number.
            episode: Episode number.
            episodic: If True, include season/episode in name.

        Returns:
            Tuple of (directory path, new filename).
        """
        path = Path(file_path)
        directory = path.parent
        extension = path.suffix

        if episodic:
            episode_name = self.generate_episode_name(season, episode)
        else:
            if self._include_year:
                episode_name = self._config.format_movie_name(self._title, self._year)
            else:
                episode_name = self._title

        new_name = f"{episode_name}{extension}"
        return directory, new_name

    def rename_file(
        self,
        file_path: str | Path,
        season: int,
        episode: int,
        episodic: bool = True,
    ) -> RenameResult:
        """Rename a media file.

        Args:
            file_path: Path to the file to rename.
            season: Season number.
            episode: Episode number.
            episodic: If True, include season/episode in name.

        Returns:
            RenameResult with success status and paths.
        """
        original_path = Path(file_path)

        if not original_path.exists():
            error = f"File does not exist: {file_path}"
            self._logger.error(error)
            return RenameResult(
                success=False,
                original_path=original_path,
                error=error,
            )

        try:
            directory, new_name = self.generate_new_name(
                file_path, season, episode, episodic
            )
            new_path = directory / new_name

            # Check if new path already exists (and is different from original)
            if new_path.exists() and new_path != original_path:
                error = f"Target file already exists: {new_path}"
                self._logger.error(error)
                return RenameResult(
                    success=False,
                    original_path=original_path,
                    error=error,
                )

            os.rename(str(original_path), str(new_path))

            self._logger.info(f"Renamed {original_path.name} -> {new_name}")
            return RenameResult(
                success=True,
                original_path=original_path,
                new_path=new_path,
            )

        except PermissionError as e:
            error = f"Permission denied: {e}"
            self._logger.error(error)
            return RenameResult(
                success=False,
                original_path=original_path,
                error=error,
            )
        except OSError as e:
            error = f"OS error during rename: {e}"
            self._logger.error(error)
            return RenameResult(
                success=False,
                original_path=original_path,
                error=error,
            )
