# media_organizer/app.py
import sys
from pathlib import Path
from ui import run_app
from media import MediaScanner
from media import MediaRenamer
from media import MetadataManager
import click

@click.command()
@click.option('--root', default='F:', help='Root path to use for directory truee')
def main(root: str = "F:"):
    
    # Otherwise, run in TUI mode
    try:
        run_app(root)
        return 0
    except Exception as e:
        print(f"Error running TUI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
