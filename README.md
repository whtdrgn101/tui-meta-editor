# Media Organizer

A desktop application for organizing media files by renaming and updating metadata. Built to assist with ripping and metadata editing of TV series, ensuring consistent file naming and metadata conventions when converting DVDs and Blu-Ray discs for media servers.

## Features

- **GUI Interface**: Modern dark-themed PySide6 desktop application
- **Batch Renaming**: Rename media files with consistent naming patterns
- **Metadata Editing**: Update metadata for MP4 and MKV files
- **Episode Sequencing**: Automatic season/episode numbering
- **Genre Support**: Set genre metadata from predefined categories
- **Drag & Drop**: Drop folders or media files directly onto the application
- **Format Support**: Works with MP4 and MKV media files

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- [MKVToolNix](https://mkvtoolnix.download/downloads.html) - Required for editing MKV file metadata

### Installing uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Installing MKVToolNix

- **macOS**: `brew install mkvtoolnix`
- **Ubuntu/Debian**: `sudo apt install mkvtoolnix`
- **Windows**: Download from [MKVToolNix downloads](https://mkvtoolnix.download/downloads.html#windows)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd tui-meta-editor
   ```

2. Install dependencies with uv:
   ```bash
   uv sync
   ```

3. For development (includes test dependencies):
   ```bash
   uv sync --dev
   ```

## Running the Application

### GUI Mode (Default)

```bash
uv run python -m media_organizer
```

### With Options

```bash
# Specify a root directory for the file browser
uv run python -m media_organizer --root /path/to/media

# Enable debug logging
uv run python -m media_organizer --debug
```

### Using the Installed Command

```bash
uv run mediaedit
```

## Usage

1. **Browse**: Click the Browse button to select a root folder
2. **Scan**: After selecting a folder, click Scan to find media files
3. **Configure**: Set title, genre, year, and episode numbering options in the left panel
4. **Select Files**: Check the files you want to process in the file table
5. **Rename/Metadata**: Use the Rename or Metadata buttons to process selected files

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_gui.py

# Run specific test class
uv run pytest tests/test_gui.py::TestMediaOrganizerWindowToolbar
```

## Test Coverage

Generate a coverage report:

```bash
# Terminal report with missing lines
uv run pytest --cov=media_organizer --cov-report=term-missing

# HTML report (opens in browser)
uv run pytest --cov=media_organizer --cov-report=html
# Then open htmlcov/index.html
```

Current coverage: **99%**

## Project Structure

```
media_organizer/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── config.py            # Application configuration
├── logging_config.py    # Logging setup
├── models.py            # Data models (MediaFile, MediaMetadata, Genre)
├── protocols.py         # Protocol definitions
├── core/
│   ├── metadata.py      # Metadata management
│   ├── renamer.py       # File renaming logic
│   └── scanner.py       # Media file scanner
├── editors/
│   ├── mkv_editor.py    # MKV metadata editor (uses mkvpropedit)
│   └── mp4_editor.py    # MP4 metadata editor (uses mutagen)
└── ui/
    └── gui.py           # PySide6 GUI application
```

## Configuration

The application uses sensible defaults but can be configured through `AppConfig`:

- **Media Extensions**: `.mp4`, `.mkv`
- **Default Year**: Current year
- **Default Season**: 1
- **Default Episode**: 1

## License

MIT License - See LICENSE file for details.

## Author

Timothy A. DeWees
