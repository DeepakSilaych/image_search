"""
Main application window
"""
from pathlib import Path

from PyQt6.QtCore import Qt, QThread, QTimer
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QStackedWidget, QProgressBar,
    QFileDialog, QApplication, QMessageBox
)

from .theme import STYLESHEET, COLORS
from .image_grid import ImageGrid
from .image_preview import ImagePreviewDialog
from .settings_panel import SettingsPanel
from .workers import SearchWorker, IndexWorker, BrowseWorker
from .image_scanner import ImageScanner, get_macos_image_locations


class MainWindow(QMainWindow):
    """Main application window with search, browse, and settings tabs"""
    
    def __init__(self, base_dir: Path = None):
        super().__init__()
        
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent.parent
        self.engine = None
        self._search_thread = None
        self._index_thread = None
        self._scan_thread = None
        self._browse_thread = None
        self._is_first_launch = True
        
        self.setWindowTitle("Image Search")
        self.setMinimumSize(1100, 750)
        self.resize(1400, 900)
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Apply theme
        self.setStyleSheet(STYLESHEET)
        
        self._setup_ui()
        self._setup_shortcuts()
        
        # Initialize engine after UI is ready
        QTimer.singleShot(100, self._init_engine)
        
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header with tabs and search
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Main content area
        self.stack = QStackedWidget()
        
        # Search/Browse view
        self.search_view = self._create_search_view()
        self.stack.addWidget(self.search_view)
        
        # Settings view
        self.settings_panel = SettingsPanel(data_dir=self.base_dir)
        self.settings_panel.faces_updated.connect(self._on_faces_updated)
        self.stack.addWidget(self.settings_panel)
        
        main_layout.addWidget(self.stack, stretch=1)
        
        # Status bar
        self.status_bar = self._create_status_bar()
        main_layout.addWidget(self.status_bar)
        
    def _create_header(self) -> QFrame:
        header = QFrame()
        header.setFixedHeight(140)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-bottom: 1px solid {COLORS['separator']};
            }}
        """)
        
        layout = QVBoxLayout(header)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(16)
        
        # Top row: Title and tabs
        top_row = QHBoxLayout()
        
        # App title
        title_container = QHBoxLayout()
        title_container.setSpacing(12)
        
        # Icon
        icon_label = QLabel("🔍")
        icon_label.setStyleSheet("font-size: 28px;")
        title_container.addWidget(icon_label)
        
        title = QLabel("Image Search")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 700;
            color: {COLORS['text_primary']};
        """)
        title_container.addWidget(title)
        
        top_row.addLayout(title_container)
        top_row.addStretch()
        
        # Tab buttons
        self.tab_buttons = QHBoxLayout()
        self.tab_buttons.setSpacing(4)
        
        self.search_tab = self._create_tab_button("Search", active=True)
        self.search_tab.clicked.connect(lambda: self._switch_tab(0))
        self.tab_buttons.addWidget(self.search_tab)
        
        self.settings_tab = self._create_tab_button("Faces", active=False)
        self.settings_tab.clicked.connect(lambda: self._switch_tab(1))
        self.tab_buttons.addWidget(self.settings_tab)
        
        top_row.addLayout(self.tab_buttons)
        
        # Scan Photos button
        scan_btn = QPushButton("📷 Scan Photos")
        scan_btn.setObjectName("secondaryBtn")
        scan_btn.clicked.connect(self._scan_system_photos)
        top_row.addWidget(scan_btn)
        
        # Add images button
        add_btn = QPushButton("+ Add Images")
        add_btn.clicked.connect(self._add_images_dialog)
        top_row.addWidget(add_btn)
        
        layout.addLayout(top_row)
        
        # Search bar row
        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        
        # Search icon overlay
        search_container = QWidget()
        search_container.setStyleSheet("background: transparent;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchBar")
        self.search_input.setPlaceholderText("Search your photos... (e.g., 'sunset at beach' or 'photos of mom')")
        self.search_input.returnPressed.connect(self._do_search)
        search_layout.addWidget(self.search_input)
        
        search_row.addWidget(search_container, stretch=1)
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.setFixedWidth(100)
        search_btn.clicked.connect(self._do_search)
        search_row.addWidget(search_btn)
        
        layout.addLayout(search_row)
        
        return header
        
    def _create_tab_button(self, text: str, active: bool = False) -> QPushButton:
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setChecked(active)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'%s' % COLORS['bg_tertiary'] if active else 'transparent'};
                color: {'%s' % COLORS['text_primary'] if active else COLORS['text_tertiary']};
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
            }}
        """)
        return btn
        
    def _create_search_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Image grid
        self.image_grid = ImageGrid()
        self.image_grid.image_clicked.connect(self._show_preview)
        layout.addWidget(self.image_grid)
        
        return view
        
    def _create_status_bar(self) -> QFrame:
        bar = QFrame()
        bar.setFixedHeight(36)
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-top: 1px solid {COLORS['separator']};
            }}
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_tertiary']};
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Image count
        self.count_label = QLabel("")
        self.count_label.setObjectName("statusLabel")
        layout.addWidget(self.count_label)
        
        return bar
        
    def _setup_shortcuts(self):
        # Cmd+F to focus search
        focus_search = QShortcut(QKeySequence("Ctrl+F"), self)
        focus_search.activated.connect(lambda: self.search_input.setFocus())
        
        # Escape to clear search
        clear_search = QShortcut(QKeySequence("Escape"), self)
        clear_search.activated.connect(self._clear_search)
        
        # Cmd+O to add images
        add_images = QShortcut(QKeySequence("Ctrl+O"), self)
        add_images.activated.connect(self._add_images_dialog)
        
    def _switch_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        self.search_tab.setChecked(index == 0)
        self.settings_tab.setChecked(index == 1)
        
        # Update tab button styles
        for i, btn in enumerate([self.search_tab, self.settings_tab]):
            active = (i == index)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'%s' % COLORS['bg_tertiary'] if active else 'transparent'};
                    color: {'%s' % COLORS['text_primary'] if active else COLORS['text_tertiary']};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_tertiary']};
                    color: {COLORS['text_primary']};
                }}
            """)
            
    def _init_engine(self):
        """Initialize search engine in background"""
        self.status_label.setText("Loading AI models...")
        QApplication.processEvents()
        
        try:
            from image_search.core import SearchEngine
            
            self.engine = SearchEngine(data_dir=self.base_dir)
            self.status_label.setText("Ready")
            
            # Load existing images
            self._load_indexed_images()
        except Exception as e:
            self.status_label.setText(f"Error: {e}")
            QMessageBox.warning(self, "Initialization Error", str(e))
            
    def _load_indexed_images(self):
        """Load and display all indexed images"""
        if not self.engine:
            return
        
        # Wait for any previous browse to finish
        if self._browse_thread is not None and self._browse_thread.isRunning():
            self._browse_thread.quit()
            self._browse_thread.wait()
            
        self.status_label.setText("Loading images...")
        
        self._browse_thread = QThread()
        self._browse_worker = BrowseWorker(self.engine)
        self._browse_worker.moveToThread(self._browse_thread)
        
        self._browse_thread.started.connect(self._browse_worker.run)
        self._browse_worker.finished.connect(self._on_browse_complete)
        self._browse_worker.finished.connect(self._browse_thread.quit)
        self._browse_worker.finished.connect(lambda: self._browse_thread.wait() if self._browse_thread else None)
        self._browse_worker.error.connect(lambda e: self.status_label.setText(f"Error: {e}"))
        
        self._browse_thread.start()
        
    def _on_browse_complete(self, results: list):
        self.image_grid.display_indexed_images(results)
        self.count_label.setText(f"{len(results)} images")
        self.status_label.setText("Ready")
        
        # Auto-scan on first launch if no images indexed
        if self._is_first_launch and len(results) == 0:
            self._is_first_launch = False
            self._prompt_auto_scan()
        else:
            self._is_first_launch = False
            
    def _prompt_auto_scan(self):
        """Prompt user to scan their photos on first launch"""
        locations = get_macos_image_locations()
        loc_names = [loc.name for loc in locations[:4]]
        
        reply = QMessageBox.question(
            self,
            "Scan Your Photos?",
            f"Would you like to automatically discover and index photos from your Mac?\n\n"
            f"Locations: {', '.join(loc_names)}{'...' if len(locations) > 4 else ''}\n\n"
            f"This may take a few minutes depending on your photo library size.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._scan_system_photos()
            
    def _scan_system_photos(self):
        """Scan macOS standard photo locations"""
        if not self.engine:
            QMessageBox.warning(self, "Not Ready", "Please wait for the engine to initialize.")
            return
            
        self.status_label.setText("Scanning for photos...")
        self.progress_bar.setMaximum(0)  # Indeterminate
        self.progress_bar.show()
        
        # Run scanner in background
        self._scan_thread = QThread()
        self._scanner = ImageScanner(max_images=5000)
        self._scanner.moveToThread(self._scan_thread)
        
        self._scan_thread.started.connect(self._scanner.run)
        self._scanner.progress.connect(self._on_scan_progress)
        self._scanner.finished.connect(self._on_scan_complete)
        self._scanner.finished.connect(self._scan_thread.quit)
        self._scanner.error.connect(lambda e: self.status_label.setText(f"Scan error: {e}"))
        
        self._scan_thread.start()
        
    def _on_scan_progress(self, location: str, count: int):
        self.status_label.setText(f"Scanning {location}... ({count} found)")
        
    def _on_scan_complete(self, image_paths: list):
        self.progress_bar.hide()
        
        if not image_paths:
            self.status_label.setText("No images found")
            QMessageBox.information(
                self, "Scan Complete",
                "No images were found in standard photo locations."
            )
            return
            
        # Ask before indexing
        reply = QMessageBox.question(
            self,
            "Index Photos?",
            f"Found {len(image_paths)} images.\n\n"
            f"Index them now? (This will take ~{len(image_paths) * 0.75 / 60:.0f} minutes)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._index_images(image_paths)
        
    def _do_search(self):
        query = self.search_input.text().strip()
        if not query or not self.engine:
            return
        
        # Wait for any previous search to finish
        if self._search_thread is not None and self._search_thread.isRunning():
            self._search_thread.quit()
            self._search_thread.wait()
            
        self.status_label.setText(f"Searching: {query}")
        
        # Run search in background thread
        self._search_thread = QThread()
        self._search_worker = SearchWorker(self.engine, query, limit=50)
        self._search_worker.moveToThread(self._search_thread)
        
        self._search_thread.started.connect(self._search_worker.run)
        self._search_worker.finished.connect(self._on_search_complete)
        self._search_worker.finished.connect(self._search_thread.quit)
        self._search_worker.finished.connect(self._cleanup_search_thread)
        self._search_worker.error.connect(lambda e: self.status_label.setText(f"Error: {e}"))
        
        self._search_thread.start()
        
    def _cleanup_search_thread(self):
        """Clean up search thread after completion"""
        if self._search_thread is not None:
            self._search_thread.wait()
        
    def _on_search_complete(self, results: list):
        self.image_grid.display_results(results)
        self.count_label.setText(f"{len(results)} results")
        self.status_label.setText("Ready")
        
    def _clear_search(self):
        self.search_input.clear()
        self._load_indexed_images()
        
    def _show_preview(self, path: str, metadata: dict):
        dialog = ImagePreviewDialog(path, metadata, self)
        dialog.exec()
        
    def _add_images_dialog(self):
        if not self.engine:
            QMessageBox.warning(self, "Not Ready", "Please wait for the engine to initialize.")
            return
            
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images",
            str(Path.home() / "Pictures"),
            "Images (*.jpg *.jpeg *.png *.webp *.heic)"
        )
        
        if files:
            self._index_images(files)
            
    def _index_images(self, paths: list):
        """Index images in background"""
        self.status_label.setText("Indexing images...")
        self.progress_bar.setMaximum(len(paths))
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        self._index_thread = QThread()
        self._index_worker = IndexWorker(self.engine, paths)
        self._index_worker.moveToThread(self._index_thread)
        
        self._index_thread.started.connect(self._index_worker.run)
        self._index_worker.progress.connect(self._on_index_progress)
        self._index_worker.finished.connect(self._on_index_complete)
        self._index_worker.finished.connect(self._index_thread.quit)
        self._index_worker.error.connect(lambda e: self.status_label.setText(f"Error: {e}"))
        
        self._index_thread.start()
        
    def _on_index_progress(self, current: int, total: int, path: str):
        self.progress_bar.setValue(current)
        name = Path(path).name
        self.status_label.setText(f"Indexing {current}/{total}: {name}")
        
    def _on_index_complete(self, count: int):
        self.progress_bar.hide()
        self.status_label.setText(f"Indexed {count} images")
        self._load_indexed_images()
        
    def _on_faces_updated(self):
        """Reload engine when faces are updated"""
        if self.engine:
            # Reinitialize face identifier
            try:
                self.engine.embedder.face_identifier._load_from_disk()
                self.engine.embedder.face_identifier._scan_and_update_faces()
                self.status_label.setText("Face database updated")
            except Exception as e:
                self.status_label.setText(f"Error updating faces: {e}")
                
    # Drag and drop support
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            # Check if any URLs are images
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.heic')):
                        event.acceptProposedAction()
                        return
                        
    def dropEvent(self, event: QDropEvent):
        image_paths = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.heic')):
                    image_paths.append(path)
                elif Path(path).is_dir():
                    # Add all images from directory
                    for f in Path(path).rglob("*"):
                        if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.heic'):
                            image_paths.append(str(f))
                            
        if image_paths:
            self._index_images(image_paths)

