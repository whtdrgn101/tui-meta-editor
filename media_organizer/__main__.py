#!/usr/bin/env python3
"""Entry point for Media Organizer application."""

import sys
from pathlib import Path

import click

from .config import AppConfig
from .logging_config import setup_logging


@click.command()
@click.option(
    "--root",
    default=None,
    help="Root path for directory tree",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
def main(root: Path | None, debug: bool) -> int:
    """Media Organizer - Rename and update metadata for media files."""
    # Load configuration
    config = AppConfig.from_env()

    # Setup logging
    log_level = "DEBUG" if debug else config.log_level
    setup_logging(level=log_level)

    # Determine root path
    root_path = root if root else config.default_root

    try:
        from .ui.gui import run_gui

        run_gui(root_path, config)
        return 0

    except ImportError as e:
        if "PySide6" in str(e):
            click.echo(
                "Error: PySide6 is required. "
                "Install with: pip install PySide6",
                err=True,
            )
        else:
            click.echo(f"Import error: {e}", err=True)
        return 1

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
