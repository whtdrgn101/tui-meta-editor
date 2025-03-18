# media_organizer/ui/tui.py
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DirectoryTree, Footer, Header, Input, Static
from textual.widgets import Label, DataTable, Select
from textual import work
from textual.coordinate import Coordinate
import os
import asyncio
from pathlib import Path
from media import MediaRenamer, MediaScanner, MetadataManager

class MediaFile:
    def __init__(self, path, original_name, metadata=None):
        self.path = path
        self.original_name = original_name
        self.metadata = metadata or {}

class MediaOrganizerApp(App):
    title = ""
    season = 1
    episode = 1
    
    CSS = """
    Screen {
        background: #0f0f1f;
    }
    
    Header {
        dock: top;
        height: 3;
        background: #3498db;
        color: white;
    }
    
    Footer {
        dock: bottom;
        height: 1;
    }
    
    DirectoryTree {
        width: 30%;
        height: 100%;
        border: solid #3498db;
    }
    
    .container {
        height: 100%;
    }
    .input-container {
        width: 30%;
        height: 100%;
        border: solid #3498db;
    }
    .files-container {
        width: 40%;
        height: 100%;
        border: solid #3498db;
    }
    
    #status-bar {
        height: 1;
        dock: bottom;
        background: #2c3e50;
        color: white;
    }
    
    Button {
        margin: 1 2;
    }
    
    .action-bar {
        height: 3;
        background: #2c3e50;
        color: white;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "rename_files", "Rename Files"),
        ("s", "scan_directory", "Scan Directory"),
    ]

    GENRES = [line.strip() for line in """
        Action
        Adventure
        Animated
        Anime
        Comedy
        Drama
        Fantasy
        Horror
        Musical
        Mystery
        Romance
        Science Fiction
        Sports
        Thriller
        Western
        """.splitlines()]
    GENRES =  list(zip(GENRES, GENRES))
    ROOT = ""

    def __init__(self, root: str):
        super().__init__()
        self.scanner = MediaScanner()
        self.metadata_manager = MetadataManager()
        self.media_files = []
        self.current_dir = None
        self.ROOT = root
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        
        with Horizontal(classes="container"):
            yield DirectoryTree(id="dir-tree", path=self.ROOT)
            with Vertical(classes="input-container"): 
                yield Label("Title:")
                yield Input("", id="title-input")
                yield Label("Genre")
                yield Select[str](id="genre-select", options=self.GENRES)
                yield Label("Season:")
                yield Input("", id="season-input", type="integer")
                yield Label("Episode:")
                yield Input("", id="episode-input", type="integer")
                yield Button("Scan Directory", id="scan-btn", variant="primary")

            with Vertical(classes="files-container"):
                
                with Horizontal(classes="action-bar"):
                    yield Button("Rename All", id="rename-btn", variant="success", disabled=True)
                    yield Button("Update Metadata", id="metadata-btn", variant="warning", disabled=True)

                # Create table for showing files
                table = DataTable(id="files-table")
                table.add_columns("Original Name", "Status")
                yield table
                
                
        
        yield Static("Ready", id="status-bar")
    
    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.query_one("#dir-tree").focus()
    
    def on_directory_tree_directory_selected(self, event) -> None:
        """Handle selection of a directory."""
        self.current_dir = event.path
        self.update_status(f"Selected directory: {self.current_dir}")
    
    def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        button_id = event.button.id
        title_input = self.query_one("#title-input")
        if(title_input):
            self.title = title_input.value
        season_input = self.query_one("#season-input")
        if season_input:
            self.season = int(season_input.value)
        episode_input = self.query_one("#episode-input")
        if(episode_input):
            self.episode = int(episode_input.value)
        genre_select = self.query_one("#genre-select")
        if(genre_select):
            self.genre = genre_select.value

        if button_id == "scan-btn":
            if self.current_dir:
                self.scan_directory(self.current_dir)
                renameBtn = self.query_one("#rename-btn")
                renameBtn.disabled = False
                betadataBtn = self.query_one("#metadata-btn")
                betadataBtn.disabled = False

            else:
                self.update_status("Please select a directory first")
        
        elif button_id == "rename-btn":
            self.rename_files()
        
        elif button_id == "metadata-btn":
            self.update_metadata()
    
    @work
    async def scan_directory(self, directory=None) -> None:
        """Scan the selected directory for media files."""
        directory = directory or self.current_dir
        if not directory:
            self.update_status("No directory selected")
            return
        
        self.update_status(f"Scanning {directory}...")
        
        # Reset media files list
        self.media_files = []
        
        # Scan for media files
        found_files = self.scanner.scan_directory(directory)
        
        # Process each file
        table = self.query_one("#files-table")
        table.clear()
        
        for file_path in found_files:
            original_name = os.path.basename(file_path)
            
            media_file = MediaFile(file_path, original_name)
            self.media_files.append(media_file)
            
            # Add to table
            table.add_row(original_name, "Pending")
        
        self.update_status(f"Found {len(self.media_files)} media files")
    
    @work
    async def rename_files(self) -> None:
        """Rename all scanned files."""
        if not self.media_files:
            self.update_status("No files to rename")
            return
        
        self.update_status("Renaming files...")
        table = self.query_one("#files-table")
    
        renamer = MediaRenamer(self.title)
        cur_episode = self.episode
        for i, media_file in enumerate(self.media_files):
            coord = Coordinate(i,1)
            try:
                
                # Update status in table
                table.update_cell_at(coord, "Processing...")
                await asyncio.sleep(0.1)  # Small delay for UI responsiveness
                
                # Perform the rename
                success = renamer.rename_file(media_file.path, self.season, cur_episode)

                # Update status
                if success:
                    table.update_cell_at(coord, "Renamed")
                    cur_episode = cur_episode + 1
                else:
                    table.update_cell_at(coord, "Failed")
            except Exception as e:
                table.update_cell_at(coord, f"Error: {str(e)}")
        
        self.update_status("Renaming complete")
        self.scan_directory()
    
    @work
    async def update_metadata(self) -> None:
        """Update metadata for all scanned files."""
        if not self.media_files:
            self.update_status("No files to update")
            return
        
        self.update_status("Updating metadata...")
        table = self.query_one("#files-table")
        
        for i, media_file in enumerate(self.media_files):
            coord = Coordinate(i,1)
            try:
                # Update status in table
                table.update_cell_at(coord, "Updating metadata...")
                await asyncio.sleep(0.1)  # Small delay for UI responsiveness
                
                # Update metadata (this will call your implementation)
                metadata = {
                    "title": self.title,
                    "season": self.season, 
                    "episode": i + 1,
                    "genre": self.genre
                }
                success = self.metadata_manager.update_metadata(media_file.path, metadata)
                
                # Update status
                if success:
                    table.update_cell_at(coord, "Updated")
                else:
                    table.update_cell_at(coord, "Failed")
            except Exception as e:
                table.update_cell_at(coord, f"Error: {str(e)}")
        
        self.update_status("Metadata update complete")
    
    def update_status(self, message) -> None:
        """Update the status bar with a message."""
        self.query_one("#status-bar").update(message)

def run_app(root: str):
    """Run the application."""
    app = MediaOrganizerApp(root)
    app.run()

if __name__ == "__main__":
    run_app()
