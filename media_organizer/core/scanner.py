"""Media file scanner for discovering media files in directories."""

import logging
import os
from pathlib import Path
from typing import Optional

from ..config import AppConfig
from ..models import MediaFile


class MediaScanner:
    """Scanner for finding media files in directories."""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        """Initialize the scanner.

        Args:
            config: Application configuration. If None, uses defaults.
        """
        self._config = config or AppConfig()
        self._logger = logging.getLogger(__name__)
        self._scanned_files: list[MediaFile] = []

    @property
    def scanned_files(self) -> list[MediaFile]:
        """Return list of scanned media files."""
        return self._scanned_files

    @property
    def media_extensions(self) -> set[str]:
        """Return set of supported media file extensions."""
        return self._config.media_extensions

    def scan_directory(self, directory_path: str | Path) -> list[MediaFile]:
        """Scan a directory recursively for media files.

        Args:
            directory_path: Path to the directory to scan.

        Returns:
            List of MediaFile objects for found media files.
        """
        self._scanned_files = []
        directory = Path(directory_path)

        if not directory.exists():
            self._logger.error(f"Directory does not exist: {directory_path}")
            return []

        if not directory.is_dir():
            self._logger.error(f"Path is not a directory: {directory_path}")
            return []

        self._logger.info(f"Scanning directory: {directory}")

        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file

                    if file_path.suffix.lower() in self.media_extensions:
                        media_file = MediaFile.from_path(file_path)
                        self._scanned_files.append(media_file)
                        self._logger.debug(f"Found media file: {file_path}")

            # Sort files alphabetically by name (case-insensitive)
            self._scanned_files.sort(key=lambda f: f.original_name.lower())

            self._logger.info(f"Found {len(self._scanned_files)} media files")
            return self._scanned_files

        except PermissionError as e:
            self._logger.error(f"Permission denied scanning {directory_path}: {e}")
            return self._scanned_files
        except OSError as e:
            self._logger.error(f"Error scanning directory {directory_path}: {e}")
            return self._scanned_files

    def filter_by_extension(self, extension: str) -> list[MediaFile]:
        """Filter scanned files by extension.

        Args:
            extension: File extension to filter by (with or without dot).

        Returns:
            List of MediaFile objects matching the extension.
        """
        if not extension.startswith("."):
            extension = f".{extension}"

        extension = extension.lower()
        return [f for f in self._scanned_files if f.extension == extension]

    def get_file_count(self) -> int:
        """Get count of scanned media files.

        Returns:
            Number of media files found.
        """
        return len(self._scanned_files)

    def clear(self) -> None:
        """Clear the list of scanned files."""
        self._scanned_files = []
        self._logger.debug("Cleared scanned files list")
