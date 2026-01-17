"""PySide6-based GUI for Media Organizer."""

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QColor, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig
from ..core.metadata import MetadataManager
from ..core.renamer import MediaRenamer
from ..core.scanner import MediaScanner
from ..logging_config import get_logger
from ..models import Genre, MediaFile, MediaMetadata

# Dark theme stylesheet
DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #e0e0e0;
}
QGroupBox {
    border: 1px solid #3a3a4e;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QPushButton {
    background-color: #7c3aed;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    color: white;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #8b5cf6;
}
QPushButton:pressed {
    background-color: #6d28d9;
}
QPushButton:disabled {
    background-color: #3a3a4e;
    color: #666;
}
QLineEdit, QSpinBox, QComboBox {
    background-color: #2a2a3e;
    border: 1px solid #3a3a4e;
    border-radius: 4px;
    padding: 6px;
    color: #e0e0e0;
}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #7c3aed;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #2a2a3e;
    border: 1px solid #3a3a4e;
    selection-background-color: #7c3aed;
}
QTableWidget {
    background-color: #2a2a3e;
    alternate-background-color: #252535;
    border: 1px solid #3a3a4e;
    border-radius: 4px;
    gridline-color: #3a3a4e;
}
QTableWidget::item {
    padding: 4px;
}
QTableWidget::item:selected {
    background-color: #7c3aed;
}
QHeaderView::section {
    background-color: #1e1e2e;
    border: none;
    border-bottom: 1px solid #3a3a4e;
    padding: 8px;
    font-weight: bold;
}
QTreeView {
    background-color: #2a2a3e;
    border: 1px solid #3a3a4e;
    border-radius: 4px;
}
QTreeView::item:selected {
    background-color: #7c3aed;
}
QStatusBar {
    background-color: #1e1e2e;
    border-top: 1px solid #3a3a4e;
}
QToolBar {
    background-color: #1e1e2e;
    border-bottom: 1px solid #3a3a4e;
    spacing: 8px;
    padding: 4px;
}
QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 6px;
    color: #e0e0e0;
}
QToolButton:hover {
    background-color: #3a3a4e;
}
QCheckBox {
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #3a3a4e;
    background-color: #2a2a3e;
}
QCheckBox::indicator:checked {
    background-color: #7c3aed;
    border-color: #7c3aed;
}
QSplitter::handle {
    background-color: #3a3a4e;
}
QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 12px;
    border-radius: 6px;
}
QScrollBar::handle:vertical {
    background-color: #3a3a4e;
    border-radius: 6px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #4a4a5e;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #1e1e2e;
    height: 12px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background-color: #3a3a4e;
    border-radius: 6px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #4a4a5e;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QLabel {
    color: #e0e0e0;
}
"""


class ScanWorker(QThread):
    """Background worker for scanning directories."""

    finished = Signal(list)  # Emits list of MediaFile

    def __init__(self, scanner: MediaScanner, directory: Path) -> None:
        super().__init__()
        self._scanner = scanner
        self._directory = directory

    def run(self) -> None:
        files = self._scanner.scan_directory(self._directory)
        self.finished.emit(files)


class RenameWorker(QThread):
    """Background worker for renaming files."""

    progress = Signal(int, str)  # row index, status message
    finished = Signal()

    def __init__(
        self,
        files: list[tuple[int, MediaFile]],
        renamer: MediaRenamer,
        season: int,
        episode: int,
        episodic: bool,
    ) -> None:
        super().__init__()
        self._files = files  # List of (row_index, MediaFile)
        self._renamer = renamer
        self._season = season
        self._episode = episode
        self._episodic = episodic

    def run(self) -> None:
        current_episode = self._episode
        for row_index, media_file in self._files:
            self.progress.emit(row_index, "Processing...")
            result = self._renamer.rename_file(
                media_file.path,
                self._season,
                current_episode,
                self._episodic,
            )
            if result.success:
                self.progress.emit(row_index, "Renamed")
                if self._episodic:
                    current_episode += 1
            else:
                self.progress.emit(row_index, f"Failed: {result.error}")
        self.finished.emit()


class MetadataWorker(QThread):
    """Background worker for updating metadata."""

    progress = Signal(int, str)  # row index, status message
    finished = Signal()

    def __init__(
        self,
        files: list[tuple[int, MediaFile]],
        manager: MetadataManager,
        metadata: MediaMetadata,
    ) -> None:
        super().__init__()
        self._files = files  # List of (row_index, MediaFile)
        self._manager = manager
        self._base_metadata = metadata

    def run(self) -> None:
        for i, (row_index, media_file) in enumerate(self._files):
            self.progress.emit(row_index, "Updating...")
            # Create metadata with incrementing episode number
            metadata = MediaMetadata(
                title=self._base_metadata.title,
                season=self._base_metadata.season,
                episode=self._base_metadata.episode + i,
                genre=self._base_metadata.genre,
                year=self._base_metadata.year,
            )
            result = self._manager.update_metadata(media_file.path, metadata)
            status = "Updated" if result.success else f"Failed: {result.error}"
            self.progress.emit(row_index, status)
        self.finished.emit()


class MediaOrganizerWindow(QMainWindow):
    """Main window for the Media Organizer GUI."""

    def __init__(self, root: Path, config: Optional[AppConfig] = None) -> None:
        super().__init__()
        self._config = config or AppConfig()
        self._logger = get_logger("gui")
        self._root = root

        # Business logic components
        self._scanner = MediaScanner(self._config)
        self._metadata_manager = MetadataManager(config=self._config)

        # Application state
        self._media_files: list[MediaFile] = []
        self._current_dir: Optional[Path] = None
        self._worker: Optional[QThread] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the main UI layout."""
        self.setWindowTitle("Media Organizer")
        self.setMinimumSize(1000, 600)

        # Enable drag & drop
        self.setAcceptDrops(True)

        # Create toolbar
        self._create_toolbar()

        # Central widget with splitter for 2 panels
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        # Create panels
        splitter.addWidget(self._create_left_panel())
        splitter.addWidget(self._create_right_panel())

        # Set initial sizes (40%, 60%)
        splitter.setSizes([400, 600])

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._update_status("Ready")

    def _create_toolbar(self) -> None:
        """Create the main toolbar with action buttons."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Browse action - change root folder
        browse_icon = self.style().standardIcon(QStyle.SP_DirIcon)
        self._browse_action = QAction(browse_icon, "Browse", self)
        self._browse_action.setToolTip("Select root folder for directory browser")
        self._browse_action.triggered.connect(self._on_browse_clicked)
        toolbar.addAction(self._browse_action)

        # Scan action
        scan_icon = self.style().standardIcon(QStyle.SP_FileDialogContentsView)
        self._scan_action = QAction(scan_icon, "Scan", self)
        self._scan_action.setToolTip("Scan selected directory for media files")
        self._scan_action.setEnabled(False)
        self._scan_action.triggered.connect(self._on_scan_clicked)
        toolbar.addAction(self._scan_action)

        toolbar.addSeparator()

        # Rename action
        rename_icon = self.style().standardIcon(QStyle.SP_FileDialogDetailedView)
        self._rename_action = QAction(rename_icon, "Rename", self)
        self._rename_action.setToolTip("Rename selected files")
        self._rename_action.setEnabled(False)
        self._rename_action.triggered.connect(self._on_rename_clicked)
        toolbar.addAction(self._rename_action)

        # Metadata action
        meta_icon = self.style().standardIcon(QStyle.SP_FileDialogInfoView)
        self._metadata_action = QAction(meta_icon, "Metadata", self)
        self._metadata_action.setToolTip("Update metadata for selected files")
        self._metadata_action.setEnabled(False)
        self._metadata_action.triggered.connect(self._on_metadata_clicked)
        toolbar.addAction(self._metadata_action)

        toolbar.addSeparator()

        # Refresh action
        refresh_icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        self._refresh_action = QAction(refresh_icon, "Refresh", self)
        self._refresh_action.setToolTip("Refresh current directory")
        self._refresh_action.setEnabled(False)
        self._refresh_action.triggered.connect(self._on_scan_clicked)
        toolbar.addAction(self._refresh_action)

        # Spacer to push directory label to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)

        # Directory path label
        self._dir_label = QLabel("No folder selected")
        self._dir_label.setStyleSheet("color: #888; padding-right: 8px;")
        toolbar.addWidget(self._dir_label)

        # Close button (styled red to stand out)
        close_icon = self.style().standardIcon(QStyle.SP_TitleBarCloseButton)
        self._close_button = QToolButton()
        self._close_button.setIcon(close_icon)
        self._close_button.setText("Close")
        self._close_button.setToolTip("Close application")
        self._close_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._close_button.setStyleSheet("""
            QToolButton {
                background-color: #8b2942;
                color: #ffffff;
                border: 1px solid #a33a52;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QToolButton:hover {
                background-color: #a33a52;
                border-color: #c44a62;
            }
            QToolButton:pressed {
                background-color: #6b1932;
            }
        """)
        self._close_button.clicked.connect(self.close)
        toolbar.addWidget(self._close_button)

    def _create_left_panel(self) -> QWidget:
        """Create the input form panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Title input
        layout.addWidget(QLabel("Title:"))
        self._title_input = QLineEdit()
        layout.addWidget(self._title_input)

        # Genre select
        layout.addWidget(QLabel("Genre:"))
        self._genre_combo = QComboBox()
        self._genre_combo.addItem("", "")  # Empty option
        for value, label in Genre.choices():
            self._genre_combo.addItem(label, value)
        layout.addWidget(self._genre_combo)

        # Year input
        layout.addWidget(QLabel("Year:"))
        self._year_spin = QSpinBox()
        self._year_spin.setRange(1900, 2100)
        self._year_spin.setValue(self._config.default_year)
        layout.addWidget(self._year_spin)

        # Sequence series group
        sequence_group = QGroupBox("Episode Numbering")
        sequence_layout = QVBoxLayout(sequence_group)

        self._sequence_check = QCheckBox("Sequence Series?")
        self._sequence_check.toggled.connect(self._on_sequence_toggled)
        sequence_layout.addWidget(self._sequence_check)

        # Season/Episode row
        se_layout = QHBoxLayout()

        se_layout.addWidget(QLabel("Season:"))
        self._season_spin = QSpinBox()
        self._season_spin.setRange(1, 99)
        self._season_spin.setValue(self._config.default_season)
        self._season_spin.setEnabled(False)
        se_layout.addWidget(self._season_spin)

        se_layout.addWidget(QLabel("Episode:"))
        self._episode_spin = QSpinBox()
        self._episode_spin.setRange(1, 999)
        self._episode_spin.setValue(self._config.default_episode)
        self._episode_spin.setEnabled(False)
        se_layout.addWidget(self._episode_spin)

        sequence_layout.addLayout(se_layout)

        # Episode padding row
        padding_layout = QHBoxLayout()
        padding_layout.addWidget(QLabel("Episode Padding:"))
        self._padding_combo = QComboBox()
        self._padding_combo.addItem("2 digits (EP01)", 2)
        self._padding_combo.addItem("3 digits (EP001)", 3)
        # Set default to config value
        default_index = 0 if self._config.episode_padding == 2 else 1
        self._padding_combo.setCurrentIndex(default_index)
        self._padding_combo.setEnabled(False)
        padding_layout.addWidget(self._padding_combo)
        sequence_layout.addLayout(padding_layout)

        layout.addWidget(sequence_group)

        layout.addStretch()
        return panel

    def _create_right_panel(self) -> QWidget:
        """Create the file list panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Select All checkbox row
        select_layout = QHBoxLayout()
        self._select_all_checkbox = QCheckBox("Select All")
        self._select_all_checkbox.setChecked(True)
        self._select_all_checkbox.stateChanged.connect(self._on_select_all_changed)
        select_layout.addWidget(self._select_all_checkbox)
        select_layout.addStretch()
        layout.addLayout(select_layout)

        # File table with enhanced columns
        self._file_table = QTableWidget()
        self._file_table.setColumnCount(5)
        self._file_table.setHorizontalHeaderLabels(
            ["", "Name", "Extension", "Size", "Status"]
        )
        self._file_table.setAlternatingRowColors(True)
        self._file_table.setSortingEnabled(True)

        # Column sizing
        header = self._file_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Checkbox
        self._file_table.setColumnWidth(0, 30)
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Extension
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Size
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status

        layout.addWidget(self._file_table, stretch=1)

        return panel

    def _on_browse_clicked(self) -> None:
        """Handle browse button click to select folder and scan it."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Scan",
            str(self._root),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if folder:
            self._current_dir = Path(folder)
            self._on_folder_selected()
            self._on_scan_clicked()

    def _on_folder_selected(self) -> None:
        """Enable folder-dependent actions and update UI when a folder is selected."""
        self._scan_action.setEnabled(True)
        self._refresh_action.setEnabled(True)
        self._dir_label.setText(str(self._current_dir))

    def _on_sequence_toggled(self, checked: bool) -> None:
        """Handle sequence series checkbox toggle."""
        self._season_spin.setEnabled(checked)
        self._episode_spin.setEnabled(checked)
        self._padding_combo.setEnabled(checked)

    def _on_select_all_changed(self, state: int) -> None:
        """Handle Select All checkbox state change."""
        check_state = Qt.Checked if state == Qt.Checked.value else Qt.Unchecked
        for i in range(self._file_table.rowCount()):
            item = self._file_table.item(i, 0)
            if item:
                item.setCheckState(check_state)

    def _get_selected_files(self) -> list[tuple[int, MediaFile]]:
        """Return list of (row_index, MediaFile) for checked rows."""
        selected = []
        for i in range(self._file_table.rowCount()):
            item = self._file_table.item(i, 0)
            if item and item.checkState() == Qt.Checked:
                selected.append((i, self._media_files[i]))
        return selected

    def _cleanup_worker(self) -> None:
        """Clean up any existing worker thread."""
        if self._worker is not None:
            self._worker.wait()
            self._worker.deleteLater()
            self._worker = None

    def _on_scan_clicked(self) -> None:
        """Handle scan button click."""
        if not self._current_dir:
            self._update_status("Please select a directory first")
            return

        self._update_status(f"Scanning {self._current_dir}...")
        self._scan_action.setEnabled(False)

        self._cleanup_worker()
        self._worker = ScanWorker(self._scanner, self._current_dir)
        self._worker.finished.connect(self._on_scan_finished)
        self._worker.start()

    def _on_scan_finished(self, files: list[MediaFile]) -> None:
        """Handle scan completion."""
        self._cleanup_worker()
        self._media_files = files
        self._scan_action.setEnabled(True)

        # Disable sorting while populating
        self._file_table.setSortingEnabled(False)

        # Populate table with 5 columns
        self._file_table.setRowCount(len(files))
        for i, media_file in enumerate(files):
            # Checkbox column
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Checked)
            self._file_table.setItem(i, 0, checkbox_item)

            # Name column (without extension)
            name_item = QTableWidgetItem(media_file.path.stem)
            self._file_table.setItem(i, 1, name_item)

            # Extension column
            ext_item = QTableWidgetItem(media_file.extension)
            self._file_table.setItem(i, 2, ext_item)

            # Size column (formatted)
            size = media_file.path.stat().st_size
            size_item = QTableWidgetItem(self._format_file_size(size))
            self._file_table.setItem(i, 3, size_item)

            # Status column with color
            status_item = QTableWidgetItem("Pending")
            status_item.setForeground(QColor("#fbbf24"))  # Yellow
            self._file_table.setItem(i, 4, status_item)

        # Re-enable sorting
        self._file_table.setSortingEnabled(True)

        # Reset Select All checkbox
        self._select_all_checkbox.setChecked(True)

        # Enable toolbar actions
        has_files = len(files) > 0
        self._rename_action.setEnabled(has_files)
        self._metadata_action.setEnabled(has_files)

        self._update_status(f"Found {len(files)} media files")

    def _on_rename_clicked(self) -> None:
        """Handle rename button click."""
        if not self._media_files:
            return

        selected_files = self._get_selected_files()
        if not selected_files:
            self._update_status("No files selected")
            return

        title = self._title_input.text()
        if not title:
            self._update_status("Please enter a title")
            return

        self._update_status(f"Renaming {len(selected_files)} files...")
        self._set_buttons_enabled(False)

        # Apply selected padding to config
        self._config.episode_padding = self._padding_combo.currentData()
        renamer = MediaRenamer(title, config=self._config)
        self._cleanup_worker()
        self._worker = RenameWorker(
            selected_files,
            renamer,
            self._season_spin.value(),
            self._episode_spin.value(),
            self._sequence_check.isChecked(),
        )
        self._worker.progress.connect(self._on_file_progress)
        self._worker.finished.connect(self._on_rename_finished)
        self._worker.start()

    def _on_rename_finished(self) -> None:
        """Handle rename completion."""
        self._set_buttons_enabled(True)
        self._update_status("Renaming complete")

        # Rescan to refresh file list (cleanup happens in _on_scan_clicked)
        if self._current_dir:
            self._on_scan_clicked()

    def _on_metadata_clicked(self) -> None:
        """Handle metadata update button click."""
        if not self._media_files:
            return

        selected_files = self._get_selected_files()
        if not selected_files:
            self._update_status("No files selected")
            return

        title = self._title_input.text()
        if not title:
            self._update_status("Please enter a title")
            return

        self._update_status(f"Updating metadata for {len(selected_files)} files...")
        self._set_buttons_enabled(False)

        metadata = MediaMetadata(
            title=title,
            season=self._season_spin.value(),
            episode=self._episode_spin.value(),
            genre=self._genre_combo.currentData() or "",
            year=self._year_spin.value(),
        )

        self._cleanup_worker()
        self._worker = MetadataWorker(
            selected_files,
            self._metadata_manager,
            metadata,
        )
        self._worker.progress.connect(self._on_file_progress)
        self._worker.finished.connect(self._on_metadata_finished)
        self._worker.start()

    def _on_metadata_finished(self) -> None:
        """Handle metadata update completion."""
        self._cleanup_worker()
        self._set_buttons_enabled(True)
        self._update_status("Metadata update complete")

    def _on_file_progress(self, row: int, status: str) -> None:
        """Handle file processing progress update."""
        item = self._file_table.item(row, 4)  # Status is column 4
        if item:
            item.setText(status)
            # Color based on status
            if status.startswith("Failed"):
                item.setForeground(QColor("#ef4444"))  # Red
            elif status in ("Renamed", "Updated"):
                item.setForeground(QColor("#22c55e"))  # Green
            else:
                item.setForeground(QColor("#fbbf24"))  # Yellow

    def _set_buttons_enabled(self, enabled: bool) -> None:
        """Enable or disable toolbar actions."""
        self._scan_action.setEnabled(enabled)
        has_files = len(self._media_files) > 0
        self._rename_action.setEnabled(enabled and has_files)
        self._metadata_action.setEnabled(enabled and has_files)

    def _format_file_size(self, size: int) -> str:
        """Format file size in human-readable form."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _update_status(self, message: str) -> None:
        """Update the status bar message."""
        self._status_bar.showMessage(message)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop event."""
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            if path.is_dir():
                self._current_dir = path
                self._on_folder_selected()
                self._on_scan_clicked()
            elif path.is_file() and path.suffix.lower() in self._config.media_extensions:
                # Scan the parent directory
                self._current_dir = path.parent
                self._on_folder_selected()
                self._on_scan_clicked()


def run_gui(root: Path, config: Optional[AppConfig] = None) -> None:
    """Run the PySide6 GUI application.

    Args:
        root: Root directory path for the file browser.
        config: Application configuration. If None, uses defaults.
    """
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLESHEET)
    window = MediaOrganizerWindow(root, config)
    window.show()
    app.exec()
