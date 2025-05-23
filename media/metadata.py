# media_organizer/media/metadata.py
from typing import Dict, Optional, Any
import os
from pathlib import Path
import subprocess
from media import MediaRenamer

class MetadataManager:
    """Class for managing metadata of media files."""
    
    def __init__(self):
        """Initialize the metadata manager."""
        # You'll need to implement this with appropriate libraries
        pass
    
    def read_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Read metadata from a media file.
        
        Args:
            file_path: Path to the media file
            
        Returns:
            Dictionary containing metadata
        """
        # STUB: Implement media metadata extraction
        # For MP4/M4V files you might use mutagen or similar
        # For MKV files you might need specialized tools
        
        print(f"Reading metadata from {file_path}")
        
        # This should be replaced with actual implementation
        return {
            "title": "",
            "season": 0,
            "episode": 0,
            "genre": "",
            "collection": ""
        }
    
    def update_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata of a media file.
        
        Args:
            file_path: Path to the media file
            metadata: Dictionary containing metadata to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            # STUB: Implement media metadata writing
            # Different file types require different approaches
            
            if file_ext in ['.mp4', '.m4v']:
                # Implement MP4/M4V metadata writing
                return self._update_mp4_metadata(file_path, metadata)
            elif file_ext == '.mkv':
                # Implement MKV metadata writing
                return self._update_mkv_metadata(file_path, metadata)
            else:
                print(f"Unsupported file type: {file_ext}")
                return False
                
        except Exception as e:
            print(f"Error updating metadata: {e}")
            return False
    
    def _update_mp4_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        
        from mutagen.mp4 import MP4
        
        try:
            mp4 = MP4(file_path)
              
            # Update title
            if "title" in metadata:
                renamer = MediaRenamer(metadata['title'])
                showTitle = renamer.generate_episode_name(metadata['season'], metadata['episode'])
                mp4['\xa9nam'] = showTitle
                
            # Update TV show info
            if "season" in metadata and "episode" in metadata:
                # Format for TV shows: [season number, episode number, episode ID]
                mp4['tvsn'] = [metadata["season"]]
                mp4['tves'] = [metadata["episode"]]

            if "genre" in metadata:
                mp4['\xa9gen'] = metadata["genre"]
            
            if "year" in metadata:
                mp4['\xa9day'] = [str(metadata["year"])]
                
            # Save changes
            mp4.save()
            return True
        except Exception as e:
            print(f"Error updating MP4 metadata: {e}")
            return False
    
    def _update_mkv_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:

        if "title" in metadata:
            try:
                renamer = MediaRenamer(metadata['title'])
                showTitle = renamer.generate_episode_name(metadata['season'], metadata['episode'])
                output = subprocess.run(["mkvpropedit", file_path, '-s', f"title=\"{showTitle}\""], capture_output=True, text=True)
            except Exception as ex:
                print(ex)
        
        # Return True to simulate success in the stub
        return True
