# media_organizer/media/metadata.py
from typing import Dict, Optional, Any
import os
from pathlib import Path

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
                mp4['\xa9nam'] = metadata["title"]
                
            # Update TV show info
            if "season" in metadata and "episode" in metadata:
                # Format for TV shows: [season number, episode number, episode ID]
                mp4['tvsn'] = [metadata["season"]]
                mp4['tves'] = [metadata["episode"]]
                
            # Save changes
            mp4.save()
            return True
        except Exception as e:
            print(f"Error updating MP4 metadata: {e}")
            return False
        
        
        print(f"Updating MP4 metadata for {file_path}")
        print(f"  Title: {metadata.get('title', 'N/A')}")
        print(f"  Season: {metadata.get('season', 'N/A')}")
        print(f"  Episode: {metadata.get('episode', 'N/A')}")
        
        # Return True to simulate success in the stub
        return True
    
    def _update_mkv_metadata(self, file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for MKV files.
        
        Args:
            file_path: Path to the MKV file
            metadata: Dictionary containing metadata to update
            
        Returns:
            True if successful, False otherwise
        """
        if "title" in metadata:
            os.system(f"mkvpropedit \"{file_path}\" -s title=\"{metadata["title"]}\"")
        
        print(f"Updating MKV metadata for {file_path}")
        print(f"  Title: {metadata.get('title', 'N/A')}")
        print(f"  Season: {metadata.get('season', 'N/A')}")
        print(f"  Episode: {metadata.get('episode', 'N/A')}")
        
        # Return True to simulate success in the stub
        return True
