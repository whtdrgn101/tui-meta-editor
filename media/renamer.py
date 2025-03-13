# media/renamer.py
import os
from pathlib import Path

class MediaRenamer:
    """Class for renaming media files based on patterns."""
    title = ""
    

    def __init__(self, title):
       self.title = title
    
    def rename_file(self, file_path: str, season: int, episode: int) -> bool:
        path, new_filename = self.generate_new_name(file_path, season, episode)
        os.rename(file_path, f"{path}/{new_filename}")
        return True
    
    def generate_new_name(self, file_path: str, season: int, episode: int) -> str:
        file_path = Path(file_path)
        directory = os.path.dirname(file_path)
        extension = file_path.suffix
        
        # Format according to the pattern
        new_name = f"{self.title} S{season:02d} EP{episode:02d}{extension}"
        return directory, new_name
