"""Data models and enumerations for Media Organizer."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Genre(str, Enum):
    """Enumeration of supported media genres."""

    ACTION = "Action"
    ADVENTURE = "Adventure"
    ANIMATED = "Animated"
    ANIME = "Anime"
    COMEDY = "Comedy"
    DRAMA = "Drama"
    FANTASY = "Fantasy"
    HORROR = "Horror"
    MUSICAL = "Musical"
    MYSTERY = "Mystery"
    ROMANCE = "Romance"
    SCIENCE_FICTION = "Science Fiction"
    SPORTS = "Sports"
    THRILLER = "Thriller"
    WESTERN = "Western"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        """Return list of (value, value) tuples for UI selects."""
        return [(g.value, g.value) for g in cls]

    @classmethod
    def from_string(cls, value: str) -> Optional["Genre"]:
        """Convert a string to a Genre enum, returning None if not found."""
        for genre in cls:
            if genre.value.lower() == value.lower():
                return genre
        return None


@dataclass
class MediaMetadata:
    """Metadata for a media file."""

    title: str = ""
    season: int = 0
    episode: int = 0
    genre: str = ""
    year: int = 0
    collection: str = ""

    def to_dict(self) -> dict:
        """Convert metadata to dictionary for backward compatibility."""
        return {
            "title": self.title,
            "season": self.season,
            "episode": self.episode,
            "genre": self.genre,
            "year": self.year,
            "collection": self.collection,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MediaMetadata":
        """Create MediaMetadata from dictionary."""
        return cls(
            title=data.get("title", ""),
            season=data.get("season", 0),
            episode=data.get("episode", 0),
            genre=data.get("genre", ""),
            year=data.get("year", 0),
            collection=data.get("collection", ""),
        )


@dataclass
class MediaFile:
    """Represents a media file with its path and metadata."""

    path: Path
    original_name: str
    metadata: MediaMetadata = field(default_factory=MediaMetadata)
    selected: bool = True

    @property
    def extension(self) -> str:
        """Return the lowercase file extension."""
        return self.path.suffix.lower()

    @classmethod
    def from_path(cls, file_path: Path | str) -> "MediaFile":
        """Create MediaFile from a path."""
        path = Path(file_path) if isinstance(file_path, str) else file_path
        return cls(path=path, original_name=path.name)


@dataclass
class RenameResult:
    """Result of a file rename operation."""

    success: bool
    original_path: Path
    new_path: Optional[Path] = None
    error: Optional[str] = None

    @property
    def message(self) -> str:
        """Return a human-readable message about the result."""
        if self.success:
            return f"Renamed to {self.new_path.name}" if self.new_path else "Renamed"
        return f"Failed: {self.error}" if self.error else "Failed"


@dataclass
class MetadataUpdateResult:
    """Result of a metadata update operation."""

    success: bool
    file_path: Path
    error: Optional[str] = None

    @property
    def message(self) -> str:
        """Return a human-readable message about the result."""
        if self.success:
            return "Updated"
        return f"Failed: {self.error}" if self.error else "Failed"
