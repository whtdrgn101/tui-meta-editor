"""Tests for media_organizer.models module."""

import pytest
from pathlib import Path

from media_organizer.models import (
    Genre,
    MediaFile,
    MediaMetadata,
    MetadataUpdateResult,
    RenameResult,
)


class TestGenre:
    """Tests for Genre enum."""

    def test_genre_values(self):
        """Test that all expected genres exist."""
        assert Genre.ACTION.value == "Action"
        assert Genre.COMEDY.value == "Comedy"
        assert Genre.SCIENCE_FICTION.value == "Science Fiction"
        assert Genre.ANIME.value == "Anime"

    def test_genre_choices_returns_list_of_tuples(self):
        """Test choices() returns list of (value, value) tuples."""
        choices = Genre.choices()
        assert isinstance(choices, list)
        assert len(choices) == 15  # 15 genres defined
        assert all(isinstance(c, tuple) and len(c) == 2 for c in choices)

    def test_genre_choices_values_match(self):
        """Test that choice tuples have matching values."""
        choices = Genre.choices()
        for value, label in choices:
            assert value == label

    def test_genre_from_string_exact_match(self):
        """Test from_string with exact case match."""
        assert Genre.from_string("Action") == Genre.ACTION
        assert Genre.from_string("Science Fiction") == Genre.SCIENCE_FICTION

    def test_genre_from_string_case_insensitive(self):
        """Test from_string is case insensitive."""
        assert Genre.from_string("action") == Genre.ACTION
        assert Genre.from_string("ACTION") == Genre.ACTION
        assert Genre.from_string("sCiEnCe FiCtIoN") == Genre.SCIENCE_FICTION

    def test_genre_from_string_not_found(self):
        """Test from_string returns None for unknown genre."""
        assert Genre.from_string("Unknown") is None
        assert Genre.from_string("") is None
        assert Genre.from_string("NotAGenre") is None


class TestMediaMetadata:
    """Tests for MediaMetadata dataclass."""

    def test_default_values(self):
        """Test default values for MediaMetadata."""
        metadata = MediaMetadata()
        assert metadata.title == ""
        assert metadata.season == 0
        assert metadata.episode == 0
        assert metadata.genre == ""
        assert metadata.year == 0
        assert metadata.collection == ""

    def test_custom_values(self):
        """Test MediaMetadata with custom values."""
        metadata = MediaMetadata(
            title="Test Show",
            season=2,
            episode=10,
            genre="Action",
            year=2024,
            collection="My Collection",
        )
        assert metadata.title == "Test Show"
        assert metadata.season == 2
        assert metadata.episode == 10
        assert metadata.genre == "Action"
        assert metadata.year == 2024
        assert metadata.collection == "My Collection"

    def test_to_dict(self):
        """Test to_dict returns correct dictionary."""
        metadata = MediaMetadata(
            title="Test",
            season=1,
            episode=5,
            genre="Comedy",
            year=2023,
            collection="Series",
        )
        result = metadata.to_dict()
        assert result == {
            "title": "Test",
            "season": 1,
            "episode": 5,
            "genre": "Comedy",
            "year": 2023,
            "collection": "Series",
        }

    def test_from_dict_complete(self):
        """Test from_dict with all fields."""
        data = {
            "title": "From Dict",
            "season": 3,
            "episode": 7,
            "genre": "Drama",
            "year": 2022,
            "collection": "Test",
        }
        metadata = MediaMetadata.from_dict(data)
        assert metadata.title == "From Dict"
        assert metadata.season == 3
        assert metadata.episode == 7
        assert metadata.genre == "Drama"
        assert metadata.year == 2022
        assert metadata.collection == "Test"

    def test_from_dict_partial(self):
        """Test from_dict with missing fields uses defaults."""
        data = {"title": "Partial"}
        metadata = MediaMetadata.from_dict(data)
        assert metadata.title == "Partial"
        assert metadata.season == 0
        assert metadata.episode == 0
        assert metadata.genre == ""
        assert metadata.year == 0

    def test_from_dict_empty(self):
        """Test from_dict with empty dict uses all defaults."""
        metadata = MediaMetadata.from_dict({})
        assert metadata.title == ""
        assert metadata.season == 0

    def test_to_dict_from_dict_roundtrip(self):
        """Test roundtrip conversion."""
        original = MediaMetadata(
            title="Roundtrip",
            season=1,
            episode=2,
            genre="Action",
            year=2024,
            collection="Test",
        )
        restored = MediaMetadata.from_dict(original.to_dict())
        assert restored == original


