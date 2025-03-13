# media_organizer/app.py
import argparse
import sys
from pathlib import Path

from ui import run_app
from media import MediaScanner
from media import MediaRenamer
from media import MetadataManager

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Media Organizer - A tool to rename and organize media files."
    )
    
    parser.add_argument(
        "--cli", 
        action="store_true",
        help="Run in command-line mode instead of TUI mode"
    )
    
    parser.add_argument(
        "--scan", 
        metavar="DIR",
        help="Scan directory for media files"
    )
    
    parser.add_argument(
        "--rename", 
        action="store_true",
        help="Rename files according to the pattern"
    )
    
    parser.add_argument(
        "--metadata", 
        action="store_true",
        help="Update metadata for media files"
    )
    
    parser.add_argument(
        "--preview", 
        action="store_true",
        help="Preview changes without applying them"
    )
    
    return parser.parse_args()

def cli_mode(args):
    """Run in command-line mode."""
    scanner = MediaScanner()
    renamer = MediaRenamer("test1")
    metadata_manager = MetadataManager()
    
    # Scan directory if provided
    if args.scan:
        print(f"Scanning directory: {args.scan}")
        scan_path = Path(args.scan)
        
        if not scan_path.exists() or not scan_path.is_dir():
            print(f"Error: {args.scan} is not a valid directory")
            return 1
            
        media_files = scanner.scan_directory(args.scan)
        print(f"Found {len(media_files)} media files")
        
        if not media_files:
            return 0
            
        # Process files
        for file_path in media_files:
            original_name = Path(file_path).name
            new_name = renamer.generate_new_name(file_path)
            
            # Preview changes
            if args.preview or not (args.rename or args.metadata):
                print(f"Original: {original_name}")
                print(f"New name: {new_name}")
                print("-" * 50)
            
            # Rename files if requested
            if args.rename and not args.preview:
                try:
                    file_dir = Path(file_path).parent
                    new_path = file_dir / new_name
                    Path(file_path).rename(new_path)
                    print(f"Renamed: {original_name} -> {new_name}")
                    
                    # Update file_path to the new path for metadata updates
                    file_path = str(new_path)
                except Exception as e:
                    print(f"Error renaming {original_name}: {e}")
            
            # Update metadata if requested
            if args.metadata and not args.preview:
                try:
                    # Extract info from the new filename
                    title, season, episode = renamer.extract_info_from_filename(new_name)
                    metadata = {
                        "title": title,
                        "season": season,
                        "episode": episode
                    }
                    
                    success = metadata_manager.update_metadata(file_path, metadata)
                    if success:
                        print(f"Updated metadata for {Path(file_path).name}")
                    else:
                        print(f"Failed to update metadata for {Path(file_path).name}")
                except Exception as e:
                    print(f"Error updating metadata for {Path(file_path).name}: {e}")
    
    return 0

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Run in CLI mode if requested
    if args.cli or args.scan:
        return cli_mode(args)
    
    # Otherwise, run in TUI mode
    try:
        run_app()
        return 0
    except Exception as e:
        print(f"Error running TUI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
