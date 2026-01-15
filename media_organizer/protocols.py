"""Protocol definitions for Media Organizer."""

from pathlib import Path
from typing import Protocol, runtime_checkable

from .models import MediaMetadata


@runtime_checkable
class MetadataEditor(Protocol):
    """Protocol for format-specific metadata editors.

    Implementations of this protocol handle reading and writing
    metadata for specific file formats (MP4, MKV, etc.).
    """

    @property
    def supported_extensions(self) -> set[str]:
        """Return set of supported file extensions (lowercase, with dot)."""
        ...

    def read(self, file_path: Path) -> MediaMetadata:
        """Read metadata from a media file.

        Args:
            file_path: Path to the media file.

        Returns:
            MediaMetadata containing the file's metadata.
        """
        ...

    def write(self, file_path: Path, metadata: MediaMetadata) -> bool:
        """Write metadata to a media file.

        Args:
            file_path: Path to the media file.
            metadata: Metadata to write to the file.

        Returns:
            True if successful, False otherwise.
        """
        ...
