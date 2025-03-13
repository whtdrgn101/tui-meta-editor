# __init__.py
"""
Media Organizer

A tool to organize media files by renaming them according to a consistent pattern
and updating their metadata.

This package provides both a TUI (Text User Interface) and a CLI (Command Line Interface)
for managing your media files.
"""

__version__ = '0.1.0'
__author__ = 'Timothy A. DeWees'
__license__ = 'MIT'

# Import main components for easier access
from app import main
from ui.tui import run_app
from media.scanner import MediaScanner
from media.renamer import MediaRenamer
from media.metadata import MetadataManager

# Define what gets imported with "from media_organizer import *"
__all__ = [
    'main',
    'run_app',
    'MediaScanner',
    'MediaRenamer',
    'MetadataManager',
]
