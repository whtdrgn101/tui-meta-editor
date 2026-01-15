"""MP4/M4V metadata editor implementation."""

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from ..models import MediaMetadata


class MP4Editor:
    """Metadata editor for MP4 and M4V files using mutagen."""

    supported_extensions: set[str] = {".mp4", ".m4v"}

    def __init__(self) -> None:
        """Initialize the MP4 editor."""
        self._logger = logging.getLogger(__name__)

    @contextmanager
    def _open_mp4(self, file_path: Path) -> Generator:
        """Context manager for opening MP4 files.

        Args:
            file_path: Path to the MP4 file.

        Yields:
            MP4 file object from mutagen.
        """
        from mutagen.mp4 import MP4

        mp4 = MP4(str(file_path))
        yield mp4

    def read(self, file_path: Path) -> MediaMetadata:
        """Read metadata from an MP4/M4V file.

        Args:
            file_path: Path to the media file.

        Returns:
            MediaMetadata containing the file's metadata.
        """
        from mutagen.mp4 import MP4

        try:
            mp4 = MP4(str(file_path))

            # Extract title
            title = ""
            if "\xa9nam" in mp4:
                title_list = mp4.get("\xa9nam", [""])
                title = title_list[0] if title_list else ""

            # Extract season
            season = 0
            if "tvsn" in mp4:
                season_list = mp4.get("tvsn", [0])
                season = season_list[0] if season_list else 0

            # Extract episode
            episode = 0
            if "tves" in mp4:
                episode_list = mp4.get("tves", [0])
                episode = episode_list[0] if episode_list else 0

            # Extract genre
            genre = ""
            if "\xa9gen" in mp4:
                genre_list = mp4.get("\xa9gen", [""])
                genre = genre_list[0] if genre_list else ""

            # Extract year
            year = 0
            if "\xa9day" in mp4:
                year_list = mp4.get("\xa9day", [""])
                if year_list and year_list[0]:
                    try:
                        # Year might be in format "2024" or "2024-01-15"
                        year_str = str(year_list[0])[:4]
                        year = int(year_str)
                    except (ValueError, IndexError):
                        pass

            return MediaMetadata(
                title=title,
                season=season,
                episode=episode,
                genre=genre,
                year=year,
            )

        except Exception as e:
            self._logger.error(f"Failed to read MP4 metadata from {file_path}: {e}")
            return MediaMetadata()

    def write(self, file_path: Path, metadata: MediaMetadata) -> bool:
        """Write metadata to an MP4/M4V file.

        Args:
            file_path: Path to the media file.
            metadata: Metadata to write to the file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with self._open_mp4(file_path) as mp4:
                self._apply_metadata(mp4, metadata)
                mp4.save()

            self._logger.debug(f"Successfully wrote metadata to {file_path}")
            return True

        except Exception as e:
            self._logger.error(f"Failed to write MP4 metadata to {file_path}: {e}")
            return False

    def _apply_metadata(self, mp4, metadata: MediaMetadata) -> None:
        """Apply metadata to an MP4 file object.

        Args:
            mp4: Mutagen MP4 object.
            metadata: Metadata to apply.
        """
        # Title
        if metadata.title:
            mp4["\xa9nam"] = metadata.title

        # TV show info
        if metadata.season > 0:
            mp4["tvsn"] = [metadata.season]

        if metadata.episode > 0:
            mp4["tves"] = [metadata.episode]

        # Genre
        if metadata.genre:
            mp4["\xa9gen"] = metadata.genre

        # Year
        if metadata.year > 0:
            mp4["\xa9day"] = [str(metadata.year)]
