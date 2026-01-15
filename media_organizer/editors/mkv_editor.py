"""MKV metadata editor implementation."""

import logging
import subprocess
from pathlib import Path

from ..models import MediaMetadata


class MKVEditor:
    """Metadata editor for MKV files using mkvpropedit."""

    supported_extensions: set[str] = {".mkv"}

    def __init__(self, mkvpropedit_path: str = "mkvpropedit") -> None:
        """Initialize the MKV editor.

        Args:
            mkvpropedit_path: Path to the mkvpropedit executable.
        """
        self._mkvpropedit = mkvpropedit_path
        self._logger = logging.getLogger(__name__)

    def read(self, file_path: Path) -> MediaMetadata:
        """Read metadata from an MKV file.

        Note: MKV metadata reading is limited. This implementation
        extracts the title using mkvinfo if available.

        Args:
            file_path: Path to the media file.

        Returns:
            MediaMetadata containing the file's metadata.
        """
        try:
            # Try to get title using mkvinfo
            result = subprocess.run(
                ["mkvinfo", str(file_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            title = ""
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "Title:" in line:
                        # Extract title from line like "| + Title: Show Name"
                        parts = line.split("Title:", 1)
                        if len(parts) > 1:
                            title = parts[1].strip()
                            break

            return MediaMetadata(title=title)

        except FileNotFoundError:
            self._logger.warning("mkvinfo not found, cannot read MKV metadata")
            return MediaMetadata()
        except subprocess.TimeoutExpired:
            self._logger.error(f"Timeout reading metadata from {file_path}")
            return MediaMetadata()
        except Exception as e:
            self._logger.error(f"Failed to read MKV metadata from {file_path}: {e}")
            return MediaMetadata()

    def write(self, file_path: Path, metadata: MediaMetadata) -> bool:
        """Write metadata to an MKV file.

        Note: MKV metadata writing is limited to title using mkvpropedit.
        Season, episode, genre, and year are not currently supported
        in MKV container format via mkvpropedit.

        Args:
            file_path: Path to the media file.
            metadata: Metadata to write to the file.

        Returns:
            True if successful, False otherwise.
        """
        if not metadata.title:
            self._logger.debug("No title provided, skipping MKV metadata write")
            return True

        try:
            result = subprocess.run(
                [
                    self._mkvpropedit,
                    str(file_path),
                    "--edit",
                    "info",
                    "--set",
                    f"title={metadata.title}",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                self._logger.debug(f"Successfully wrote metadata to {file_path}")
                return True
            else:
                self._logger.error(
                    f"mkvpropedit failed for {file_path}: {result.stderr}"
                )
                return False

        except FileNotFoundError:
            self._logger.error(
                f"mkvpropedit not found at '{self._mkvpropedit}'. "
                "Please install MKVToolNix."
            )
            return False
        except subprocess.TimeoutExpired:
            self._logger.error(f"Timeout writing metadata to {file_path}")
            return False
        except Exception as e:
            self._logger.error(f"Failed to write MKV metadata to {file_path}: {e}")
            return False

    def is_available(self) -> bool:
        """Check if mkvpropedit is available.

        Returns:
            True if mkvpropedit can be executed, False otherwise.
        """
        try:
            result = subprocess.run(
                [self._mkvpropedit, "--version"],
                capture_output=True,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