class TestMediaFile:
    """Tests for MediaFile dataclass."""

    def test_from_path_with_path_object(self, tmp_path):
        """Test from_path with Path object."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()
        media_file = MediaFile.from_path(file_path)
        assert media_file.path == file_path
        assert media_file.original_name == "test.mp4"

    def test_from_path_with_string(self, tmp_path):
        """Test from_path with string path."""
        file_path = tmp_path / "test.mkv"
        file_path.touch()
        media_file = MediaFile.from_path(str(file_path))
        assert media_file.path == file_path
        assert media_file.original_name == "test.mkv"

    def test_extension_property_lowercase(self, tmp_path):
        """Test extension property returns lowercase."""
        file_path = tmp_path / "test.MP4"
        file_path.touch()
        media_file = MediaFile.from_path(file_path)
        assert media_file.extension == ".mp4"

    def test_extension_property_various(self, tmp_path):
        """Test extension property for various extensions."""
        for ext in [".mp4", ".mkv", ".m4v", ".avi"]:
            file_path = tmp_path / f"test{ext}"
            file_path.touch()
            media_file = MediaFile.from_path(file_path)
            assert media_file.extension == ext

    def test_default_metadata(self, tmp_path):
        """Test default metadata is empty MediaMetadata."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()
        media_file = MediaFile.from_path(file_path)
        assert media_file.metadata == MediaMetadata()

    def test_default_selected_true(self, tmp_path):
        """Test selected defaults to True."""
        file_path = tmp_path / "test.mp4"
        file_path.touch()
        media_file = MediaFile.from_path(file_path)
        assert media_file.selected is True


class TestRenameResult:
    """Tests for RenameResult dataclass."""

    def test_success_result(self, tmp_path):
        """Test successful rename result."""
        original = tmp_path / "old.mp4"
        new = tmp_path / "new.mp4"
        result = RenameResult(
            success=True,
            original_path=original,
            new_path=new,
        )
        assert result.success is True
        assert result.original_path == original
        assert result.new_path == new
        assert result.error is None

    def test_failure_result(self, tmp_path):
        """Test failed rename result."""
        original = tmp_path / "old.mp4"
        result = RenameResult(
            success=False,
            original_path=original,
            error="Permission denied",
        )
        assert result.success is False
        assert result.error == "Permission denied"
        assert result.new_path is None

    def test_message_success_with_path(self, tmp_path):
        """Test message property for success with new_path."""
        result = RenameResult(
            success=True,
            original_path=tmp_path / "old.mp4",
            new_path=tmp_path / "new.mp4",
        )
        assert result.message == "Renamed to new.mp4"

    def test_message_success_without_path(self, tmp_path):
        """Test message property for success without new_path."""
        result = RenameResult(
            success=True,
            original_path=tmp_path / "old.mp4",
        )
        assert result.message == "Renamed"

    def test_message_failure_with_error(self, tmp_path):
        """Test message property for failure with error."""
        result = RenameResult(
            success=False,
            original_path=tmp_path / "old.mp4",
            error="File not found",
        )
        assert result.message == "Failed: File not found"

    def test_message_failure_without_error(self, tmp_path):
        """Test message property for failure without error."""
        result = RenameResult(
            success=False,
            original_path=tmp_path / "old.mp4",
        )
        assert result.message == "Failed"


class TestMetadataUpdateResult:
    """Tests for MetadataUpdateResult dataclass."""

    def test_success_result(self, tmp_path):
        """Test successful update result."""
        result = MetadataUpdateResult(
            success=True,
            file_path=tmp_path / "test.mp4",
        )
        assert result.success is True
        assert result.error is None

    def test_failure_result(self, tmp_path):
        """Test failed update result."""
        result = MetadataUpdateResult(
            success=False,
            file_path=tmp_path / "test.mp4",
            error="Write failed",
        )
        assert result.success is False
        assert result.error == "Write failed"

    def test_message_success(self, tmp_path):
        """Test message property for success."""
        result = MetadataUpdateResult(
            success=True,
            file_path=tmp_path / "test.mp4",
        )
        assert result.message == "Updated"

    def test_message_failure_with_error(self, tmp_path):
        """Test message property for failure with error."""
        result = MetadataUpdateResult(
            success=False,
            file_path=tmp_path / "test.mp4",
            error="Disk full",
        )
        assert result.message == "Failed: Disk full"

    def test_message_failure_without_error(self, tmp_path):
        """Test message property for failure without error."""
        result = MetadataUpdateResult(
            success=False,
            file_path=tmp_path / "test.mp4",
        )
        assert result.message == "Failed"
