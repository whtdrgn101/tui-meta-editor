"""Metadata manager for coordinating metadata operations across formats."""

import logging
from pathlib import Path
from typing import Callable, Optional

from ..config import AppConfig
from ..editors.mkv_editor import MKVEditor
from ..editors.mp4_editor import MP4Editor
from ..models import MediaMetadata, MetadataUpdateResult
from ..protocols import MetadataEditor
from .renamer import MediaRenamer


class MetadataManager:
    """Manager for reading and writing metadata across different file formats."""

    def __init__(
        self,
        editors: Optional[dict[str, MetadataEditor]] = None,
        renamer_factory: Optional[Callable[[str], MediaRenamer]] = None,
        config: Optional[AppConfig] = None,
    ) -> None:
        """Initialize the metadata manager.

        Args:
            editors: Dictionary mapping extensions to editor instances.
                     If None, uses default editors.
            renamer_factory: Factory function for creating MediaRenamer instances.
                            If None, uses MediaRenamer class directly.
            config: Application configuration. If None, uses defaults.
        """
        self._config = config or AppConfig()
        self._editors = editors or self._default_editors()
        self._renamer_factory = renamer_factory or self._default_renamer_factory
        self._logger = logging.getLogger(__name__)

    def _default_editors(self) -> dict[str, MetadataEditor]:
        """Create default editors for supported formats.

        Returns:
            Dictionary mapping extensions to editor instances.
        """
        mp4_editor = MP4Editor()
        mkv_editor = MKVEditor(self._config.mkvpropedit_path)

        return {
            ".mp4": mp4_editor,
            ".m4v": mp4_editor,
            ".mkv": mkv_editor,
        }

    def _default_renamer_factory(self, title: str) -> MediaRenamer:
        """Default factory for creating MediaRenamer instances.

        Args:
            title: Show title for the renamer.

        Returns:
            Configured MediaRenamer instance.
        """
        return MediaRenamer(title, config=self._config)

    def _get_editor(self, file_path: Path) -> Optional[MetadataEditor]:
        """Get the appropriate editor for a file.

        Args:
            file_path: Path to the file.

        Returns:
            Editor instance or None if no editor supports the format.
        """
        extension = file_path.suffix.lower()
        return self._editors.get(extension)

    def read_metadata(self, file_path: str | Path) -> MediaMetadata:
        """Read metadata from a media file.

        Args:
            file_path: Path to the media file.

        Returns:
            MediaMetadata containing the file's metadata.
        """
        path = Path(file_path)
        self._logger.debug(f"Reading metadata from {path}")

        editor = self._get_editor(path)
        if not editor:
            self._logger.warning(f"No editor for file type: {path.suffix}")
            return MediaMetadata()

        return editor.read(path)

    def update_metadata(
        self,
        file_path: str | Path,
        metadata: MediaMetadata | dict,
    ) -> MetadataUpdateResult:
        """Update metadata of a media file.

        Args:
            file_path: Path to the media file.
            metadata: Metadata to write (MediaMetadata or dict for compatibility).

        Returns:
            MetadataUpdateResult with success status.
        """
        path = Path(file_path)
        self._logger.debug(f"Updating metadata for {path}")

        # Convert dict to MediaMetadata for backward compatibility
        if isinstance(metadata, dict):
            metadata = MediaMetadata.from_dict(metadata)

        # Generate formatted title if title, season, and episode are provided
        if metadata.title and metadata.season > 0 and metadata.episode > 0:
            renamer = self._renamer_factory(metadata.title)
            formatted_title = renamer.generate_episode_name(
                metadata.season, metadata.episode
            )
            # Create new metadata with formatted title
            metadata = MediaMetadata(
                title=formatted_title,
                season=metadata.season,
                episode=metadata.episode,
                genre=metadata.genre,
                year=metadata.year,
                collection=metadata.collection,
            )

        editor = self._get_editor(path)
        if not editor:
            error = f"Unsupported file type: {path.suffix}"
            self._logger.warning(error)
            return MetadataUpdateResult(
                success=False,
                file_path=path,
                error=error,
            )

        try:
            success = editor.write(path, metadata)
            if success:
                self._logger.info(f"Successfully updated metadata for {path.name}")
            else:
                self._logger.error(f"Failed to update metadata for {path.name}")

            return MetadataUpdateResult(
                success=success,
                file_path=path,
                error=None if success else "Editor write failed",
            )

        except Exception as e:
            error = str(e)
            self._logger.error(f"Error updating metadata for {path}: {error}")
            return MetadataUpdateResult(
                success=False,
                file_path=path,
                error=error,
            )

    def get_supported_extensions(self) -> set[str]:
        """Get all supported file extensions.

        Returns:
            Set of supported extensions (lowercase, with dot).
        """
        return set(self._editors.keys())
