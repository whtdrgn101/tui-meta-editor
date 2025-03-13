# media_organizer/media/scanner.py
import os
from pathlib import Path
from typing import List, Set

class MediaScanner:
    """Class for scanning directories to find media files."""
    
    # Define media file extensions we're interested in
    MEDIA_EXTENSIONS = {'.mp4', '.mkv', '.m4v', '.avi'}
    
    def __init__(self):
        self.scanned_files = []
    
    def scan_directory(self, directory_path: str) -> List[str]:
        """
        Scan a directory recursively for media files.
        
        Args:
            directory_path: Path to the directory to scan
            
        Returns:
            List of paths to media files
        """
        self.scanned_files = []
        
        try:
            # Convert to Path object for better cross-platform compatibility
            directory = Path(directory_path)
            
            # Check if directory exists
            if not directory.exists() or not directory.is_dir():
                print(f"Error: {directory_path} is not a valid directory")
                return []
            
            # Walk through the directory recursively
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check if file has a media extension
                    if file_path.suffix.lower() in self.MEDIA_EXTENSIONS:
                        self.scanned_files.append(str(file_path))
            
            return self.scanned_files
            
        except Exception as e:
            print(f"Error scanning directory: {e}")
            return []
    
    def filter_by_extension(self, extension: str) -> List[str]:
        """
        Filter the scanned files by extension.
        
        Args:
            extension: File extension to filter by (with or without dot)
            
        Returns:
            List of paths matching the extension
        """
        if not extension.startswith('.'):
            extension = f".{extension}"
            
        return [f for f in self.scanned_files if Path(f).suffix.lower() == extension.lower()]
    
    def get_file_count(self) -> int:
        """
        Get the count of found media files.
        
        Returns:
            Number of media files found
        """
        return len(self.scanned_files)
