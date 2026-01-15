"""
Media Organizer

A tool to organize media files by renaming them according to a consistent pattern
and updating their metadata.

This package provides both a TUI (Text User Interface) and a GUI (PySide6)
for managing your media files.
"""

__version__ = "0.2.0"
__author__ = "Timothy A. DeWees"
__license__ = "MIT"

from .models import MediaFile, MediaMetadata, Genre, RenameResult
from .config import AppConfig
from .protocols import MetadataEditor

__all__ = [
    "MediaFile",
    "MediaMetadata",
    "Genre",
    "RenameResult",
    "AppConfig",
    "MetadataEditor",
]
